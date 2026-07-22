/** Multi-table workspace client for the Graph / Tables tab.
 *  Loaded as /ui/table_client.js — keep this out of the Python notebook.
 *
 *  Query-agent chat payloads with ``rows`` land here (optional ``excel`` base64).
 *  History grows left→right in #table-tabs; unread count badges #graph-badge.
 */
window.__stTables = [];
window.__stActiveTableId = null;
window.__stAttachedTableId = null;
window.__stTableUnread = 0;

window.__stEsc = function (s) {
  return String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
};

window.__stBumpTableBadge = function () {
  window.__stTableUnread = (window.__stTableUnread || 0) + 1;
  const b = document.getElementById('graph-badge');
  if (!b) return;
  b.textContent = String(window.__stTableUnread);
  b.classList.remove('hidden');
};

window.__stClearTableBadge = function () {
  window.__stTableUnread = 0;
  const b = document.getElementById('graph-badge');
  if (!b) return;
  b.textContent = '';
  b.classList.add('hidden');
};

window.__stUpdateTableChrome = function () {
  const n = window.__stTables.length;
  const badge = document.getElementById('table-count-badge');
  if (badge) {
    badge.textContent = n ? String(n) : '';
    badge.classList.toggle('hidden', !n);
  }
  const empty = document.getElementById('table-empty');
  if (empty) empty.classList.toggle('hidden', n > 0);
};

window.__stShowTable = function (id) {
  window.__stActiveTableId = id;
  document.querySelectorAll('[data-table-tab]').forEach((el) => {
    el.classList.toggle('btn-active', el.getAttribute('data-table-tab') === id);
    el.classList.toggle('btn-primary', el.getAttribute('data-table-tab') === id);
    el.classList.toggle('btn-ghost', el.getAttribute('data-table-tab') !== id);
  });
  document.querySelectorAll('[data-table-panel]').forEach((el) => {
    el.classList.toggle('hidden', el.getAttribute('data-table-panel') !== id);
  });
};

window.__stRemoveTable = function (id, ev) {
  if (ev) ev.stopPropagation();
  window.__stTables = window.__stTables.filter((t) => t.id !== id);
  if (window.__stActiveTableId === id) {
    window.__stActiveTableId = window.__stTables.length
      ? window.__stTables[window.__stTables.length - 1].id
      : null;
  }
  if (window.__stAttachedTableId === id) {
    window.__stClearTableAttachment();
  }
  window.__stRenderTables();
  if (window.__stActiveTableId) window.__stShowTable(window.__stActiveTableId);
};

window.__stClearTableAttachment = function () {
  window.__stAttachedTableId = null;
  const hid = document.getElementById('attached-table-id');
  if (hid) hid.value = '';
  const chip = document.getElementById('table-ref-chip');
  if (chip) {
    chip.innerHTML = '';
    chip.classList.add('hidden');
  }
  document.querySelectorAll('[data-table-tab]').forEach((el) => {
    el.classList.remove('ring-2', 'ring-accent');
  });
};

