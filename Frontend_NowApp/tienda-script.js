// --- /Frontend/tienda-script.js (VERSIÓN CORREGIDA FINAL) ---

document.addEventListener('DOMContentLoaded', () => {
    // --- 1. CONFIGURACIÓN INICIAL Y GUARDIA DE SEGURIDAD ---
    const token = localStorage.getItem('accessToken');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    // --- SELECCIÓN DE ELEMENTOS DEL DOM ---
    const productGrid = document.getElementById('product-grid');
    const filterButtons = document.querySelectorAll('.filter-btn');
    const rateAppButton = document.querySelector('.rate-button');
    const reviewModal = document.getElementById('review-modal');
    const closeModalButton = reviewModal.querySelector('.close-button');
    const reviewForm = document.getElementById('review-form');
    const starsContainer = document.getElementById('score-stars');
    const reviewMessage = document.getElementById('review-message');

    let allProducts = [];
    let currentScore = 0;

    // --- 2. LÓGICA DE CARGA DE PRODUCTOS ---
    async function fetchProducts() {
        try {
            const response = await fetch('http://localhost:8000/api/products');
            if (!response.ok) throw new Error('No se pudieron cargar los productos.');
            allProducts = await response.json();
            displayProducts(allProducts);
        } catch (error) {
            console.error("Error al cargar productos:", error);
            productGrid.innerHTML = '<p>Error al cargar productos. Intente más tarde.</p>';
        }
    }

    function displayProducts(productsToDisplay) {
        productGrid.innerHTML = '';
        productsToDisplay.forEach(product => {
            const card = document.createElement('div');
            card.className = 'product-card';
            const priceFormatted = new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' }).format(product.price);
            card.innerHTML = `
                <img src="${product.image_urls[0]}" alt="${product.name}">
                <div class="card-content">
                    <h3 class="product-name">${product.name}</h3>
                    <p class="product-price">${priceFormatted}</p>
                    <p class="product-store">Vendido por: ${formatStoreName(product.store_id)}</p>
                    <button class="button add-to-cart-btn" data-product-id="${product._id}">Añadir al Carrito</button>
                </div>
            `;
            productGrid.appendChild(card);
        });
    }

    // --- 3. LÓGICA DE FILTROS ---
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            const storeId = button.dataset.storeId;
            const filteredProducts = storeId === 'all' ? allProducts : allProducts.filter(p => p.store_id === storeId);
            displayProducts(filteredProducts);
        });
    });

    // --- 4. LÓGICA PARA AÑADIR AL CARRITO ---
    productGrid.addEventListener('click', async (event) => {
        if (event.target.classList.contains('add-to-cart-btn')) {
            const button = event.target;
            const productId = button.dataset.productId;
            
            const originalText = button.textContent;
            button.textContent = 'Añadiendo...';
            button.disabled = true;

            try {
                const response = await fetch('http://localhost:8000/api/cart/items', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                    body: JSON.stringify({ product_id: productId, quantity: 1 })
                });
                const data = await response.json();
                if (!response.ok) throw new Error(data.detail || 'No se pudo añadir.');

                button.textContent = '¡Añadido! ✅';
                setTimeout(() => {
                    button.textContent = originalText;
                    button.disabled = false;
                }, 1500);
            } catch (error) {
                console.error("Error al añadir al carrito:", error);
                button.textContent = 'Error ❌';
                 setTimeout(() => {
                    button.textContent = originalText;
                    button.disabled = false;
                }, 2000);
            }
        }
    });

    // --- 5. LÓGICA PARA EL MODAL DE CALIFICACIÓN (CORREGIDA) ---
    function openModal() { reviewModal.classList.add('show'); }
    function closeModal() { reviewModal.classList.remove('show'); }

    rateAppButton.addEventListener('click', openModal);
    closeModalButton.addEventListener('click', closeModal);
    window.addEventListener('click', (event) => {
        if (event.target === reviewModal) closeModal();
    });

    for (let i = 1; i <= 10; i++) { /* Generación de estrellas */ }
    for (let i = 1; i <= 10; i++) {
        const star = document.createElement('span');
        star.className = 'star';
        star.textContent = '★';
        star.dataset.score = i;
        starsContainer.appendChild(star);
    }
    const allStars = document.querySelectorAll('.star');

    starsContainer.addEventListener('mouseover', (event) => {
        if (event.target.classList.contains('star')) {
            const hoverScore = event.target.dataset.score;
            allStars.forEach((s, index) => {
                s.style.color = index < hoverScore ? '#ffc107' : '#ddd';
            });
        }
    });

    starsContainer.addEventListener('mouseout', () => {
        allStars.forEach((s, index) => {
            s.style.color = index < currentScore ? '#ffc107' : '#ddd';
        });
    });

    starsContainer.addEventListener('click', (event) => {
        if (event.target.classList.contains('star')) {
            currentScore = event.target.dataset.score;
            allStars.forEach((s, index) => {
                s.classList.toggle('selected', index < currentScore);
            });
        }
    });

    // Enviar formulario de calificación
    reviewForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        reviewMessage.textContent = '';
        if (currentScore === 0) {
            reviewMessage.textContent = 'Por favor, selecciona una puntuación.';
            return;
        }

        const comment = document.getElementById('review-comment').value;

        try {
            const response = await fetch('http://localhost:8000/api/reviews', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                body: JSON.stringify({ score: parseInt(currentScore), comment: comment })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || 'Error al enviar.');

            reviewForm.innerHTML = `<h3 class="success">¡Gracias por tu opinión!</h3>`;
            setTimeout(closeModal, 2000);
        } catch (error) {
            reviewMessage.textContent = error.message;
            console.error(error);
        }
    });
    
    // --- 6. FUNCIONES AUXILIARES ---
    function formatStoreName(storeId) {
        return storeId.replace('store_', '').replace(/_/g, ' ').replace(/(^\w|\s\w)/g, m => m.toUpperCase());
    }

    // --- PUNTO DE ENTRADA ---
    fetchProducts();
});