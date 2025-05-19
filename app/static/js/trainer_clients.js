// app/static/js/trainer_clients.js

document.addEventListener('DOMContentLoaded', () => {
    const formAdd   = document.getElementById('form-add-client');
    const tableBody = document.querySelector('#clients-table tbody');
  
    // 1) Carica la lista dei clienti via session cookie
    function loadClients() {
      fetch('/api/trainer/clients', {
        credentials: 'same-origin'     // include il cookie di sessione
      })
        .then(r => {
          if (!r.ok) throw new Error('Impossibile caricare i clienti');
          return r.json();
        })
        .then(clients => {
          if (clients.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="2" class="text-center">Nessun cliente</td></tr>';
            return;
          }
          tableBody.innerHTML = clients.map(c => `
            <tr>
              <td>${c.id}</td>
              <td>${c.username}</td>
            </tr>
          `).join('');
        })
        .catch(err => {
          tableBody.innerHTML = `<tr><td colspan="2" class="text-danger">${err.message}</td></tr>`;
        });
    }
  
    // 2) Creazione di un nuovo cliente
    formAdd.addEventListener('submit', e => {
        e.preventDefault();
        const data = {
            username: formAdd.username.value,
            password: formAdd.password.value
        };

        if (!data.username || !data.password) {
            alert('Username e password sono obbligatori');
            return;
        }

        fetch('/api/trainer/clients', {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => {
            // Prima controlliamo lo status della risposta
            if (response.status === 401) {
                window.location.href = '/login';
                throw new Error('Sessione scaduta');
            }
            // Poi processiamo il JSON
            return response.json().then(data => ({
                ok: response.ok,
                status: response.status,
                data
            }));
        })
        .then(({ ok, data }) => {
            if (!ok) {
                throw new Error(data.error || 'Errore durante la creazione del cliente');
            }
            
            // Success
            formAdd.reset();
            alert('Cliente creato con successo!');
            loadClients();
        })
        .catch(err => {
            if (err.message !== 'Sessione scaduta') {
                console.error(err);
                alert(err.message);
            }
        });
    });

    // Assicuriamoci di caricare i clienti all'avvio
    loadClients();
});