window.__stAttachTableToChat = function (id) {
  const t = (window.__stTables || []).find((x) => x.id === id);
  if (!t) {
    console.warn('__stAttachTableToChat: unknown table', id);
    return;
  }
  window.__stAttachedTableId = id;
  const hid = document.getElementById('attached-table-id');
  if (hid) hid.value = id;
  const chip = document.getElementById('table-ref-chip');
  if (chip) {
    const title = t.title || t.twin || id;
    const n = t.row_count != null ? t.row_count : (t.rows || []).length;
    chip.classList.remove('hidden');
    chip.innerHTML =
      '<div class="inline-flex items-center gap-1.5 max-w-full rounded-full border border-primary/40 bg-base-100 pl-2 pr-1 py-0.5 text-xs shadow-sm" data-attached-table="' +
      window.__stEsc(id) +
      '">' +
      '<i data-lucide="table-2" class="w-3.5 h-3.5 opacity-70 shrink-0"></i>' +
      '<span class="font-medium truncate max-w-[10rem]" title="' +
      window.__stEsc(title) +
      '">' +
      window.__stEsc(title) +
      '</span>' +
      '<span class="badge badge-ghost badge-xs shrink-0">' +
      window.__stEsc(n) +
      '</span>' +
      '<button type="button" class="btn btn-ghost btn-xs btn-circle min-h-0 h-5 w-5" title="Remove attachment" data-clear-table-attach="1">' +
      '<i data-lucide="x" class="w-3 h-3"></i></button></div>';
    const clearBtn = chip.querySelector('[data-clear-table-attach]');
    if (clearBtn) {
      clearBtn.addEventListener('click', (ev) => {
        ev.preventDefault();
        ev.stopPropagation();
        window.__stClearTableAttachment();
      });
    }
  } else {
    console.warn('__stAttachTableToChat: #table-ref-chip missing');
  }
  document.querySelectorAll('[data-table-tab]').forEach((el) => {
    const on = el.getAttribute('data-table-tab') === id;
    el.classList.toggle('ring-2', on);
    el.classList.toggle('ring-accent', on);
  });
  if (window.lucide) lucide.createIcons();
};

window.__stSyncTableToServer = function (entry) {
  if (!entry || !entry.id) return;
  fetch('/api/tables', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    credentials: 'same-origin',
    body: JSON.stringify({
      id: entry.id,
      title: entry.title,
      twin: entry.twin,
      columns: entry.columns,
      rows: entry.rows,
    }),
  }).catch((err) => console.warn('table sync failed', err));
};

window.__stExcelHref = function (excel) {
  if (!excel || !excel.content_base64) return null;
  const mime = excel.mime || 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
  return 'data:' + mime + ';base64,' + excel.content_base64;
};

window.__stRenderTablePanel = function (t) {
  const cols = t.columns || [];
  const rows = t.rows || [];
  const thead = cols.map((c) => '<th class="whitespace-nowrap">' + window.__stEsc(c) + '</th>').join('');
  const body = rows
    .map((row) => {
      const cells = cols
        .map((c) => {
          const v = row && typeof row === 'object' ? row[c] : '';
          return '<td class="whitespace-nowrap max-w-xs truncate" title="' + window.__stEsc(v) + '">' + window.__stEsc(v) + '</td>';
        })
        .join('');
      return '<tr>' + cells + '</tr>';
    })
    .join('');

  const href = window.__stExcelHref(t.excel);
  const fname = (t.excel && t.excel.filename) || (t.twin + '.xlsx');
  const dl = href
    ? '<a class="btn btn-ghost btn-xs gap-1" download="' + window.__stEsc(fname) + '" href="' + href + '">' +
      '<i data-lucide="download" class="w-3.5 h-3.5"></i>Excel</a>'
    : '';

  const note = t.question
    ? '<p class="text-xs opacity-60 px-3 pb-2 truncate" title="' + window.__stEsc(t.question) + '">' +
      window.__stEsc(t.question) +
      '</p>'
    : '';

  const attachBtn =
    '<button type="button" data-attach-table="' +
    window.__stEsc(t.id) +
    '" class="btn btn-primary btn-xs gap-1">' +
    '<i data-lucide="paperclip" class="w-3.5 h-3.5"></i>Attach</button>';

  return (
    '<div data-table-panel="' +
    window.__stEsc(t.id) +
    '" class="flex flex-col flex-1 min-h-0 hidden">' +
    '<div class="flex items-center gap-2 px-3 py-2 border-b border-base-300 bg-base-100/60">' +
    '<span class="font-medium text-sm">' +
    window.__stEsc(t.title) +
    '</span>' +
    '<span class="badge badge-ghost badge-sm">' +
    window.__stEsc(t.row_count) +
    ' rows</span>' +
    '<div class="flex-1"></div>' +
    attachBtn +
    dl +
    '</div>' +
    note +
    '<div class="flex-1 min-h-0 overflow-auto px-2 pb-4">' +
    '<table class="table table-zebra table-xs w-max min-w-full">' +
    '<thead><tr>' +
    thead +
    '</tr></thead><tbody>' +
    body +
    '</tbody></table></div></div>'
  );
};

