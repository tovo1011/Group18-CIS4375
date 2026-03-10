# Perfume Store Dashboard - Frontend

A modern Vue.js 3 dashboard for managing a perfume store with a professional login page.

## Features

- 🔐 **Login Page** - Secure authentication with validation
- 📊 **Dashboard** - Overview of store metrics and statistics
- 🎨 **Modern UI** - Beautiful gradient design with responsive layout
- 🔌 **Pinia Store** - State management for authentication
- 🛣️ **Vue Router** - Client-side routing with protected routes
- ⚡ **Vite** - Fast build tool and development server

## Project Structure

```
frontend/
├── src/
│   ├── components/        # Reusable Vue components
│   ├── views/            # Page components (LoginPage, Dashboard)
│   ├── router/           # Vue Router configuration
│   ├── stores/           # Pinia stores (auth store)
│   ├── App.vue           # Root component
│   └── main.js           # Application entry point
├── public/
│   └── style.css         # Global styles
├── index.html            # HTML entry point
├── vite.config.js        # Vite configuration
└── package.json          # Project dependencies
```

## Installation

1. **Install dependencies:**
```bash
npm install
```

## Development

2. **Start the development server:**
```bash
npm run dev
```

The application will open at `http://localhost:5173`

## Demo Credentials

Use any email and password to log in:
- **Email:** manager@perfume.com
- **Password:** any password

## Build

3. **Build for production:**
```bash
npm run build
```

4. **Preview production build:**
```bash
npm run preview
```

## Features

### Login Page
- Email and password validation
- Error handling
- Loading state during authentication
- Responsive design

### Dashboard
- Welcome message with user's name
- 4 statistics cards (Products, Revenue, Customers, Orders)
- Popular products list
- Recent orders list
- Sidebar navigation menu
- Navigation bar with logout functionality

## Technologies Used

- **Vue.js 3** - Progressive JavaScript framework
- **Vue Router 4** - Routing library
- **Pinia** - State management
- **Vite** - Frontend build tool
- **Axios** - HTTP client (ready to use for API calls)

## Next Steps

To enhance the dashboard, consider:

1. **Connect to Backend API**
   - Replace mock data with real API calls using Axios
   - Update the auth store to call your backend login endpoint

2. **Add More Pages**
   - Products management page
   - Customers page
   - Analytics page
   - Settings page

3. **Improve Authentication**
   - JWT token management
   - Token refresh mechanism
   - Role-based access control (RBAC)

4. **Database Integration**
   - Store user data in backend
   - Implement proper session management
   - Add database schemas for products, customers, orders

## License

MIT
