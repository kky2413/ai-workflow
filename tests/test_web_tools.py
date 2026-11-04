"""Isolated tests for local-only web auditing and API checks."""
import http.server
import json
from pathlib import Path
import tempfile
import threading
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import web_project_audit
import web_api_check


class WebProjectAuditTests(unittest.TestCase):
    def test_detects_stack_scripts_entries_without_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'package.json').write_text(json.dumps({'name': 'sample', 'scripts': {'dev': 'vite', 'test': 'vitest'},
                                                           'dependencies': {'react': '*', 'vite': '*'}}))
            (root / 'package-lock.json').write_text('{}')
            (root / 'index.html').write_text('<html></html>')
            (root / 'src').mkdir()
            (root / 'src' / 'App.jsx').write_text('export default () => null')
            (root / 'src' / 'app.test.js').write_text('')
            result = web_project_audit.audit(root)
            self.assertEqual(result['files_scanned'], 5)
            self.assertEqual(result['packages'][0]['scripts'], ['dev', 'test'])
            self.assertEqual(result['packages'][0]['frameworks'], ['react', 'vite'])
            self.assertIn('src/App.jsx', result['entrypoints'])
            self.assertEqual(result['test_count'], 1)

    def test_ignores_dependencies_and_env(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'index.html').write_text('test')
            (root / '.env').write_text('SECRET=hidden')
            (root / 'node_modules').mkdir()
            (root / 'node_modules' / 'private.test.js').write_text('test')
            result = web_project_audit.audit(root)
            self.assertEqual(result['files_scanned'], 1)
            self.assertEqual(result['test_count'], 0)

    def test_missing_directory_fails(self):
        with self.assertRaises(ValueError):
            web_project_audit.audit('/this/path/should/not/exist/web-audit')


class Server(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.reply(200, {'status': 'ok', 'version': 1})
        elif self.path == '/items':
            self.reply(200, {'items': [{'id': '001', 'label': 'hello'}]})
        elif self.path == '/bad':
            self.reply(422, {'error': 'bad input'})
        elif self.path == '/redirect':
            self.send_response(302)
            self.send_header('Location', 'https://example.org/')
            self.end_headers()
        else:
            self.reply(404, {'error': 'not found'})

    def do_POST(self):
        size = int(self.headers.get('Content-Length', '0'))
        payload = json.loads(self.rfile.read(size))
        self.reply(201, {'value': payload})

    def reply(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class WebApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Server)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_get_checks_status_fields_and_subset(self):
        cases = {'base_url': self.base, 'cases': [
            {'name': 'health', 'path': '/health', 'expect_status': 200, 'expect_json': {'status': 'ok'}},
            {'name': 'items', 'path': '/items', 'expect_status': 200, 'expect_json_fields': ['items.0.id']},
            {'name': 'error', 'path': '/bad', 'expect_status': 422, 'expect_json': {'error': 'bad input'}}]}
        result = web_api_check.execute(cases)
        self.assertEqual(len(result), 3)
        self.assertTrue(all(x['passed'] for x in result))

    def test_reports_real_content_mismatch(self):
        result = web_api_check.execute({'base_url': self.base, 'cases': [
            {'path': '/health', 'expect_status': 200, 'expect_json': {'status': 'wrong'}}]})
        self.assertFalse(result[0]['passed'])
        self.assertIn('불일치', result[0]['error'])

    def test_rejects_external_host_and_credentials(self):
        for url in ['https://127.0.0.1:123', 'http://example.org', 'http://user:pw@127.0.0.1:1000']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                web_api_check.validate_base(url)

    def test_rejects_unsafe_paths_and_empty_tests(self):
        for route in ['//evil.org/a', '/../secret', '/%2e%2e/private', 'https://evil.org']:
            with self.subTest(route=route), self.assertRaises(ValueError):
                web_api_check.validate_path(route)
        with self.assertRaises(ValueError):
            web_api_check.validate_spec({'base_url': self.base, 'cases': []})

    def test_write_requires_explicit_opt_in(self):
        spec = {'base_url': self.base, 'cases': [
            {'path': '/items', 'method': 'POST', 'body': {'title': 'x'}, 'expect_status': 201,
             'expect_json': {'value': {'title': 'x'}}}]}
        with self.assertRaises(ValueError):
            web_api_check.execute(spec)
        self.assertTrue(web_api_check.execute(spec, allow_writes=True)[0]['passed'])

    def test_does_not_follow_redirect(self):
        results = web_api_check.execute({'base_url': self.base, 'cases': [
            {'path': '/redirect', 'expect_status': 302}]})
        self.assertEqual(results[0]['actual_status'], 302)
        self.assertTrue(results[0]['passed'])


if __name__ == '__main__':
    unittest.main()
