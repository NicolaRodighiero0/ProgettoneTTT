document.addEventListener('DOMContentLoaded', function() {
    // Form validation
    const loginForm = document.querySelector('.needs-validation');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            if (!loginForm.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            loginForm.classList.add('was-validated');
        });
    }

    // Add input focus effects
    const formInputs = document.querySelectorAll('.form-control');
    
    formInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.closest('.input-group').classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.closest('.input-group').classList.remove('focused');
        });
    });
});

// Password visibility toggle
function togglePassword() {
    const passwordInput = document.getElementById('password');
    const toggleButton = document.querySelector('.password-toggle i');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleButton.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        toggleButton.classList.replace('fa-eye-slash', 'fa-eye');
    }
}

// Add the function to window to make it accessible from HTML
window.togglePassword = togglePassword;