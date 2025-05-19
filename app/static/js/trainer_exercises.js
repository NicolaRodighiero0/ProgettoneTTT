// app/static/js/trainer_exercises.js

document.addEventListener('DOMContentLoaded', () => {
    // Elementi DOM
    const filterMuscle     = document.getElementById('filter-muscle');
    const filterObjective  = document.getElementById('filter-objective');
    const filterDifficulty = document.getElementById('filter-difficulty');
    const btnFilter        = document.getElementById('btn-filter');
    const btnClear         = document.getElementById('btn-clear');
    const btnToggleForm    = document.getElementById('btn-toggle-form');
    const btnCancelAdd     = document.getElementById('btn-cancel-add');
    const formAdd          = document.getElementById('form-add-exercise');
    const tableBody        = document.querySelector('#exercises-table tbody');
  
    // Editing modal
    const editModalEl      = document.getElementById('editModal');
    const editModal        = new bootstrap.Modal(editModalEl);
    const formEdit         = document.getElementById('form-edit-exercise');
    const editNameInput    = document.getElementById('edit-name');
    const editDescInput    = document.getElementById('edit-description');
    const editObjSelect    = document.getElementById('edit-objective');
    const editDiffSelect   = document.getElementById('edit-difficulty');
  
    // Select dentro formAdd
    const addObjSelect     = formAdd.querySelector('select[name="objective"]');
    const addDiffSelect    = formAdd.querySelector('select[name="difficulty"]');
  
    let currentExercises = [];
  
    // 1) Carica metadati e popola tutti i <select>
    Promise.all([
      fetch('/api/muscle-groups', { credentials:'same-origin' }).then(r=>r.json()),
      fetch('/api/objectives',    { credentials:'same-origin' }).then(r=>r.json()),
      fetch('/api/difficulties',  { credentials:'same-origin' }).then(r=>r.json())
    ]).then(([mgs, objs, diffs]) => {
      // filtro muscoli
      mgs.forEach(m => filterMuscle.add(new Option(m.name, m.name)));
  
      // obiettivi
      objs.forEach(o => {
        filterObjective.add(new Option(o.name, o.name));
        addObjSelect   .add(new Option(o.name, o.name));
        editObjSelect  .add(new Option(o.name, o.name));
      });
  
      // difficoltà
      diffs.forEach(d => {
        filterDifficulty.add(new Option(d.level, d.level));
        addDiffSelect    .add(new Option(d.level, d.level));
        editDiffSelect   .add(new Option(d.level, d.level));
      });
  
      // inizializza la tabella
      loadExercises();
    });
  
    // 2) Funzione per caricare e disegnare la tabella
    function loadExercises() {
      const params = new URLSearchParams();
      if (filterMuscle.value)     params.append('muscle_group', filterMuscle.value);
      if (filterObjective.value)  params.append('objective',    filterObjective.value);
      if (filterDifficulty.value) params.append('difficulty',   filterDifficulty.value);
  
      fetch('/api/exercises?' + params, { credentials:'same-origin' })
        .then(r => { if(!r.ok) throw new Error('Errore caricamento'); return r.json(); })
        .then(exs => {
          currentExercises = exs;
          if (exs.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="4" class="text-center">Nessun esercizio</td></tr>';
            return;
          }
          tableBody.innerHTML = exs.map(e => `
            <tr>
              <td>${e.name}</td>
              <td>${e.objective}</td>
              <td>${e.difficulty}</td>
              <td>
                <button class="btn btn-sm btn-warning edit-btn" data-id="${e.id}">Modifica</button>
                <button class="btn btn-sm btn-danger delete-btn" data-id="${e.id}">Elimina</button>
              </td>
            </tr>
          `).join('');
  
          // associa eventi
          tableBody.querySelectorAll('.delete-btn').forEach(btn => {
            btn.onclick = () => deleteExercise(btn.dataset.id);
          });
          tableBody.querySelectorAll('.edit-btn').forEach(btn => {
            btn.onclick = () => openEditModal(btn.dataset.id);
          });
        })
        .catch(e => {
          tableBody.innerHTML = `<tr><td colspan="4" class="text-danger">${e.message}</td></tr>`;
        });
    }
  
    // 3) Crea nuovo esercizio
    formAdd.addEventListener('submit', e => {
      e.preventDefault();
      const data = {
        name:        formAdd.name.value,
        description: formAdd.description.value,
        objective:   formAdd.objective.value,
        difficulty:  formAdd.difficulty.value
      };
      fetch('/api/exercises', {
        method: 'POST',
        credentials:'same-origin',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify(data)
      })
      .then(r => { if(!r.ok) throw new Error('Errore creazione'); return r.json(); })
      .then(() => {
        formAdd.reset();
        formAdd.style.display = 'none';
        loadExercises();
      })
      .catch(e => alert(e.message));
    });
  
    btnCancelAdd.addEventListener('click', () => {
      formAdd.reset();
      formAdd.style.display = 'none';
    });
  
    btnToggleForm.addEventListener('click', () => {
      formAdd.style.display = formAdd.style.display === 'none' ? 'flex' : 'none';
    });
  
    // 4) Filtri
    btnFilter.addEventListener('click', loadExercises);
    btnClear .addEventListener('click', () => {
      filterMuscle.value = '';
      filterObjective.value = '';
      filterDifficulty.value = '';
      loadExercises();
    });
  
    // 5) Delete
    function deleteExercise(id) {
      if (!confirm('Confermi eliminazione?')) return;
      fetch(`/api/exercises/${id}`, {
        method:'DELETE', credentials:'same-origin'
      })
      .then(r => { if(!r.ok) throw new Error('Errore eliminazione'); })
      .then(loadExercises)
      .catch(e => alert(e.message));
    }
  
    // 6) Edit: apri modal
    function openEditModal(id) {
      const ex = currentExercises.find(x => x.id == id);
      formEdit.dataset.id    = id;
      editNameInput.value    = ex.name;
      editDescInput.value    = ex.description;
      editObjSelect.value    = ex.objective;
      editDiffSelect.value   = ex.difficulty;
      editModal.show();
    }
  
    // 7) Submit edit
    formEdit.addEventListener('submit', e => {
      e.preventDefault();
      const id = formEdit.dataset.id;
      const data = {
        name:        editNameInput.value,
        description: editDescInput.value,
        objective:   editObjSelect.value,
        difficulty:  editDiffSelect.value
      };
      fetch(`/api/exercises/${id}`, {
        method:'PUT',
        credentials:'same-origin',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify(data)
      })
      .then(r => { if(!r.ok) throw new Error('Errore salvataggio'); })
      .then(() => {
        editModal.hide();
        loadExercises();
      })
      .catch(e => alert(e.message));
    });
  });
  