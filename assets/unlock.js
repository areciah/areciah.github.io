const form = document.getElementById('unlock-form');
const statusText = document.getElementById('unlock-status');
const password = document.getElementById('post-password');
const payload = JSON.parse(document.getElementById('protected-data').textContent);
const bytes = encoded => Uint8Array.from(atob(encoded), c => c.charCodeAt(0));

form.addEventListener('submit', async event => {
  event.preventDefault();
  const button = form.querySelector('button');
  button.disabled = true;
  statusText.textContent = '확인 중…';
  try {
    const material = await crypto.subtle.importKey('raw', new TextEncoder().encode(password.value),
      'PBKDF2', false, ['deriveKey']);
    const key = await crypto.subtle.deriveKey({
      name: 'PBKDF2', hash: 'SHA-256', salt: bytes(payload.salt), iterations: payload.iterations
    }, material, { name: 'AES-GCM', length: 256 }, false, ['decrypt']);
    const plaintext = await crypto.subtle.decrypt({name: 'AES-GCM', iv: bytes(payload.nonce)},
      key, bytes(payload.ciphertext));
    const body = document.getElementById('protected-body');
    body.innerHTML = new TextDecoder().decode(plaintext);
    body.dispatchEvent(new CustomEvent('article-unlocked', { bubbles: true }));
    body.hidden = false;
    password.value = '';
    form.hidden = true;
    body.focus();
  } catch {
    statusText.textContent = '본문을 열 수 없습니다. 비밀번호를 확인해 주세요.';
    password.focus();
  } finally {
    button.disabled = false;
  }
});
