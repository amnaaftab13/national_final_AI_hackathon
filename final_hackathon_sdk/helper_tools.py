from agents import function_tool,Runner
from configuration import session,ADMIN_PHONE_NUMBER
import asyncio
from dashboard_cache import (
    get_cached_dashboard,
    cache_dashboard,
    invalidate_dashboard_cache,
    get_cache_stats
)
from datetime import datetime
import httpx 
from pydantic import BaseModel
from typing import List
from configuration import TWILIO_WHATSAPP,client

@function_tool
def notify_admin_for_purchase(
    product_name: str, 
    current_stock: int, 
    reorder_quantity: int = 10,
    supplier_name: str = "Unknown Supplier", 
    supplier_account: str = "N/A",
    calculated_amount_paid: float = 0.0 
):
    """
    Admin ko WhatsApp message bhejta hai ke stock kam hai aur payment karni hai.
    Supplier ki details aur payable amount bhi shamil ki gayi hain.
    """
    if not ADMIN_PHONE_NUMBER:
        print("❌ Admin notification failed: ADMIN_PHONE_NUMBER not set.")
        return "Admin notification failed: Number not configured."
    
    try:
        message_body = (
            f"🔥 LOW STOCK ALERT 🔥\n\n"
            f"📦 Product: {product_name}\n"
            f"📊 Current Stock: {current_stock} units\n"
            f"🛒 Suggested Order: {reorder_quantity} units\n\n"
            f"--- 💸 PAYMENT DETAILS ---\n"
            f"💰 PAYABLE AMOUNT: Rs. {calculated_amount_paid:,.2f}\n" 
            f"🏭 Supplier Name: {supplier_name}\n"
            f"💳 Account/Details: {supplier_account}\n\n"
            f"Action Required: Supplier ko payment kar dein.\n\n"
            f"Payment ke baad, 'Supplier paid {product_name}' reply karein."
        )
        
        client.messages.create(
             from_=TWILIO_WHATSAPP,
             to=ADMIN_PHONE_NUMBER,
             body=message_body
        )

        print(f"✅ Admin ko notification bhej di gayi hai for {product_name}")
        print(f"📝 Message Body:\n{message_body}") 
        return f"Admin notified successfully for {product_name}. Supplier: {supplier_name}"
    
    except Exception as e:
        print(f"❌ Admin notification send ERROR: {e}")
        return f"Admin notification failed: {e}"
    
#  Send Business Recommendations to Admin
@function_tool
def notify_admin_business_recommendations(recommendations: str):
    """Admin ko business suggestions bhejta hai"""
    if not ADMIN_PHONE_NUMBER:
        return "Admin number not configured"
    
    try:
        message_body = (
            f"💼 BUSINESS INSIGHTS & RECOMMENDATIONS\n\n"
            f"{recommendations}\n\n"
        )
        
        client.messages.create(
            from_=TWILIO_WHATSAPP,
            to=ADMIN_PHONE_NUMBER,
            body=message_body
        )
        
        print(f"✅ Business recommendations sent to admin")
        print(f"📝 Recommendations:\n{recommendations}")
        return "Admin notified with business recommendations"
    
    except Exception as e:
        print(f"❌ Recommendation notification ERROR: {e}")
        return f"Failed: {e}"

    
@function_tool
async def simulate_easypaisa_payment(order_id: str, sender_number: str, amount: float):
    """
    Simulates a local Easypaisa payment confirmation.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/mock/easypaisa/payment",
                json={
                    "order_id": order_id,
                    "sender_number": sender_number,
                    "amount": amount
                },
                timeout=10.0
            )
            data = response.json()
            print(f"✅ Easypaisa simulated: {data}")
            
            
            # CACHE INVALIDATION after payment
            
            print("🗑️  Invalidating dashboard cache after payment...")
            invalidate_dashboard_cache()
            
            return data
    except Exception as e:
        print(f"❌ Easypaisa simulation failed: {e}")
        return {"status": "failed", "error": str(e)}
@function_tool
def invalidate_cache_after_transaction():
    """
    Invalidate dashboard cache after any financial transaction
    (Kisi bhi financial transaction ke baad dashboard cache clear karo)
    
    WHEN TO USE:
    - After order creation
    - After payment processing
    - After supplier purchase finalization
    """
    print("🗑️  [FINANCE AGENT] Invalidating dashboard cache...")
    invalidate_dashboard_cache()
    return {
        "status": "success",
        "message": "Dashboard cache invalidated successfully",
        "timestamp": datetime.now().isoformat()
    }
    
