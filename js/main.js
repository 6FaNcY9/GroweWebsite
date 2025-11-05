// Main page functionality
document.addEventListener('DOMContentLoaded', () => {
    displayFeaturedProducts();
});

function displayFeaturedProducts() {
    const featuredGrid = document.getElementById('featured-grid');
    if (!featuredGrid) return;
    
    // Get first 6 products as featured
    const featuredProducts = getAllProducts().slice(0, 6);
    
    featuredGrid.innerHTML = featuredProducts.map(product => createProductCard(product)).join('');
}

function createProductCard(product) {
    const inStock = product.stock > 0;
    return `
        <div class="product-card">
            <div class="product-image">${product.image}</div>
            <h3>${product.name}</h3>
            <span class="product-category">${product.category}</span>
            <p class="product-description">${product.description}</p>
            <p class="product-price">$${product.price.toFixed(2)}</p>
            <p style="color: ${inStock ? '#4caf50' : '#f44336'}; font-size: 0.9rem;">
                ${inStock ? `In Stock (${product.stock})` : 'Out of Stock'}
            </p>
            <button class="add-to-cart" onclick="addToCart(${product.id})" ${!inStock ? 'disabled' : ''}>
                ${inStock ? 'Add to Cart' : 'Out of Stock'}
            </button>
        </div>
    `;
}
