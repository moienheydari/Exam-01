// Update time field based on selected date
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

window.addEventListener('DOMContentLoaded', () => {
  updateAdditionalPeople();
});

// Simple auth validator for login
function validateAuthForm(form) {
  return { ok: true };
}

// Attach page-specific validation (relying on global utility in validation.js)
attachFormValidation('form[action*="book"]', validateAuthForm);