/* ============================================================
   Workout Builder – gestione tabella dinamica
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  const tableBody  = document.querySelector('#exercise-table tbody');
  const addBtn     = document.getElementById('add-row');
  const payloadInp = document.getElementById('exercise_payload');

  /* ---------- helpers ---------- */
  const updateOrder = () => {
    tableBody.querySelectorAll('tr').forEach((tr, i) => {
      tr.querySelector('.order').textContent = i + 1;
    });
  };

  const makeExerciseSelect = (selected = null) => {
    const sel = document.createElement('select');
    sel.className = 'form-select exercise-id';
    exerciseOptions.forEach(ex => {
      sel.innerHTML +=
        `<option value="${ex.id}" ${ex.id == selected ? 'selected' : ''}>
           ${ex.name}
         </option>`;
    });
    return sel;
  };

  const makeMachineSelect = (selected = null) => {
    const sel = document.createElement('select');
    sel.className = 'form-select machine-id';
    sel.innerHTML = '<option value="">—</option>';
    machineOptions.forEach(m => {
      sel.innerHTML +=
        `<option value="${m.id}" ${m.id == selected ? 'selected' : ''}>
           ${m.name}
         </option>`;
    });
    return sel;
  };

  /* Abilita/disabilita campi in base ai flag dell'esercizio */
  const applyFlags = (tr, ex) => {
    const toggle = (cls, on) => {
      const input = tr.querySelector(cls);
      input.disabled = !on;
      if (!on) input.value = '';
    };

    toggle('.repetitions',  ex.requires_repetitions);
    toggle('.sets',         ex.requires_sets);
    toggle('.suggested_kg', ex.requires_weight);
    toggle('.exec_time_s',  ex.requires_duration);
    toggle('.rest_s',       ex.requires_rest);

    const mcSel = tr.querySelector('.machine-id');
    mcSel.disabled = !ex.requires_machine;
    if (!ex.requires_machine) mcSel.value = '';
  };

  /* ---------- crea riga ---------- */
  const addRow = (prefill = {}) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="order"></td>
      <td></td>
      <td></td>
      <td><input type="number" class="form-control repetitions"  min="0"></td>
      <td><input type="number" class="form-control sets"         min="0"></td>
      <td><input type="number" class="form-control suggested_kg" min="0" step="0.1"></td>
      <td><input type="number" class="form-control exec_time_s"  min="0"></td>
      <td><input type="number" class="form-control rest_s"       min="0"></td>
      <td class="text-center">
        <button type="button" class="btn btn-sm btn-outline-danger remove-row">&times;</button>
      </td>`;

    /* select esercizio + listener */
    const exSel = makeExerciseSelect(prefill.exercise_id);
    tr.children[1].appendChild(exSel);

    /* select macchinario */
    const machineSel = makeMachineSelect(prefill.machine_id);
    tr.children[2].appendChild(machineSel);

    exSel.addEventListener('change', () => {
      const ex = exerciseOptions.find(o => o.id == exSel.value);
      applyFlags(tr, ex);
    });

    /* pre-compila campi se siamo in edit */
    if (prefill.repetitions)  tr.querySelector('.repetitions').value   = prefill.repetitions;
    if (prefill.sets)         tr.querySelector('.sets').value          = prefill.sets;
    if (prefill.suggested_kg) tr.querySelector('.suggested_kg').value  = prefill.suggested_kg;
    if (prefill.exec_time_s)  tr.querySelector('.exec_time_s').value   = prefill.exec_time_s;
    if (prefill.rest_s)       tr.querySelector('.rest_s').value        = prefill.rest_s;

    tableBody.appendChild(tr);
    updateOrder();

    /* imposta flag iniziali */
    const exInit = exerciseOptions.find(o => o.id == exSel.value);
    if (exInit) applyFlags(tr, exInit);
  };

  /* ---------- event listeners ---------- */
  addBtn?.addEventListener('click', () => addRow());

  tableBody.addEventListener('click', e => {
    if (e.target.classList.contains('remove-row')) {
      e.target.closest('tr').remove();
      updateOrder();
    }
  });

  /* ---------- serializza prima del submit ---------- */
  window.buildPayload = () => {
    const rows = [...tableBody.querySelectorAll('tr')].map(tr => ({
      exercise_id  : tr.querySelector('.exercise-id').value,
      machine_id   : tr.querySelector('.machine-id').value     || null,
      repetitions  : tr.querySelector('.repetitions').value    || null,
      sets         : tr.querySelector('.sets').value           || null,
      suggested_kg : tr.querySelector('.suggested_kg').value   || null,
      exec_time_s  : tr.querySelector('.exec_time_s').value    || null,
      rest_s       : tr.querySelector('.rest_s').value         || null
    }));

    if (!rows.length) {
      alert('Devi inserire almeno un esercizio');
      return false;
    }

    payloadInp.value = JSON.stringify(rows);
    return true;
  };

  /* ------------------------------------------------------------------
     In modalità "edit" applica i flag agli esercizi pre‑caricati
     e blocca le select relative a esercizio/macchinario.
     In questo modo i campi non previsti dall'esercizio restano
     non modificabili, mentre per le nuove righe rimangono liberi.
  ------------------------------------------------------------------ */
  if (typeof IS_EDIT_MODE !== 'undefined' && IS_EDIT_MODE) {
    tableBody.querySelectorAll('tr').forEach(tr => {
      const exSel = tr.querySelector('.exercise-id');
      const mcSel = tr.querySelector('.machine-id');

      if (exSel) exSel.disabled = true;
      if (mcSel) mcSel.disabled = true;

      const exObj = exerciseOptions.find(o => o.id == exSel.value);
      if (exObj) applyFlags(tr, exObj);
    });
  }

  /* se ci sono esercizi, crea la prima riga all’apertura (solo modalità new) */
  if (!IS_EDIT_MODE && exerciseOptions && exerciseOptions.length && !tableBody.children.length) {
    addRow();
  }
});
