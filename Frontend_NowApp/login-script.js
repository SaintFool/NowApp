
document.addEventListener('DOMContentLoaded', () => {

    const loginForm = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');

    if (!loginForm) {
        console.error("El formulario de login no se encontró en la página.");
        return; 
    }

    loginForm.addEventListener('submit', async (event) => {
        
        event.preventDefault();
        
        errorMessage.textContent = '';

        const username = event.target.username.value;
        const password = event.target.password.value;

        if (!username || !password) {
            errorMessage.textContent = 'Por favor, ingrese usuario y contraseña.';
            return;
        }

        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        try {

            const response = await fetch('http://localhost:8000/api/auth/login', {
                method: 'POST',

                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData
            });
            
  
            const data = await response.json();

            if (!response.ok) {

                throw new Error(data.detail || 'Ocurrió un error al intentar iniciar sesión.');
            }

            console.log("Login exitoso. Token recibido:", data.access_token);
            localStorage.setItem('accessToken', data.access_token);
            

            window.location.href = 'index.html';

        } catch (error) {
        
            console.error('Error de inicio de sesión:', error);
            errorMessage.textContent = error.message;
        }
    });
});