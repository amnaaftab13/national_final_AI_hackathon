# CRUD Server - AI Fashion Bazar

**Agentic AI Platform for Pakistan’s Informal Digital Economy**


## 🎯 Overview

FastAPI-based backend server managing products, sales, purchases, suppliers, marketing campaigns, and business insights with JWT authentication.

**Tech Stack:** FastAPI, Motor (MongoDB), Cloudinary, JWT, bcrypt

---

## ✨ Features

- 🔐 **Admin Authentication** - JWT-based login/register with password hashing
- 📦 **Product Management** - CRUD operations with image upload
- 💰 **Sales Tracking** - Order recording with auto stock updates
- 🏭 **Supplier Management** - Purchase records and random supplier selection
- 📱 **Marketing Campaigns** - Campaign creation and status tracking
- 📊 **Business Insights** - AI-generated recommendations storage
- 📈 **Analytics Dashboard** - Comprehensive business metrics

---

## 🚀 Installation

### Install dependencies
uv add fastapi uvicorn motor cloudinary python-dotenv passlib[bcrypt] python-jose python-multipart

---

## ⚙️ Configuration

Create `.env` file:
```env
# MongoDB
MONGO_URI=mongodb://localhost:27017/
# or Atlas: mongodb+srv://user:pass@cluster.mongodb.net/

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# JWT Secret (32+ characters)
JWT_SECRET_KEY=your-secret-key-change-this-in-production-minimum-32-chars
```

**Database:** `menudb`

**Collections:** `products`, `sales`, `supplier_purchases`, `suppliers`, `marketing_campaigns`, `business_insights`, `admins`

---

## 🛠 API Endpoints

### Authentication (3 endpoints)

1. **`POST /api/admins/register`** - Register admin (name, email, password, image)
2. **`POST /api/admins/login`** - Login and get JWT token
3. **`GET /api/admins/me`** - Get current admin info (protected)

**Token expiry:** 24 hours

---

### Products (5 endpoints)

4. **`POST /products`** - Create product with image
5. **`GET /products`** - Get all products
6. **`GET /api/products/{name}`** - Get single product
7. **`PUT /api/update_multiple_stocks`** - Batch stock update
8. **`DELETE /api/products/{name}`** - Delete product

---

### Sales (3 endpoints)

9. **`POST /api/sales`** - Record sale (auto-updates stock)
10. **`GET /api/sales`** - Get all sales + revenue summary
11. **`GET /api/sales/product-analysis`** - Product-wise sales metrics

---

### Purchases (2 endpoints)

12. **`GET /api/purchases`** - Get purchase history
13. **`POST /api/purchases/complete`** - Complete purchase (auto-increments stock)

---

### Suppliers (1 endpoint)

14. **`GET /api/suppliers/random`** - Get random supplier details

---

### Marketing (3 endpoints)

15. **`POST /api/marketing/campaigns`** - Create campaign
16. **`GET /api/marketing/campaigns`** - Get campaigns (filter by status)
17. **`PUT /api/marketing/campaigns/{id}/status`** - Update status

---

### Insights (3 endpoints)

18. **`POST /api/insights`** - Save business insight
19. **`GET /api/insights`** - Get insights (filter by status/priority)
20. **`PUT /api/insights/{id}/review`** - Mark as reviewed/implemented

---

### Analytics (1 endpoint)

21. **`GET /api/analytics/summary`** - Dashboard metrics (sales, purchases, P/L, inventory, campaigns)

---

## 🐛 Troubleshooting

**MongoDB Connection Failed**
- Verify `MONGO_URI` in `.env`
- Check MongoDB service running
- For Atlas: Check network access

**JWT Authentication Error**
- Verify `JWT_SECRET_KEY` is 32+ characters
- Check Authorization header: `Bearer <token>`
- Token expires after 24 hours

**Cloudinary Upload Error**
- Verify all credentials in `.env`
- Check internet connectivity


---

## 🔒 Security

- ✅ Bcrypt password hashing
- ✅ JWT authentication (24h expiry)
- ✅ Protected routes
- ✅ CORS configuration
- ✅ Input validation via Pydantic

---

## 📈 Key Features

**Auto Stock Management:**
- Sales reduce stock automatically
- Purchases increase stock automatically

**Analytics:**
- Real-time P/L calculation
- Product-wise sales analysis
- Low stock alerts

---

**Team:** Amna Aftab, Arishah Khan  
**Built with:** FastAPI + MongoDB + JWT + Cloudinary