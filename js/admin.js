// Admin panel functionality
document.addEventListener('DOMContentLoaded', () => {
    displayAdminProducts();
    updateStats();
    setupAddProductForm();
});

function setupAddProductForm() {
    const form = document.getElementById('add-product-form');
    if (!form) return;
    
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const newProduct = {
            name: document.getElementById('product-name').value,
            category: document.getElementById('product-category').value,
            price: parseFloat(document.getElementById('product-price').value),
            description: document.getElementById('product-description').value,
            image: document.getElementById('product-image').value || '🌱',
            stock: parseInt(document.getElementById('product-stock').value)
        };
        
        addProduct(newProduct);
        showAdminMessage('Product added successfully!', 'success');
        form.reset();
        displayAdminProducts();
        updateStats();
    });
}

function displayAdminProducts() {
    const productsList = document.getElementById('admin-products-list');
    if (!productsList) return;
    
    const products = getAllProducts();
    
    if (products.length === 0) {
        productsList.innerHTML = '<p style="text-align: center; color: #666;">No products yet. Add your first product!</p>';
        return;
    }
    
    productsList.innerHTML = products.map(product => `
        <div class="admin-product-item">
            <div class="admin-product-info">
                <h4>${product.image} ${product.name}</h4>
                <p>Category: ${product.category}</p>
                <p>${product.description}</p>
                <p>Stock: ${product.stock} units</p>
            </div>
            <div class="admin-product-price">$${product.price.toFixed(2)}</div>
            <div class="admin-product-actions">
                <button class="btn-edit" onclick="editProduct(${product.id})">Edit</button>
                <button class="btn-delete" onclick="deleteProductHandler(${product.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

function editProduct(id) {
    const product = getProductById(id);
    if (!product) return;
    
    const newName = prompt('Product Name:', product.name);
    if (newName === null) return;
    
    const newPrice = prompt('Price:', product.price);
    if (newPrice === null) return;
    
    const newDescription = prompt('Description:', product.description);
    if (newDescription === null) return;
    
    const newStock = prompt('Stock:', product.stock);
    if (newStock === null) return;
    
    updateProduct(id, {
        name: newName || product.name,
        price: parseFloat(newPrice) || product.price,
        description: newDescription || product.description,
        stock: parseInt(newStock) || product.stock
    });
    
    showAdminMessage('Product updated successfully!', 'success');
    displayAdminProducts();
}

function deleteProductHandler(id) {
    if (confirm('Are you sure you want to delete this product?')) {
        deleteProduct(id);
        showAdminMessage('Product deleted successfully!', 'success');
        displayAdminProducts();
        updateStats();
    }
}

function updateStats() {
    const totalProducts = document.getElementById('total-products');
    const totalCategories = document.getElementById('total-categories');
    
    if (totalProducts) {
        const products = getAllProducts();
        totalProducts.textContent = products.length;
        
        const categories = new Set(products.map(p => p.category));
        totalCategories.textContent = categories.size;
    }
}

function showAdminMessage(text, type) {
    const existingMessage = document.querySelector('.message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    const message = document.createElement('div');
    message.className = `message ${type}`;
    message.textContent = text;
    
    const adminPanel = document.querySelector('.admin-panel .container');
    if (adminPanel) {
        adminPanel.insertBefore(message, adminPanel.firstChild);
        
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 3000);
    }
}
