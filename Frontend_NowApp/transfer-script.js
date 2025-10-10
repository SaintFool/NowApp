document.addEventListener('DOMContentLoaded', () => {
    // 1. OBTENEMOS EL TOKEN Y PROTEGEMOS LA PÁGINA
    const token = localStorage.getItem('accessToken');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    // Seleccionamos los elementos del DOM que necesitaremos
    const transferForm = document.getElementById('transfer-form');
    const cuentaOrigenInput = document.getElementById('cuenta-origen');
    const messageElement = document.getElementById('transfer-message');

    // 2. OBTENEMOS LOS DATOS DEL USUARIO PARA RELLENAR EL FORMULARIO
    async function fetchUserInfoAndPopulateForm() {
        const headers = { 'Authorization': `Bearer ${token}` };
        try {
            const response = await fetch('http://localhost:8000/api/me/info', { headers });
            if (!response.ok) {
                // Si el token es inválido, redirigimos al login.
                throw new Error('Sesión inválida.');
            }
            const data = await response.json();
            // Rellenamos el campo de la cuenta de origen
            cuentaOrigenInput.value = data.account_number;
        } catch (error) {
            console.error(error);
            localStorage.removeItem('accessToken');
            window.location.href = 'login.html';
        }
    }

    // Llamamos a la función para que se ejecute al cargar la página
    fetchUserInfoAndPopulateForm();

    // 3. MANEJAMOS EL ENVÍO DEL FORMULARIO
    transferForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevenimos la recarga de la página

        // Limpiamos mensajes anteriores
        messageElement.textContent = '';
        messageElement.className = 'message';

        // Capturamos los datos del formulario
        const cuentaOrigen = cuentaOrigenInput.value;
        const cuentaDestino = event.target.elements['cuenta-destino'].value;
        const monto = parseFloat(event.target.elements.monto.value);

        // Preparamos el cuerpo de la petición (el "payload")
        const requestBody = {
            cuenta_origen: cuentaOrigen,
            cuenta_destino: cuentaDestino,
            monto: monto
        };

        try {
            const response = await fetch('http://localhost:8000/api/transfers', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json' // ¡Importante para POST con JSON!
                },
                body: JSON.stringify(requestBody) // Convertimos el objeto JS a un string JSON
            });

            const data = await response.json();

            if (!response.ok) {
                // Usamos 'data.detail' porque así lo configuran las HTTPException de FastAPI
                const errorMessage = data.detail || 'Ocurrió un error en la transferencia.';
                throw new Error(errorMessage);
            }
            
            // ¡ÉXITO!
            messageElement.textContent = "¡Transferencia realizada con éxito!";
            messageElement.classList.add('success');

            // Opcional: Deshabilitar el botón y redirigir tras unos segundos
            transferForm.querySelector('button').disabled = true;
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 2000); // Redirige a la página principal tras 2 segundos

        } catch (error) {
            // El error.message contendrá lo que viene de la API (ej: "Saldo insuficiente...")
            messageElement.textContent = error.message;
            messageElement.classList.add('error');
            console.error('Error en la transferencia:', error);
        }
    });
});