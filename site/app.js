// ── Tab switching ──
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');

    document.querySelectorAll('.worksheet').forEach(ws => ws.classList.add('hidden'));
    document.getElementById('ws-' + tab.dataset.tab).classList.remove('hidden');

    // Turn off all projected hints
    document.querySelectorAll('.row').forEach(r => r.classList.remove('active'));
  });
});

// ── Tap a problem row → toggle projected hint in its white space ──
document.querySelectorAll('.row').forEach(row => {
  row.addEventListener('click', () => {
    const wasActive = row.classList.contains('active');

    // Turn off other hints on this page
    row.closest('.page')
      .querySelectorAll('.row.active')
      .forEach(r => r.classList.remove('active'));

    if (!wasActive) {
      row.classList.add('active');
    }
  });
});
