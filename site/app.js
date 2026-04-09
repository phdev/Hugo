document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    document.querySelectorAll('.paper').forEach(p => p.classList.add('hidden'));
    document.getElementById('ws-' + tab.dataset.tab).classList.remove('hidden');
    document.querySelectorAll('.problem-block').forEach(b => b.classList.remove('active'));
  });
});

document.querySelectorAll('.problem-block').forEach(block => {
  block.addEventListener('click', () => {
    const wasActive = block.classList.contains('active');
    block.closest('.paper')
      .querySelectorAll('.problem-block.active')
      .forEach(b => b.classList.remove('active'));
    if (!wasActive) block.classList.add('active');
  });
});
