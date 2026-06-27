document.querySelectorAll('.day-check').forEach(cb => {
  cb.addEventListener('change', function () {
    toggleTimeInput(this.dataset.day);
  });
});

function toggleTimeInput(day) {
  const cb = document.getElementById('day_' + day);
  const timeInput = document.getElementById('time_' + day);
  if (!cb || !timeInput) return;
  timeInput.classList.toggle('d-none', !cb.checked);
  timeInput.required = cb.checked;
}

document.getElementById('add-stop')?.addEventListener('click', function () {
  const container = document.getElementById('stops-container');
  if (!container) return;
  const stopCount = container.querySelectorAll('input').length + 1;
  const input = document.createElement('input');
  input.type = 'text';
  input.name = 'stops';
  input.className = 'form-control mb-2';
  input.placeholder = `Stop ${stopCount} – place name`;
  container.appendChild(input);
});

// Create/Edit tour custom validator
function validateTourForm(form) {
  // meeting point OR new_meetpoint (but not both empty)
  const select = form.querySelector('select[name="meetpoint_place_id"]');
  const input = form.querySelector('input[name="new_meetpoint"]');
  const hasSel = select && select.value.trim() !== '';
  const hasNew = input && input.value.trim() !== '';
  if (!hasSel && !hasNew) return { ok: false, message: 'Select or enter meeting point', field: select || input };
  if (hasSel && hasNew) return { ok: false, message: 'Choose only one meeting point', field: select };

  // schedule: at least one day and time for checked days
  const dayChecks = form.querySelectorAll('input[name="schedule_days"]');
  const tourScheduleContainer = form.querySelector('.tour-schedule-container');
  const anyDay = [...dayChecks].some(cb => cb.checked);
  if (!anyDay) return { ok: false, message: 'Select at least one day', field: tourScheduleContainer };

  // stops: at least 4 filled (also check whitespace)
  const stops = form.querySelectorAll('input[name="stops"]');
  const filled = [...stops].filter(s => s.value.trim() !== '').length;
  if (filled < 4) return { ok: false, message: 'Enter at least 4 stops', field: stops[0] };

  // On create form, require the 5 promotional photos
  const action = form.getAttribute('action') || '';
  if (action.includes('create_tour')) {
    for (let i = 1; i <= 5; i++) {
      const ph = form.querySelector(`input[name="photo_${i}"]`);
      if (ph && ph.files && ph.files.length === 0) {
        return { ok: false, message: `Upload Photo ${i}`, field: ph };
      }
    }
  }

  return { ok: true };
}

// Attach page-specific validation (relying on global utility in script.js)
attachFormValidation('form[action*="create_tour"], form[action*="edit_tour"]', validateTourForm);
