// static/js/about.js

/**
 * Alterna la visibilità della bio per il membro specificato.
 * @param {string} memberId - identificatore ('mario', 'luca', 'anna', ...)
 */
function toggleBio(memberId) {
    const bioEl = document.getElementById(`bio-${memberId}`);
    const btn = document.querySelector(`.team-member[data-member="${memberId}"] .btn-bio`);
    if (!bioEl || !btn) return;
  
    if (bioEl.style.display === 'block') {
      bioEl.style.display = 'none';
      btn.textContent = 'Mostra Bio';
    } else {
      bioEl.style.display = 'block';
      btn.textContent = 'Nascondi Bio';
    }
  }
  
  // Eventuale: animazione al caricamento (fade-in)
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.team-member').forEach((el, idx) => {
      el.style.opacity = 0;
      setTimeout(() => {
        el.style.transition = 'opacity 0.6s';
        el.style.opacity = 1;
      }, idx * 150);
    });
  });