# Frontend - AI Fashion Bazar

**Admin Dashboard & Multi-Language Interface for Agentic AI Platform for Pakistan’s Informal Digital Economy**


## 🎯 Overview

Next.js 15-based admin dashboard with multi-language support (English/Urdu), real-time analytics, and futuristic UI design.

**Tech Stack:** Next.js 15, TypeScript, Tailwind CSS, Framer Motion, Recharts, next-intl

---

## ✨ Features

- 🌍 **Multi-Language Support** - English & Urdu (RTL support)
- 🎨 **Futuristic UI** - Neon effects, animated backgrounds, glassmorphism
- 📊 **Analytics Dashboard** - Real-time charts with Recharts
- 🔐 **JWT Authentication** - Secure admin login with token management
- 📱 **Fully Responsive** - Mobile-first design (xs to 4K)
- 🎬 **Video Backgrounds** - Dynamic loading states
- 💫 **Framer Motion** - Smooth animations and transitions
- 🛍️ **Product Management** - Add/view products with image upload

---


## ⚙️ Configuration

### Environment Variables

Create `.env` file:
```env
# API Endpoints
NEXT_PUBLIC_API_URL=https://your-backend-url.com
NEXT_PUBLIC_CRUD_URL=https://your-crud-url.com
```

### Internationalization Setup

Supported locales: `en` (English), `ur` (Urdu)

**Language files location:** `/messages/`
- `en.json` - English translations
- `ur.json` - Urdu translations

---

## 📄 Pages Overview

### Public Pages

#### 1. **Landing Page** (`/page.tsx`)
- Animated fashion carousel
- Video background
- Mouse-tracking parallax effects
- Multi-language support

#### 2. **Login Page** (`/[locale]/login/page.tsx`)
- JWT authentication
- Password visibility toggle
- Form validation with toast notifications
- Language switcher

---

### Protected Dashboard Pages

#### 3. **Dashboard Center** (`/[locale]/dashboard/page.tsx`)
- **Real-time Analytics:**
  - Total revenue, low-selling products
  - Inventory boost %, revenue increase %
- **Interactive Charts:**
  - Pie chart (product performance)
  - Bar chart (pricing suggestions)
  - Line chart (price comparison)
- **Business Insights:**
  - Top recommendations with priority ranking
  - Inventory actions
  - Marketing suggestions
- **Responsive Design:** Stacks on mobile, grid on desktop

#### 4. **View Products** (`/[locale]/dashboard/view-products/page.tsx`)
- Product grid with full images
- Category, stitching type, color filters
- Stock availability display
- Responsive card layout

#### 5. **Add Product** (`/[locale]/dashboard/add-product/page.tsx`)
- Multi-field form (name, price, stock, category, etc.)
- Image upload with Cloudinary integration
- Real-time validation
- Neon-styled inputs

#### 6. **Sales Report** (`/[locale]/dashboard/sales-report/page.tsx`)
- Order-wise breakdown
- Product summary table
- Total revenue calculation
- Payment method tracking

#### 7. **Purchase Report** (`/[locale]/dashboard/purchase-report/page.tsx`)
- Supplier transaction history
- Total spent calculation
- Quantity purchased tracking

#### 8. **Profit/Loss Report** (`/[locale]/dashboard/profit-loss/page.tsx`)
- Net profit/loss calculation
- Sales vs purchases comparison
- Profit margin percentage
- Visual progress bars

#### 9. **Marketing Campaigns** (`/[locale]/dashboard/marketing-campaigns/page.tsx`)
- Starfield background animation
- Campaign cards with details
- Status tracking (active/paused/completed)
- Discount & pricing display

---

## 🧩 Components

### Core Components

#### **Sidebar** (`/Components/Sidebar.tsx`)
- Collapsible navigation
- Admin profile display
- Multi-language menu items
- Logout functionality

#### **LanguageSwitcher** (`/Components/LanguageSwitcher.tsx`)
- Toggle between English/Urdu
- Persists language preference
- Updates all page content dynamically

#### **UserProvider** (`/[locale]/dashboard/layout.tsx`)
- Context API for admin state
- LocalStorage integration
- JWT token management

---

## 🎨 Styling System

### Tailwind Custom Classes

**Responsive Breakpoints:**

sm: 640px   /* Mobile landscape */
md: 768px   /* Tablet */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
2xl: 1536px /* 4K */


**Custom Animations:**

.animate-scroll - Infinite horizontal scroll
.animate-slowPulse - Neon glow effect
.animate-gradient-x - Gradient movement
.neon-card - Glowing card with hover effect


---

## 🐛 Troubleshooting

**Login Issues**
- Verify API endpoint in `.env`
- Check JWT token expiry (24h)
- Clear localStorage: `localStorage.clear()`

**Language Not Switching**
- Check locale parameter in URL (`/en/...` or `/ur/...`)
- Verify translation files exist in `/messages/`
- Clear browser cache

---

## 🔒 Authentication Flow
```
1. User enters credentials → Login page
2. POST request to /api/admins/login
3. Store JWT token in localStorage
4. Redirect to /dashboard
5. Token sent in Authorization header for protected routes
6. Token expires after 24h → Auto logout
```

---

## 📱 Responsive Design Highlights

**Mobile (< 640px):**
- Single column layouts
- Collapsible sidebar
- Touch-optimized buttons
- Reduced chart sizes

**Tablet (640px - 1024px):**
- 2-column grids
- Visible sidebar
- Medium chart sizes

**Desktop (> 1024px):**
- Multi-column layouts
- Full-width charts
- Hover effects enabled

---

## 🎬 Video Assets

Required videos in `/public/`:
- `agentic_bg.mp4` - Landing page background
- `loader.mp4` - Loading states

**Specifications:**
- Format: MP4 (H.264)
- Max size: 5MB
- Resolution: 1920x1080

---


**Team:** Amna Aftab, Arishah Khan  
**Built with:** Next.js 15 + TypeScript + Tailwind CSS + Framer Motion