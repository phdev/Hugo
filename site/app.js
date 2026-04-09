// ── Tab switching ──
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    document.querySelectorAll('.paper').forEach(p => p.classList.add('hidden'));
    document.getElementById('ws-' + tab.dataset.tab).classList.remove('hidden');
    document.querySelectorAll('.problem-block').forEach(b => b.classList.remove('active'));
  });
});

// ── Help button press-and-hold interaction ──
const DWELL_MS = 800; // must hold for this long to trigger

document.querySelectorAll('.help-btn').forEach(btn => {
  let pressStart = null;
  let animFrame = null;
  const block = btn.closest('.problem-block');

  function startPress(e) {
    e.preventDefault();
    e.stopPropagation();

    // If already active, dismiss on tap
    if (block.classList.contains('active')) {
      block.classList.remove('active');
      return;
    }

    pressStart = performance.now();
    btn.classList.add('pressing');
    animate();
  }

  function animate() {
    if (!pressStart) return;
    const elapsed = performance.now() - pressStart;
    const progress = Math.min(elapsed / DWELL_MS, 1);
    btn.style.setProperty('--press', progress.toFixed(3));

    if (progress >= 1) {
      // Triggered!
      trigger();
      return;
    }
    animFrame = requestAnimationFrame(animate);
  }

  function trigger() {
    cancelPress();
    // Close other hints on this page
    block.closest('.paper')
      .querySelectorAll('.problem-block.active')
      .forEach(b => b.classList.remove('active'));
    block.classList.add('active');
  }

  function cancelPress() {
    pressStart = null;
    if (animFrame) cancelAnimationFrame(animFrame);
    animFrame = null;
    btn.classList.remove('pressing');
    btn.style.setProperty('--press', '0');
  }

  // Mouse events
  btn.addEventListener('mousedown', startPress);
  btn.addEventListener('mouseup', cancelPress);
  btn.addEventListener('mouseleave', cancelPress);

  // Touch events
  btn.addEventListener('touchstart', startPress, { passive: false });
  btn.addEventListener('touchend', cancelPress);
  btn.addEventListener('touchcancel', cancelPress);
});
