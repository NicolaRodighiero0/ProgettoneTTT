/* ============================================================
   Trainer Dashboard – stats + click through
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {

  /* ---------- 1. scarica le statistiche ---------- */
  fetch('/api/trainer/stats', { credentials: 'same-origin' })
    .then(resp => {
      if (!resp.ok) throw new Error('Impossibile caricare le statistiche');
      return resp.json();
    })
    .then(stats => {
      document.getElementById('stat-clients'  ).textContent = stats.clients;
      document.getElementById('stat-workouts' ).textContent = stats.workouts;
      document.getElementById('stat-exercises').textContent = stats.exercises;
      document.getElementById('stat-machines' ).textContent = stats.machines;
    })
    .catch(err => {
      console.error(err);
      document.querySelectorAll('.stat-number')
              .forEach(el => el.textContent = '–');
      alert(err.message);
    });

  /* ---------- 2. rendi cliccabili i riquadri con data-link ---------- */
  document.querySelectorAll('.stat-card[data-link]').forEach(card => {
    card.style.cursor = 'pointer';
    card.addEventListener('click', () =>
      window.location.href = card.dataset.link
    );
  });
});
