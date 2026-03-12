const topBody = document.querySelector('#topTable tbody');
const watchBody = document.querySelector('#watchTable tbody');
const trackBody = document.querySelector('#trackTable tbody');
const regime = document.getElementById('regime');
const preset = document.getElementById('preset');

preset.addEventListener('change', async () => {
  await fetch('/api/preset', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ preset: preset.value })
  });
});

function renderTop(rows) {
  topBody.innerHTML = rows.map(r => `<tr>
    <td>${r.symbol}</td>
    <td><span class="badge">${r.setup}</span></td>
    <td>${(+r.entry).toFixed(6)}</td>
    <td class="red">${(+r.sl).toFixed(6)}</td>
    <td class="green">${(+r.tp1).toFixed(6)} / ${( +r.tp2).toFixed(6)}</td>
    <td>${(+r.confidence).toFixed(1)}%</td>
    <td>${(+r.score).toFixed(1)}</td>
    <td>${(r.reasons || []).slice(0,3).join('<br/>')}</td>
  </tr>`).join('');
}

function renderWatch(rows) {
  watchBody.innerHTML = rows.map(r => `<tr>
    <td>${r.symbol}</td><td>${r.ret5.toFixed(2)}%</td><td>${r.ret15.toFixed(2)}%</td><td>${r.rsi.toFixed(1)}</td><td>${r.vr.toFixed(2)}</td>
  </tr>`).join('');
}

function renderTracked(rows) {
  trackBody.innerHTML = rows.map(r => `<tr>
    <td>${new Date(r.created_at).toLocaleTimeString()}</td><td>${r.symbol}</td><td>${r.setup}</td><td>${r.status}</td><td>${r.outcome}</td><td>${new Date(r.ttl_expires_at).toLocaleTimeString()}</td>
  </tr>`).join('');
}

function renderRegime(r) {
  regime.innerHTML = `
    <p><b>Regime:</b> ${r.market_regime}</p>
    <p><b>Volatility (ATR%):</b> ${r.avg_volatility}</p>
    <p><b>Active pumps:</b> ${r.active_pumps}</p>
    <p><b>Preset:</b> ${r.preset}</p>
  `;
}

async function tick() {
  const data = await (await fetch('/api/dashboard')).json();
  renderTop(data.top_signals);
  renderWatch(data.watchlist_near_trigger);
  renderTracked(data.tracked);
  renderRegime(data.regime);
}

setInterval(tick, 4000);
tick();
