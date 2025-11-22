"""
State Manager Module
Handles degraded mode state, message caching, and MCP health monitoring
"""
import json
import os
import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, asdict


@dataclass
class PendingMessage:
    """Represents a cached user message"""
    user_message: str
    user_number: str
    timestamp: str
    retry_count: int = 0
    conversation_context: str = "" 

    def to_dict(self):
        return asdict(self)


class StateManager:
    def __init__(self, cache_file: str = "cached_messages.json"):
        self.cache_file = cache_file
        self.degraded_mode = False
        self.pending_messages: List[PendingMessage] = []
        self.mcp_check_interval = 30 
        self.mcp_health_task: Optional[asyncio.Task] = None
        self.max_retry_count = 3
        
        # Initialize cache file if it doesn't exist
        if not os.path.exists(self.cache_file):
            with open(self.cache_file, "w") as f:
                json.dump({
                    "messages": [],
                    "saved_at": datetime.now().isoformat(),
                    "degraded_mode": False
                }, f)
        
        # Callbacks for mode changes
        self.on_degraded_callbacks: List[Callable] = []
        self.on_online_callbacks: List[Callable] = []
        
        # Load existing cache on initialization
        self.load_cache()
    
   
    # Cache Management
    def add_message(self, user_message: str, user_number: str) -> None:
        """Add a message to pending queue"""
        msg = PendingMessage(
            user_message=user_message,
            user_number=user_number,
            timestamp=datetime.now().isoformat()
        )
        self.pending_messages.append(msg)
        self.save_cache()
        print(f"💾 Message cached. Total pending: {len(self.pending_messages)}")
    
    def save_cache(self) -> bool:
        """Save pending messages to file"""
        try:
            data = {
                "messages": [msg.to_dict() for msg in self.pending_messages],
                "saved_at": datetime.now().isoformat(),
                "degraded_mode": self.degraded_mode
            }
            with open(self.cache_file, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"⚠ Failed to save cache: {e}")
            return False
    
    def load_cache(self) -> bool:
        """Load pending messages from file"""
        if not os.path.exists(self.cache_file):
            return False
        
        try:
            with open(self.cache_file, "r") as f:
                data = json.load(f)
            
            self.pending_messages = [
                PendingMessage(**msg) for msg in data.get("messages", [])
            ]
            
            saved_at = data.get("saved_at", "unknown")
            print(f"📂 Loaded {len(self.pending_messages)} messages from cache")
            print(f"   (saved at: {saved_at})")
            return True
        
        except Exception as e:
            print(f"⚠ Failed to load cache: {e}")
            return False
    
    def clear_cache(self) -> None:
        """Clear all pending messages"""
        self.pending_messages.clear()
        self.save_cache()
        print("🗑 Cache cleared")
    
    def get_pending_count(self) -> int:
        """Get count of pending messages"""
        return len(self.pending_messages)
    
    def get_pending_messages(self) -> List[PendingMessage]:
        """Get copy of pending messages"""
        return self.pending_messages.copy()
    
    def remove_message(self, msg: PendingMessage) -> None:
        """Remove a specific message from queue"""
        try:
            self.pending_messages.remove(msg)
            self.save_cache()
        except ValueError:
            pass
    
    def increment_retry(self, msg: PendingMessage) -> bool:
        """Increment retry count. Returns True if max retries reached"""
        msg.retry_count += 1
        if msg.retry_count >= self.max_retry_count:
            print(f"⚠ Message exceeded max retries: {msg.user_message[:50]}...")
            self.remove_message(msg)
            return True
        return False
    
    # Degraded Mode Management
    def enable_degraded_mode(self, reason: str = "") -> None:
        """Switch to degraded mode"""
        if not self.degraded_mode:
            self.degraded_mode = True
            print(f"\n{'='*60}")
            print(f"🔴 DEGRADED MODE ENABLED")
            print(f"📝 Reason: {reason}")
            print(f"{'='*60}\n")
            self.save_cache()
            
            # Trigger callbacks
            for callback in self.on_degraded_callbacks:
                try:
                    callback()
                except Exception as e:
                    print(f"⚠ Callback error: {e}")
    
    def disable_degraded_mode(self) -> None:
        """Switch to normal mode"""
        if self.degraded_mode:
            self.degraded_mode = False
            print(f"\n{'='*60}")
            print("🟢 SYSTEM BACK ONLINE")
            print(f"{'='*60}\n")
            self.save_cache()
            
            # Trigger callbacks
            for callback in self.on_online_callbacks:
                try:
                    callback()
                except Exception as e:
                    print(f"⚠ Callback error: {e}")
    
    def is_degraded(self) -> bool:
        """Check if system is in degraded mode"""
        return self.degraded_mode
    
    def register_degraded_callback(self, callback: Callable) -> None:
        """Register callback for when system goes offline"""
        self.on_degraded_callbacks.append(callback)
    
    def register_online_callback(self, callback: Callable) -> None:
        """Register callback for when system comes online"""
        self.on_online_callbacks.append(callback)
    
    # MCP Error Detection
    def is_mcp_error(self, error: Exception) -> bool:
        """Detect if error is MCP-related"""
        error_text = str(error).lower()
        
        mcp_error_keywords = [
            "timeout", "timed out",
            "connection", "connect",
            "refused", "unavailable",
            "mcp", "server",
            "network", "unreachable",
            "errno", "oserror",
            "clientconnectionerror",
            "cannot connect"
        ]
        
        for keyword in mcp_error_keywords:
            if keyword in error_text:
                print(f"🔍 MCP error detected: '{keyword}' in '{error_text[:100]}'")
                return True
        
        return False
    
    # Status & Reporting
    def get_status(self) -> Dict:
        """Get current system status"""
        return {
            "degraded_mode": self.degraded_mode,
            "pending_messages": len(self.pending_messages),
            "cache_file": self.cache_file,
            "cache_exists": os.path.exists(self.cache_file),
            "mcp_check_interval": self.mcp_check_interval,
            "health_monitor_running": self.mcp_health_task is not None and not self.mcp_health_task.done()
        }
    
    def print_status(self) -> None:
        """Print formatted status report"""
        status = self.get_status()
        print("\n" + "="*50)
        print("📊 SYSTEM STATUS")
        print("="*50)
        print(f"Mode: {'🔴 DEGRADED' if status['degraded_mode'] else '🟢 ONLINE'}")
        print(f"Pending Messages: {status['pending_messages']}")
        print(f"Health Monitor: {'✅ Running' if status['health_monitor_running'] else '❌ Stopped'}")
        print(f"Cache File: {status['cache_file']}")
        print("="*50 + "\n")
    
    # Health Monitor Task Management 
    def set_health_task(self, task: asyncio.Task) -> None:
        """Set the MCP health monitoring task"""
        self.mcp_health_task = task
    
    def cancel_health_task(self) -> None:
        """Cancel the health monitoring task"""
        if self.mcp_health_task and not self.mcp_health_task.done():
            self.mcp_health_task.cancel()
            print("🛑 Health monitor task cancelled")

# Global Instance (Singleton Pattern)
_state_manager_instance: Optional[StateManager] = None


def get_state_manager() -> StateManager:
    """Get or create the global StateManager instance"""
    global _state_manager_instance
    if _state_manager_instance is None:
        _state_manager_instance = StateManager()
    return _state_manager_instance

# Convenience Functions
def is_degraded() -> bool:
    """Quick check if system is in degraded mode"""
    return get_state_manager().is_degraded()


def cache_message(user_message: str, user_number: str) -> None:
    """Quick function to cache a message"""
    get_state_manager().add_message(user_message, user_number)


def get_pending_count() -> int:
    """Quick function to get pending message count"""
    return get_state_manager().get_pending_count()


def enable_degraded(reason: str = "") -> None:
    """Quick function to enable degraded mode"""
    get_state_manager().enable_degraded_mode(reason)


def disable_degraded() -> None:
    """Quick function to disable degraded mode"""
    get_state_manager().disable_degraded_mode()


def is_mcp_error(error: Exception) -> bool:
    """Quick check if error is MCP-related"""
    return get_state_manager().is_mcp_error(error)