const $ = (id) => document.getElementById(id);

$('example').onclick = () => {
  $('message').value = 'URGENT: Your Microsoft 365 password expires today. Verify immediately at http://192.0.2.10/login?password=reset';
  $('status').textContent = 'Example loaded. Click Analyze safely to review it.';
};

$('analyze').onclick = async () => {
  const text = $('message').value;
  $('status').textContent = 'Analyzing locally…';
  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Analysis failed');
    $('results').hidden = false;
    $('score').textContent = data.score + '/100';
    $('verdict').textContent = data.verdict + ' · ' + data.confidence + ' confidence';
    $('findings').innerHTML = data.findings.map(f => `<article class="finding ${f.severity}"><div><b>${escapeHtml(f.title)}</b><span class="pill">${escapeHtml(f.severity)} +${f.points}</span></div><p>${escapeHtml(f.detail)}</p></article>`).join('');
    $('recommendations').innerHTML = data.recommendations.map(r => `<li>${escapeHtml(r)}</li>`).join('');
    $('urls').innerHTML = data.urls.length ? data.urls.map(u => `<li><code>${escapeHtml(u)}</code></li>`).join('') : '<li>No URLs extracted.</li>';
    $('status').textContent = 'Analysis complete. Review the evidence before making a decision.';
  } catch (error) {
    $('status').textContent = error.message;
  }
};

function escapeHtml(value) {
  return value.replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
}
