// AgriConnect MVP JavaScript

// Global variables
let cartCount = 0;

// Document ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize application
function initializeApp() {
    updateCartBadge();
    setupEventListeners();
    loadAnimations();
}

// Setup event listeners
function setupEventListeners() {
    // Cart functionality
    setupCartFunctionality();
    
    // Product selection (blue tick)
    setupProductSelection();
    
    // Forms
    setupForms();
    
    // Quantity controls
    setupQuantityControls();
    
    // Search functionality
    setupSearchFunctionality();
}

// Cart functionality
function setupCartFunctionality() {
    // Add to cart buttons
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', handleAddToCart);
    });

    // Update cart item buttons
    const updateCartButtons = document.querySelectorAll('.update-cart-btn');
    updateCartButtons.forEach(button => {
        button.addEventListener('click', handleUpdateCartItem);
    });

    // Remove cart item buttons
    const removeCartButtons = document.querySelectorAll('.remove-cart-btn');
    removeCartButtons.forEach(button => {
        button.addEventListener('click', handleRemoveCartItem);
    });
}

// Product selection functionality (blue tick)
function setupProductSelection() {
    const selectionCheckboxes = document.querySelectorAll('.selection-checkbox');
    
    selectionCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('click', function(e) {
            e.preventDefault();
            toggleItemSelection(this);
        });
    });
}

// Toggle item selection
function toggleItemSelection(element) {
    const itemId = element.dataset.itemId;
    const row = element.closest('.cart-item-row');
    
    fetch('/toggle_cart_item_selection', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            item_id: itemId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update UI
            if (data.selected) {
                element.classList.add('selected');
                element.innerHTML = '<i class="fas fa-check-circle text-primary"></i>';
                row.classList.add('selected');
                
                // Add animation
                row.classList.add('selection-highlight');
                setTimeout(() => row.classList.remove('selection-highlight'), 300);
            } else {
                element.classList.remove('selected');
                element.innerHTML = '<i class="far fa-circle"></i>';
                row.classList.remove('selected');
            }
            
            updateSelectedTotal();
        } else {
            showAlert('error', data.message || 'Error updating selection');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('error', 'Error updating selection');
    });
}

// Handle add to cart
function handleAddToCart(e) {
    e.preventDefault();
    const button = e.target.closest('.add-to-cart-btn');
    const productId = button.dataset.productId;
    const quantity = button.dataset.quantity || 1;
    
    // Show loading state
    const originalContent = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Adding...';
    button.disabled = true;
    
    const formData = new FormData();
    formData.append('product_id', productId);
    formData.append('quantity', quantity);
    formData.append('csrf_token', getCSRFToken());
    
    fetch('/add_to_cart', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', data.message);
            updateCartBadge(data.cart_count);
            
            // Update button to show added state temporarily
            button.innerHTML = '<i class="fas fa-check me-1"></i>Added!';
            button.classList.remove('btn-outline-success');
            button.classList.add('btn-success');
            
            setTimeout(() => {
                button.innerHTML = originalContent;
                button.classList.add('btn-outline-success');
                button.classList.remove('btn-success');
                button.disabled = false;
            }, 2000);
        } else {
            showAlert('error', data.message);
            button.innerHTML = originalContent;
            button.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('error', 'Error adding item to cart');
        button.innerHTML = originalContent;
        button.disabled = false;
    });
}

// Handle update cart item
function handleUpdateCartItem(e) {
    e.preventDefault();
    const button = e.target.closest('.update-cart-btn');
    const itemId = button.dataset.itemId;
    const quantityInput = document.querySelector(`input[data-item-id="${itemId}"]`);
    const quantity = parseInt(quantityInput.value);
    
    if (quantity <= 0) {
        if (confirm('Are you sure you want to remove this item from your cart?')) {
            removeCartItem(itemId);
        }
        return;
    }
    
    updateCartItemQuantity(itemId, quantity);
}

// Handle remove cart item
function handleRemoveCartItem(e) {
    e.preventDefault();
    const button = e.target.closest('.remove-cart-btn');
    const itemId = button.dataset.itemId;
    
    if (confirm('Are you sure you want to remove this item from your cart?')) {
        removeCartItem(itemId);
    }
}

// Update cart item quantity
function updateCartItemQuantity(itemId, quantity) {
    fetch('/update_cart_item', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            item_id: itemId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', 'Cart updated successfully');
            location.reload(); // Reload to update totals
        } else {
            showAlert('error', data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('error', 'Error updating cart');
    });
}

// Remove cart item
function removeCartItem(itemId) {
    updateCartItemQuantity(itemId, 0);
}

