import os
from dotenv import load_dotenv
from agents import  AsyncOpenAI, OpenAIChatCompletionsModel, SQLiteSession
from agents.run import RunConfig
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams
from twilio.rest import Client


load_dotenv()


# ======================== Model Configuration =======================

gemini_api_key = os.getenv("GEMINI_API_KEY")
external_client = AsyncOpenAI(
    api_key= gemini_api_key,
    base_url= "https://generativelanguage.googleapis.com/v1beta/openai/",
)
    
model = OpenAIChatCompletionsModel(
    model= "gemini-2.5-flash",
    openai_client= external_client,
)

config = RunConfig(
    model= model,
    model_provider=external_client,
    
)

# ============================== MCP & Session Configuration ===================

# URL = os.getenv("BASE_URL")
# MCP_SERVER_URL=f"{URL}/mcp"
MCP_SERVER_URL = "http://localhost:8080/mcp"
mcp_params = MCPServerStreamableHttpParams(url=MCP_SERVER_URL)
CRUD_BASE_URL=os.getenv("CRUD_BASE_URL")
session = SQLiteSession("conversation_123")
scheduled_session = SQLiteSession("scheduled_business_decisions")
admin_session = SQLiteSession("admin_dashboard_session")

# ====================== Shared MCP Client (async context) ====================

mcp_client = MCPServerStreamableHttp(
    params=mcp_params,
    name="MySharedMCPClient",
    cache_tools_list=True
)

# =========================== Whatsapp Configuration ========================


TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP = "whatsapp:+14155238886"
ADMIN_PHONE_NUMBER = os.getenv("ADMIN_PHONE_NUMBER")

client = Client(TWILIO_SID, TWILIO_AUTH)
if not ADMIN_PHONE_NUMBER:
    print("⚠ WARNING: ADMIN_PHONE_NUMBER .env mein set nahi hai. Admin notifications nahi jaayengi.")

