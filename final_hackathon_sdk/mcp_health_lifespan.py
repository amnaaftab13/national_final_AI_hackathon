
from agents.tracing import add_trace_processor
from contextlib import asynccontextmanager
import asyncio
from state_manager import get_state_manager 
from trace_file import FileTracingProcessor
from agents import Runner
from datetime import datetime,timedelta
from configuration import scheduled_session, mcp_client
from fastapi import FastAPI
from agents_file import insight_agent
from message_handler import process_user_message

state = get_state_manager()

# ======================= MCP Health Monitoring ============================
async def mcp_health_monitor():
    """Background task to monitor MCP health and auto-reconnect"""
    
    #  IMMEDIATE CHECK at startup
    if state.is_degraded():
        print("🔍 Initial health check...")
        await asyncio.sleep(2)  
        try:
            await mcp_client.connect()
            print("✅ MCP reconnected on startup!")
            state.disable_degraded_mode()
            await process_pending_messages()
        except Exception as e:
            print(f"⚠ Initial reconnect failed: {e}")
    
    #  Then continue with periodic checks
    while True:
        await asyncio.sleep(state.mcp_check_interval)
        
        if state.is_degraded():
            print("🔄 Attempting MCP reconnection...")
            try:
                await mcp_client.connect()
                print("✅ MCP reconnected!")
                state.disable_degraded_mode()
                
                # Process pending messages
                await process_pending_messages()
                
            except Exception as e:
                print(f"❌ Reconnection failed: {e}")
                print(f"⏳ Retry in {state.mcp_check_interval}s...")

async def process_pending_messages():
    """Process all cached messages after reconnection"""
    pending = state.get_pending_messages()
    
    if not pending:
        return
    
    print(f"📬 Processing {len(pending)} cached messages...")
    
    for msg in pending:
        try:
            asyncio.create_task(
                process_user_message(msg.user_message, msg.user_number)
            )
            state.remove_message(msg)
            await asyncio.sleep(2)  
            
        except Exception as e:
            print(f"⚠ Failed to process: {e}")
            if state.increment_retry(msg):
                print(f"⚠ Message dropped after {state.max_retry_count} retries")
    
    print(f"✅ Processing complete. Remaining: {state.get_pending_count()}")

#  ==================== 24-Hour Autonomous Business Cycle ==============
async def run_autonomous_business_cycle():
    """
    Runs FULLY AUTONOMOUS business analysis every 24 hours
    """
    await asyncio.sleep(24 * 60 * 60) 

    while True:
        try:
            print("\n" + "="*70)
            print("🤖 [SCHEDULED AUTONOMOUS RUN] Starting 24-hour business cycle...")
            print(f"🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*70)

            print("🔍 [SCHEDULED] Step 1: Running Insight Agent...")

            try:
                result = await Runner.run(
                    insight_agent,
                    """
                    Execute full autonomous workflow:
                    1. Analyze low-selling products
                    2. Trigger full strategic analysis for REPORT
                    It should respond in PROSE format (not JSON) since this is a WhatsApp request.
                    """,
                    session=scheduled_session  
                )

                print("RESULT:", result.final_output)

            except Exception as e:
                print(f"⚠ [INSIGHT AGENT] Error: {e}")
                import traceback
                print(traceback.format_exc())

        except Exception as e:
            print(f"⚠ [MAIN LOOP] Error: {e}")
            import traceback
            print(traceback.format_exc())

        await asyncio.sleep(24 * 60 * 60)  # sleep 24 hours

#  ============================== Lifespan Management =======================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("⚙ Starting application...")
    # Register file-based tracing for hackathon logs
    add_trace_processor(FileTracingProcessor(json_path="agent_logs_autonomous.jsonl",
                                             readable_path="agent_logs_autonomous.txt",
                                             debug_mode=True))
    print("🧾 FileTracingProcessor registered -> logging to agent_logs.jsonl")
    
    try:
        await mcp_client.connect()
        print("✅ MCP connected!")
        state.disable_degraded_mode()
        
        if state.get_pending_count() > 0:
            print(f"📬 Found {state.get_pending_count()} pending messages")
            await process_pending_messages()
    
    except Exception as e:
        print(f"❌ MCP connection failed: {e}")
        state.enable_degraded_mode("Initial connection failed")
    
    health_task = asyncio.create_task(mcp_health_monitor())
    state.set_health_task(health_task)
    
    #  24-Hour Autonomous Business Cycle
    business_cycle_task = asyncio.create_task(run_autonomous_business_cycle())
    print("✅ 24-hour autonomous business cycle scheduled")
    
    state.print_status()
    
    yield
    
    state.cancel_health_task()
    business_cycle_task.cancel()  
    
    if hasattr(mcp_client, "disconnect"):
        try:
            await mcp_client.disconnect()
        except:
            pass
    
    print("🔌 Application shutdown")

