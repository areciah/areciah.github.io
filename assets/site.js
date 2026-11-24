(function () {
  const printButton = document.querySelector('[data-print-cv]');
  if (printButton) printButton.addEventListener('click', () => window.print());

  const root = document.documentElement;
  if (!root.classList.contains('intro-pending')) return;

  const intro = document.getElementById('intro');
  const shell = document.querySelector('.site-shell');
  if (!intro || !shell) {
    root.classList.remove('intro-pending');
    return;
  }

  shell.inert = true;
  document.body.style.overflow = 'hidden';
  const finish = () => {
    root.classList.remove('intro-pending');
    shell.inert = false;
    document.body.style.overflow = '';
    try { sessionStorage.setItem('arecia-intro-archive-v5', '1'); } catch (e) { /* Storage may be unavailable. */ }
  };

  const duration = window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 500 : 4200;
  window.setTimeout(finish, duration);
}());
