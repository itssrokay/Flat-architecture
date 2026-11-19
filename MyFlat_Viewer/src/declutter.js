// V1.4: the "More" menu in the top bar (views, measuring, tools). Buttons keep their ids, so main.js still drives them.
const btn = document.getElementById('moreBtn'), menu = document.getElementById('moreMenu');
function place() {
  const r = btn.getBoundingClientRect();
  menu.style.top = (r.bottom + 6) + 'px';
  menu.style.right = Math.max(8, innerWidth - r.right) + 'px';
}
function set(open) {
  menu.classList.toggle('hidden', !open); btn.classList.toggle('on', open); btn.setAttribute('aria-expanded', String(open));
  if (open) place();
}
btn.addEventListener('click', (e) => { e.stopPropagation(); set(menu.classList.contains('hidden')); });
document.addEventListener('pointerdown', (e) => {
  if (!menu.classList.contains('hidden') && !menu.contains(e.target) && !btn.contains(e.target)) set(false);
});
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') set(false); });
menu.addEventListener('click', (e) => { if (e.target.closest('#viewButtons button, #resetBtn, #immBtn')) set(false); });
addEventListener('resize', () => { if (!menu.classList.contains('hidden')) place(); });
