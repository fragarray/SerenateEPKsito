/**
 * assets/js/lang.js
 * Language toggle with localStorage persistence and accessibility support.
 * Updated for semantic markup, ARIA and skip-link support.
 */

/**
 * Switch the page language.
 * @param {string} lang - 'it' or 'en'
 */
export function setLang(lang) {
  // Persist choice
  try { localStorage.setItem('lang', lang); } catch (_) {}

  // Update <html lang>
  document.documentElement.lang = lang;

  // Show/hide data-lang elements (remove leftover inline style set at build-time)
  document.querySelectorAll('[data-lang]').forEach(el => {
    const match = el.dataset.lang === lang;
    el.hidden = !match;
    // Remove legacy inline display:none so CSS isn't fighting JS
    if (el.style.display) el.style.display = '';
  });

  // Update lang buttons: active class + aria-current
  document.querySelectorAll('.lang-btn').forEach(btn => {
    const isActive = btn.dataset.langTarget === lang;
    btn.classList.toggle('active', isActive);
    btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
    if (isActive) {
      btn.setAttribute('aria-current', 'true');
    } else {
      btn.removeAttribute('aria-current');
    }
  });
}

/** Initialise on DOMContentLoaded */
function init() {
  // Read persisted language, default to 'it'
  let lang = 'it';
  try {
    const stored = localStorage.getItem('lang');
    if (stored === 'it' || stored === 'en') lang = stored;
  } catch (_) {}

  // Wire up buttons using data-lang-target attribute
  document.querySelectorAll('.lang-btn').forEach(btn => {
    // Derive target from text content if attribute not set
    if (!btn.dataset.langTarget) {
      btn.dataset.langTarget = btn.textContent.trim().toLowerCase().startsWith('ita') ? 'it' : 'en';
    }
    btn.addEventListener('click', () => setLang(btn.dataset.langTarget));
  });

  setLang(lang);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