window.__stRenderTables = function () {
  const tabs = document.getElementById('table-tabs');
  const panels = document.getElementById('table-panels');
  if (!tabs || !panels) return;

  tabs.innerHTML = window.__stTables
    .map((t) => {
      const active = t.id === window.__stActiveTableId;
      const btnCls = active ? 'btn btn-primary btn-xs' : 'btn btn-ghost btn-xs';
      return (
        '<div class="inline-flex items-center max-w-[12rem] shrink-0" data-table-tab-wrap="' +
        window.__stEsc(t.id) +
        '">' +
        '<button type="button" data-table-tab="' +
        window.__stEsc(t.id) +
        '" class="' +
        btnCls +
        ' gap-1 rounded-r-none max-w-[9rem]" title="Show & attach ' +
        window.__stEsc(t.title) +
        '">' +
        '<span class="truncate">' +
        window.__stEsc(t.title) +
        '</span></button>' +
        '<button type="button" data-table-close="' +
        window.__stEsc(t.id) +
        '" class="' +
        btnCls +
        ' rounded-l-none px-1.5 border-l border-base-300/40" title="Close table">×</button></div>'
      );
    })
    .join('');

  // Tab = show + attach; dedicated close button = remove
  tabs.querySelectorAll('[data-table-tab]').forEach((btn) => {
    const id = btn.getAttribute('data-table-tab');
    btn.addEventListener('click', (ev) => {
      ev.preventDefault();
      ev.stopPropagation();
      window.__stShowTable(id);
      window.__stAttachTableToChat(id);
    });
  });
  tabs.querySelectorAll('[data-table-close]').forEach((btn) => {
    const id = btn.getAttribute('data-table-close');
    btn.addEventListener('click', (ev) => {
      ev.preventDefault();
      ev.stopPropagation();
      window.__stRemoveTable(id, ev);
    });
  });

  panels.innerHTML = window.__stTables.map((t) => window.__stRenderTablePanel(t)).join('');
  panels.querySelectorAll('[data-attach-table]').forEach((btn) => {
    const id = btn.getAttribute('data-attach-table');
    btn.addEventListener('click', (ev) => {
      ev.preventDefault();
      ev.stopPropagation();
      window.__stShowTable(id);
      window.__stAttachTableToChat(id);
    });
  });
  window.__stUpdateTableChrome();
  if (window.__stActiveTableId) window.__stShowTable(window.__stActiveTableId);
  if (window.__stAttachedTableId) {
    document.querySelectorAll('[data-table-tab]').forEach((el) => {
      const on = el.getAttribute('data-table-tab') === window.__stAttachedTableId;
      el.classList.toggle('ring-2', on);
      el.classList.toggle('ring-accent', on);
    });
  }
  if (window.lucide) lucide.createIcons();
};

/** Append a query-agent table payload into the Tables workspace. */
window.loadTableFromChat = function (payload) {
  try {
    if (!payload || !Array.isArray(payload.rows) || !payload.rows.length) return null;
    const twin = String(payload.twin_name || 'query');
    const cols = Object.keys(payload.rows[0] || {});
    if (!cols.length) return null;
    const id = 'tbl-' + Date.now() + '-' + Math.floor(Math.random() * 1e4);
    const entry = {
      id,
      twin,
      title: twin.replace(/_/g, ' '),
      columns: cols,
      rows: payload.rows,
      row_count: payload.row_count != null ? payload.row_count : payload.rows.length,
      excel: payload.excel || null,
      question: window.__stLastChatMessage || '',
    };
    window.__stTables.push(entry);
    window.__stActiveTableId = id;
    window.__stRenderTables();
    window.__stBumpTableBadge();
    window.__stSyncTableToServer(entry);
    return id;
  } catch (err) {
    console.error('loadTableFromChat failed', err);
    return null;
  }
};
