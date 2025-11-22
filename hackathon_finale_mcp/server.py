from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import uvicorn
from dotenv import load_dotenv
import os
import cloudinary
import cloudinary.uploader
from cloudinary.exceptions import Error as CloudinaryError
import asyncio
from bson import ObjectId
import aiohttp
from typing import Optional
from datetime import datetime, timedelta

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")

print("PAGE ID:", FACEBOOK_PAGE_ID)
print("ACCESS TOKEN:", FACEBOOK_PAGE_ACCESS_TOKEN)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.debug(f"MONGO_URI: {os.getenv('MONGO_URI')[:10]}... (masked)")
logger.debug(f"CLOUDINARY_CLOUD_NAME: {os.getenv('CLOUDINARY_CLOUD_NAME')}")
logger.debug(f"CLOUDINARY_API_KEY: {os.getenv('CLOUDINARY_API_KEY')[:5]}... (masked)")


mcp = FastMCP(name="FastMCP", stateless_http=False, json_response=True)


connection = os.getenv("MONGO_URI")
if not connection:
    logger.error("MONGO_URI not set in environment variables")
    raise ValueError("MONGO_URI not set")
DB_NAME = "menudb"
COLLECTION_NAME = "products"

client = AsyncIOMotorClient(connection)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

if not all([cloudinary.config().cloud_name, cloudinary.config().api_key, cloudinary.config().api_secret]):
    logger.error("Cloudinary configuration incomplete")
    raise ValueError("Cloudinary configuration incomplete")


class Product(BaseModel):
    name: str
    price: int
    stock: int
    size: str | None = None
    color: str | None = None
    category: str | None = None
    image_url: str | None = None


