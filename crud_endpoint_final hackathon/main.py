from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt , JWTError
from datetime import datetime, timedelta
from typing import Optional, List
import logging
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import cloudinary
import cloudinary.uploader
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware
import random
import bcrypt

# ================= LOAD ENVIRONMENT VARIABLES================

load_dotenv()

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ===================== PASSWORD HASHING & JWT CONFIGURATION ===============

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production-minimum-32-chars")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admins/login")


logger.debug(f"MONGO_URI: {os.getenv('MONGO_URI')[:10]}... (masked)")
logger.debug(f"CLOUDINARY_CLOUD_NAME: {os.getenv('CLOUDINARY_CLOUD_NAME')}")

app = FastAPI(title="Extended CRUD Server with Marketing & Analytics")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =================DATABASE CONNECTION===================

connection = os.getenv("MONGO_URI")
if not connection:
    logger.error("MONGO_URI not set")
    raise ValueError("MONGO_URI not set")

DB_NAME = "menudb"
COLLECTION_NAME = "products"
SALES_COLLECTION = "sales"
PURCHASES_COLLECTION = "supplier_purchases"
SUPPLIERS_COLLECTION = "suppliers"
CAMPAIGNS_COLLECTION = "marketing_campaigns"  
BUSINESS_INSIGHTS_COLLECTION = "business_insights"  
ADMIN_COLLECTION = "admins"


client = AsyncIOMotorClient(connection)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
sales_collection = db[SALES_COLLECTION]
purchases_collection = db[PURCHASES_COLLECTION]
suppliers_collection = db[SUPPLIERS_COLLECTION]
campaigns_collection = db[CAMPAIGNS_COLLECTION]  
insights_collection = db[BUSINESS_INSIGHTS_COLLECTION]  
admins_collection = db[ADMIN_COLLECTION]


# ================= CLOUDINARY CONFIGURATION ===================

CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
API_KEY = os.getenv("CLOUDINARY_API_KEY")
API_SECRET = os.getenv("CLOUDINARY_API_SECRET")


if not all([CLOUD_NAME, API_KEY, API_SECRET]):
    logging.error("Cloudinary configuration incomplete. Check environment variables.")
    raise ValueError("Cloudinary configuration incomplete. Please set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET.")

cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=API_KEY,
    api_secret=API_SECRET,
    secure=True
)

# ==================== AUTHENTICATION HELPER FUNCTIONS ==================


def hash_password(password: str) -> str:
    """Hash password using bcrypt directly"""
    password_bytes = password.encode('utf-8')[:72] 
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt directly"""
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_admin(token: str = Depends(oauth2_scheme)):
    """Verify JWT token and get current admin."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        admin = await admins_collection.find_one({"email": email})
        if admin is None:
            raise credentials_exception
        return admin
    
    except JWTError:
        raise credentials_exception


#  ======================== MODELS ========================

class Product(BaseModel):
    name: str
    price: float
    stock: int
    category: str | None = None
    stitching_type: str | None = None
    color: str | None = None
    description: str | None = None
    image_url: str | None = None

class SalesRecord(BaseModel):
    order_id: str
    total_sales_amount: float
    products_sold: list[dict]
    paid_at: str
    payment_method: str
    customer_phone: str | None = None

class SupplierPurchaseRecord(BaseModel):
    product_name: str
    quantity_purchased: int
    supplier_name: str | None = "Unknown Supplier"
    amount_paid: float
    payment_status: str = "pending"

class Supplier(BaseModel):
    name: str
    contact_person: str | None = None
    phone: str
    email: str | None = None
    address: str | None = None
    account_details: str | None = None


class MarketingCampaign(BaseModel):
    product_name: str
    campaign_type: str  
    price: float
    discount: str | None = None
    cta: str = "Shop Now!"
    product_image: str | None = None
    poster_url: str | None = None
    status: str = "active"  

