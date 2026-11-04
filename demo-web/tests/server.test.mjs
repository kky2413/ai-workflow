import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createApp } from '../server.mjs';

async function fixture(fn) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'web-practice-'));
  const fileName = path.join(dir, 'items.json');
  const server = createApp({ fileName });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}`;
  const request = (route, options) => fetch(base + route, options);
  const json = (method, data) => ({ method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
  try { await fn({ base, request, json, fileName }); }
  finally { await new Promise(resolve => server.close(resolve)); fs.rmSync(dir, { recursive: true, force: true }); }
}

test('health, static page, and empty list', async () => fixture(async ({ request }) => {
  const health = await request('/api/health');
  assert.equal(health.status, 200);
  assert.deepEqual(await health.json(), { status: 'ok' });
  const page = await request('/');
  assert.equal(page.status, 200);
  assert.match(await page.text(), /작업 기록 관리/);
  const css = await request('/styles.css');
  assert.equal(css.status, 200);
  const items = await request('/api/items');
  assert.deepEqual(await items.json(), { items: [] });
}));

test('create, update, delete and durable local save', async () => fixture(async ({ request, json, fileName }) => {
  const created = await request('/api/items', json('POST', { title: '  sample  ' }));
  assert.equal(created.status, 201);
  const { item } = await created.json();
  assert.equal(item.title, 'sample');
  assert.equal(item.done, false);
  const updated = await request(`/api/items/${item.id}`, json('PATCH', { done: true, title: 'changed' }));
  assert.equal(updated.status, 200);
  assert.deepEqual((await updated.json()).item, { id: item.id, title: 'changed', done: true });
  assert.equal(JSON.parse(fs.readFileSync(fileName)).length, 1);
  const deleted = await request(`/api/items/${item.id}`, { method: 'DELETE' });
  assert.equal(deleted.status, 200);
  assert.deepEqual(JSON.parse(fs.readFileSync(fileName)), []);
}));

test('malformed requests and missing ids fail clearly', async () => fixture(async ({ request, json }) => {
  assert.equal((await request('/api/items', json('POST', { title: '' }))).status, 400);
  assert.equal((await request('/api/items', json('POST', { title: 'ok', admin: true }))).status, 400);
  assert.equal((await request('/api/items', { method: 'POST', body: '{oops', headers: { 'Content-Type': 'application/json' } })).status, 400);
  assert.equal((await request('/api/items', { method: 'POST', body: 'no content type' })).status, 415);
  assert.equal((await request('/api/items/00000000-0000-0000-0000-000000000000', json('PATCH', { done: true }))).status, 404);
  assert.equal((await request('/api/items/00000000-0000-0000-0000-000000000000', { method: 'DELETE' })).status, 404);
  assert.equal((await request('/not-found')).status, 404);
  assert.equal((await request('/../../server.mjs')).status, 404);
}));

test('stored records load after server restart (store layer)', async () => fixture(async ({ request, json, fileName }) => {
  await request('/api/items', json('POST', { title: 'persist me' }));
  const { createStore } = await import('../store.mjs');
  assert.equal(createStore(fileName).list()[0].title, 'persist me');
}));
