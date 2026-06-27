// Simple auth validator for login
function validateAuthForm(form) {
  return { ok: true };
}

// Attach page-specific validation (relying on global utility in validation.js)
attachFormValidation('form[action*="report_tour"]', validateAuthForm);
