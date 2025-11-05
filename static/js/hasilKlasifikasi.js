document.addEventListener('DOMContentLoaded', function () {
  // navigation buttons
  const navItems = document.querySelectorAll('#question-nav .nav-item');
  const questions = document.querySelectorAll('#questions-list article');

  function clearNavActive() {
    navItems.forEach((b) => b.classList.remove('bg-blue-600', 'text-white'));
    navItems.forEach((b) => b.classList.add('bg-blue-50', 'text-blue-700'));
  }

  function setActive(index) {
    clearNavActive();
    const btn = navItems[index];
    if (!btn) return;
    btn.classList.remove('bg-blue-50', 'text-blue-700');
    btn.classList.add('bg-blue-600', 'text-white');

    const target = document.getElementById('question-' + index);
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'center' });
      // brief flash
      target.classList.add('ring-4', 'ring-blue-200');
      setTimeout(() => target.classList.remove('ring-4', 'ring-blue-200'), 800);
    }
  }

  navItems.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const idx = Number(btn.getAttribute('data-index'));
      setActive(idx);
    });
  });

  // default active first
  if (navItems.length) setActive(0);

  // change-select handlers
  const selects = document.querySelectorAll('.change-select');
  selects.forEach((sel, i) => {
    sel.addEventListener('change', () => {
      const val = sel.value;
      const article = sel.closest('article');
      if (!article) return;
      const labelEl = article.querySelector('.current-label');
      if (labelEl && val) labelEl.textContent = val;

      // visual: change color of right box based on selection
      const box = sel.closest('div.bg-blue-600');
      if (box) {
        // remove previous bg classes if any
        // keep simple: switch bg to different shades depending on label
        const map = {
          C1: 'bg-blue-600',
          C2: 'bg-indigo-600',
          C3: 'bg-teal-600',
          C4: 'bg-amber-600',
          C5: 'bg-emerald-600',
          C6: 'bg-violet-600',
        };
        // remove known classes then add
        Object.values(map).forEach((c) => box.classList.remove(c));
        const newCls = map[val] || 'bg-blue-600';
        box.classList.add(newCls);
      }

      // TODO: send AJAX to server to save change if API exists
    });
  });

  // Download button: ensure it opens in new tab if it's a blob/file link
  const downloadBtn = document.getElementById('download-btn');
  if (downloadBtn) {
    downloadBtn.addEventListener('click', (e) => {
      // if href is '#', prevent
      if (downloadBtn.getAttribute('href') === '#') e.preventDefault();
    });
  }
});