def upload_image_to_cloudinary(file: UploadFile) -> str:
    try:
        result = cloudinary.uploader.upload(file.file)
        return result["secure_url"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {e}")

def safe_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format.")
product_cache = {
    "data": None,
    "last_updated": None
}
PRODUCT_CACHE_DURATION = timedelta(minutes=2)

@mcp.tool()
async def fetch_all_products():
    """
    Fetch all products with 2-minute caching
    """
    global product_cache
    
    now = datetime.now()
    
    if (product_cache["data"] is not None and 
        product_cache["last_updated"] is not None and
        (now - product_cache["last_updated"]) < PRODUCT_CACHE_DURATION):
        
        print("⚡ Returning cached products")
        return product_cache["data"]
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/products") as response:
                data = await response.json()
        
        if not data.get("success"):
            return {"status": "failed", "message": "No products found"}

        products = data["data"]
        formatted_products = [
            {
                "name": p["name"],
                "price": p["price"],
                "stock": p["stock"],
                "image_url": p.get("image_url"),
                "description": p.get("description")
            }
            for p in products
        ]
        
        result = {
            "status": "success",
            "message": "🛍 Available Products",
            "products": formatted_products
        }
        
        product_cache["data"] = result
        product_cache["last_updated"] = now
        
        print(f"✅ Products cached at {now}")
        return result

    except Exception as e:
        return {"status": "failed", "error": str(e)}
    

@mcp.tool()
async def upload_product_image(image_path: str, product_name: str):
    """Uploads product image to Cloudinary and saves URL in MongoDB."""
    try:
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return {"status": "failed", "error": f"Image file not found: {image_path}"}
        logger.info(f"Uploading image for {product_name}...")
        loop = asyncio.get_event_loop()
        upload_result = await loop.run_in_executor(
            None,
            lambda: cloudinary.uploader.upload(
                image_path,
                folder="inventory_images",
                public_id=os.path.splitext(os.path.basename(image_path))[0]
            )
        )
        logger.info(f"Cloudinary upload result: {upload_result}")
        image_url = upload_result.get("secure_url")
        if not image_url:
            return {"status": "failed", "error": "Cloudinary did not return a secure URL"}

        try:
            result = await collection.update_one(
                {"name": product_name.lower()},
                {"$set": {"image_url": image_url}},
                upsert=True
            )
            logger.info(f"Database update result: matched={result.matched_count}, upserted={result.upserted_id}")
            return {
                "status": "success",
                "product": product_name,
                "image_url": image_url,
                "message": "Image uploaded and saved in MongoDB!"
            }
        except Exception as e:
            logger.error(f"Database operation failed: {e}")
            return {"status": "failed", "error": f"Database operation failed: {e}"}
    except CloudinaryError as ce:
        logger.error(f"Cloudinary upload failed: {ce}")
        return {"status": "failed", "error": str(ce)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"status": "failed", "error": str(e)}
    

REORDER_THRESHOLD = 3 

@mcp.tool()
async def inventory_evaluation(product_name: str, quantity: int = 1):
    """
    Checks stock availability for the requested product. 
    Returns the product's full details and availability status, 
    including a flag for re-ordering. 
    
    Args:
        product_name: Name of the product to check
        quantity: Quantity requested (default: 1)-
    
    Returns:
        Dictionary with status, availability, and detailed message, and reorder_needed flag.
    """
    try:
        logger.info("="*70)
        logger.info(f"🔍 INVENTORY EVALUATION TOOL CALLED")
        logger.info(f"📝 Product Name Received: '{product_name}'")
        logger.info(f"📊 Quantity Requested: {quantity}")
        logger.info(f"🗄 Database: {DB_NAME}, Collection: {COLLECTION_NAME}")
        logger.info("="*70)
        
        search_name = product_name.lower().strip()
        logger.info(f"🔍 Normalized Search Term: '{search_name}'")
        
        product = await collection.find_one({"name": {"$regex": search_name, "$options": "i"}})
        
        if not product:
            logger.warning(f"❌ Product '{product_name}' NOT FOUND in database")
            
            all_products = await collection.find({}).limit(10).to_list(length=10)
            available_names = [p.get("name") for p in all_products]
            logger.info(f"📋 Available products in DB: {available_names}")
            
            return {
                "status": "not_found",
                "stock_available": False, 
                "message": f" Product '{product_name}' not found in inventory.\n\nAvailable products: {', '.join(available_names[:3])}",
                "product_details": None,
                "reorder_needed": False 
            }
        
        logger.info(f"✅ Product FOUND in database!")
        logger.info(f"📦 Full Product Data: {product}")
        
        product_info = {
            "id": str(product.get("_id")),
            "name": product.get("name", "Unknown"),
            "price": product.get("price", 0),
            "stock": product.get("stock", 0),
            "description": product.get("description", "No description available"),
            "image_url": product.get("image_url", "")
        }
        
        stock = product_info["stock"]
        required_quantity = max(1, quantity)
        is_available = stock >= required_quantity
        
        reorder_needed = stock <= REORDER_THRESHOLD
        
        logger.info(f"📊 STOCK CHECK:")
        logger.info(f"   - Available Stock: {stock}")
        logger.info(f"   - Required Quantity: {required_quantity}")
        logger.info(f"   - Status: {'✅ AVAILABLE' if is_available else '❌ INSUFFICIENT'}")
        logger.info(f"   - Reorder Needed: {reorder_needed} (Threshold: {REORDER_THRESHOLD})") 
        logger.info("="*70)
        
        if is_available:
            message = (
                f"✅ Stock Available!\n\n"
                f"📦 Product: {product_info['name']}\n"
                f"💰 Price: Rs.{product_info['price']}\n"
                f"📊 Available Stock: {stock} units\n"
                f"🛒 Requested: {required_quantity} unit(s)\n"
                f"📝 Description: {product_info['description']}\n\n"
                f"✅ Your order can be placed successfully!"
            )
        else:
            message = (
                f"❌ Insufficient Stock!\n\n"
                f"📦 Product: {product_info['name']}\n"
                f"💰 Price: Rs.{product_info['price']}\n"
                f"📊 Available Stock: {stock} units\n"
                f"🛒 Requested: {required_quantity} unit(s)\n"
                f"⚠ Short by: {required_quantity - stock} units\n\n"
                f"Sorry, we don't have enough stock for your order."
            )

        result = {
            "status": "success",
            "stock_available": is_available,
            "required_quantity": required_quantity,
            "available_stock": stock,
            "message": message,
            "product_details": product_info,
            "reorder_needed": reorder_needed 
        }
        
        logger.info(f" Returning result: {result}")
        return result
        
    except Exception as e:
        logger.error(f" CRITICAL ERROR in inventory_evaluation: {e}", exc_info=True)
        return {
            "status": "error", 
            "error": str(e), 
            "stock_available": False,
            "reorder_needed": False, 
            "message": f"⚠ System error occurred: {str(e)}\nPlease contact support."
        }
        

@mcp.tool()
async def evaluate_multiple_inventory(products_list: list[dict]):
    """
    Checks stock availability for a list of requested products.
    The input should be a list of dictionaries: [{'name': 'product_a', 'quantity': 2}, ...].
    
    Args:
        products_list: A list of dicts, where each dict has 'name' (str) and 'quantity' (int).
    
    Returns:
        A comprehensive report on the availability of all requested products.
    """
    logger.info("="*70)
    logger.info("🛒 MULTIPLE INVENTORY EVALUATION TOOL CALLED")
    
    full_report = []
    
    overall_order_status = "Available"
    
    for item in products_list:
        product_name = item.get('name', 'N/A')
        quantity = item.get('quantity', 1)
        
        result = await inventory_evaluation(product_name, quantity)
        
        if not result.get('stock_available'):
            overall_order_status = "Insufficient Stock"
            
        full_report.append(result)

    summary_message = f"🛒 Order Summary: Overall Status: {overall_order_status}.\n\n"
    
    for item in full_report:
        details = item.get('product_details', {})
        name = details.get('name', item.get('name', 'Unknown Product'))
        
        if item.get('status') == 'not_found':
            summary_message += f" {name}: Not Found in Inventory.\n"
        elif item.get('stock_available'):
            summary_message += (
                f" {name}: Available! (Requested: {item.get('required_quantity', 0)}, "
                f"Available: {item.get('available_stock', 0)}).\n"
            )
        else:
            shortage = item.get('required_quantity', 0) - item.get('available_stock', 0)
            summary_message += (
                f"⚠ {name}: INSUFFICIENT STOCK! (Available: {item.get('available_stock', 0)}, "
                f"Short by: {shortage}).\n"
            )

    logger.info(f" Multiple Inventory Evaluation Completed. Status: {overall_order_status}")
    
    return {
        "status": overall_order_status,
        "message": summary_message,
        "report": full_report
    } 
    
@mcp.tool()
async def create_order(products_list: list[dict], total_amount: float, customer_phone: str):
    """
    Creates a new order in the system with multiple products and stores the full order data.
    
    Args:
        products_list: List of products, e.g., [{'name': 'Kurta Pajama', 'quantity': 2, 'price': 2500.0}, ...]
        total_amount: Grand total of the order.
        customer_phone: Customer's identifier.
    """
    try:
        order_id = f"ORD{str(ObjectId())[:8].upper()}"
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        order_data = {
            "order_id": order_id,
            "products": products_list,  
            "total_amount": total_amount,
            "customer_phone": customer_phone,
            "payment_status": "pending",
            "delivery_status": "awaiting_payment",
            "created_at": created_at
        }
        
     
        
        logger.info(f"🧾 ORDER CREATED (Multiple Products): {order_data}")

        message = (
            f"✅ Order Created Successfully!\n\n"
            f"🆔 Order ID: {order_id}\n"
            f"💵 Total: Rs.{total_amount}\n"
            f"💳 Payment Details:\n"
            f"📲 EasyPaisa / JazzCash: 0300-1234567\n"
            f"💰 Amount: Rs.{total_amount}\n"
            f"🔖 Order Ref: #{order_id}\n\n"
            f"Payment karne ke baad 'paid' ya 'payment done' bhej dein!"
        )

        return {
            "status": "success",
            "order": order_data,
            "message": message
        }

    except Exception as e:
        logger.error(f"❌ create_order failed: {e}")
        return {"status": "failed", "error": str(e)}
    


@mcp.tool()
async def process_payment(
    order_id: str, 
    total_amount: float = 0.0, 
    products_list: list[dict] = None, 
    payment_method: str = "easypaisa",
    customer_phone: str = None
):
    """
    Payment process karta hai AUR database mein save karta hai
    """
    try:
        payment_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if not products_list or total_amount == 0.0:
            logger.warning(f"⚠ Incomplete payment data for order {order_id}")
            return {"status": "failed", "error": "Incomplete payment data"}
        
        sale_data = {
            "order_id": order_id,
            "total_sales_amount": total_amount,
            "products_sold": [
                {
                    "name": p["name"], 
                    "quantity": p["quantity"], 
                    "price": p["price"], 
                    "total": p["quantity"] * p["price"]
                }
                for p in products_list
            ],
            "paid_at": payment_time,
            "payment_method": payment_method,
            "customer_phone": customer_phone
        }
        
        try:
            logger.info(f"📦 Sending sale_data to FastAPI: {sale_data}")  
            print("📦 Sending sale_data to FastAPI:", sale_data)
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{BASE_URL}/api/sales",
                    json=sale_data
                ) as response:
                    db_response = await response.json()
                    logger.info(f"🧾 DB Response: {db_response}")         
                    print("🧾 DB Response:", db_response) 
                    
                    if not db_response.get("success"):
                        logger.error(f"❌ Database save failed: {db_response}")
                        return {
                            "status": "failed",
                            "error": "Failed to save sale in database"
                        }
                    
                    logger.info(f"✅ Sale saved to DB: {order_id}")
        
        except Exception as db_error:
            logger.error(f"❌ Database error: {db_error}")
            return {
                "status": "failed",
                "error": f"Database connection failed: {str(db_error)}"
            }
        
        message = (
            f"✅ Payment Received Successfully!\n\n"
            f"🆔 Order ID: {order_id}\n"
            f"💳 Method: {payment_method.capitalize()}\n"
            f"🕓 Paid At: {payment_time}\n\n"
            f"🚚 Your order is now being prepared.\n"
            f"📦 Delivery in 3–5 working days!\n\n"
            f"Thank you for shopping with us 💚"
        )

        return {
            "status": "success",
            "message": message,
            "sale_saved": True,
            "order_id": order_id
        }

    except Exception as e:
        logger.error(f"❌ process_payment failed: {e}")
        return {"status": "failed", "error": str(e)}


