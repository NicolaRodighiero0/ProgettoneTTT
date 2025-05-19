document.addEventListener('DOMContentLoaded', function() {
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

    // Aggiungi animazioni agli elementi
    const cards = document.querySelectorAll('.detail-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.5s ease ' + (index * 0.1) + 's';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100);
    });
});