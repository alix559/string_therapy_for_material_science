/** Category / IO viz client for the FastHTML shell.
 *  Loaded as /ui/viz_client.js — keep this out of the Python notebook.
 *
 *  One shared #io-view slot receives settings / router payloads.
 *  Picker icons are built dynamically (not a fixed server-rendered set).
 */
window.__stPlotlyDefaults = {
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: { family: 'ui-sans-serif, system-ui, sans-serif' },
  margin: { t: 48, r: 24, b: 48, l: 56 },
};

/** id → [label, lucide icon] for dynamic picker buttons */
window.__stIoMeta = {
  predict: ['Predict', 'calculator'],
  viz: ['Visualize', 'chart-column'],
  scatter: ['Scatter', 'chart-scatter'],
  heatmap: ['Heatmap', 'grid-3x3'],
  timeseries: ['Timeseries', 'line-chart'],
  encode_pass: ['Encode', 'orbit'],
  attention_heatmap: ['Attention', 'brain'],
  property_diagnostics: ['Parity', 'git-compare'],
  latent_interpolation: ['Latent', 'waypoints'],
  molecular_structure: ['Molecule', 'atom'],
  roundtrip: ['Roundtrip', 'refresh-cw'],
  table_analyst: ['Analyst', 'chart-column'],
  start_max: ['Start MAX', 'play'],
  load_weights: ['Weights', 'hard-drive'],
  stop_max: ['Stop MAX', 'square'],
};

window.__stDefaultVizUrl = '';
window.__stIoUnlocked = false;
window.__stLastChatMessage = '';
window.__stActiveEndpoints = [];
/** Left→right history of IO viz returns (newest on the right), capped at max. */
window.__stVizHistory = [];
window.__stVizHistSeq = 0;
window.__stVizHistoryMax = 5;

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
  if (viz === 'predict_panel') return 'predict';
  if (viz === 'settings_panel') {
    const action = (parsed.panel && parsed.panel.action) || '';
    return action || 'start_max';
  }
  return viz || '';
};

window.__stMetaForId = function(id) {
  const m = window.__stIoMeta[id];
  if (m) return { label: m[0], icon: m[1] };
  const label = String(id || 'viz').replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  return { label, icon: 'chart-scatter' };
};

window.__stShowIoView = function() {
  document.querySelectorAll('#chat-view, #graph-view, #io-view').forEach((el) => {
    el.classList.add('hidden');
  });
  const view = document.getElementById('io-view');
  if (view) view.classList.remove('hidden');
  document.querySelectorAll('[data-taskbar-icon]').forEach((b) => {
    b.classList.remove('ring-2', 'ring-primary', 'text-primary');
  });
};

window.__stSetIoHeader = function(label, badge) {
  const title = document.getElementById('io-title');
  const badgeEl = document.getElementById('io-badge');
  if (title) title.textContent = label || 'Visualization';
  if (badgeEl) {
    badgeEl.textContent = badge || '';
    badgeEl.classList.toggle('hidden', !badge);
  }
};

window.__stBindIoEndpoint = function(ep) {
  const view = document.getElementById('io-view');
  if (!view) return;
  const intent = (ep && (ep.intent || ep.id)) || '';
  const id = window.__stIconIdFromEndpoint(ep || {}) || window.__stStripCategoryPrefix(intent);
  view.dataset.vizUrl = (ep && ep.url) || view.dataset.vizUrl || window.__stDefaultVizUrl;
  view.dataset.vizMethod = ((ep && ep.method) || view.dataset.vizMethod || 'post').toLowerCase();
  view.dataset.vizIntent = intent || id || '';
  const meta = window.__stMetaForId(id);
  window.__stSetIoHeader(meta.label, intent || id);
};

