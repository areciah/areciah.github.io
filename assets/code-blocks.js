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
        button.textContent = '복사';
        button.addEventListener('click', async () => {
          try {
            await navigator.clipboard.writeText(code.textContent);
            button.textContent = '복사됨';
          } catch {
            button.textContent = '복사 실패';
          }
        });
        bar.append(button);
      }
      pre.before(bar);
    }
  }
  document.querySelectorAll('.post-body').forEach(decorate);
  document.addEventListener('article-unlocked', event => decorate(event.target));
})();
