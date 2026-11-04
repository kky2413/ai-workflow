import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createStore } from './store.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const assets = new Map([
  ['/', ['index.html', 'text/html; charset=utf-8']],
  ['/index.html', ['index.html', 'text/html; charset=utf-8']],
  ['/app.js', ['app.js', 'text/javascript; charset=utf-8']],
  ['/styles.css', ['styles.css', 'text/css; charset=utf-8']]
]);

function send(res, code, data) {
  const bytes = Buffer.from(JSON.stringify(data));
  res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8', 'Content-Length': bytes.length, 'Cache-Control': 'no-store' });
  res.end(bytes);
}

async function parseBody(req) {
  if (!req.headers['content-type']?.toLowerCase().startsWith('application/json')) {
    const error = new Error('Content-Type must be application/json');
    error.status = 415;
    throw error;
  }
  let size = 0;
  const chunks = [];
  for await (const chunk of req) {
    size += chunk.length;
    if (size > 64 * 1024) {
      const error = new Error('Request too large');
      error.status = 413;
      throw error;
    }
    chunks.push(chunk);
  }
  try { return JSON.parse(Buffer.concat(chunks).toString('utf8')); }
  catch { const error = new Error('Malformed JSON'); error.status = 400; throw error; }
}

export function createApp({ fileName = path.join(here, 'data', 'items.json') } = {}) {
  const store = createStore(fileName);
  return http.createServer(async (req, res) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'");
    try {
      const url = new URL(req.url, 'http://localhost');
      const pathname = url.pathname;
      if (req.method === 'GET' && assets.has(pathname)) {
        const [file, type] = assets.get(pathname);
        const content = fs.readFileSync(path.join(here, 'public', file));
        res.writeHead(200, { 'Content-Type': type, 'Content-Length': content.length });
        res.end(content);
        return;
      }
      if (pathname === '/api/health' && req.method === 'GET') return send(res, 200, { status: 'ok' });
      if (pathname === '/api/items' && req.method === 'GET') return send(res, 200, { items: store.list() });
      if (pathname === '/api/items' && req.method === 'POST') {
        const item = store.create(await parseBody(req));
        return send(res, 201, { item });
      }
      const match = new RegExp('^/api/items/([0-9a-f-]{36})$').exec(pathname);
      if (match && req.method === 'PATCH') {
        const updated = store.update(match[1], await parseBody(req));
        return updated ? send(res, 200, { item: updated }) : send(res, 404, { error: 'Item not found' });
      }
      if (match && req.method === 'DELETE') {
        return store.remove(match[1]) ? send(res, 200, { deleted: true }) : send(res, 404, { error: 'Item not found' });
      }
      send(res, 404, { error: 'Route not found' });
    } catch (error) {
      const status = error.status || (error instanceof TypeError ? 400 : 500);
      send(res, status, { error: status === 500 ? 'Internal server error' : error.message });
      if (status === 500) console.error('Unexpected server error:', error);
    }
  });
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const host = process.env.HOST || '127.0.0.1';
  const port = Number(process.env.PORT || 3000);
  if (!Number.isInteger(port) || port < 0 || port > 65535) {
    console.error('PORT must be an integer between 0 and 65535');
    process.exit(2);
  }
  const server = createApp();
  server.listen(port, host, () => console.log(`Practice server: http://${host}:${server.address().port}`));
}
