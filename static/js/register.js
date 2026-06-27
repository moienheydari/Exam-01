document.querySelectorAll('input[name="user_type"]').forEach(radio => {
  radio.addEventListener('change', function () {
    const guideSection = document.getElementById('guide-fields');
    if (guideSection) {
      guideSection.classList.toggle('d-none', this.value !== 'guide');
    }

    // clear any inline validation messages in the containing form
    const guideFields = document.getElementById('guide-fields');
    clearFieldError(guideFields);
    const form = radio.closest('form');
    if (form) clearValidation(form);
  });
});

document.querySelectorAll('input[name="languages"]').forEach(cb => {
  cb.addEventListener('change', function () {
    const guideFields = document.getElementById('guide-fields');
    if (guideFields) {
      clearFieldError(guideFields);
    }
  });
});

// Auth validator for signup checking languages if guide
function validateAuthForm(form) {
  const guideFields = document.getElementById('guide-fields');
  if (guideFields && !guideFields.classList.contains('d-none')) {
    const checkboxes = [...document.querySelectorAll('input[name="languages"]')];
    const checkedCount = checkboxes.filter(cb => cb.checked).length;
    if (checkedCount === 0) {
      return {
        ok: false,
        message: 'Please choose at least one language to proceed.',
        field: guideFields
      };
    }
  }
  return { ok: true };
}

// Attach page-specific validation (relying on global utility in validation.js)
attachFormValidation('form[action*="signup"]', validateAuthForm);
