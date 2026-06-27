// Week start-date reload and navigate to the anchor
document.getElementById('filter-week-start')?.addEventListener('change', function () {
  if (!this.value) return;

  const url = new URL(window.location.href);
  url.searchParams.set('start', this.value);
  url.hash = 'tours-anchor';
  window.location.href = url.toString();
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

// Scroll to tours-anchor on load if start arg exists
window.addEventListener('DOMContentLoaded', () => {
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has('start')) {
    document.getElementById('tours-anchor')?.scrollIntoView({ behavior: 'auto' });
  }
});
