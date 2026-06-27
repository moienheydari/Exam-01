/* -- FORM VALIDATION -- */

// Show first invalid field with message
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

// Clear visual error states on a field
function clearFieldError(field) {
  if (!field) return;
  field.classList.remove('is-invalid');
  const fb = field.nextElementSibling;
  if (fb && fb.classList && fb.classList.contains('invalid-feedback')) {
    fb.textContent = '';
    fb.classList.remove('d-block');
  }
}

// Show visual validation error message under a field
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

// Clear all validation errors in a form
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
            res.field.scrollIntoView({ behavior: 'smooth', block: 'center' });
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
