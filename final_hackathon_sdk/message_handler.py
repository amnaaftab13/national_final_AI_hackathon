from state_manager import (
    get_state_manager,  
    cache_message, 
    enable_degraded,
    is_mcp_error
)
import traceback
state = get_state_manager()
from agents import Runner
from agents_file import main_agent
from configuration import session
from configuration import TWILIO_WHATSAPP,client

# ================= Message Processing ===================

async def process_user_message(user_message: str, user_number: str):
    """Process message with comprehensive error handling"""
    try:
        query = f"""
        [User Context]
        User Phone: {user_number}
        User Message: '{user_message}'
        """

        try:
            print(f"🤖 Running agent for: {user_message[:10]}...")
            result = await Runner.run(main_agent, query, session=session)
            reply = getattr(result, "final_output", "Done ✅")
            
            print(f"✅ Agent completed successfully")

        except Exception as e:
            print(f"\n{'!'*70}")
            print(f"⚠ EXCEPTION CAUGHT IN RUNNER")
            print(f"{'!'*70}")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}")
            print(f"\nFull Traceback:")
            print(traceback.format_exc())
            print(f"{'!'*70}\n")

            if is_mcp_error(e):
                print(f"🔴 MCP ERROR DETECTED - Switching to degraded mode")
                enable_degraded(f"Runner exception: {type(e).__name__}")
                cache_message(user_message, user_number)
                reply = (
                    "⚠ System temporarily offline. "
                    "Your message is saved and will be processed automatically."
                )
            else:
                print(f"⚠ Non-MCP error: {e}")
                reply = "⚙ Technical issue occurred. Please try again."

        
    #     client.messages.create(
    #         from_=TWILIO_WHATSAPP,
    #         to=user_number,
    #         body=reply
    #    ) 
        print(f"📤 Reply: {reply}")

    except Exception as outer_e:
        print(f"⚠ OUTER FATAL ERROR: {outer_e}")
        print(traceback.format_exc())
