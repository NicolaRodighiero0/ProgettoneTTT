// app/static/js/client_dashboard.js

document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('dashboard');
    const listEl = document.getElementById('workout-list');
    const userId = container.dataset.userId;
  
    // Se non abbiamo userId, non procediamo
    if (!userId) return;
  
          fetch(`/api/workouts/history/${userId}`, {
                credentials: 'same-origin'  // include i cookie di sessione
         })
      .then(resp => {
        if (!resp.ok) throw new Error('Impossibile caricare le schede');
        return resp.json();
      })
      .then(data => {
        if (data.length === 0) {
          listEl.innerHTML = '<li class="workout-item text-center">Nessuna scheda disponibile.</li>';
          return;
        }
  
        // Popola la lista
        listEl.innerHTML = data.map(w => `
          <li class="workout-item">
            <div class="workout-info">
              <div class="name">${w.name || 'Scheda del ' + w.date_created}</div>
              <div class="date">Creato: ${w.date_created} – Trainer: ${w.trainer_name}</div>
            </div>
            <a href="/client/workout/${w.id}" class="btn btn-primary btn-start">Avvia</a>
          </li>
        `).join('');
      })
      .catch(err => {
        listEl.innerHTML = `<li class="workout-item text-danger">${err.message}</li>`;
        console.error(err);
      });
  });
  