// ── Tab switching ──
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');

    document.querySelectorAll('.worksheet').forEach(ws => ws.classList.add('hidden'));
    document.getElementById('ws-' + tab.dataset.tab).classList.remove('hidden');

    // Close all hints when switching tabs
    document.querySelectorAll('.problem').forEach(p => p.classList.remove('hinting'));
  });
});

// ── Click a problem → toggle its overlay hint ──
document.querySelectorAll('.problem').forEach(problem => {
  problem.addEventListener('click', () => {
    const wasHinting = problem.classList.contains('hinting');

    // Close other hints on the same worksheet
    problem.closest('.worksheet-paper')
      .querySelectorAll('.problem.hinting')
      .forEach(p => p.classList.remove('hinting'));

    // Toggle this one
    if (!wasHinting) {
      problem.classList.add('hinting');
    }
  });
});
