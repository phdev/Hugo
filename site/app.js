// ── Tab switching ──
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');

    const target = tab.dataset.tab;
    document.querySelectorAll('.worksheet').forEach(ws => ws.classList.add('hidden'));
    document.getElementById('ws-' + target).classList.remove('hidden');

    // Close all open hints when switching tabs
    document.querySelectorAll('.hint-zone').forEach(hz => hz.classList.remove('visible'));
  });
});

// ── Problem click → toggle hint ──
document.querySelectorAll('.problem').forEach(problem => {
  problem.addEventListener('click', () => {
    const hintId = 'hint-' + problem.dataset.hint;
    const hintZone = document.getElementById(hintId);
    if (!hintZone) return;

    // Close other hints in the same worksheet
    const worksheet = problem.closest('.worksheet-paper');
    worksheet.querySelectorAll('.hint-zone.visible').forEach(hz => {
      if (hz.id !== hintId) hz.classList.remove('visible');
    });

    hintZone.classList.toggle('visible');
  });
});
