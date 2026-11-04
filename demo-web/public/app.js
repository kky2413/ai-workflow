const el = id => document.getElementById(id);
let items = [];
let editingId = null;

async function request(url, options) {
  let response;
  try { response = await fetch(url, options); }
  catch { throw new Error('서버와 연결할 수 없습니다. 서버 실행 상태를 확인하세요.'); }
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
  return payload;
}

const jsonOptions = (method, data) => ({ method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });

function render() {
  const query = el('search').value.trim().toLocaleLowerCase();
  el('count-all').textContent = String(items.length);
  el('count-open').textContent = String(items.filter(x => !x.done).length);
  el('count-done').textContent = String(items.filter(x => x.done).length);
  const visible = items.filter(x => x.title.toLocaleLowerCase().includes(query));
  el('empty').hidden = visible.length > 0;
  const list = el('items');
  list.replaceChildren();
  for (const item of visible) {
    const li = document.createElement('li');
    if (item.done) li.classList.add('done');
    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.textContent = item.done ? '완료 취소' : '완료';
    toggle.setAttribute('aria-label', `${item.title} ${toggle.textContent}`);
    toggle.addEventListener('click', () => mutate(() => request(`/api/items/${item.id}`, jsonOptions('PATCH', { done: !item.done }))));
    const title = document.createElement('span');
    title.className = 'item-title';
    title.textContent = item.title; // user input is never injected via innerHTML
    const edit = document.createElement('button');
    edit.type = 'button';
    edit.textContent = '수정';
    edit.setAttribute('aria-label', `${item.title} 수정`);
    edit.addEventListener('click', () => { editingId = item.id; el('edit-title').value = item.title; el('edit-dialog').showModal(); });
    const remove = document.createElement('button');
    remove.type = 'button';
    remove.className = 'delete';
    remove.textContent = '삭제';
    remove.setAttribute('aria-label', `${item.title} 삭제`);
    remove.addEventListener('click', () => mutate(() => request(`/api/items/${item.id}`, { method: 'DELETE' })));
    li.append(toggle, title, edit, remove);
    list.append(li);
  }
}

async function refresh() {
  const data = await request('/api/items');
  if (!Array.isArray(data.items)) throw new Error('서버 응답 형식이 올바르지 않습니다.');
  items = data.items;
  render();
}

async function mutate(action) {
  try { await action(); await refresh(); el('feedback').textContent = '변경사항이 저장되었습니다.'; }
  catch (error) { el('feedback').textContent = `오류: ${error.message}`; }
}

el('create-form').addEventListener('submit', event => {
  event.preventDefault();
  const title = el('new-title').value.trim();
  if (!title || title.length > 80) return;
  mutate(async () => { await request('/api/items', jsonOptions('POST', { title })); el('new-title').value = ''; });
});
el('search').addEventListener('input', render);
el('edit-form').addEventListener('submit', event => {
  if (event.submitter?.value !== 'save') return;
  event.preventDefault();
  const title = el('edit-title').value.trim();
  if (!title || title.length > 80 || !editingId) return;
  const id = editingId;
  el('edit-dialog').close();
  editingId = null;
  mutate(() => request(`/api/items/${id}`, jsonOptions('PATCH', { title })));
});
refresh().catch(error => { el('feedback').textContent = `오류: ${error.message}`; });
