document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('accessToken');

    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    // Un solo punto de entrada para cargar todos los datos.
    loadDashboardData(token);
});

async function loadDashboardData(token) {
    const headers = { 'Authorization': `Bearer ${token}` };

    try {
        // Hacemos una SOLA llamada al nuevo endpoint /api/me/info
        const infoResponse = await fetch('http://localhost:8000/api/me/info', { headers });

        if (infoResponse.status === 401) { // El token expiró o es inválido
             throw new Error('Sesión inválida, por favor inicie sesión de nuevo.');
        }
        if (!infoResponse.ok) {
            throw new Error('No se pudieron obtener los datos principales.');
        }

        const infoData = await infoResponse.json();

        // Ahora pedimos los movimientos, que es una llamada separada.
        const movementsResponse = await fetch('http://localhost:8000/api/me/movements', { headers });
        if (!movementsResponse.ok) throw new Error('No se pudieron obtener los movimientos.');

        const movementsData = await movementsResponse.json();
        
        // Con todos los datos en nuestro poder, "pintamos" la página.
        displayUserInfo(infoData);
        displayMovements(movementsData, infoData.account_number);

    } catch (error) {
        console.error("Error al cargar el dashboard:", error);
        // Si cualquier petición falla, borramos el token y lo enviamos al login.
        localStorage.removeItem('accessToken');
        window.location.href = 'login.html';
    }
}

function displayUserInfo(data) {
    // El endpoint /me/info ya nos da todo: nombre, apellido, y saldo.
    document.getElementById('user-welcome').textContent = `¡Bienvenido, ${data.nombre} ${data.apellido}!`;
    
    const balanceElement = document.getElementById('account-balance');
    const formattedBalance = new Intl.NumberFormat('es-PE', { 
        style: 'currency', 
        currency: 'PEN' 
    }).format(data.balance);
    balanceElement.textContent = formattedBalance;
}

function displayMovements(data, accountNumber) {
    const movementsList = document.getElementById('movements-list');
    movementsList.innerHTML = ''; 

    if (data.movements && data.movements.length > 0) {
        data.movements.forEach(mov => {
            const listItem = document.createElement('li');
            const esRetiro = mov.origen === accountNumber;
            const monto = esRetiro ? `- S/ ${mov.monto.toFixed(2)}` : `+ S/ ${mov.monto.toFixed(2)}`;
            const claseMonto = esRetiro ? 'withdrawal' : 'deposit';
            const descripcion = esRetiro ? `Transferencia a ${mov.destino}` : `Transferencia de ${mov.origen}`;

            listItem.innerHTML = `
                <span class="description">${descripcion}</span>
                <span class="amount ${claseMonto}">${monto}</span>
            `;
            movementsList.appendChild(listItem);
        });
    } else {
        movementsList.innerHTML = '<li>No se han encontrado movimientos.</li>';
    }
}