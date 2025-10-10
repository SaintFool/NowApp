document.addEventListener('DOMContentLoaded', () => {
    // --- 1. CONFIGURACIÓN INICIAL Y GUARDIA DE SEGURIDAD ---
    const token = localStorage.getItem('accessToken');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    // Seleccionamos todos los elementos del DOM que manipularemos.
    const cartContent = document.getElementById('cart-content');
    const emptyCartMessage = document.getElementById('empty-cart-message');
    const itemsContainer = document.getElementById('cart-items-container');
    const subtotalsList = document.getElementById('subtotals-list');
    const totalPriceElement = document.getElementById('total-price');
    const checkoutButton = document.getElementById('checkout-button');
    const checkoutMessage = document.getElementById('checkout-message');

    
    // --- 2. FUNCIÓN PRINCIPAL PARA CARGAR LOS DATOS DEL CARRITO ---
    async function loadCartData() {
        const headers = { 'Authorization': `Bearer ${token}` };
        try {
            const response = await fetch('http://localhost:8000/api/cart', { headers });
            
            if (response.status === 401) { // Token inválido o expirado
                throw new Error('Sesión inválida. Por favor, inicie sesión de nuevo.');
            }
            if (!response.ok) {
                throw new Error('No se pudo cargar el carrito.');
            }

            const data = await response.json();
            
            if (data.exists === false || data.cart.items.length === 0) {
                // Si el carrito está vacío, mostramos el mensaje apropiado.
                cartContent.style.display = 'none';
                emptyCartMessage.style.display = 'block';
            } else {
                // Si hay items, mostramos el contenido 
                cartContent.style.display = 'block';
                emptyCartMessage.style.display = 'none';
                renderCart(data.cart);
            }

        } catch (error) {
            console.error("Error al cargar el carrito:", error);
            localStorage.removeItem('accessToken');
            window.location.href = 'login.html';
        }
    }

    // --- 3. FUNCIÓN PARA INTAR LOS DATOS DEL CARRITO EN EL HTML ---
    function renderCart(cart) {
        itemsContainer.innerHTML = '';
        subtotalsList.innerHTML = '';

        cart.items.forEach(item => {
            const itemElement = document.createElement('div');
            itemElement.className = 'cart-item';
            const itemTotalPrice = (item.quantity * item.price_per_unit).toFixed(2);
            
            itemElement.innerHTML = `
                <div class="item-info">
                    <span class="item-name">${item.name}</span>
                    <span class="item-store">Vendido por: ${formatStoreName(item.store_id)}</span>
                </div>
                <div class="item-details">
                    <span class="item-quantity">Cantidad: ${item.quantity}</span>
                    <span class="item-price">S/ ${itemTotalPrice}</span>
                </div>
            `;
            itemsContainer.appendChild(itemElement);
        });

        cart.subtotals_by_store.forEach(subtotal => {
            const subtotalElement = document.createElement('div');
            subtotalElement.className = 'summary-line';
            
            subtotalElement.innerHTML = `
                <span>Pago a ${formatStoreName(subtotal.store_id)}:</span>
                <span>S/ ${subtotal.subtotal.toFixed(2)}</span>
            `;
            subtotalsList.appendChild(subtotalElement);
        });

        totalPriceElement.textContent = `S/ ${cart.total_price.toFixed(2)}`;
    }

    // --- 4. EVENT LISTENER PARA EL BOTÓN DE FINALIZAR COMPRA ---
    checkoutButton.addEventListener('click', async () => {
        checkoutButton.disabled = true;
        checkoutButton.textContent = 'Procesando pago...';
        checkoutMessage.textContent = '';
        checkoutMessage.className = 'message';

        const headers = { 'Authorization': `Bearer ${token}` };

        try {
            const response = await fetch('http://localhost:8000/api/orders', {
                method: 'POST',
                headers: headers
            });

            const data = await response.json();

            if (!response.ok) {
                // Mostramos el error específico que nos da la API (ej: "Saldo insuficiente").
                throw new Error(data.detail || 'No se pudo completar la compra.');
            }

            // ¡ÉXITO!
            checkoutMessage.textContent = `¡Compra exitosa! Pedido #${data.order_number}`;
            checkoutMessage.classList.add('success');

            // Ocultamos el botón de pagar para que no se pueda hacer clic de nuevo.
            checkoutButton.style.display = 'none';

            // Redirigimos a la página principal después de 3 segundos.
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 3000);

        } catch (error) {
            console.error('Error en el checkout:', error);
            checkoutMessage.textContent = error.message;
            checkoutMessage.classList.add('error');
            
            // Habilitamos el botón de nuevo para que el usuario pueda reintentar.
            checkoutButton.disabled = false;
            checkoutButton.textContent = 'Finalizar Compra y Pagar';
        }
    });

    // --- FUNCIÓN AUXILIAR PARA FORMATEAR NOMBRES ---
    function formatStoreName(storeId) {
        return storeId
            .replace('store_', '')
            .replace(/_/g, ' ')
            .replace(/(^\w|\s\w)/g, m => m.toUpperCase());
    }

    // --- PUNTO DE ENTRADA: LLAMAMOS A LA FUNCIÓN PRINCIPAL ---
    loadCartData();
});