@mcp.tool()
async def generate_sales_report_http():
    """
    Database se saare sales fetch karke report banata hai.
    Session dependency KHATAM!
    """
    try:
        logger.info("📊 Fetching sales from database...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/api/sales") as response:
                db_response = await response.json()
        
        if not db_response.get("success"):
            logger.warning("⚠ No sales data in database")
            return {
                "report_type": "sales_summary",
                "status": "warning",
                "message": "No sales data found in database",
                "data": {
                    "total_orders": 0,
                    "total_revenue": 0.0,
                    "transactions": [],
                    "product_summary": {}
                }
            }
        
        report_data = db_response.get("data", {})
        
        logger.info(f"✅ Report Generated: {report_data.get('total_orders')} orders, Rs.{report_data.get('total_revenue')}")

        return {
            "report_type": "sales_summary",
            "status": "success",
            "message": f"Report generated: {report_data.get('total_orders')} orders found",
            "data": report_data
        }

    except Exception as e:
        logger.error(f"❌ Report generation failed: {e}")
        return {
            "report_type": "sales_summary",
            "status": "error",
            "message": f"Error: {str(e)}",
            "data": {}
        }


@mcp.tool()
async def get_random_supplier_details():
    """
    CRUD Server (Port 8002) se randomly ek supplier ki details fetch karta hai.
    (Buying Agent yeh tool call karega)
    """
    logger.info("MCP TOOL: Fetching random supplier details from CRUD Server.")
    
    CRUD_SERVER_URL = BASE_URL
    ENDPOINT = "/api/suppliers/random" 
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{CRUD_SERVER_URL}{ENDPOINT}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        supplier_data = data.get("data")
                        logger.info(f"✅ Random supplier fetched: {supplier_data.get('name')}")
                        return {
                            "status": "success",
                            "message": "Random supplier details fetched successfully.",
                            "supplier_data": supplier_data
                        }
                    else:
                        error_msg = data.get("detail", "No suppliers found or unknown CRUD error.")
                        logger.error(f"❌ CRUD Server returned failure: {error_msg}")
                        return {"status": "failed", "message": error_msg}
                else:
                    error_text = await response.text()
                    logger.error(f"❌ HTTP Error {response.status} from CRUD Server: {error_text}")
                    return {"status": "failed", "message": f"CRUD Server connection error: {response.status}"}

    except Exception as e:
        logger.error(f"❌ get_random_supplier_details failed: {e}")
        return {"status": "failed", "message": f"Connection failed: {str(e)}"}


