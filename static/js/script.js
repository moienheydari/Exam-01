/* ==========================================
   Space Tours – script.js
   All event listeners are guarded with ?. so
   missing elements on other pages do not throw.
   ========================================== */


// ---- INDEX PAGE: Filter logic ----

// ---- INDEX PAGE: Filter logic ----

// Week start-date picker: compute end date (start + 6 days) and reload
document.getElementById('filter-week-start')?.addEventListener('change', function () {
  if (!this.value) return;

  // Compute end date = start + 6 days
  const start = new Date(this.value);
  start.setHours(12); // avoid DST edge-cases
  const end = new Date(start);
  end.setDate(end.getDate() + 6);

  // Update readonly end input for instant visual feedback
  const endInput = document.getElementById('filter-week-end');
  if (endInput) endInput.value = end.toISOString().slice(0, 10);

  // Navigate to the new week with anchor
  const url = new URL(window.location.href);
  url.searchParams.set('start', this.value);
  url.hash = 'tours-anchor';
  window.location.href = url.toString();
});

// Prevent user from typing in the readonly end-date field
document.getElementById('filter-week-end')?.addEventListener('click', function () {
  document.getElementById('filter-week-start')?.focus();
});

// Duration slider: update label + filter cards
document.getElementById('filter-duration')?.addEventListener('input', function () {
  updateDurLabel(parseInt(this.value));
  applyFilters();
});

function updateDurLabel(val) {
  const display = document.getElementById('dur-display');
  if (!display) return;
  display.textContent = val === 0 ? 'Any' : `\u2264 ${val} min`;
}

// Language checkboxes: filter cards + update button label
document.querySelectorAll('.lang-check').forEach(cb => {
  cb.addEventListener('change', function () {
    updateLangLabel();
    applyFilters();
  });
});

function updateLangLabel() {
  const checked = [...document.querySelectorAll('.lang-check:checked')];
  const btn = document.getElementById('lang-btn-label');
  if (!btn) return;
  if (checked.length === 0) {
    btn.textContent = 'Languages';
  } else if (checked.length === 1) {
    btn.textContent = checked[0].dataset.label;
  } else {
    btn.textContent = `Languages (${checked.length})`;
  }
}

function applyFilters() {
  const durVal = parseInt(document.getElementById('filter-duration')?.value || 0);
  const checkedLangs = [...document.querySelectorAll('.lang-check:checked')]
    .map(cb => cb.value.toLowerCase());

  document.querySelectorAll('.tour-card').forEach(card => {
    const cardLang = card.dataset.language?.toLowerCase() || '';
    const cardDur = parseInt(card.dataset.duration) || 0;

    let show = true;
    // Duration: 0 = no filter; otherwise hide cards exceeding slider max
    if (durVal > 0 && cardDur > durVal) show = false;
    // Language: if any checked, card must match one
    if (checkedLangs.length > 0 && !checkedLangs.includes(cardLang)) show = false;

    card.classList.toggle('d-none', !show);
  });
}

// Clear all filters
document.getElementById('clear-filters-btn')?.addEventListener('click', function () {
  const slider = document.getElementById('filter-duration');
  if (slider) slider.value = 0;
  updateDurLabel(0);
  document.querySelectorAll('.lang-check').forEach(cb => cb.checked = false);
  updateLangLabel();
  applyFilters();
});


// ---- TOUR BOOKING PAGE: Date select → populate hidden time ----

document.getElementById('date-select')?.addEventListener('change', function () {
  const opt = this.options[this.selectedIndex];
  const timeField = document.getElementById('selected-time');
  if (timeField) timeField.value = opt.dataset.time || '';
});

// Person count → show/hide additional people inputs
function updateAdditionalPeople() {
  const select = document.getElementById('person-count');
  if (!select) return;
  const count = parseInt(select.value) || 1;
  [1, 2, 3].forEach(i => {
    const el = document.getElementById('addit-' + i);
    if (!el) return;
    const hide = i >= count; // show addit-i when count > i
    el.classList.toggle('d-none', hide);
    const input = el.querySelector('input');
    if (input) {
      input.required = !hide;
      if (hide) {
        input.value = ''; // clear value when depopulating/hiding
      }
    }
  });
}

document.getElementById('person-count')?.addEventListener('change', updateAdditionalPeople);


// ---- REGISTER PAGE: Show guide-only fields ----

function validateLanguages() {
  const guideFields = document.getElementById('guide-fields');
  const checkboxes = [...document.querySelectorAll('input[name="languages"]')];
  if (!guideFields || guideFields.classList.contains('d-none')) {
    checkboxes.forEach(cb => {
      cb.required = false;
      clearFieldError(cb);
    });
    return;
  }

  const checkedCount = checkboxes.filter(cb => cb.checked).length;
  if (checkedCount > 0) {
    checkboxes.forEach(cb => {
      cb.required = false;
      clearFieldError(cb);
      clearFieldError(guideFields);
    });
  } else {
    checkboxes.forEach(cb => cb.required = true);
    // show the error under the whole guide-fields block (better placement)
    if (guideFields) {
      clearFieldError(guideFields);
      showFieldError(guideFields, 'Please choose at least one language to proceed.');
    } else if (checkboxes[0]) {
      showFieldError(checkboxes[0], 'Please choose at least one language to proceed.');
    }
  }
}

