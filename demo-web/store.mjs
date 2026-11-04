import fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';

const validTitle = value => typeof value === 'string' && value.trim().length >= 1 && value.trim().length <= 80;

export function createStore(fileName) {
  if (!fileName || typeof fileName !== 'string') throw new Error('A data file path is required');
  let items = [];
  if (fs.existsSync(fileName)) {
    const loaded = JSON.parse(fs.readFileSync(fileName, 'utf8'));
    if (!Array.isArray(loaded) || !loaded.every(item =>
      item && typeof item.id === 'string' && validTitle(item.title) && typeof item.done === 'boolean')) {
      throw new Error('Invalid stored data format');
    }
    items = loaded;
  }
  function save(next) {
    fs.mkdirSync(path.dirname(fileName), { recursive: true });
    const tmp = `${fileName}.${process.pid}.${randomUUID()}.tmp`;
    try {
      fs.writeFileSync(tmp, JSON.stringify(next, null, 2), { encoding: 'utf8', flag: 'wx' });
      fs.renameSync(tmp, fileName);
    } finally {
      if (fs.existsSync(tmp)) fs.unlinkSync(tmp);
    }
    items = next;
  }
  return {
    list() { return items.map(item => ({ ...item })); },
    create(input) {
      if (!input || typeof input !== 'object' || Array.isArray(input) || !validTitle(input.title) ||
          Object.keys(input).some(key => key !== 'title')) {
        throw new TypeError('title must be 1–80 characters');
      }
      const item = { id: randomUUID(), title: input.title.trim(), done: false };
      save([...items, item]);
      return { ...item };
    },
    update(id, patch) {
      const idx = items.findIndex(item => item.id === id);
      if (idx === -1) return null;
      if (!patch || typeof patch !== 'object' || Array.isArray(patch) ||
          Object.keys(patch).length === 0 ||
          Object.keys(patch).some(key => !['title', 'done'].includes(key)) ||
          ('title' in patch && !validTitle(patch.title)) ||
          ('done' in patch && typeof patch.done !== 'boolean')) {
        throw new TypeError('Invalid title or done field');
      }
      const updated = { ...items[idx], ...patch };
      if (typeof updated.title === 'string') updated.title = updated.title.trim();
      const next = [...items];
      next[idx] = updated;
      save(next);
      return { ...updated };
    },
    remove(id) {
      if (!items.some(item => item.id === id)) return false;
      save(items.filter(item => item.id !== id));
      return true;
    }
  };
}