@mcp.tool()
async def finalize_supplier_purchase_and_update_stock(
    product_name: str, 
    quantity_purchased: int, 
    amount_paid: float,
    supplier_name: str):
    """
    Admin ki confirmation ke baad, supplier purchase ko record karta hai aur turant stock badhata hai. 
    Yeh naye 'POST /api/purchases/complete' endpoint ko call karta hai.
    """
    logger.info(f"MCP TOOL: Finalizing purchase for {product_name} - Qty: {quantity_purchased}")
    try:
        payload = {
            "product_name": product_name,
            "quantity_purchased": quantity_purchased,
            "supplier_name": supplier_name,
            "amount_paid": amount_paid,
            "payment_status": "completed" 
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{BASE_URL}/api/purchases/complete", json=payload) as response:
                db_response = await response.json()

                if response.status == 200 and db_response.get("success"):
                    logger.info("✅ Purchase finalized and stock updated via HTTP.")
                    return {
                        "status": "success", 
                        "message": db_response.get("message"),
                        "new_stock": db_response.get("new_stock")
                    }
                else:
                    error_detail = db_response.get('detail', 'Unknown error from CRUD Server')
                    logger.error(f"❌ HTTP Error finalizing purchase: {response.status}, Detail: {error_detail}")
                    return {"status": "error", "message": f"Server error: {error_detail}"}

    except Exception as e:
        logger.error(f"❌ finalize_supplier_purchase_and_update_stock failed: {e}")
        return {"status": "failed", "error": str(e)}


@mcp.tool()
async def generate_purchase_report():
    """
    Admin dashboard ke liye saari supplier purchases fetch karke report banata hai.
    """
    logger.info("MCP TOOL: Fetching purchase report via HTTP.")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/api/purchases") as response:
                if response.status == 200:
                    report_data = await response.json()
                    logger.info("✅ Purchase report fetched successfully.")
                    
                    data = report_data.get("data", {})
                    return {
                        "report_type": "supplier_purchases",
                        "total_spent": data.get("total_spent"),
                        "total_records": data.get("total_records"),
                        "data": data.get("transactions", [])
                    }
                else:
                    error_detail = await response.text()
                    logger.error(f"❌ HTTP Error fetching purchase report: {response.status}")
                    return {"status": "error", "message": f"Server error: {error_detail}"}

    except Exception as e:
        logger.error(f"❌ generate_purchase_report failed: {e}")
        return {"status": "failed", "error": str(e)}


    

@mcp.tool()
async def order_summary(order_id: str):
    """
    Mock tool: Returns a fake order summary (to show order tracking via WhatsApp).
    """
    try:
        mock_order = {
            "order_id": order_id,
            "status": "in_transit",
            "estimated_delivery": "3-5 working days",
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        message = (
            f"🚚 Order Status Update!\n\n"
            f"🆔 Order ID: {order_id}\n"
            f"📦 Status: {mock_order['status']}\n"
            f"⏳ Estimated Delivery: {mock_order['estimated_delivery']}\n"
            f"🕓 Last Update: {mock_order['last_update']}\n\n"
            f"Thank you for your patience 💚"
        )

        return {"status": "success", "order": mock_order, "message": message}

    except Exception as e:
        logger.error(f"❌ order_summary failed: {e}")
        return {"status": "failed", "error": str(e)}
           


@mcp.tool()
async def calculate_profit_loss(sales_data: dict, purchase_data: dict):
    """
    Sales aur purchase data ko analyze karke profit/loss calculate karta hai.
    Analytics Agent autonomously isko use karega final P/L report banane ke liye.
    
    Args:
        sales_data: generate_sales_report_http() ka complete output
        purchase_data: generate_purchase_report() ka complete output
    
    Returns:
        Comprehensive profit/loss summary with formatted message
    """
    try:
        logger.info("🧮 MCP TOOL: Calculating Profit/Loss...")
        
        # Extract totals from both reports
        total_sales = sales_data.get("data", {}).get("total_revenue", 0.0)
        total_purchases = purchase_data.get("total_spent", 0.0)
        
        # Calculate P/L
        profit_loss = total_sales - total_purchases
        
        # Generate user-friendly message
        status_message = "💰 PROFIT/LOSS REPORT 📊\n"
        status_message += f"Total Sales Revenue: Rs. {total_sales:,.2f}\n"
        status_message += f"Total Inventory Spent: Rs. {total_purchases:,.2f}\n"
        
        if profit_loss >= 0:
            status_message += f" Net Profit: Rs. {profit_loss:,.2f}"
        else:
            status_message += f" Net Loss: Rs. {abs(profit_loss):,.2f}"
        
        logger.info(f" P/L Calculated: Sales={total_sales}, Purchases={total_purchases}, P/L={profit_loss}")
        
        return {
            "report_type": "profit_loss_summary",
            "status": "success",
            "message": status_message,
            "data": {
                "total_sales": total_sales,
                "total_purchases": total_purchases,
                "profit_loss": profit_loss
            }
        }
    
    except Exception as e:
        logger.error(f" calculate_profit_loss failed: {e}")
        return {
            "report_type": "profit_loss_summary",
            "status": "error",
            "message": f"Calculation failed: {str(e)}",
            "data": {}
        }
        

@mcp.tool()
async def analyze_low_selling_products(sales_threshold: int = 5):
    """
    Analyzes sales data to identify products with sales below threshold.
    
    Args:
        sales_threshold: Minimum sales count (default: 5)
    
    Returns:
        List of low-selling products with detailed metrics
    """
    try:
        logger.info(f"🔍 Analyzing low-selling products (threshold: {sales_threshold})...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/api/sales/product-analysis") as response:
                if response.status != 200:
                    return {
                        "status": "error",
                        "message": "Failed to fetch sales data",
                        "products": []
                    }
                
                sales_data = await response.json()
        
        if not sales_data.get("success"):
            return {
                "status": "error",
                "message": "No sales data available",
                "products": []
            }
        
        product_sales = sales_data.get("data", {}).get("product_summary", {})
        
        all_products = await collection.find({}).to_list(length=None)
        
        low_sellers = []
        for product in all_products:
            product_name = product.get("name", "")
            sales_count = product_sales.get(product_name, {}).get("quantity", 0)
            
            if sales_count < sales_threshold:
                low_sellers.append({
                    "name": product_name,
                    "sales_count": sales_count,
                    "stock": product.get("stock", 0),
                    "price": product.get("price", 0),
                    "image_url": product.get("image_url", "")
                })
        
        logger.info(f" Found {len(low_sellers)} low-selling products")
        
        return {
            "status": "success",
            "threshold": sales_threshold,
            "low_selling_count": len(low_sellers),
            "products": low_sellers,
            "message": f"Identified {len(low_sellers)} products with sales below {sales_threshold}"
        }
    
    except Exception as e:
        logger.error(f" analyze_low_selling_products error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "products": []
        }


async def post_to_facebook_page(message: str, image_url: Optional[str] = None) -> dict:
    try:
        if not FACEBOOK_PAGE_ID or not FACEBOOK_PAGE_ACCESS_TOKEN:
            logger.error(" Facebook credentials missing in .env")
            return {"status": "failed", "message": "Credentials missing"}

        async with aiohttp.ClientSession() as session:
            post_result = {}

            if image_url:
                upload_url = f"https://graph.facebook.com/v18.0/{FACEBOOK_PAGE_ID}/photos"
                upload_data = {
                    "url": image_url,
                    "published": "true",
                    "caption": message,
                    "access_token": FACEBOOK_PAGE_ACCESS_TOKEN
                }
                async with session.post(upload_url, data=upload_data) as resp:
                    post_result = await resp.json()
            else:
                publish_url = f"https://graph.facebook.com/v18.0/{FACEBOOK_PAGE_ID}/feed"
                publish_data = {
                    "message": message,
                    "access_token": FACEBOOK_PAGE_ACCESS_TOKEN
                }
                async with session.post(publish_url, data=publish_data) as resp:
                    post_result = await resp.json()

            if "id" in post_result:
                post_id = post_result["id"]
                logger.info(f" Facebook feed post created: {post_id}")
                return {
                    "status": "success",
                    "post_id": post_id,
                    "post_url": f"https://facebook.com/{post_id}"
                }

            error_msg = post_result.get("error", {}).get("message", "Unknown error")
            return {"status": "failed", "message": error_msg}

    except Exception as e:
        logger.error(f" post_to_facebook_page failed: {e}")
        return {"status": "failed", "message": str(e)}



async def post_to_facebook_background(campaign_id: str, message: str, image_url: Optional[str]):
    """
    Background task: Facebook par post karo aur database update karo
    Ye function agent ke response ke baad quietly run hoga
    """
    try:
        logger.info(f"🔄 Background posting started for campaign: {campaign_id}")
        
        facebook_result = await post_to_facebook_page(message=message, image_url=image_url)
        
        update_data = {
            "facebook_post_status": facebook_result.get("status"),
            "facebook_post_id": facebook_result.get("post_id", "N/A"),
            "facebook_post_url": facebook_result.get("post_url", "N/A"),
            "posted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        async with aiohttp.ClientSession() as session:
            await session.patch(
                f"{BASE_URL}/api/marketing/campaigns/{campaign_id}",
                json=update_data
            )
        
        if facebook_result.get("status") == "success":
            logger.info(f"✅ Background post SUCCESS: {facebook_result.get('post_id')}")
        else:
            logger.error(f"❌ Background post FAILED: {facebook_result.get('message')}")
        
    except Exception as e:
        logger.error(f"❌ Background posting error for {campaign_id}: {e}")



@mcp.tool()
async def generate_facebook_poster(product_name: str, campaign_type: str = "low_sales_boost"):
    """
    NEW BEHAVIOR:
    1. Campaign turant create karo
    2. Agent ko "success" return karo (FAST!)
    3. Background mein Facebook par post karo (SLOW part)
    """
    try:
        logger.info(f"🎨 Creating campaign for {product_name}...")

        product = await collection.find_one({"name": {"$regex": product_name, "$options": "i"}})
        if not product:
            return {"status": "failed", "message": f"Product {product_name} not found"}

        price = product.get("price", 0)
        image_url = product.get("image_url", None)
        stock = product.get("stock", 0)

        discount_text = "20% OFF!" if campaign_type == "low_sales_boost" else "Limited Stock!"
        facebook_message = f"""
🔥 SPECIAL OFFER 🔥

{product_name}
💰 Price: Rs. {price:,}
🎁 {discount_text}

✨ High Quality | Fast Delivery
📲 Order Now via WhatsApp!

#Fashion #Sale #Shopping #Pakistan
        """.strip()

        poster_data = {
            "product_name": product_name,
            "campaign_type": campaign_type,
            "price": price,
            "discount": discount_text,
            "cta": "Shop Now on WhatsApp!",
            "product_image": image_url,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "facebook_post_status": "pending",  
            "facebook_post_id": "processing",
            "facebook_post_url": "processing"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{BASE_URL}/api/marketing/campaigns", json=poster_data) as resp:
                db_result = await resp.json()
        
        campaign_id = db_result.get("campaign_id", "N/A")
        logger.info(f"✅ Campaign created in DB: {campaign_id}")

        asyncio.create_task(
            post_to_facebook_background(campaign_id, facebook_message, image_url)
        )
        logger.info(f"🚀 Background posting scheduled for {product_name}")

        return {
            "status": "success",
            "product_name": product_name,
            "campaign_id": campaign_id,
            "facebook_posted": "scheduled", 
            "message": f"✅ Campaign created! Facebook posting in progress (Campaign ID: {campaign_id})"
        }

    except Exception as e:
        logger.error(f"❌ generate_facebook_poster error: {e}")
        return {"status": "failed", "message": str(e)}


# ==========================================================
# BONUS: Batch Tool (Multiple Products at Once)
# ==========================================================
@mcp.tool()
async def generate_facebook_campaign_batch(product_names: list[str], campaign_type: str = "low_sales_boost"):
    """
    Multiple products ko parallel process karo
    Example: ["Maxi", "Abaya", "Frock"] → 3 campaigns ek saath
    """
    try:
        logger.info(f" Batch campaign starting for {len(product_names)} products...")
        
        # Saare products ko parallel process karo
        tasks = [
            generate_facebook_poster(product_name, campaign_type)
            for product_name in product_names
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successes
        success_count = sum(
            1 for r in results 
            if isinstance(r, dict) and r.get("status") == "success"
        )
        
        logger.info(f" Batch complete: {success_count}/{len(product_names)} successful")
        
        return {
            "status": "success",
            "total_products": len(product_names),
            "successful_campaigns": success_count,
            "failed_campaigns": len(product_names) - success_count,
            "results": [
                {
                    "product": r.get("product_name", "Unknown"),
                    "status": r.get("status", "error"),
                    "campaign_id": r.get("campaign_id", "N/A")
                }
                for r in results if isinstance(r, dict)
            ],
            "message": f" Batch complete! {success_count} campaigns created and posting in background."
        }
        
    except Exception as e:
        logger.error(f" Batch campaign error: {e}")
        return {"status": "failed", "message": str(e)}


@mcp.tool()
async def generate_profit_loss_report():
    """
    Runs Sales Report + Purchase Report in parallel,
    then uses both results to calculate Profit/Loss.
    Returns one combined JSON.
    """

    try:
        sales_task = asyncio.create_task(generate_sales_report_http())
        purchase_task = asyncio.create_task(generate_purchase_report())

        sales_result, purchase_result = await asyncio.gather(
            sales_task, purchase_task
        )

        profit_loss_result = await calculate_profit_loss(
            sales_result,
            purchase_result
        )
        return {
            "status": "success",
            "message": "Full business report generated successfully",
            "sales_report": sales_result,
            "purchase_report": purchase_result,
            "profit_loss_report": profit_loss_result
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }
    

app = FastAPI(title="MCP Server with Test Endpoints")

@app.get("/")
async def root():
    return {
        "status": "running",
        "service": "MCP Server + MongoDB + Cloudinary",
        "mcp_endpoint": "/mcp",
        "test_endpoints": {
            "database": "/test/db",
            "inventory": "/test/inventory/{product_name}",
            "low_sellers": "/test/low-sellers"
        }
    }

@app.get("/test/db")
async def test_db():
    try:
        count = await collection.count_documents({})
        products = await collection.find({}).limit(10).to_list(length=10)
        product_names = [p.get("name") for p in products]
        return {
            "status": "success",
            "db_name": DB_NAME,
            "collection": COLLECTION_NAME,
            "total_products": count,
            "sample_products": product_names
        }
    except Exception as e:
        logger.error(f"Database test failed: {e}", exc_info=True)
        return {"status": "failed", "error": str(e)}

@app.get("/test/inventory/{product_name}")
async def test_inventory(product_name: str, quantity: int = 1):
    logger.info(f"🧪 TEST ENDPOINT CALLED: /test/inventory/{product_name}")
    result = await inventory_evaluation(product_name, quantity)
    logger.info(f"🧪 TEST RESULT: {result}")
    return result

@app.get("/test/low-sellers")
async def test_low_sellers():
    result = await analyze_low_selling_products(sales_threshold=3)
    return result

@app.get("/test/poster/{product_name}")
async def test_poster(product_name: str):
    result = await generate_facebook_poster(product_name, "low_sales_boost")
    return result

@app.get("/test/facebook-post")
async def test_facebook_post():
    result = await post_to_facebook_page(
        message="🧪 Test post from your e-commerce system!\n\nThis is an automated test.",
        image_url=None
    )
    return result

mcp_app = mcp.streamable_http_app()
app.mount("/mcp", mcp_app)

if __name__ == "__main__":
    logger.info("🚀 Starting FastAPI + MCP Server on port 8080...")
    uvicorn.run("server:mcp_app", host="0.0.0.0", port=8080, reload=True)