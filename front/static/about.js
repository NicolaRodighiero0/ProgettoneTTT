document.addEventListener('DOMContentLoaded', function() {
    // Gestione tema chiaro/scuro
    const toggleBtn = document.getElementById('theme-toggle');
    const body = document.body;

    function setTheme(theme) {
        if (theme === 'dark') {
            body.classList.add('dark');
            toggleBtn.textContent = '☀️';
        } else {
            body.classList.remove('dark');
            toggleBtn.textContent = '🌙';
        }
        localStorage.setItem('theme', theme);
    }

    // Carica il tema salvato o usa light come default
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);

    // Cambia tema al clic
    toggleBtn.addEventListener('click', () => {
        const newTheme = localStorage.getItem('theme') === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    });

    // Animazioni al caricamento
    const animateElements = document.querySelectorAll('.team-member, .project-card, .meaning-card');
    
    animateElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = `all 0.5s ease ${index * 0.1}s`;
        
        setTimeout(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, 100);
    });

    // Effetto hover per le card
    const cards = document.querySelectorAll('.team-member, .feature');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-5px)';
            card.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
            card.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.1)';
        });
    });
});