document.querySelectorAll('input[name="user_type"]').forEach(radio => {
  radio.addEventListener('change', function () {
    const guideSection = document.getElementById('guide-fields');
    if (guideSection) {
      guideSection.classList.toggle('d-none', this.value !== 'guide');
      validateLanguages();
    }

    // clear any inline validation messages in the containing form
    const guideFields = document.getElementById('guide-fields');
    clearFieldError(guideFields);
    const form = radio.closest('form');
    if (form) clearValidation(form);
  });
});

document.querySelectorAll('input[name="languages"]').forEach(cb => {
  cb.addEventListener('change', validateLanguages);
});


// ---- CREATE/EDIT TOUR: Toggle time input when day checkbox is checked ----

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


// ---- CREATE TOUR: Add stop button (like example's add-subject) ----

document.getElementById('add-stop')?.addEventListener('click', function () {
  const container = document.getElementById('stops-container');
  if (!container) return;
  const stopCount = container.querySelectorAll('input').length + 1;
  const input = document.createElement('input');
  input.type = 'text';
  input.name = 'stops';
  input.className = 'form-control mb-2';
  input.placeholder = `Stop ${stopCount} – place name`;
  input.required = stopCount <= 4; // first 4 are required
  container.appendChild(input);
});

// Scroll to tours-anchor on load if start arg exists
window.addEventListener('DOMContentLoaded', () => {
  const urlParams = new URLSearchParams(window.location.search);
  // In index, if the URL has a 'start' parameter, scroll to the tours section
  if (urlParams.has('start')) {
    document.getElementById('tours-anchor')?.scrollIntoView({ behavior: 'auto' });
  }
  updateAdditionalPeople();
});


/* -- FORM VALIDATION -- */

function showFirstInvalid(form) {
  const elements = [...form.querySelectorAll('input, textarea, select')];
  const firstInvalid = elements.find(el => !el.checkValidity());
  if (firstInvalid) {
    const msg = firstInvalid.validationMessage || 'Please fill out this field.';
    showFieldError(firstInvalid, msg);
    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
    try { firstInvalid.focus(); } catch (e) { }
  }
}

function clearFieldError(field) {
  if (!field) return;
  field.classList.remove('is-invalid');
  const fb = field.nextElementSibling;
  if (fb && fb.classList && fb.classList.contains('invalid-feedback')) {
    fb.textContent = '';
    fb.classList.remove('d-block');
  }
}

function showFieldError(el, msg) {
  if (!el) return;
  if (NodeList.prototype.isPrototypeOf(el) || Array.isArray(el)) el = el[0];
  clearFieldError(el);
  el.classList.add('is-invalid');
  let fb = el.nextElementSibling;
  if (!fb || !(fb.classList && fb.classList.contains('invalid-feedback'))) {
    fb = document.createElement('div');
    fb.className = 'invalid-feedback d-block';
    if (el.parentNode) el.parentNode.insertBefore(fb, el.nextSibling);
  } else {
    fb.classList.add('d-block');
  }
  fb.textContent = msg || 'Invalid field.';
}

function clearValidation(form) {
  form.querySelectorAll('input, textarea, select').forEach(el => {
    clearFieldError(el);
  });
}

// Generic submit handler: validate using HTML5 constraints + custom rules
function attachFormValidation(formSelector, customValidator) {
  document.querySelectorAll(formSelector).forEach(form => {
    form.addEventListener('submit', function (e) {
      clearValidation(form);

      // run HTML5 built-in checks first
      if (!form.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
        showFirstInvalid(form);
        return;
      }

      // run custom validator if provided (returns { ok: bool, message?: string, field?: element })
      console.log("Custom validator check for form:", form);
      if (customValidator) {
        console.log("Running custom validator for form:", form);
        const res = customValidator(form);
        console.log("Custom validator result:", res);
        if (!res.ok) {
          e.preventDefault();
          e.stopPropagation();
          if (res.field) {
            showFieldError(res.field, res.message || 'Invalid');
            try { res.field.focus(); } catch (e) { }
          } else {
            // show first invalid
            showFirstInvalid(form);
          }
        }
      }

    });
  });

}

// ------- Page-specific custom validators -------

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
  const anyDay = [...dayChecks].some(cb => cb.checked);
  if (!anyDay) return { ok: false, message: 'Select at least one day', field: dayChecks[0] };
  const dayOrder = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  for (const d of dayOrder) {
    const cb = form.querySelector(`input[value="${d}"][name="schedule_days"]`);
    const t = form.querySelector(`#time_${d}`);
    if (cb && cb.checked && t && !t.value) return { ok: false, message: `Enter time for ${d}`, field: t };
  }

  // stops: at least 4 filled
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


// Report tour validator
function validateReportForm(form) {
  const actual = form.querySelector('#actual_part_count');
  if (!actual) return { ok: true };
  const v = parseInt(actual.value);
  if (!actual.value) return { ok: false, message: 'Enter actual participant count', field: actual };
  if (isNaN(v) || v < 0) return { ok: false, message: 'Invalid count', field: actual };
  return { ok: true };
}

// Register/login simple validators (could be extended)
function validateAuthForm(form) { return { ok: true }; }

// Attach validators
attachFormValidation('form[action*="create_tour"], form[action*="edit_tour"]', validateTourForm);
attachFormValidation('form[action*="book"]');
attachFormValidation('form[action*="report_tour"]', validateReportForm);
attachFormValidation('form[action*="signup"], form[action*="authenticate"]', validateAuthForm);

