/** Category / IO viz client for the FastHTML shell.
 *  Loaded as /ui/viz_client.js — keep this out of the Python notebook.
 */
window.__stPlotlyDefaults = {
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: { family: 'ui-sans-serif, system-ui, sans-serif' },
  margin: { t: 48, r: 24, b: 48, l: 56 },
};
window.__stLegacyToFigure = function(payload) {
  const plot = (payload && payload.plot) || {};
  const kind = String((payload && payload.visualization) || plot.type || '').toLowerCase();
  if (kind === 'scatter' || plot.points) {
    const pts = plot.points || [];
    return {
      data: [{ type:'scatter', mode:'lines+markers', x: pts.map(p=>p.x), y: pts.map(p=>p.y),
               marker:{size:10}, line:{} }],
      layout: { title:'Solubility scatter', xaxis:{title: plot.x_label||'x'}, yaxis:{title: plot.y_label||'y'} }
    };
  }
  if (kind === 'heatmap' || plot.z != null) {
    return {
      data: [{ type:'heatmap', x: plot.x||[], y:(plot.y||[]).map(String), z: plot.z||[], colorscale:'YlGnBu' }],
      layout: { title:'Solubility heatmap', xaxis:{title: plot.x_label||'x'}, yaxis:{title: plot.y_label||'y'} }
    };
  }
  if (kind.includes('time') || plot.series) {
    const s = plot.series || [];
    return {
      data: [{ type:'scatter', mode:'lines+markers', x:s.map(p=>p.t), y:s.map(p=>p.y), marker:{size:9}, line:{width:3} }],
      layout: { title:'Solubility timeseries', xaxis:{title: plot.x_label||'t'}, yaxis:{title: plot.y_label||'y'} }
    };
  }
  return null;
};
window.__stFigureFromResponse = function(payload) {
  if (payload && payload.plotly && Array.isArray(payload.plotly.data)) {
    return { data: payload.plotly.data, layout: Object.assign({}, window.__stPlotlyDefaults, payload.plotly.layout||{}) };
  }
  const legacy = window.__stLegacyToFigure(payload||{});
  if (!legacy) return null;
  return { data: legacy.data, layout: Object.assign({}, window.__stPlotlyDefaults, legacy.layout||{}) };
};
window.__stShowIoView = function(iconId) {
  document.querySelectorAll('[id$="-view"]').forEach(el => el.classList.add('hidden'));
  const chat = document.getElementById('chat-view'); if (chat) chat.classList.add('hidden');
  const graph = document.getElementById('graph-view'); if (graph) graph.classList.add('hidden');
  const view = document.getElementById(iconId + '-view');
  if (view) view.classList.remove('hidden');
  document.querySelectorAll('[data-io-icon]').forEach(b => {
    b.classList.remove('ring-2','ring-primary','text-primary');
  });
  const t = document.querySelector('[data-io-icon="' + iconId + '"]');
  if (t) t.classList.add('ring-2','ring-primary','text-primary');
  document.querySelectorAll('[data-taskbar-icon]').forEach(b => {
    b.classList.remove('ring-2','ring-primary','text-primary');
  });
};
window.__stRenderSettingsPanel = function(chart, payload) {
  const panel = (payload && payload.panel) || {};
  const rows = panel.rows || [];
  const ready = Boolean(panel.ready);
  const note = panel.note || '';
  const title = panel.title || 'Settings';
  const badge = ready
    ? '<span class="badge badge-success badge-sm">ready</span>'
    : '<span class="badge badge-warning badge-sm">not ready</span>';
  const trs = rows.map(([k, v]) => (
    '<tr><td class="font-medium opacity-70 pr-4 py-1 align-top">' + String(k) +
    '</td><td class="py-1 break-all font-mono text-xs">' + String(v == null ? '' : v) +
    '</td></tr>'
  )).join('');
  chart.innerHTML =
    '<div class="p-4 overflow-auto h-full">' +
      '<div class="flex items-center gap-2 mb-2">' +
        '<h3 class="font-semibold text-lg">' + title + '</h3>' + badge +
      '</div>' +
      (note ? '<p class="text-sm opacity-70 mb-3">' + note + '</p>' : '') +
      '<div class="overflow-x-auto rounded-lg border border-base-300 bg-base-100/80">' +
        '<table class="table table-sm"><tbody>' + trs + '</tbody></table>' +
      '</div>' +
    '</div>';
};
window.renderIoVizFromPayload = async function(iconId, payload) {
  const view = document.getElementById(iconId + '-view');
  const chart = document.getElementById(iconId + '-chart');
  const status = document.getElementById(iconId + '-status');
  if (!view || !chart) return;
  window.__stShowIoView(iconId);
  if (status) { status.hidden = false; status.textContent = 'Rendering…'; status.classList.remove('text-error'); }
  if (chart.data) { try { Plotly.purge(chart); } catch (e) {} }
  try {
    if (payload && payload.status === 'error') throw new Error(payload.error || 'viz error');
    if (payload && payload.panel) {
      if (status) status.hidden = true;
      window.__stRenderSettingsPanel(chart, payload);
    } else {
      const fig = window.__stFigureFromResponse(payload || {});
      if (!fig) throw new Error('No plotly/plot payload');
      if (status) status.hidden = true;
      chart.innerHTML = '';
      await Plotly.newPlot(chart, fig.data, fig.layout, { responsive: true, displayModeBar: false });
      requestAnimationFrame(() => { try { Plotly.Plots.resize(chart); } catch (e) {} });
    }
  } catch (err) {
    if (status) {
      status.hidden = false;
      status.textContent = 'Failed: ' + (err.message || err);
      status.classList.add('text-error');
    }
  }
  if (window.lucide) lucide.createIcons();
};
window.__stCollectFormMessage = function(iconId, fallback) {
  const form = document.getElementById(iconId + '-form');
  if (!form) return fallback || '';
  const parts = [];
  form.querySelectorAll('[name]').forEach((el) => {
    const name = el.getAttribute('name');
    const val = (el.value || '').trim();
    if (!val) return;
    if (name === 'smiles' || name === 'message') parts.push(val);
    else parts.push(name + '=' + val);
  });
  return parts.join(' ') || fallback || '';
};
window.loadIoViz = async function(iconId, message) {
  const view = document.getElementById(iconId + '-view');
  const chart = document.getElementById(iconId + '-chart');
  const status = document.getElementById(iconId + '-status');
  if (!view || !chart) return;
  const url = view.dataset.vizUrl || '';
  const method = (view.dataset.vizMethod || 'post').toUpperCase();
  const intent = view.dataset.vizIntent || iconId;
  const fromForm = window.__stCollectFormMessage(iconId, '');
  const msg = (message && String(message).trim()) || fromForm || ('Show ' + intent);
  if (status) { status.hidden = false; status.textContent = 'Loading ' + intent + '…'; status.classList.remove('text-error'); }
  if (chart.data) { try { Plotly.purge(chart); } catch (e) {} }
  if (!url) {
    if (status) { status.textContent = 'No endpoint URL for ' + iconId; status.classList.add('text-error'); }
    return;
  }
  try {
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: method === 'GET' ? undefined : JSON.stringify({
        message: msg,
        response_format: 'json',
        endpoint: intent,
        visualization: window.__stStripCategoryPrefix(intent) || iconId,
      }),
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const payload = await res.json();
    await window.renderIoVizFromPayload(iconId, payload);
  } catch (err) {
    if (status) {
      status.hidden = false;
      status.textContent = 'Failed: ' + (err.message || err) + ' — is pixi run serve-viz up?';
      status.classList.add('text-error');
    }
  }
};
window.submitIoForm = function(iconId) {
  window.loadIoViz(iconId, window.__stCollectFormMessage(iconId, window.__stLastChatMessage));
  return false;
};
window.__stIoUnlocked = false;
window.__stLastChatMessage = '';
window.__stStripCategoryPrefix = function(intent) {
  let s = String(intent || '');
  for (const p of ['solubility_', 'settings_']) {
    if (s.startsWith(p)) return s.slice(p.length);
  }
  return s;
};
window.__stIconIdFromEndpoint = function(ep) {
  return window.__stStripCategoryPrefix(ep.id || '')
    || window.__stStripCategoryPrefix(ep.intent || '');
};
window.__stIconIdFromParsed = function(parsed) {
  const ep = String((parsed && parsed.endpoint) || '');
  const stripped = window.__stStripCategoryPrefix(ep);
  if (stripped && stripped !== ep) return stripped;
  if (ep.startsWith('settings_')) return ep.slice('settings_'.length);
  if (ep.startsWith('solubility_')) return ep.slice('solubility_'.length);
  const viz = String((parsed && parsed.visualization) || '');
  if (viz === 'parity') return 'property_diagnostics';
  if (viz === 'settings_panel') {
    const action = (parsed.panel && parsed.panel.action) || '';
    return action || 'start_max';
  }
  return viz || '';
};
window.revealIoIcons = function(endpoints) {
  const picker = document.getElementById('viz-picker');
  if (!picker) return [];
  const ids = (endpoints || [])
    .map(window.__stIconIdFromEndpoint)
    .filter(Boolean);
  const idSet = new Set(ids);
  picker.querySelectorAll('[data-io-icon]').forEach((btn) => {
    const id = btn.getAttribute('data-io-icon');
    const show = !idSet.size || idSet.has(id);
    btn.classList.toggle('hidden', !show);
  });
  picker.classList.remove('hidden');
  window.__stIoUnlocked = true;
  if (window.lucide) lucide.createIcons();
  return ids;
};
window.openIoViz = function(iconId) {
  if (!window.__stIoUnlocked) return;
  window.__stShowIoView(iconId);
  window.loadIoViz(iconId, window.__stLastChatMessage);
  if (window.lucide) lucide.createIcons();
};
window.openIoVizFromChat = function(iconId, payload) {
  window.revealIoIcons([{ id: iconId, intent: (payload && payload.endpoint) || iconId }]);
  window.renderIoVizFromPayload(iconId, payload || {});
};
window.addEventListener('message', (ev) => {
  const data = ev.data || {};
  if (data.type !== 'string-therapy:open-category') return;
  const endpoints = data.endpoints || [];
  const ids = window.revealIoIcons(endpoints);
  const first = ids[0] || (endpoints[0] && window.__stIconIdFromEndpoint(endpoints[0]));
  if (first) window.openIoViz(first);
});
