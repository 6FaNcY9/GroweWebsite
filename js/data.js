// Product Data - This serves as our database
let products = [
    {
        id: 1,
        name: "Tomato Seeds",
        category: "vegetables",
        price: 3.99,
        description: "Delicious heirloom tomatoes perfect for salads and cooking",
        image: "🍅",
        stock: 150
    },
    {
        id: 2,
        name: "Basil Seeds",
        category: "herbs",
        price: 2.99,
        description: "Fresh basil for all your culinary needs",
        image: "🌿",
        stock: 200
    },
    {
        id: 3,
        name: "Sunflower Seeds",
        category: "flowers",
        price: 4.49,
        description: "Beautiful sunflowers that brighten any garden",
        image: "🌻",
        stock: 100
    },
    {
        id: 4,
        name: "Carrot Seeds",
        category: "vegetables",
        price: 3.49,
        description: "Sweet and crunchy carrots for your garden",
        image: "🥕",
        stock: 180
    },
    {
        id: 5,
        name: "Strawberry Seeds",
        category: "fruits",
        price: 5.99,
        description: "Grow your own delicious strawberries at home",
        image: "🍓",
        stock: 120
    },
    {
        id: 6,
        name: "Lavender Seeds",
        category: "flowers",
        price: 4.99,
        description: "Aromatic lavender for a relaxing garden",
        image: "💜",
        stock: 90
    },
    {
        id: 7,
        name: "Mint Seeds",
        category: "herbs",
        price: 2.49,
        description: "Refreshing mint for teas and cooking",
        image: "🌱",
        stock: 220
    },
    {
        id: 8,
        name: "Bell Pepper Seeds",
        category: "vegetables",
        price: 4.29,
        description: "Colorful bell peppers for your vegetable garden",
        image: "🫑",
        stock: 130
    },
    {
        id: 9,
        name: "Rose Seeds",
        category: "flowers",
        price: 6.99,
        description: "Beautiful roses in various colors",
        image: "🌹",
        stock: 75
    },
    {
        id: 10,
        name: "Cilantro Seeds",
        category: "herbs",
        price: 2.79,
        description: "Fresh cilantro for Mexican and Asian cuisine",
        image: "🌿",
        stock: 160
    },
    {
        id: 11,
        name: "Lettuce Seeds",
        category: "vegetables",
        price: 2.99,
        description: "Crispy lettuce for fresh salads",
        image: "🥬",
        stock: 200
    },
    {
        id: 12,
        name: "Watermelon Seeds",
        category: "fruits",
        price: 5.49,
        description: "Juicy watermelons for summer enjoyment",
        image: "🍉",
        stock: 80
    }
];

// Load products from localStorage if available
function loadProducts() {
    const savedProducts = localStorage.getItem('groweProducts');
    if (savedProducts) {
        products = JSON.parse(savedProducts);
    }
}

// Save products to localStorage
function saveProducts() {
    localStorage.setItem('groweProducts', JSON.stringify(products));
}

// Initialize products on page load
loadProducts();

// Get product by ID
function getProductById(id) {
    return products.find(product => product.id === id);
}

// Get all products
function getAllProducts() {
    return products;
}

// Add new product
function addProduct(product) {
    const newId = Math.max(...products.map(p => p.id), 0) + 1;
    const newProduct = {
        id: newId,
        ...product
    };
    products.push(newProduct);
    saveProducts();
    return newProduct;
}

// Update product
function updateProduct(id, updates) {
    const index = products.findIndex(p => p.id === id);
    if (index !== -1) {
        products[index] = { ...products[index], ...updates };
        saveProducts();
        return products[index];
    }
    return null;
}

// Delete product
function deleteProduct(id) {
    const index = products.findIndex(p => p.id === id);
    if (index !== -1) {
        products.splice(index, 1);
        saveProducts();
        return true;
    }
    return false;
}

// Filter products by category
function filterByCategory(category) {
    if (category === 'all') {
        return products;
    }
    return products.filter(product => product.category === category);
}

// Sort products
function sortProducts(productsArray, sortType) {
    const sorted = [...productsArray];
    switch(sortType) {
        case 'name':
            return sorted.sort((a, b) => a.name.localeCompare(b.name));
        case 'price-low':
            return sorted.sort((a, b) => a.price - b.price);
        case 'price-high':
            return sorted.sort((a, b) => b.price - a.price);
        default:
            return sorted;
    }
}