// Setup quantity controls
function setupQuantityControls() {
    const quantityControls = document.querySelectorAll('.quantity-control');
    
    quantityControls.forEach(control => {
        const minusBtn = control.querySelector('.qty-minus');
        const plusBtn = control.querySelector('.qty-plus');
        const input = control.querySelector('input[type="number"]');
        
        if (minusBtn && plusBtn && input) {
            minusBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const currentValue = parseInt(input.value) || 1;
                if (currentValue > 1) {
                    input.value = currentValue - 1;
                    input.dispatchEvent(new Event('change'));
                }
            });
            
            plusBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const currentValue = parseInt(input.value) || 0;
                const maxValue = parseInt(input.max) || 999;
                if (currentValue < maxValue) {
                    input.value = currentValue + 1;
                    input.dispatchEvent(new Event('change'));
                }
            });
        }
    });
}

// Setup forms
function setupForms() {
    // Offer form
    const offerForm = document.getElementById('offerForm');
    if (offerForm) {
        offerForm.addEventListener('submit', handleOfferSubmission);
    }
    
    // Search form auto-submit on filter change
    const searchFilters = document.querySelectorAll('.search-filter');
    searchFilters.forEach(filter => {
        filter.addEventListener('change', function() {
            if (this.closest('form')) {
                this.closest('form').submit();
            }
        });
    });
}

// Handle offer submission
function handleOfferSubmission(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    
    // Ensure CSRF token is included
    if (!formData.get('csrf_token')) {
        formData.append('csrf_token', getCSRFToken());
    }
    
    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalContent = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Sending...';
    submitBtn.disabled = true;
    
    fetch('/send_offer', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', data.message);
            form.reset();
            
            // Close modal if it exists
            const modal = form.closest('.modal');
            if (modal) {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) bsModal.hide();
            }
        } else {
            showAlert('error', data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('error', 'Error sending offer');
    })
    .finally(() => {
        submitBtn.innerHTML = originalContent;
        submitBtn.disabled = false;
    });
}

// Setup search functionality
function setupSearchFunctionality() {
    const searchInput = document.querySelector('input[name="search_query"]');
    if (searchInput) {
        // Add search suggestions functionality here if needed
        searchInput.addEventListener('input', debounce(function() {
            // Auto-search functionality can be added here
        }, 300));
    }
}

// Update cart badge
function updateCartBadge(count = null) {
    const cartBadge = document.getElementById('cart-badge');
    if (!cartBadge) return;
    
    if (count !== null) {
        cartCount = count;
    } else {
        // Fetch current cart count
        fetch('/api/cart_count')
            .then(response => response.json())
            .then(data => {
                cartCount = data.count;
                updateBadgeDisplay();
            })
            .catch(error => console.error('Error fetching cart count:', error));
        return;
    }
    
    updateBadgeDisplay();
}

// Update badge display
function updateBadgeDisplay() {
    const cartBadge = document.getElementById('cart-badge');
    if (!cartBadge) return;
    
    if (cartCount > 0) {
        cartBadge.textContent = cartCount;
        cartBadge.style.display = 'block';
    } else {
        cartBadge.style.display = 'none';
    }
}

// Update selected total in cart
function updateSelectedTotal() {
    const selectedItems = document.querySelectorAll('.cart-item-row.selected');
    let total = 0;
    
    selectedItems.forEach(item => {
        const priceElement = item.querySelector('.item-total');
        if (priceElement) {
            const price = parseFloat(priceElement.textContent.replace('₹', ''));
            total += price;
        }
    });
    
    const selectedTotalElement = document.getElementById('selected-total');
    if (selectedTotalElement) {
        selectedTotalElement.textContent = `₹${total.toFixed(2)}`;
    }
    
    // Update negotiate button state
    const negotiateBtn = document.getElementById('negotiate-selected-btn');
    if (negotiateBtn) {
        negotiateBtn.disabled = selectedItems.length === 0;
    }
}

// Show alert message
function showAlert(type, message, duration = 5000) {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Find or create alert container
    let alertContainer = document.querySelector('.alert-container');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.className = 'alert-container position-fixed top-0 end-0 p-3';
        alertContainer.style.zIndex = '1050';
        document.body.appendChild(alertContainer);
    }
    
    alertContainer.appendChild(alertDiv);
    
    // Auto-dismiss after duration
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, duration);
}

// Get CSRF token
function getCSRFToken() {
    return document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || 
           document.querySelector('input[name="csrf_token"]')?.value || '';
}

// Debounce function
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction() {
        const context = this;
        const args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Load animations
function loadAnimations() {
    // Intersection Observer for animations
    if ('IntersectionObserver' in window) {
        const animatedElements = document.querySelectorAll('.fade-in, .slide-up');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate');
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        animatedElements.forEach(el => observer.observe(el));
    }
}

// Price formatting
function formatPrice(price) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(price);
}

// Date formatting
function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(date);
}

// Image lazy loading
function setupLazyLoading() {
    if ('IntersectionObserver' in window) {
        const lazyImages = document.querySelectorAll('img[data-src]');
        
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(img => imageObserver.observe(img));
    }
}

// Export functions for use in other scripts
window.AgriConnect = {
    showAlert,
    updateCartBadge,
    formatPrice,
    formatDate,
    getCSRFToken
};
