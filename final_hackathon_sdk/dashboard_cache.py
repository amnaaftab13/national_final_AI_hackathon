"""
Dashboard Cache Manager - Optimized for Low Latency & Cost Reduction
=====================================================================

Features:
- In-memory caching of dashboard data
- Auto-invalidation on sales/purchase events
- TTL-based expiry for stale data
- Thread-safe operations
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import threading
import json

class DashboardCache:
    """Thread-safe cache manager for dashboard analytics"""
    
    def __init__(self, default_ttl_minutes: int = 60):
        """
        Initialize cache manager
        
        Args:
            default_ttl_minutes: Default cache validity period (60 min = 1 hour)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self.default_ttl = timedelta(minutes=default_ttl_minutes)
        
        print(f"✅ DashboardCache initialized (TTL: {default_ttl_minutes} minutes)")
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached data if valid
        
        Returns:
            Cached data or None if expired/not found
        """
        with self._lock:
            if key not in self._cache:
                print(f"❌ Cache MISS: {key}")
                return None
            
            cached_item = self._cache[key]
            expiry_time = cached_item.get("expires_at")
            
            # Check if expired
            if datetime.now() > expiry_time:
                print(f"⏰ Cache EXPIRED: {key}")
                del self._cache[key]
                return None
            
            print(f"✅ Cache HIT: {key} (valid for {(expiry_time - datetime.now()).seconds}s)")
            return cached_item.get("data")
    
    def set(self, key: str, data: Dict[str, Any], ttl_minutes: Optional[int] = None):
        """
        Store data in cache with expiry
        
        Args:
            key: Cache key (e.g., "dashboard_data")
            data: Data to cache
            ttl_minutes: Custom TTL (uses default if None)
        """
        ttl = timedelta(minutes=ttl_minutes) if ttl_minutes else self.default_ttl
        expires_at = datetime.now() + ttl
        
        with self._lock:
            self._cache[key] = {
                "data": data,
                "cached_at": datetime.now(),
                "expires_at": expires_at
            }
            print(f"💾 Cache SET: {key} (expires: {expires_at.strftime('%H:%M:%S')})")
    
    def invalidate(self, key: str):
        """
        Manually invalidate cache entry
        
        Used when: Sales/Purchase transactions occur
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                print(f"🗑️  Cache INVALIDATED: {key}")
            else:
                print(f"⚠️  Cache key not found: {key}")
    
    def invalidate_all(self):
        """Clear entire cache (use sparingly)"""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            print(f"🗑️  Cache CLEARED: {count} entries removed")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            stats = {
                "total_entries": len(self._cache),
                "entries": []
            }
            
            for key, item in self._cache.items():
                remaining_seconds = (item["expires_at"] - datetime.now()).total_seconds()
                stats["entries"].append({
                    "key": key,
                    "cached_at": item["cached_at"].isoformat(),
                    "expires_at": item["expires_at"].isoformat(),
                    "remaining_seconds": max(0, int(remaining_seconds))
                })
            
            return stats

# Global Cache Instance

dashboard_cache = DashboardCache(default_ttl_minutes=60)  

# Helper Functions

def get_cached_dashboard() -> Optional[Dict[str, Any]]:
    """Get cached dashboard data (if valid)"""
    return dashboard_cache.get("dashboard_data")


def cache_dashboard(data: Dict[str, Any]):
    """Store dashboard data in cache"""
    dashboard_cache.set("dashboard_data", data)


def invalidate_dashboard_cache():
    """Invalidate dashboard cache after sales/purchase"""
    dashboard_cache.invalidate("dashboard_data")


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics for monitoring"""
    return dashboard_cache.get_stats()