window.__stMarkActiveIoIcon = function(iconId) {
  document.querySelectorAll('[data-io-icon]').forEach((b) => {
    b.classList.remove('ring-2', 'ring-primary', 'text-primary');
  });
  if (!iconId) return;
  const t = document.querySelector('[data-io-icon="' + iconId + '"]');
  if (t) t.classList.add('ring-2', 'ring-primary', 'text-primary');
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

/** Render a settings / router payload into the shared IO slot. */
window.renderIoVizFromPayload = async function(payload, opts) {
  opts = opts || {};
  const view = document.getElementById('io-view');
  const chart = document.getElementById('io-chart');
  const status = document.getElementById('io-status');
  if (!view || !chart) return;

  const iconId = opts.iconId || window.__stIconIdFromParsed(payload || {}) || '';
  const meta = window.__stMetaForId(iconId || 'viz');
  const intent = (payload && payload.endpoint) || iconId;
  window.__stSetIoHeader(meta.label, intent);
  window.__stShowIoView();
  window.__stMarkActiveIoIcon(iconId);

  if (status) {
    status.hidden = false;
    status.textContent = 'Rendering…';
    status.classList.remove('text-error');
  }
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

window.__stCollectFormMessage = function(fallback) {
  const form = document.getElementById('io-form');
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

/** Fetch viz for the currently bound endpoint into the shared slot. */
window.loadIoViz = async function(message) {
  const view = document.getElementById('io-view');
  const chart = document.getElementById('io-chart');
  const status = document.getElementById('io-status');
  if (!view || !chart) return;

  const url = view.dataset.vizUrl || window.__stDefaultVizUrl;
  const method = (view.dataset.vizMethod || 'post').toUpperCase();
  const intent = view.dataset.vizIntent || '';
  const iconId = window.__stStripCategoryPrefix(intent);
  const fromForm = window.__stCollectFormMessage('');
  const msg = (message && String(message).trim()) || fromForm || ('Show ' + (intent || 'viz'));

  window.__stSetIoHeader(window.__stMetaForId(iconId).label, intent || iconId);
  window.__stShowIoView();
  window.__stMarkActiveIoIcon(iconId);

  if (status) {
    status.hidden = false;
    status.textContent = 'Loading ' + (intent || iconId || 'viz') + '…';
    status.classList.remove('text-error');
  }
  if (chart.data) { try { Plotly.purge(chart); } catch (e) {} }
  if (!url) {
    if (status) { status.textContent = 'No endpoint URL'; status.classList.add('text-error'); }
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
        visualization: iconId || intent,
      }),
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const payload = await res.json();
    await window.renderIoVizFromPayload(payload, { iconId });
  } catch (err) {
    if (status) {
      status.hidden = false;
      status.textContent = 'Failed: ' + (err.message || err);
      status.classList.add('text-error');
    }
  }
};

window.submitIoForm = function() {
  window.loadIoViz(window.__stCollectFormMessage(window.__stLastChatMessage));
  return false;
};

/** Append a viz chip in #viz-picker — history grows left→right, max __stVizHistoryMax. */
window.appendVizHistory = function(payload) {
  const picker = document.getElementById('viz-picker');
  if (!picker) return null;

  const typeId = window.__stIconIdFromParsed(payload || {}) || 'viz';
  const intent = (payload && payload.endpoint) || typeId;
  const meta = window.__stMetaForId(typeId);
  // Unique instance id so repeated analyst charts append instead of replacing.
  window.__stVizHistSeq += 1;
  const histId = typeId + '__' + window.__stVizHistSeq;
  const entry = {
    id: histId,
    typeId: typeId,
    intent: intent,
    payload: payload || {},
    label: meta.label,
  };
  window.__stVizHistory.push(entry);

  // Cap at max — drop oldest (left).
  while (window.__stVizHistory.length > window.__stVizHistoryMax) {
    const dropped = window.__stVizHistory.shift();
    const oldBtn = picker.querySelector('[data-io-icon="' + dropped.id + '"]');
    if (oldBtn) oldBtn.remove();
  }

  const btn = document.createElement('button');
  btn.type = 'button';
  btn.id = 'io-icon-' + histId;
  btn.title = meta.label;
  btn.setAttribute('data-io-icon', histId);
  btn.className = 'btn btn-ghost btn-circle btn-xs';
  btn.innerHTML = '<i data-lucide="' + meta.icon + '" class="w-3.5 h-3.5"></i>';
  btn.addEventListener('click', () => window.openVizHistory(histId));
  picker.appendChild(btn);

  picker.classList.remove('hidden');
  window.__stIoUnlocked = true;
  if (window.lucide) lucide.createIcons();
  return histId;
};

/** Re-open a cached history entry in the shared IO slot (no refetch). */
window.openVizHistory = function(histId) {
  if (!window.__stIoUnlocked) return;
  const entry = (window.__stVizHistory || []).find((h) => h.id === histId);
  if (!entry) return;
  const typeId = entry.typeId || entry.id;
  window.__stBindIoEndpoint({
    id: typeId,
    intent: entry.intent,
    url: window.__stDefaultVizUrl,
    method: 'post',
  });
  window.__stShowIoView();
  window.__stMarkActiveIoIcon(histId);
  window.renderIoVizFromPayload(entry.payload || {}, { iconId: typeId });
  if (window.lucide) lucide.createIcons();
};

/** @deprecated kept for callers; category clicks no longer use this. */
window.revealIoIcons = function(endpoints) {
  const ids = [];
  (endpoints || []).forEach((ep) => {
    const id = window.__stIconIdFromEndpoint(ep);
    if (id) ids.push(id);
  });
  return ids;
};

window.openIoViz = function(histId) {
  window.openVizHistory(histId);
};

/** Controller returned a figure — append chip + fill the IO slot. */
window.openIoVizFromChat = function(payload) {
  try {
    const histId = window.appendVizHistory(payload || {}) || 'viz';
    const typeId = window.__stIconIdFromParsed(payload || {}) || 'viz';
    const intent = (payload && payload.endpoint) || typeId;
    window.__stBindIoEndpoint({
      id: typeId,
      intent: intent,
      url: window.__stDefaultVizUrl,
      method: 'post',
    });
    window.__stShowIoView();
    window.__stMarkActiveIoIcon(histId);
    window.renderIoVizFromPayload(payload || {}, { iconId: typeId });
  } catch (err) {
    console.error('openIoVizFromChat failed', err);
  }
};

// Category node clicks must NOT populate the picker or fetch viz —
// visualizations only arrive via openIoVizFromChat (controller return).
