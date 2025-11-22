import asyncio
import uvicorn
from twilio.twiml.messaging_response import MessagingResponse
from typing import List
import traceback
from agents import  Runner
import os
import re
import json
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dashboard_cache import (
    get_cached_dashboard,
    cache_dashboard,
    invalidate_dashboard_cache,
    get_cache_stats
)
from twilio.rest import Client
from configuration import  session,admin_session,scheduled_session,CRUD_BASE_URL
from fastapi import Response, Request, Body
from agents_file import insight_agent,analytics_agent
from datetime import datetime
from mcp_health_lifespan import lifespan
from state_manager import (
    get_state_manager, 
    is_degraded, 
    cache_message, 
   )
from message_handler import process_user_message
from pathlib import Path
from typing import Optional,List,Dict,Any

state = get_state_manager()



class ProductInsight(BaseModel):
    name: str
    sales_count: int
    stock_level: int
    sales_trend: str  

class ProductInsightsRequest(BaseModel):
    products: List[ProductInsight]

app = FastAPI(title="Agent SDK + WhatsApp Integration", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

  

# =================================Endpoints==========================

@app.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    user_message = form.get("Body", "").strip()
    user_number = form.get("From", "")
    
    print(f"\n{'='*70}")
    print(f"📩 From: {user_number}")
    print(f"💬 Message: '{user_message}'")

    twilio_resp = MessagingResponse()

    #  ADMIN ON-DEMAND REPORT
    if user_number == os.getenv("ADMIN_PHONE_NUMBER") and user_message.upper() in ["REPORT DETAILS", "REPORT", "DETAILS"]:
        print("📊 [ON-DEMAND] Admin requested business report")

        try:
            print("🔍 [ON-DEMAND] Triggering autonomous agent workflow...")
            
            result = await Runner.run(
                insight_agent,
                f"""WHATSAPP REPORT REQUEST from admin {user_number}

                Execute full autonomous workflow:
                1. Analyze low-selling products
                2. Trigger full strategic analysis for REPORT

                It should respond in PROSE format (not JSON) since this is a WhatsApp request.""",
                session=scheduled_session
            )
            
            print("RESULT",result.final_output)
            
            #  CACHE INVALIDATION after report generation
            print("🗑️  Invalidating dashboard cache after report generation...")
            invalidate_dashboard_cache()
        
        except Exception as e:
            print(f"⚠ [ON-DEMAND] Error: {e}")
            import traceback
            print(traceback.format_exc())

        print(f"{'='*70}\n")
        return Response(content=str(MessagingResponse()), media_type="application/xml")

    # NORMAL USER FLOW
   
    if is_degraded():
        cache_message(user_message, user_number)
        twilio_resp.message(
            "⚠ System temporarily offline. "
            "Your message is saved and will be processed automatically!"
        )
        print(f"💾 Cached (Total: {state.get_pending_count()})")
    else:
        print("✅ Processing your request... 🔄")
        asyncio.create_task(process_user_message(user_message, user_number))

    print(f"{'='*70}\n")
    return Response(content=str(twilio_resp), media_type="application/xml")

#   Admin Dashboard Endpoints (WITH CACHING)
@app.get("/admin/sales-report")
async def get_sales_report():
    """Admin dashboard ke liye analytics data fetch karega (WITH CACHING)"""
    try:
        # ============================================
        # 🆕 CHECK CACHE FIRST
        # ============================================
        cached_data = get_cached_dashboard()
        if cached_data and "sales_report" in cached_data:
            print("✅ [CACHE HIT] Returning cached sales report")
            return {
                "status": "success", 
                "report": cached_data["sales_report"],
                "cached": True,
                "generated_at": cached_data.get("generated_at")
            }
        
        print("❌ [CACHE MISS] Generating new sales report...")
        
        # ============================================
        # GENERATE NEW REPORT
        # ============================================
        result = await Runner.run(
            analytics_agent,
            "Generate latest sales report summary for dashboard.",
            session=session
        )
        
        # Extract report data
        report_data = None
        
        if hasattr(result, 'tool_outputs') and result.tool_outputs:
            report_data = result.tool_outputs[-1]
            print(f"✅ Found in tool_outputs: {report_data}")
        
        elif hasattr(result, 'raw_responses') and result.raw_responses:
            for response in result.raw_responses:
                if hasattr(response, 'content'):
                    for block in response.content:
                        if hasattr(block, 'type') and block.type == 'tool_use':
                            if hasattr(block, 'output'):
                                report_data = block.output
                                print(f"✅ Found in raw_responses: {report_data}")
                                break
        
        if not report_data:
            final_out = getattr(result, "final_output", "")
            if "json" in final_out:
                import re
                import json
                match = re.search(r'```json\s*(\{.*?\})\s*```', final_out, re.DOTALL)
                if match:
                    report_data = json.loads(match.group(1))
                    print(f"✅ Extracted from markdown: {report_data}")
            else:
                report_data = final_out
        
        # ============================================
        # 🆕 UPDATE CACHE
        # ============================================
        cached_dashboard = get_cached_dashboard() or {}
        cached_dashboard["sales_report"] = report_data
        cached_dashboard["generated_at"] = datetime.now().isoformat()
        cache_dashboard(cached_dashboard)
        print("💾 Sales report cached successfully")
        
        return {
            "status": "success", 
            "report": report_data,
            "cached": False,
            "generated_at": cached_dashboard["generated_at"]
        }
    
    except Exception as e:
        import traceback
        print(f"❌ Error: {e}")
        print(traceback.format_exc())
        return {"status": "error", "message": str(e)}


@app.get("/admin/purchase-report")
async def get_purchase_report():
    """Admin dashboard ke liye supplier purchases data (WITH CACHING)"""
    try:
        #  CHECK CACHE FIRST
        cached_data = get_cached_dashboard()
        if cached_data and "purchase_report" in cached_data:
            print("✅ [CACHE HIT] Returning cached purchase report")
            return {
                "status": "success", 
                "report": cached_data["purchase_report"],
                "cached": True,
                "generated_at": cached_data.get("generated_at")
            }
        
        print("❌ [CACHE MISS] Generating new purchase report...")
         # GENERATE NEW REPORT
      
        result = await Runner.run(
            analytics_agent,
            "Generate detailed supplier purchase report summary for dashboard.",
            session=admin_session
        )
        
        # Extract report data (same logic as sales)
        report_data = None
        if hasattr(result, 'tool_outputs') and result.tool_outputs:
            report_data = result.tool_outputs[-1] 
        
        if not report_data:
            final_out = getattr(result, "final_output", "")
            import re
            import json
            match = re.search(r'```json\s*(\{.*?\})\s*```', final_out, re.DOTALL)
            if match:
                report_data = json.loads(match.group(1))
            else:
                report_data = final_out
        
        #  UPDATE CACHE
        cached_dashboard = get_cached_dashboard() or {}
        cached_dashboard["purchase_report"] = report_data
        cached_dashboard["generated_at"] = datetime.now().isoformat()
        cache_dashboard(cached_dashboard)
        print("💾 Purchase report cached successfully")

        return {
            "status": "success", 
            "report": report_data,
            "cached": False,
            "generated_at": cached_dashboard["generated_at"]
        }
    
    except Exception as e:
        import traceback
        print(f"❌ Error fetching purchase report: {e}")
        print(traceback.format_exc())
        return {"status": "error", "message": str(e)}


@app.get("/admin/profit-loss-report")
async def get_profit_loss_report():
    """Admin dashboard ke liye complete P/L analysis (WITH CACHING)"""
    try:
        
        #  CHECK CACHE FIRST
        cached_data = get_cached_dashboard()
        if cached_data and "profit_loss_report" in cached_data:
            print("✅ [CACHE HIT] Returning cached P/L report")
            return {
                "status": "success", 
                "report": cached_data["profit_loss_report"],
                "cached": True,
                "generated_at": cached_data.get("generated_at")
            }
        
        print("❌ [CACHE MISS] Generating new P/L report...")
        print("=" * 70)
        print("📊 [ADMIN REQUEST] Profit/Loss Report Generation")
        print(f"🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # GENERATE NEW REPORT
        result = await Runner.run(
            analytics_agent,
            "Generate complete profit and loss analysis report for the admin dashboard.",
            session=admin_session
        )
        
        print("🔍 DEBUG: Processing result...")
        
        report_data = None
        
        # Try tool_outputs
        if hasattr(result, 'tool_outputs') and result.tool_outputs:
            print(f"✅ Found {len(result.tool_outputs)} tool outputs")
            last_output = result.tool_outputs[-1]
            
            if isinstance(last_output, dict):
                report_data = last_output
                print("✅ Using tool_outputs[-1] directly (dict)")
            elif isinstance(last_output, str):
                try:
                    report_data = json.loads(last_output)
                    print("✅ Parsed tool_outputs[-1] from JSON string")
                except json.JSONDecodeError:
                    print(f"⚠ Tool output string is not valid JSON")
        
        # Try messages/content blocks
        if not report_data and hasattr(result, 'messages'):
            print("🔍 Checking messages attribute...")
            for msg in result.messages:
                if hasattr(msg, 'content'):
                    if isinstance(msg.content, list):
                        for block in msg.content:
                            if hasattr(block, 'type') and block.type == 'tool_use':
                                if hasattr(block, 'output'):
                                    report_data = block.output
                                    print("✅ Found data in tool_use.output")
                                    break
        
        # Try final_output
        if not report_data:
            final_out = getattr(result, "final_output", "")
            print(f"🔍 Checking final_output (length: {len(str(final_out))})")
            
            if final_out:
                # Extract from markdown first
                markdown_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', final_out, re.DOTALL)
                
                if markdown_match:
                    try:
                        json_str = markdown_match.group(1)
                        report_data = json.loads(json_str)
                        print("✅ Parsed from markdown code block")
                    except json.JSONDecodeError as je:
                        print(f"⚠ Markdown JSON parsing failed: {je}")
                
                # Try direct parse
                if not report_data:
                    try:
                        report_data = json.loads(final_out)
                        print("✅ Parsed final_output as direct JSON")
                    except json.JSONDecodeError:
                        json_match = re.search(r'\{[\s\S]*\}', final_out)
                        if json_match:
                            try:
                                report_data = json.loads(json_match.group(0))
                                print("✅ Extracted standalone JSON")
                            except json.JSONDecodeError:
                                pass
        
        # Final check
        if not report_data:
            print("❌ No valid report data found")
            return {
                "status": "error", 
                "message": "Agent did not return valid report data."
            }

        #  UPDATE CACHE
        cached_dashboard = get_cached_dashboard() or {}
        cached_dashboard["profit_loss_report"] = report_data
        cached_dashboard["generated_at"] = datetime.now().isoformat()
        cache_dashboard(cached_dashboard)
        print("💾 P/L report cached successfully")
        
        print(f"✅ Report generated successfully")
        print("="*70 + "\n")
        
        return {
            "status": "success", 
            "report": report_data,
            "cached": False,
            "generated_at": cached_dashboard["generated_at"]
        }
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        
        print("="*70)
        print(f"❌ CRITICAL ERROR in get_profit_loss_report")
        print(f"Error: {str(e)}")
        print(error_trace)
        print("="*70 + "\n")
        
        return {
            "status": "error", 
            "message": f"Server error: {str(e)}",
            "error_type": type(e).__name__
        }


@app.get("/admin/marketing-campaigns")
async def get_marketing_campaigns():
    """Returns list of recent marketing posters (WITH CACHING)"""
    try:
        #  CHECK CACHE FIRST
        cached_data = get_cached_dashboard()
        if cached_data and "marketing_campaigns" in cached_data:
            print("✅ [CACHE HIT] Returning cached marketing campaigns")
            return {
                "status": "success", 
                "campaigns": cached_data["marketing_campaigns"],
                "cached": True,
                "generated_at": cached_data.get("generated_at")
            }
        
        print("❌ [CACHE MISS] Fetching new marketing campaigns...")
        
        # FETCH FROM MCP
        import aiohttp
        async with aiohttp.ClientSession() as session_http:
            async with session_http.get(f"{CRUD_BASE_URL}/api/marketing/campaigns") as response:
                if response.status == 200:
                    data = await response.json()
                    campaigns = data.get("data", [])
                    
                    #  UPDATE CACHE
                    cached_dashboard = get_cached_dashboard() or {}
                    cached_dashboard["marketing_campaigns"] = campaigns
                    cached_dashboard["generated_at"] = datetime.now().isoformat()
                    cache_dashboard(cached_dashboard)
                    print("💾 Marketing campaigns cached successfully")
                    
                    return {
                        "status": "success", 
                        "campaigns": campaigns,
                        "cached": False,
                        "generated_at": cached_dashboard["generated_at"]
                    }
                else:
                    return {"status": "error", "message": "Failed to fetch campaigns"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/admin/dashboard-data")
async def get_dashboard_data():
    """Fetch complete dashboard analytics (WITH UNIFIED CACHING)"""
    try:
        #  CHECK CACHE FIRST
        cached_data = get_cached_dashboard()
        if cached_data and "dashboard" in cached_data:
            print("✅ [CACHE HIT] Returning complete cached dashboard")
            return {
                "status": "success",
                "timestamp": cached_data.get("generated_at"),
                "dashboard": cached_data["dashboard"],
                "cached": True
            }
        
        print("❌ [CACHE MISS] Generating complete dashboard data...")
        # GENERATE FRESH DATA
       
        insight_result = await Runner.run(
            insight_agent,
            "Fetch low-selling products and trigger full strategic analysis for dashboard.",
            session=scheduled_session
        )

        dashboard_data = None
        raw_output = getattr(insight_result, "final_output", None)

        if raw_output:
            if isinstance(raw_output, str):
                raw_output = raw_output.replace("```json", "").replace("```", "").strip()
            try:
                dashboard_data = json.loads(raw_output)
            except json.JSONDecodeError:
                dashboard_data = raw_output

        print("="*70)
        print("🔍 DEBUG: Dashboard JSON")
        print(f"Type: {type(dashboard_data)}")
        print(f"Data: {dashboard_data}")
        print("="*70)

        
        #  CACHE COMPLETE DASHBOARD
        cached_dashboard = get_cached_dashboard() or {}
        cached_dashboard["dashboard"] = dashboard_data
        cached_dashboard["generated_at"] = datetime.now().isoformat()
        cache_dashboard(cached_dashboard)
        print("💾 Complete dashboard cached successfully")

        return {
            "status": "success",
            "timestamp": cached_dashboard["generated_at"],
            "dashboard": dashboard_data,
            "cached": False
        }

    except Exception as e:
        print(f"❌ Dashboard Error: {e}")
        print(traceback.format_exc())
        return {"status": "error", "message": str(e)}
    
    

#  NEW ENDPOINT: Cache Statistics & Manual Control
@app.get("/admin/cache-stats")
async def get_cache_stats_endpoint():
    """Get current cache statistics for monitoring"""
    try:
        stats = get_cache_stats()
        return {
            "status": "success",
            "cache_stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/admin/cache/invalidate")
async def invalidate_cache_endpoint():
    """Manually invalidate dashboard cache (admin control)"""
    try:
        invalidate_dashboard_cache()
        return {
            "status": "success",
            "message": "Dashboard cache invalidated successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/mock/easypaisa/payment")
async def mock_easypaisa_payment(
    request: dict = Body(...),
):
    """Simulates Easypaisa payment confirmation"""
    try:
        order_id = request.get("order_id", "UNKNOWN_ORDER")
        sender_number = request.get("sender_number", "0300-0000000")
        amount = request.get("amount", 0)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        transaction_id = f"EP-{int(datetime.now().timestamp())}"
        confirmation_message = (
            f"💵 Easypaisa payment received!\n\n"
            f"📦 Order ID: {order_id}\n"
            f"📱 Sender: {sender_number}\n"
            f"💰 Amount: Rs. {amount}\n"
            f"🕓 Time: {timestamp}\n"
            f"🔖 Transaction ID: {transaction_id}"
        )

        print(f"✅ {confirmation_message}")
        
      
        #  CACHE INVALIDATION after payment
        invalidate_dashboard_cache()
        
        return {
            "status": "success",
            "transaction_id": transaction_id,
            "message": confirmation_message
        }

    except Exception as e:
        print(f"❌ Mock Easypaisa error: {e}")
        return {"status": "failed", "error": str(e)}

LOG_PATH = Path("agent_logs_autonomous.txt")

# Helpers
BOX_CHARS_REGEX = re.compile(r"[┏┓┗┛━┃╺╸╻╹╼╽╾╿╽═▁▔▕▏▎▍▌▐░▒▓◢◣◤◥\|\u2500-\u257F]")

# 1. IMPROVED HELPER (Replace existing clean_text)
def clean_text(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    # Remove specific box drawing chars but keep newlines for formatting
    s = re.sub(r"[┏┓┗┛━┃╺╸╻╹╼╽╾╿╽═▔▕▏▎▍▌▐░▒▓◢◣◤◥]", "", s)
    # Remove standard pipes used for indentation
    s = s.replace("│", "")
    s = s.replace("\t", " ")
    # Clean multiple spaces but preserve structure
    s = re.sub(r"[ \u00A0]+", " ", s)
    return s.strip() or None

# 2. IMPROVED PARSER (Replace existing parse_llm_decisions)

def parse_llm_decisions(block: str) -> List[Dict[str, Any]]:
    llm = []
    # Regex to find the decision block
    for m in re.finditer(r"(?:🧠\s*)?LLM DECISION\s*→\s*([^\n\r]+)([\s\S]{0,1500}?)(?=\n\s*[│┃]*\s*(?:├|┌|┏|🧠|🔄|⚡|📤|$))", block, flags=re.IGNORECASE):
        tool = clean_text(m.group(1))
        ctx = m.group(2)

        # Extract Agent
        agent_match = re.search(r"Agent:\s*([^\n\r]+)", ctx)
        agent = clean_text(agent_match.group(1)) if agent_match else None

        # Extract Model
        model_match = re.search(r"Model:\s*([^\n\r]+)", ctx)
        model = clean_text(model_match.group(1)) if model_match else None

        # --- NEW: Extract Arguments ---
        arguments = None
        arg_match = re.search(r"Arguments:\s*\n([\s\S]+?)(?=\n\s*[│┃]*\s*(?:⏱️|Agent:|Model:|$))", ctx)
        if arg_match:
            raw_args = arg_match.group(1)
            # Clean indentation (remove │ and leading spaces from each line)
            cleaned_lines = [re.sub(r"^[\s│┃]+", "", line) for line in raw_args.split('\n')]
            arguments = "\n".join(cleaned_lines).strip()
        # ------------------------------

        # Extract Metrics
        duration = 0.0
        tokens = {"total": 0, "input": 0, "output": 0}
        mt = re.search(r"⏱️\s*([\d.]+)s\s*\|\s*🎫\s*([0-9]+)\s*tokens\s*\(in:([0-9]+),\s*out:([0-9]+)\)", ctx)
        if mt:
            duration = safe_float(mt.group(1))
            tokens = {"total": safe_int(mt.group(2)), "input": safe_int(mt.group(3)), "output": safe_int(mt.group(4))}
        
        # Extract Reasoning
        reasoning = None
        mr = re.search(r"(?:Agent Planning|Reasoning):\s*([\s\S]{0,500}?)(?=\n\s*[│┃]*\s*(?:Arguments|⏱️))", ctx, flags=re.IGNORECASE)
        if mr:
            reasoning = clean_text(mr.group(1))

        llm.append({
            "tool": tool,
            "agent": agent,
            "model": model,
            "arguments": arguments, # Added this field
            "duration": duration,
            "tokens": tokens,
            "reasoning": reasoning
        })
    return llm

def safe_int(s: Optional[str], default: int = 0) -> int:
    try:
        return int(re.sub(r"[^\d-]", "", s)) if s is not None else default
    except Exception:
        return default

def safe_float(s: Optional[str], default: float = 0.0) -> float:
    try:
        return float(re.sub(r"[^\d\.]", "", s)) if s is not None else default
    except Exception:
        return default

def extract_date_from_text(s: str) -> Optional[str]:
    m = re.search(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", s)
    if m:
        return m.group(1)
    m2 = re.search(r"(\d{4}-\d{2}-\d{2})", s)
    if m2:
        return m2.group(1)
    return None

# Header & trace splitting
def extract_header_info(content: str) -> Dict[str, Any]:
    split = re.split(r"(?:┏[\s\S]{0,200}?NEW TRACE:|🚀\s*NEW TRACE:|NEW TRACE:)", content, maxsplit=1, flags=re.DOTALL)
    header = split[0] if split else content

    reqs = []
    for m in re.finditer(r"^[\s\|│]*[•\-\*]\s*(?:✅\s*)?(.+)$", header, flags=re.MULTILINE):
        text = clean_text(m.group(1))
        if text:
            reqs.append(text)

    started = None
    m = re.search(r"Started:\s*([^\n\r]+)", header)
    if m:
        started = clean_text(m.group(1))
    else:
        sd = extract_date_from_text(header)
        if sd:
            started = sd

    title = "AUTONOMOUS AGENTIC AI - NATIONAL HACKATHON 2025 SUBMISSION"
    return {"title": title, "requirements": reqs, "started": started or "Unknown"}

def split_traces(content: str) -> List[str]:
    parts = re.split(r"(?=(?:┏[\s\S]{0,200}?NEW TRACE:|🚀\s*NEW TRACE:|NEW TRACE:))", content, flags=re.DOTALL)
    traces = [p for p in parts if "NEW TRACE" in p]
    if not traces:
        traces = [t for t in re.split(r"\n{2,}", content) if "TRACE" in t or "📥 USER" in t]
    return traces
# Parsers for sections - ENHANCED VERSIONS
def parse_mcp_calls(block: str) -> List[Dict[str, Any]]:
    mcp_calls = []
    for m in re.finditer(r"🔌\s*MCP:\s*([^\n\r→\|]+)[→\|\s]*([^\(\n\r]+)\(?\s*found\s*([0-9]+)\s*tools[,\s]*([\d.]+)s\)?", block, flags=re.IGNORECASE):
        mcp_calls.append({
            "server": clean_text(m.group(1)),
            "action": clean_text(m.group(2)),
            "tools_found": safe_int(m.group(3)),
            "duration": safe_float(m.group(4))
        })
    if not mcp_calls:
        for m in re.finditer(r"🔌\s*MCP:\s*([^\n\r]+)", block, flags=re.IGNORECASE):
            mcp_calls.append({"server": clean_text(m.group(1)), "action": None, "tools_found": 0, "duration": 0.0})
    return mcp_calls

# -------------------------
def parse_llm_decisions(block: str) -> List[Dict[str, Any]]:
    llm = []
    
    #  REGEX:
    pattern = r"(?:├─\s*🧠\s*)?LLM DECISION\s*→\s*([^\n\r]+)([\s\S]{0,1500}?)(?=\n\s*[│┃]*\s*(?:├|┌|┏|🧠|🔄|⚡|📤|$))"
    
    for m in re.finditer(pattern, block, flags=re.IGNORECASE):
        tool = clean_text(m.group(1)) 
        ctx = m.group(2)

        # Agent 
        agent_match = re.search(r"Agent:\s*([^\n\r]+)", ctx)
        agent = clean_text(agent_match.group(1)) if agent_match else None

        # Model 
        model_match = re.search(r"Model:\s*([^\n\r]+)", ctx)
        model = clean_text(model_match.group(1)) if model_match else None

        # Arguments
        arguments = None
        arg_match = re.search(r"Arguments:\s*\n([\s\S]+?)(?=\n\s*[│┃]*\s*(?:⏱️|Agent:|Model:|$))", ctx)
        if arg_match:
            raw_args = arg_match.group(1)
            cleaned_lines = [re.sub(r"^[\s│┃]+", "", line) for line in raw_args.split('\n')]
            arguments = "\n".join(cleaned_lines).strip()

        # Metrics 
        duration = 0.0
        tokens = {"total": 0, "input": 0, "output": 0}
        mt = re.search(r"⏱️\s*([\d.]+)s\s*\|\s*🎫\s*([0-9]+)\s*tokens\s*\(in:([0-9]+),\s*out:([0-9]+)\)", ctx)
        if mt:
            try:
                duration = float(mt.group(1))
                tokens = {
                    "total": int(mt.group(2)), 
                    "input": int(mt.group(3)), 
                    "output": int(mt.group(4))
                }
            except:
                pass

        llm.append({
            "tool": tool,          
            "agent": agent,       
            "model": model,
            "arguments": arguments,
            "duration": duration,
            "tokens": tokens,
            "reasoning": None     
        })
    return llm

def parse_handoffs(block: str) -> List[Dict[str, str]]:
    """Enhanced handoff parser with deduplication"""
    handoffs = []
    seen = set()
    
    # Strategy 1: Look for AUTONOMOUS HANDOFF
    for m in re.finditer(r"(?:🔄|╔═)\s*AUTONOMOUS HANDOFF:\s*([^\n\r→│┃╗]+)\s*[→\-]\s*([^\n\r│┃╗]+)", block, flags=re.IGNORECASE):
        from_agent = clean_text(m.group(1))
        to_agent = clean_text(m.group(2))
        
        if from_agent and to_agent:
            key = f"{from_agent}→{to_agent}"
            if key not in seen:
                seen.add(key)
                handoffs.append({"from": from_agent, "to": to_agent})
    
    # Strategy 2: Look in summary section
    handoff_section = re.search(
        r"🔄\s*INTER-AGENT HANDOFFS:\s*([\s\S]{0,500}?)(?=\n\s*[│┃]\s*\n|\n\s*⚡|\n\s*🔌|╚═|$)",
        block
    )
    if handoff_section:
        content = handoff_section.group(1)
        for m in re.finditer(r"[•\-\*]\s*([^\n\r→│┃]+)\s*[→\-]\s*([^\n\r│┃]+)", content):
            from_agent = clean_text(m.group(1))
            to_agent = clean_text(m.group(2))
            
            if from_agent and to_agent:
                key = f"{from_agent}→{to_agent}"
                if key not in seen:
                    seen.add(key)
                    handoffs.append({"from": from_agent, "to": to_agent})
    
    return handoffs

def parse_final_outputs(block: str) -> List[Dict[str, Any]]:
    """ENHANCED - Multiple strategies to capture final output"""
    outs = []

    # STRATEGY 1: Look for " FINAL RESPONSE GENERATED" block
    for m in re.finditer(r"📤\s*FINAL RESPONSE GENERATED([\s\S]{0,2000}?)(?=\n\s*┌|\n\s*├|\n\s*┏|\n\s*╔|$)", block, flags=re.IGNORECASE):
        snippet = m.group(1)
        
        agent = None
        model = None
        length = 0
        preview = None
        
        # Extract agent
        agent_m = re.search(r"Agent:\s*([^\n\r│┃]+)", snippet)
        if agent_m:
            agent = clean_text(agent_m.group(1))
        
        # Extract model
        model_m = re.search(r"Model:\s*([^\n\r│┃]+)", snippet)
        if model_m:
            model = clean_text(model_m.group(1))
        
        # Extract length
        length_m = re.search(r"Length:\s*([0-9]+)\s*characters", snippet)
        if length_m:
            length = safe_int(length_m.group(1))
        
        # Extract preview - CRITICAL FIX
        # Look for "Preview:" and capture everything until metrics line (⏱️) or end
        preview_m = re.search(r"Preview:\s*([\s\S]+?)(?=\n\s*[│┃]?\s*⏱️|\n\s*┌|\n\s*├|$)", snippet)
        if preview_m:
            preview_raw = preview_m.group(1)
            # Clean but preserve newlines for multiline content
            preview = clean_text(preview_raw)
            # If still empty, try alternative
            if not preview:
                preview_m2 = re.search(r"Preview:\s*([^\n\r]+)", snippet)
                if preview_m2:
                    preview = clean_text(preview_m2.group(1))
        
        if preview or length > 0:
            outs.append({
                "agent": agent,
                "model": model,
                "length": length,
                "preview": preview
            })
    
    # STRATEGY 2: Look for " FINAL OUTPUT TO USER" in summary
    if not outs:
        # Pattern 1: Direct line after "FINAL OUTPUT TO USER:"
        m2 = re.search(r"📤\s*FINAL OUTPUT TO USER:\s*\n\s*[│┃]\s*([^\n\r]+)", block)
        if m2:
            preview = clean_text(m2.group(1))
            if preview:
                outs.append({
                    "agent": None,
                    "model": None,
                    "length": len(preview),
                    "preview": preview
                })
        
        # Pattern 2: Multiline output in summary
        if not outs:
            m3 = re.search(r"📤\s*FINAL OUTPUT TO USER:\s*\n([\s\S]{0,1000}?)(?=\n\s*[│┃]\s*\.\.\.|╚═|$)", block)
            if m3:
                content = m3.group(1)
                # Extract all lines that start with │ or ┃
                lines = []
                for line in content.split('\n'):
                    cleaned = re.sub(r"^[\s│┃]+", "", line).strip()
                    if cleaned and not cleaned.startswith('...'):
                        lines.append(cleaned)
                
                if lines:
                    preview = ' '.join(lines[:5])  
                    outs.append({
                        "agent": None,
                        "model": None,
                        "length": len(preview),
                        "preview": clean_text(preview)
                    })

    # STRATEGY 3: Look for ANY "Preview:" in the trace
    if not outs:
        for m in re.finditer(r"Preview:\s*([\s\S]{0,1000}?)(?=\n\s*[│┃]?\s*⏱️|\n\s*┌|\n\s*├|\n{2,}|$)", block):
            preview_raw = m.group(1)
            preview = clean_text(preview_raw)
            
            if preview and len(preview) > 20:  
                outs.append({
                    "agent": None,
                    "model": None,
                    "length": len(preview),
                    "preview": preview
                })
                break  
    # STRATEGY 4: Extract from LLM output that's NOT a tool call
    if not outs:
        # Look for LLM decisions followed by text content (not Arguments:)
        for m in re.finditer(r"🧠\s*LLM DECISION\s*→\s*([^\n\r]+)([\s\S]{0,1500}?)(?=\n\s*├|\n\s*┌|$)", block):
            tool_name = clean_text(m.group(1))
            context = m.group(2)
            
            # Skip if it's a tool call
            if "Arguments:" in context or "transfer" in tool_name.lower():
                continue
            
            # Look for text after the metrics line
            text_m = re.search(r"⏱️[^\n]+\n\s*[│┃]?\s*(.{30,})", context, re.DOTALL)
            if text_m:
                preview = clean_text(text_m.group(1))
                if preview and len(preview) > 20:
                    outs.append({
                        "agent": None,
                        "model": None,
                        "length": len(preview),
                        "preview": preview[:500]
                    })
                    break
    
    return outs

def parse_trace_summary(block: str) -> Dict[str, Any]:
    """Enhanced summary parser with MCP fix and Multi-line output fix"""
    summary = {"metrics": {}, "tokens": {}, "duration": 0.0, "final_output": None}

    def em(rx):
        m = re.search(rx, block, flags=re.IGNORECASE)
        return safe_int(m.group(1)) if m else 0

    # --- FIX 1: MCP Calls Logic ---
    meaningful_mcp_calls = 0
    for m in re.finditer(r"🔌\s*MCP:\s*([^\n\r→\|]+)[→\|\s]*([^\(\n\r]+)", block, flags=re.IGNORECASE):
        action = m.group(2)
        if action and "list_tools" not in action.lower():
            meaningful_mcp_calls += 1
    # ------------------------------

    summary["metrics"] = {
        "agents": em(r"Agents:\s*(\d+)"),
        "tools": em(r"Tools:\s*(\d+)"),
        "llm_calls": em(r"LLM Calls:\s*(\d+)"),
        
        "mcp_calls": meaningful_mcp_calls,  
        
        "negotiations": em(r"Negotiations:\s*(\d+)"),
        "handoffs": em(r"Handoffs:\s*(\d+)"),
        "autonomous_decisions": em(r"Autonomous Decisions:\s*(\d+)")
    }

    summary["tokens"] = {
        "total": em(r"Total:\s*(\d+)"),
        "input": em(r"Input:\s*(\d+)"),
        "output": em(r"Output:\s*(\d+)")
    }

    md = re.search(r"TOTAL DURATION:\s*([\d.]+)s", block, flags=re.IGNORECASE)
    if md:
        summary["duration"] = safe_float(md.group(1))

    # --- FIX 2: Multi-line Final Output ---
    mfo = re.search(r"📤\s*FINAL OUTPUT TO USER:\s*\n([\s\S]+?)(?=\n\s*[│┃]*\s*(?:🔌|🔄|⚡|┗))", block)
    
    if mfo:
        raw_output = mfo.group(1)
        cleaned_lines = [re.sub(r"^[\s│┃]+", "", line) for line in raw_output.split('\n')]
        summary["final_output"] = "\n".join(cleaned_lines).strip()
    else:
        # Fallback 
        finals = parse_final_outputs(block)
        if finals and finals[0].get("preview"):
            summary["final_output"] = finals[0]["preview"]

    return summary

# Parse a single trace block
def parse_trace_block(block: str) -> Optional[Dict[str, Any]]:
    tid_m = re.search(r"NEW TRACE:\s*([a-z0-9_]+)", block, flags=re.IGNORECASE)
    trace_id = clean_text(tid_m.group(1)) if tid_m else f"unknown_{abs(hash(block))%100000}"

    time_m = re.search(r"Time:\s*([^\n\r]+)", block)
    timestamp = clean_text(time_m.group(1)) if time_m else None
    if timestamp:
        dt = extract_date_from_text(timestamp)
        timestamp = dt or timestamp
    else:
        dt2 = extract_date_from_text(block)
        timestamp = dt2 or "Unknown"

    user_msg = None
    um = re.search(r"📥\s*USER[:\s]*([^\n\r]+)", block)
    if um:
        user_msg = clean_text(um.group(1))
    else:
        um2 = re.search(r"USER[:\s]*([^\n\r]+)", block)
        if um2:
            user_msg = clean_text(um2.group(1))

    mcp_calls = parse_mcp_calls(block)
    llm_decisions = parse_llm_decisions(block)
    handoffs = parse_handoffs(block)
    final_outputs = parse_final_outputs(block)
    summary = parse_trace_summary(block)

    return {
        "trace_id": trace_id,
        "timestamp": timestamp,
        "user_message": user_msg,
        "mcp_calls": mcp_calls,
        "llm_decisions": llm_decisions,
        "handoffs": handoffs,
        "final_outputs": final_outputs,
        "summary": summary
    }
# Top-level parse
def parse_log_file(content: str) -> Dict[str, Any]:
    header = extract_header_info(content)
    trace_blocks = split_traces(content)
    traces = []
    for block in trace_blocks:
        try:
            parsed = parse_trace_block(block)
            traces.append(parsed)
        except Exception as e:
            traces.append({
                "trace_id": "parse_error", 
                "error": str(e), 
                "raw_snippet_preview": clean_text(block[:400])
            })
    return {"header": header, "traces": traces, "total_traces": len(traces)}

# API endpoints - ENHANCED
@app.get("/admin/agent-logs/formatted")
async def get_formatted_logs():
    try:
        if not LOG_PATH.exists():
            raise HTTPException(status_code=404, detail=f"Log file not found at {LOG_PATH}")

        content = LOG_PATH.read_text(encoding="utf-8", errors="ignore")
        parsed = parse_log_file(content)

        # Enhanced post-processing
        for t in parsed.get("traces", []):
            # Clean handoff fields
            if t.get("handoffs"):
                for h in t["handoffs"]:
                    h["from"] = clean_text(h.get("from"))
                    h["to"] = clean_text(h.get("to"))

            # CRITICAL FIX: If final_outputs is empty but summary has final_output
            if (not t.get("final_outputs") or not any(f.get("preview") for f in t.get("final_outputs", []))) and t.get("summary", {}).get("final_output"):
                t["final_outputs"] = [{
                    "agent": None,
                    "model": None,
                    "length": len(t["summary"]["final_output"]),
                    "preview": t["summary"]["final_output"]
                }]
            
            # Additional check: if final_outputs exists but preview is None/empty
            elif t.get("final_outputs"):
                for output in t["final_outputs"]:
                    if not output.get("preview") and t.get("summary", {}).get("final_output"):
                        output["preview"] = t["summary"]["final_output"]

        return {
            "status": "success", 
            "data": parsed, 
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e), 
            "traceback": repr(e)
        }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)