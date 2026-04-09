// ── Sensor FOV toggle ──
document.getElementById('fov-check').addEventListener('change', (e) => {
  document.getElementById('fov-overlay').classList.toggle('visible', e.target.checked);
});

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

// ── Help button interaction ──
// Short tap: toggle hint immediately.
// Long press (800ms): expanding animation then trigger.
// This mirrors the real device where the camera detects a
// sustained finger press, but on the web a tap also works.
const DWELL_MS = 800;

document.querySelectorAll('.help-btn').forEach(btn => {
  let pressStart = null;
  let animFrame = null;
  let triggered = false;
  const block = btn.closest('.problem-block');

  function activate() {
    // Close other hints on this page
    block.closest('.paper')
      .querySelectorAll('.problem-block.active')
      .forEach(b => b.classList.remove('active'));
    block.classList.add('active');
  }

  function deactivate() {
    block.classList.remove('active');
  }

  function startPress(e) {
    e.preventDefault();
    e.stopPropagation();
    triggered = false;
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
      triggered = true;
      cleanupPress();
      if (block.classList.contains('active')) {
        deactivate();
      } else {
        activate();
      }
      return;
    }
    animFrame = requestAnimationFrame(animate);
  }

  function cleanupPress() {
    pressStart = null;
    if (animFrame) cancelAnimationFrame(animFrame);
    animFrame = null;
    btn.classList.remove('pressing');
    btn.style.setProperty('--press', '0');
  }

  function endPress(e) {
    e.preventDefault();
    e.stopPropagation();
    cleanupPress();
    // If the long-press already triggered, don't double-toggle
    if (triggered) return;
    // Short tap — toggle immediately
    if (block.classList.contains('active')) {
      deactivate();
    } else {
      activate();
    }
  }

  // Mouse
  btn.addEventListener('mousedown', startPress);
  btn.addEventListener('mouseup', endPress);
  btn.addEventListener('mouseleave', () => cleanupPress());

  // Touch
  btn.addEventListener('touchstart', startPress, { passive: false });
  btn.addEventListener('touchend', endPress, { passive: false });
  btn.addEventListener('touchcancel', () => cleanupPress());
});
