document.addEventListener('DOMContentLoaded', function() {
    // Inizializza AOS (Animate On Scroll)
    AOS.init({
        duration: 800,
        easing: 'ease',
        once: true
    });

    // Smooth scroll per i link interni
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Parallax effect per hero e CTA
    const heroSection = document.querySelector('.hero-section');
    const ctaSection = document.querySelector('.cta-section');
    
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        
        if (heroSection) {
            heroSection.style.backgroundPositionY = scrolled * 0.5 + 'px';
        }
        
        if (ctaSection) {
            ctaSection.style.backgroundPositionY = (scrolled - ctaSection.offsetTop) * 0.5 + 'px';
        }
    });

    // Navbar transparency on scroll
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        });
    }
});