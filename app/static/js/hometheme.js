// Script per gestire il cambio di tema chiaro/scuro e altre funzionalità
document.addEventListener('DOMContentLoaded', function() {
    // Inizializza AOS
    AOS.init({
        duration: 800,
        easing: 'ease-out',
        once: true
    });

    // Gestione navbar allo scroll
    const navbar = document.getElementById('navbar');
    const scrollThreshold = 50;
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > scrollThreshold) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    });

    // Smooth scroll per i link della navbar
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                window.scrollTo({
                    top: target.offsetTop - navbar.offsetHeight,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Gestione tema migliorata
    const toggleBtn = document.getElementById('theme-toggle');
    const root = document.documentElement;
    
    function setTheme(theme) {
        const isDark = theme === 'dark';
        
        // Applica il tema usando data-attribute
        root.setAttribute('data-theme', theme);
        
        // Aggiorna l'icona
        toggleBtn.innerHTML = isDark ? '☀️' : '🌙';
        
        // Aggiorna hero text color
        const heroContent = document.querySelector('.hero-content');
        if (heroContent) {
            heroContent.style.color = isDark ? 'var(--hero-text-dark)' : 'var(--hero-text-light)';
        }
        
        // Salva la preferenza
        localStorage.setItem('theme', theme);
        
        // Aggiorna meta theme-color per mobile
        document.querySelector('meta[name="theme-color"]')?.setAttribute(
            'content', 
            isDark ? '#121212' : '#ffffff'
        );
    }

    // Sistema preferenze iniziali
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const savedTheme = localStorage.getItem('theme');
    
    setTheme(savedTheme || (prefersDark ? 'dark' : 'light'));

    // Ascolta cambiamenti delle preferenze di sistema
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        if (!localStorage.getItem('theme')) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });

    // Toggle tema
    toggleBtn.addEventListener('click', () => {
        const newTheme = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    });

    // Animazione elementi al caricamento
    document.querySelectorAll('.fade-in').forEach((element, index) => {
        element.style.opacity = '0';
        setTimeout(() => {
            element.style.animation = 'fadeIn 0.6s ease forwards';
        }, index * 200);
    });

    // Gestione hero banner allo scroll
    const heroSection = document.querySelector('.hero-section');
    const scrollableContent = document.querySelector('.scrollable-content');

    window.addEventListener('scroll', () => {
        const scrollPosition = window.scrollY;
        
        // Effetto parallax sull'hero banner
        heroSection.style.opacity = Math.max(1 - scrollPosition / window.innerHeight, 0);
        heroSection.style.transform = `translateY(${scrollPosition * 0.5}px)`;
        
        // Nascondi completamente l'hero quando non è più visibile
        if (scrollPosition > window.innerHeight) {
            heroSection.style.visibility = 'hidden';
        } else {
            heroSection.style.visibility = 'visible';
        }
    });
});