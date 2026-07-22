/** Instant outbound chat UX — user bubble + loading dots before HTMX returns. */

window.__stChatEsc = function (s) {
  return String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
};

window.__stRemoveChatLoading = function () {
  const el = document.getElementById('chat-loading');
  if (el) el.remove();
};

window.__stScrollChatToBottom = function () {
  const view = document.getElementById('chat-view');
  if (view) view.scrollTop = view.scrollHeight;
};

/** Show Chat tab so the outgoing bubble is visible. */
window.__stShowChatView = function () {
  ['chat-view', 'graph-view', 'io-view'].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.classList.toggle('hidden', id !== 'chat-view');
  });
  document.querySelectorAll('[data-taskbar-icon]').forEach((b) => {
    b.classList.remove('ring-2', 'ring-primary', 'text-primary');
  });
  const chatBtn = document.querySelector('[data-taskbar-icon="chat"]');
  if (chatBtn) chatBtn.classList.add('ring-2', 'ring-primary', 'text-primary');
};

/**
 * Append the user message and a Router loading bubble immediately.
 * Returns false if message is empty or a request is already in flight.
 */
window.__stAppendOutgoingChat = function (message) {
  const msg = String(message || '').trim();
  if (!msg) return false;
  if (document.getElementById('chat-loading')) return false;

  const box = document.getElementById('chat-messages');
  if (!box) return false;

  window.__stShowChatView();

  let display = msg;
  const tid = window.__stAttachedTableId;
  if (tid) {
    const t = (window.__stTables || []).find((x) => x.id === tid);
    const title = (t && (t.title || t.twin)) || 'table';
    display = '@' + title + '\n' + msg;
  }

  const userHtml =
    '<div class="chat chat-end px-2">' +
    '<div class="chat-image avatar"><div class="w-10 rounded-full bg-primary text-primary-content grid place-items-center">' +
    '<i data-lucide="user" class="w-4 h-4"></i></div></div>' +
    '<div class="chat-header opacity-70 text-xs mb-1">You</div>' +
    '<div class="chat-bubble max-w-xl whitespace-pre-line shadow chat-bubble-primary">' +
    window.__stChatEsc(display) +
    '</div></div>';

  const loadingHtml =
    '<div id="chat-loading" class="chat chat-start px-2" aria-live="polite" aria-busy="true">' +
    '<div class="chat-image avatar"><div class="w-10 rounded-full bg-secondary text-secondary-content grid place-items-center">' +
    '<i data-lucide="bot" class="w-4 h-4"></i></div></div>' +
    '<div class="chat-header opacity-70 text-xs mb-1">Router</div>' +
    '<div class="chat-bubble chat-bubble-secondary shadow">' +
    '<span class="loading loading-dots loading-md text-secondary-content"></span>' +
    '</div></div>';

  box.insertAdjacentHTML('beforeend', userHtml + loadingHtml);
  if (window.lucide) lucide.createIcons();
  window.__stScrollChatToBottom();
  return true;
};
