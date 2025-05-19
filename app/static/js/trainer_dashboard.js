document.addEventListener('DOMContentLoaded', () => {
    const url = '/api/trainer/stats';
    fetch(url, { credentials: 'same-origin' })
      .then(resp => {
        if (!resp.ok) throw new Error('Impossibile caricare le statistiche');
        return resp.json();
      })
      .then(stats => {
        document.getElementById('stat-clients').textContent   = stats.clients;
        document.getElementById('stat-workouts').textContent  = stats.workouts;
        document.getElementById('stat-exercises').textContent = stats.exercises;
      })
      .catch(err => {
        console.error(err);
        document.querySelectorAll('.stat-number').forEach(el => el.textContent = '-');
        alert(err.message);
      });
  });
  