// Script per gestire il cambio di tema chiaro/scuro
document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('theme-toggle');
    const body = document.body;
    const navbar = document.getElementById('navbar');
    const footer = document.querySelector('.footer-custom');
  
    function setTheme(theme) {
      if (theme === 'dark') {
        // Applica tema scuro
        body.style.backgroundColor = '#394c5c'; // Nero per tema scuro
        body.style.color = '#d8E7ee'; // Arancione chiaro
        
        // Navbar turchese
        navbar.style.backgroundColor = '#50698d';
        navbar.style.color = '#102b53';
        navbar.style.borderBottom = '4px solid #102b53';
        
        // Cambia icona tema
        toggleBtn.textContent = '☀️';
        
        // Footer turchese
        footer.style.backgroundColor = '#50698d';
        footer.style.borderTop = '4px solid #102b53';
        
        // Cambia sfondo dei contenitori nel footer
        document.querySelectorAll('.footer-content').forEach(el => {
          el.style.backgroundColor = 'rgba(80, 105, 141, 0.8)'; // Turchese semitrasparente
        });
        
        // Aggiorna i colori di titoli e bottoni nel footer
        document.querySelectorAll('.footer-custom h3').forEach(el => {
          el.style.color = '#102b53';
        });
        
        document.querySelectorAll('.footer-custom button').forEach(el => {
          el.style.backgroundColor = '#102b53';
          el.style.color = '#394c5c';
        });
        
      } else {
        // Applica tema chiaro
        body.style.backgroundColor = '#EEe2df'; // Bianco per tema chiaro
        body.style.color = '#6da0e1';
        
        // Navbar azzurra
        navbar.style.backgroundColor = '#dec1db';
        navbar.style.color = '#5B61B2'; 
        navbar.style.borderBottom = '4px solid #5B61B2';
        
        // Cambia icona tema
        toggleBtn.textContent = '🌙';
        
        // Footer azzurro
        footer.style.backgroundColor = '#dec1db';
        footer.style.borderTop = '4px solid #5B61B2';
        
        // Ripristina sfondo dei contenitori nel footer
        document.querySelectorAll('.footer-content').forEach(el => {
          el.style.backgroundColor = 'rgba(222, 193, 219, 1)'; // Azzurro semitrasparente
        });
        
        // Ripristina i colori originali
        document.querySelectorAll('.footer-custom h3').forEach(el => {
          el.style.color = '#5B61B2';
        });
        
        document.querySelectorAll('.footer-custom button').forEach(el => {
          el.style.backgroundColor = '#5B61B2';
          el.style.color = '#EEe2df';
        });
      }
      
      // Salva preferenza tema
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
  });