class BusinessInsight(BaseModel):
    insight_type: str 
    products_affected: list[dict]
    recommendations: str
    priority: str = "medium"  
    status: str = "pending"  


# ======================= HELPER FUNCTIONS ====================

def serialize_item(item):
    """Convert MongoDB document to JSON-serializable dict"""
    return {
        "_id": str(item.get("_id")),
        "name": item.get("name"),
        "price": item.get("price"),
        "stock": item.get("stock"),
        "category": item.get("category"),
        "stitching_type": item.get("stitching_type"),
        "color": item.get("color"),
        "description": item.get("description"),
        "image_url": item.get("image_url"),
        "created_at": item.get("created_at")
    }

def upload_image_to_cloudinary(file: UploadFile) -> str:
    """Upload image to Cloudinary"""
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



#  ===================== ADMIN AUTHENTICATION ENDPOINTS =================

@app.post("/api/admins/register")
async def register_admin(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    image: UploadFile = File(None)
):
    """Register a new admin with hashed password."""
    try:
        existing = await admins_collection.find_one({"email": email})
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        if len(password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
        image_url = None
        if image:
            result = cloudinary.uploader.upload(image.file)
            image_url = result.get("secure_url")
        
        hashed_password = hash_password(password)
        
        admin_data = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "image_url": image_url,
            "role": "admin",
            "created_at": datetime.utcnow()
        }
        
        await admins_collection.insert_one(admin_data)
        logger.info(f"✅ Admin registered: {email}")
        
        return {
            "success": True,
            "message": f"Admin '{name}' registered successfully!"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Admin registration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@app.post("/api/admins/login")
async def admin_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login admin and return JWT token."""
    try:
        admin = await admins_collection.find_one({"email": form_data.username})
        
        if not admin:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if not verify_password(form_data.password, admin["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": admin["email"], "name": admin["name"]},
            expires_delta=access_token_expires
        )
        
        logger.info(f"✅ Admin logged in: {admin['email']}")
        
        return {
            "success": True,
            "message": f"Welcome {admin['name']}!",
            "access_token": access_token,
            "token_type": "bearer",
            "admin_info": {
                "name": admin["name"],
                "email": admin["email"],
                "image_url": admin.get("image_url"),
                "role": admin.get("role")
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login failed: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@app.get("/api/admins/me")
async def get_current_admin_info(current_admin: dict = Depends(get_current_admin)):
    """Get current logged-in admin info (protected route)."""
    return {
        "success": True,
        "data": {
            "_id": str(current_admin["_id"]),
            "name": current_admin["name"],
            "email": current_admin["email"],
            "image_url": current_admin.get("image_url"),
            "role": current_admin["role"]
        }
    }


@app.get("/api/admins")
async def get_all_admins(current_admin: dict = Depends(get_current_admin)):
    """Get all admins (protected route)."""
    admins = []
    async for item in admins_collection.find():
        admins.append({
            "_id": str(item.get("_id")),
            "name": item.get("name"),
            "email": item.get("email"),
            "image_url": item.get("image_url"),
            "role": item.get("role"),
            "created_at": item.get("created_at")
        })
    return {"success": True, "data": admins}

# ==================== CREATE PRODUCT ==================

@app.post("/products")
async def add_product(
    name: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    category: str = Form(...),
    stitching_type: str = Form(...),
    color: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(...)
):
    try:
        image_url = upload_image_to_cloudinary(image)
        product_data = {
            "name": name,
            "price": price,
            "stock": stock,
            "category": category,
            "stitching_type": stitching_type,
            "color": color,
            "description": description,
            "image_url": image_url,
            "created_at": datetime.utcnow()
        }
        await collection.insert_one(product_data)
        logger.info(f"✅ Product added: {name}")
        return {"success": True, "message": f"✅ Product '{name}' added successfully!"}
    except Exception as e:
        logger.error(f"Failed to add product: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")

# ================ READ ALL PRODUCTS =============
@app.get("/products")
async def get_all_products():
    try:
        products = []
        async for item in collection.find():
            products.append(serialize_item(item))
        return {"success": True, "data": products}
    except Exception as e:
        logger.error(f"Failed to fetch products: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")

# ============= READ SINGLE PRODUCT ==============

@app.get("/api/products/{name}")
async def get_product(name: str):
    try:
        product = await collection.find_one({"name": name})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"success": True, "data": serialize_item(product)}
    except Exception as e:
        logger.error(f"Failed to retrieve product {name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")

# ===================== UPDATE MULTIPLE STOCKS ====================

class StockUpdateItem(BaseModel):
    name: str
    quantity: int

@app.put("/api/update_multiple_stocks")
async def update_multiple_stocks(items: List[StockUpdateItem]):
    try:
        updated_products = []
        for item in items:
            product = await collection.find_one({"name": item.name})
            if not product:
                logger.warning(f"⚠ Product not found: {item.name}")
                continue

            current_stock = product.get("stock", 0)
            if current_stock <= 0:
                logger.warning(f"⚠ Stock already zero for {item.name}")
                continue

            new_stock = max(current_stock - item.quantity, 0)
            await collection.update_one({"name": item.name}, {"$set": {"stock": new_stock}})

            logger.info(f"📦 Stock updated for {item.name}: {current_stock} → {new_stock}")
            updated_products.append({
                "product": item.name,
                "old_stock": current_stock,
                "new_stock": new_stock
            })

        if not updated_products:
            raise HTTPException(status_code=404, detail="No valid products updated.")

        return {
            "success": True,
            "message": "✅ Stocks updated successfully!",
            "updated_products": updated_products
        }

    except Exception as e:
        logger.error(f"❌ Failed to update multiple stocks: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")

# =================== DELETE PRODUCT ==================

@app.delete("/api/products/{name}")
async def delete_product(name: str):
    try:
        result = await collection.delete_one({"name": name})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"success": True, "message": "🗑 Product deleted successfully!"}
    except Exception as e:
        logger.error(f"Failed to delete product {name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")

# ======================= SALES ENDPOINTS =====================

# Create Sale
@app.post("/api/sales")
async def create_sale(sale: SalesRecord):
    try:
        sale_data = sale.dict()
        sale_data["created_at"] = datetime.utcnow()

        result = await sales_collection.insert_one(sale_data)
        logger.info(f"✅ Sale saved: {sale.order_id}")

        for item in sale_data.get("products_sold", []):
            product_name = item.get("name")
            quantity_sold = item.get("quantity", 0)

            product = await collection.find_one({"name": product_name})
            if not product:
                logger.warning(f"⚠ Product not found: {product_name}")
                continue

            current_stock = product.get("stock", 0)
            new_stock = max(current_stock - quantity_sold, 0)

            await collection.update_one(
                {"_id": product["_id"]},
                {"$set": {"stock": new_stock}}
            )
            logger.info(f"📦 Stock updated for {product_name}: {current_stock} → {new_stock}")

        return {
            "success": True,
            "message": "✅ Sale recorded and stock updated!",
            "sale_id": str(result.inserted_id)
        }

    except Exception as e:
        logger.error(f"❌ Failed to save sale: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")

#  Fetch All Sales
@app.get("/api/sales")
async def get_all_sales():
    try:
        sales = []
        async for item in sales_collection.find().sort("created_at", -1):
            sales.append({
                "_id": str(item.get("_id")),
                "order_id": item.get("order_id"),
                "total_sales_amount": item.get("total_sales_amount"),
                "products_sold": item.get("products_sold"),
                "paid_at": item.get("paid_at"),
                "payment_method": item.get("payment_method"),
                "customer_phone": item.get("customer_phone"),
                "created_at": item.get("created_at")
            })

        total_revenue = sum(s["total_sales_amount"] for s in sales)
        total_orders = len(sales)

        product_summary = {}
        for sale in sales:
            for product in sale.get("products_sold", []):
                name = product.get("name", "Unknown")
                qty = product.get("quantity", 0)
                total = product.get("total", 0)

                if name not in product_summary:
                    product_summary[name] = {"quantity": 0, "revenue": 0.0}

                product_summary[name]["quantity"] += qty
                product_summary[name]["revenue"] += total

        return {
            "success": True,
            "data": {
                "total_orders": total_orders,
                "total_revenue": total_revenue,
                "transactions": sales,
                "product_summary": product_summary
            }
        }

    except Exception as e:
        logger.error(f"❌ Failed to fetch sales: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@app.get("/api/sales/product-analysis")
async def get_product_sales_analysis():
    """
    Returns detailed product-wise sales analysis including:
    - Total quantity sold per product
    - Total revenue per product
    - Sales velocity (useful for identifying slow movers)
    """
    try:
        sales = await sales_collection.find({}).to_list(length=None)
        
        product_summary = {}
        for sale in sales:
            for product in sale.get("products_sold", []):
                name = product.get("name", "Unknown")
                qty = product.get("quantity", 0)
                total = product.get("total", 0)
                
                if name not in product_summary:
                    product_summary[name] = {
                        "quantity": 0,
                        "revenue": 0.0,
                        "order_count": 0
                    }
                
                product_summary[name]["quantity"] += qty
                product_summary[name]["revenue"] += total
                product_summary[name]["order_count"] += 1
        
        logger.info(f"✅ Product analysis generated for {len(product_summary)} products")
        
        return {
            "success": True,
            "data": {
                "product_summary": product_summary,
                "total_products_sold": len(product_summary)
            }
        }
    
    except Exception as e:
        logger.error(f"❌ Product analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")


# ============================= PURCHASE ENDPOINTS =================

# Fetch All Purchases
@app.get("/api/purchases")
async def get_all_purchases():
    try:
        purchases = []
        async for item in purchases_collection.find().sort("purchased_at", -1):
            purchases.append({
                "_id": str(item.get("_id")),
                "product_name": item.get("product_name"),
                "quantity_purchased": item.get("quantity_purchased"),
                "amount_paid": item.get("amount_paid"),
                "supplier_name": item.get("supplier_name"),
                "purchased_at": item.get("purchased_at")
            })

        total_spent = sum(p.get("amount_paid", 0) for p in purchases)
        
        return {
            "success": True,
            "data": {
                "total_records": len(purchases),
                "total_spent": total_spent,
                "transactions": purchases
            }
        }
    except Exception as e:
        logger.error(f"❌ Failed to fetch purchases: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")

# Complete Purchase and Update Stock
@app.post("/api/purchases/complete") 
async def complete_purchase_and_update_stock_direct(purchase: SupplierPurchaseRecord):
    try:
        purchase_data = purchase.dict()
        purchase_data["purchased_at"] = datetime.utcnow()
        purchase_data["payment_status"] = "completed"
        
        product_name = purchase.product_name
        quantity_to_add = purchase.quantity_purchased
        
        await collection.update_one(
            {"name": product_name}, 
            {"$inc": {"stock": quantity_to_add}}
        )

        result = await purchases_collection.insert_one(purchase_data)
        logger.info(f"✅ Purchase completed: {product_name}")
        
        updated_product = await collection.find_one({"name": product_name})
        new_stock_level = updated_product.get("stock", "Unknown") if updated_product else "Unknown"
        
        return {
            "success": True,
            "message": f"✅ Payment confirmed! New stock: {new_stock_level}",
            "purchase_id": str(result.inserted_id),
            "new_stock": new_stock_level
        }
    
    except Exception as e:
        logger.error(f"❌ Failed to complete purchase: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")


# ================================ SUPPLIER ENDPOINTS ==========================


@app.get("/api/suppliers/random")
async def get_random_supplier_info():
    try:
        count = await suppliers_collection.count_documents({})
        if count == 0:
            raise HTTPException(status_code=404, detail="No suppliers found")
        
        random_skip = random.randint(0, count - 1)
        supplier = await suppliers_collection.find().limit(1).skip(random_skip).next()
        
        supplier["_id"] = str(supplier["_id"])
        
        logger.info(f"✅ Random supplier selected: {supplier['name']}")
        return {
            "success": True,
            "data": {
                "name": supplier.get("name"),
                "phone": supplier.get("phone"),
                "account_details": supplier.get("account_details"),
                "contact_person": supplier.get("contact_person")
            }
        }
    except Exception as e:
        logger.error(f"❌ Failed to fetch supplier: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")

# ================= MARKETING CAMPAIGN ENDPOINTS ==============

@app.post("/api/marketing/campaigns")
async def create_marketing_campaign(campaign: MarketingCampaign):
    """
    Creates a new marketing campaign record.
    Called by Marketing Agent after generating posters.
    """
    try:
        campaign_data = campaign.dict()
        campaign_data["created_at"] = datetime.utcnow()
        campaign_data["updated_at"] = datetime.utcnow()
        
        result = await campaigns_collection.insert_one(campaign_data)
        logger.info(f"✅ Marketing campaign created: {campaign.product_name}")
        
        return {
            "success": True,
            "message": f"✅ Campaign created for {campaign.product_name}",
            "campaign_id": str(result.inserted_id)
        }
    
    except Exception as e:
        logger.error(f"❌ Failed to create campaign: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@app.get("/api/marketing/campaigns")
async def get_all_campaigns(limit: int = 50, status: Optional[str] = None):
    """
    Fetches all marketing campaigns.
    Optional filter by status (active, paused, completed).
    """
    try:
        query = {}
        if status:
            query["status"] = status
        
        campaigns = []
        async for item in campaigns_collection.find(query).sort("created_at", -1).limit(limit):
            campaigns.append({
                "_id": str(item.get("_id")),
                "product_name": item.get("product_name"),
                "campaign_type": item.get("campaign_type"),
                "price": item.get("price"),
                "discount": item.get("discount"),
                "poster_url": item.get("poster_url"),
                "status": item.get("status"),
                "created_at": item.get("created_at")
            })
        
        return {
            "success": True,
            "data": campaigns,
            "total": len(campaigns)
        }
    
    except Exception as e:
        logger.error(f"❌ Failed to fetch campaigns: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@app.put("/api/marketing/campaigns/{campaign_id}/status")
async def update_campaign_status(campaign_id: str, status: str):
    """
    Updates campaign status (active → paused → completed).
    Admin can control campaign lifecycle.
    """
    try:
        if status not in ["active", "paused", "completed"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        result = await campaigns_collection.update_one(
            {"_id": safe_object_id(campaign_id)},
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        logger.info(f"✅ Campaign {campaign_id} status updated to {status}")
        
        return {
            "success": True,
            "message": f"Campaign status updated to {status}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update campaign: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")


# ===================== BUSINESS INSIGHTS ENDPOINTS ===================


@app.post("/api/insights")
async def save_business_insight(insight: BusinessInsight):
    """
    Saves business insights generated by Insight Agent.
    These are strategic recommendations for admin review.
    """
    try:
        insight_data = insight.dict()
        insight_data["created_at"] = datetime.utcnow()
        insight_data["reviewed_at"] = None
        
        result = await insights_collection.insert_one(insight_data)
        logger.info(f"✅ Business insight saved: {insight.insight_type}")
        
        return {
            "success": True,
            "message": "✅ Business insight recorded",
            "insight_id": str(result.inserted_id)
        }
    
    except Exception as e:
        logger.error(f"❌ Failed to save insight: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@app.get("/api/insights")
async def get_all_insights(status: Optional[str] = None, priority: Optional[str] = None):
    """
    Fetches business insights with optional filters.
    Admin dashboard uses this to view recommendations.
    """
    try:
        query = {}
        if status:
            query["status"] = status
        if priority:
            query["priority"] = priority
        
        insights = []
        async for item in insights_collection.find(query).sort("created_at", -1):
            insights.append({
                "_id": str(item.get("_id")),
                "insight_type": item.get("insight_type"),
                "products_affected": item.get("products_affected"),
                "recommendations": item.get("recommendations"),
                "priority": item.get("priority"),
                "status": item.get("status"),
                "created_at": item.get("created_at"),
                "reviewed_at": item.get("reviewed_at")
            })
        
        return {
            "success": True,
            "data": insights,
            "total": len(insights)
        }
    
    except Exception as e:
        logger.error(f"❌ Failed to fetch insights: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@app.put("/api/insights/{insight_id}/review")
async def mark_insight_reviewed(insight_id: str, status: str):
    """
    Marks an insight as reviewed/implemented by admin.
    Tracks which recommendations have been acted upon.
    """
    try:
        if status not in ["pending", "reviewed", "implemented"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        update_data = {
            "status": status,
            "reviewed_at": datetime.utcnow() if status != "pending" else None
        }
        
        result = await insights_collection.update_one(
            {"_id": safe_object_id(insight_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Insight not found")
        
        logger.info(f"✅ Insight {insight_id} marked as {status}")
        
        return {
            "success": True,
            "message": f"Insight marked as {status}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update insight: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")


# ========================== NEW: ANALYTICS DASHBOARD SUMMARY ===================

@app.get("/api/analytics/summary")
async def get_analytics_summary():
    """
    Provides a comprehensive business analytics summary.
    Used by admin dashboard for quick overview.
    """
    try:
        # Sales metrics
        sales = await sales_collection.find({}).to_list(length=None)
        total_revenue = sum(s.get("total_sales_amount", 0) for s in sales)
        total_orders = len(sales)
        
        # Purchase metrics
        purchases = await purchases_collection.find({}).to_list(length=None)
        total_spent = sum(p.get("amount_paid", 0) for p in purchases)
        
        # Profit/Loss
        profit_loss = total_revenue - total_spent
        
        # Product metrics
        total_products = await collection.count_documents({})
        low_stock_products = await collection.count_documents({"stock": {"$lte": 3}})
        
        # Campaign metrics
        active_campaigns = await campaigns_collection.count_documents({"status": "active"})
        
        # Pending insights
        pending_insights = await insights_collection.count_documents({"status": "pending"})
        
        return {
            "success": True,
            "data": {
                "sales": {
                    "total_revenue": round(total_revenue, 2),
                    "total_orders": total_orders,
                    "average_order_value": round(total_revenue / total_orders, 2) if total_orders > 0 else 0
                },
                "purchases": {
                    "total_spent": round(total_spent, 2),
                    "total_transactions": len(purchases)
                },
                "profit_loss": {
                    "amount": round(profit_loss, 2),
                    "status": "profit" if profit_loss >= 0 else "loss",
                    "margin_percentage": round((profit_loss / total_revenue * 100), 2) if total_revenue > 0 else 0
                },
                "inventory": {
                    "total_products": total_products,
                    "low_stock_alerts": low_stock_products
                },
                "marketing": {
                    "active_campaigns": active_campaigns
                },
                "insights": {
                    "pending_recommendations": pending_insights
                }
            }
        }
    
    except Exception as e:
        logger.error(f"❌ Analytics summary failed: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")


# ========================= RUN SERVER ========================

if __name__ == "__main__":
    logger.info("🚀 Starting Extended CRUD Server on port 8002...")
    logger.info("📊 New Features: Marketing Campaigns, Business Insights, Analytics")
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)