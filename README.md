# 🌱 Growe - Plant Seeds E-Commerce Website

A complete, responsive website for selling plant seeds with an easy-to-use admin panel for product management.

## Features

### Customer Features
- **Homepage** - Beautiful hero section with featured seed products
- **Product Catalog** - Browse all available plant seeds with filtering and sorting
- **Category Filtering** - Filter products by category (Vegetables, Herbs, Flowers, Fruits)
- **Product Sorting** - Sort by name, price (low to high), or price (high to low)
- **Shopping Cart** - Add products to cart, adjust quantities, and view cart total
- **Responsive Design** - Works seamlessly on desktop, tablet, and mobile devices
- **Stock Tracking** - Real-time stock availability display

### Admin Features
- **Product Management Dashboard** - View all products at a glance
- **Add New Products** - Easy form to add new seed products
- **Edit Products** - Update product details (name, price, description, stock)
- **Delete Products** - Remove products from the catalog
- **Statistics** - View total products and categories count
- **Persistent Storage** - Products saved to browser's localStorage

## Technologies Used

- **HTML5** - Semantic markup
- **CSS3** - Modern styling with flexbox and grid
- **JavaScript (ES6+)** - Dynamic functionality
- **LocalStorage API** - Client-side data persistence

## File Structure

```
GroweWebsite/
├── index.html          # Homepage
├── products.html       # Product listing page
├── admin.html          # Admin panel
├── css/
│   ├── style.css       # Main stylesheet
│   └── admin.css       # Admin panel styles
└── js/
    ├── data.js         # Product data management
    ├── cart.js         # Shopping cart functionality
    ├── main.js         # Homepage scripts
    ├── products.js     # Products page scripts
    └── admin.js        # Admin panel scripts
```

## Getting Started

### Running Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/6FaNcY9/GroweWebsite.git
   cd GroweWebsite
   ```

2. Start a local web server (choose one):
   
   **Using Python 3:**
   ```bash
   python3 -m http.server 8000
   ```
   
   **Using Node.js (with npx):**
   ```bash
   npx http-server -p 8000
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

### Using the Website

**As a Customer:**
1. Browse products on the homepage or products page
2. Filter by category or sort by name/price
3. Click "Add to Cart" to add items
4. View cart by clicking the cart icon in the navigation
5. Adjust quantities or remove items in the cart
6. Click "Checkout" to complete your order

**As an Admin:**
1. Navigate to the Admin page from the navigation menu
2. Fill out the form to add new products
3. View all products in the "Current Products" section
4. Click "Edit" to update product details
5. Click "Delete" to remove products

## Product Categories

- 🥬 **Vegetables** - Tomatoes, Carrots, Lettuce, Bell Peppers, etc.
- 🌿 **Herbs** - Basil, Mint, Cilantro, etc.
- 🌻 **Flowers** - Sunflowers, Roses, Lavender, etc.
- 🍓 **Fruits** - Strawberries, Watermelon, etc.

## Data Persistence

The website uses browser localStorage to persist:
- Product catalog (can be updated via admin panel)
- Shopping cart items
- Product quantities and details

**Note:** Data is stored locally in your browser. Clearing browser data will reset products to defaults.

## Browser Compatibility

- Chrome (recommended)
- Firefox
- Safari
- Edge
- Opera

## Future Enhancements

Potential features for future development:
- User authentication system
- Payment gateway integration
- Order history tracking
- Product reviews and ratings
- Image upload for products
- Backend database integration
- Email notifications
- Advanced search functionality
- Wishlist feature

## License

© 2024 Growe. All rights reserved.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

For questions or support:
- Email: info@growe.com
- Phone: (555) 123-4567
