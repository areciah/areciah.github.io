(function () {
  const statusWord = document.querySelector('[data-hero-status]');
  const statusDots = document.querySelector('[data-hero-dots]');
  if (statusWord && statusDots) {
    const words = ['탐색 중', '분석 중', '기록 중'];
    const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
    let wordIndex = 0;
    let dotCount = 0;
    let timer;

    const start = () => {
      if (timer) return;
      statusDots.textContent = '';
      timer = window.setInterval(() => {
        if (dotCount === 3) {
          wordIndex = (wordIndex + 1) % words.length;
          dotCount = 0;
          statusWord.textContent = words[wordIndex];
        } else {
          dotCount += 1;
        }
        statusDots.textContent = '.'.repeat(dotCount);
      }, 520);
    };
    const stop = () => {
      window.clearInterval(timer);
      timer = undefined;
      wordIndex = 0;
      dotCount = 0;
      statusWord.textContent = words[0];
      statusDots.textContent = '...';
    };
    if (!motionPreference.matches) start();
    motionPreference.addEventListener('change', () => motionPreference.matches ? stop() : start());
  }

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
