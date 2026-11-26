(() => {
  const names = { py: 'Python', python: 'Python', js: 'JavaScript', javascript: 'JavaScript',
    sh: 'Shell', bash: 'Bash', json: 'JSON', html: 'HTML', css: 'CSS', sql: 'SQL' };
  function decorate(root) {
    for (const code of root.querySelectorAll('pre > code')) {
      const pre = code.parentElement;
      const wrapper = code.closest('[class*="language-"]');
      const lang = wrapper?.className.match(/(?:^|\s)language-([^\s]+)/)?.[1];
      const bar = document.createElement('div');
      bar.className = 'code-bar';
      const output = /^(txt|text|plaintext|output|console)$/.test(lang);
      bar.textContent = output ? (lang === 'output' || lang === 'console' ? '실행 결과' : '텍스트') : (names[lang] || lang || '코드');
      if (!output) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'copy-code';
        button.setAttribute('aria-label', '코드 복사');
        button.title = '코드 복사';
        button.innerHTML = `<svg viewBox="0 0 24 24" width="17" height="17" fill="none"
          stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <g class="copy-sheets"><rect x="8" y="8" width="12" height="13" rx="2"/>
          <path d="M15 5V4a1 1 0 0 0-1-1H5a2 2 0 0 0-2 2v10a1 1 0 0 0 1 1h1"/></g>
          <path class="copy-check" d="m5 12 4 4L19 6"/></svg>`;
        const status = document.createElement('span');
        status.className = 'copy-feedback';
        status.setAttribute('role', 'status');
        let resetTimer;
        button.addEventListener('click', async () => {
          try {
            await navigator.clipboard.writeText(code.textContent);
            button.classList.add('copied');
            status.textContent = '복사됨';
          } catch {
            button.classList.remove('copied');
            status.textContent = '복사 실패';
          }
          clearTimeout(resetTimer);
          resetTimer = setTimeout(() => {
            button.classList.remove('copied');
            status.textContent = '';
          }, 2000);
        });
        bar.append(status, button);
      }
      pre.before(bar);
    }
  }
  document.querySelectorAll('.post-body').forEach(decorate);
  document.addEventListener('article-unlocked', event => decorate(event.target));
})();
