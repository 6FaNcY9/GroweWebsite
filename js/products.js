// Products page functionality
let currentCategory = 'all';
let currentSort = 'name';

document.addEventListener('DOMContentLoaded', () => {
    displayProducts();
    setupFilters();
});

function setupFilters() {
    const categoryFilter = document.getElementById('category-filter');
    const sortFilter = document.getElementById('sort-filter');
    
    if (categoryFilter) {
        categoryFilter.addEventListener('change', (e) => {
            currentCategory = e.target.value;
            displayProducts();
        });
    }
    
    if (sortFilter) {
        sortFilter.addEventListener('change', (e) => {
            currentSort = e.target.value;
            displayProducts();
        });
    }
}

function displayProducts() {
    const productsGrid = document.getElementById('products-grid');
    if (!productsGrid) return;
    
    let productsToDisplay = filterByCategory(currentCategory);
    productsToDisplay = sortProducts(productsToDisplay, currentSort);
    
    if (productsToDisplay.length === 0) {
        productsGrid.innerHTML = '<p style="text-align: center; grid-column: 1/-1; color: #666;">No products found in this category.</p>';
        return;
    }
    
    productsGrid.innerHTML = productsToDisplay.map(product => createProductCard(product)).join('');
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
