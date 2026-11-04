#!/usr/bin/env python3
"""Run opt-in API contract checks against loopback HTTP only (no redirects/proxy)."""
import argparse
import ipaddress
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

MAX_RESPONSE = 1024 * 1024
WRITE_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}
ALLOWED_METHODS = {'GET', 'HEAD'} | WRITE_METHODS


class RefuseRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def validate_base(url):
    if not isinstance(url, str):
        raise ValueError('base_url 문자열이 필요합니다')
    parsed = urllib.parse.urlsplit(url)
    if (parsed.scheme != 'http' or parsed.username or parsed.password or
            parsed.query or parsed.fragment or parsed.path not in ('', '/')):
        raise ValueError('인증·쿼리가 없는 loopback HTTP base_url만 허용합니다')
    if parsed.hostname not in {'localhost', '127.0.0.1', '::1'}:
        raise ValueError('외부 호스트는 허용하지 않습니다')
    host = '127.0.0.1' if parsed.hostname == 'localhost' else parsed.hostname
    if not ipaddress.ip_address(host).is_loopback:
        raise ValueError('loopback IP가 아닙니다')
    port = parsed.port or 80
    display_host = f'[{host}]' if ':' in host else host
    return f'http://{display_host}:{port}'


def validate_path(path):
    if not isinstance(path, str) or not path.startswith('/') or path.startswith('//') or '#' in path:
        raise ValueError('상대 API 경로는 /로 시작해야 합니다')
    decoded = urllib.parse.unquote(path.split('?', 1)[0])
    if any(x in ('.', '..') for x in decoded.split('/')) or '\\' in decoded:
        raise ValueError('경로 탐색이 의심되는 API 경로입니다')
    return path


def validate_spec(spec, allow_writes=False):
    if not isinstance(spec, dict):
        raise ValueError('설정 JSON의 최상위는 객체여야 합니다')
    base = validate_base(spec.get('base_url'))
    cases = spec.get('cases')
    if not isinstance(cases, list) or not 1 <= len(cases) <= 100:
        raise ValueError('cases는 1~100개의 테스트 목록이어야 합니다')
    result = []
    for i, case in enumerate(cases, 1):
        if not isinstance(case, dict):
            raise ValueError(f'case {i}: 객체여야 합니다')
        method = case.get('method', 'GET')
        if not isinstance(method, str) or method not in ALLOWED_METHODS:
            raise ValueError(f'case {i}: 허용되지 않은 HTTP 메서드')
        if method in WRITE_METHODS and not allow_writes:
            raise ValueError(f'case {i}: 쓰기 요청은 --allow-writes가 필요합니다')
        path = validate_path(case.get('path'))
        expected = case.get('expect_status')
        if type(expected) is not int or not 100 <= expected <= 599:
            raise ValueError(f'case {i}: expect_status(100~599) 필요')
        fields = case.get('expect_json_fields', [])
        if not isinstance(fields, list) or any(not isinstance(f, str) or not f for f in fields):
            raise ValueError(f'case {i}: expect_json_fields는 문자열 목록이어야 합니다')
        if method in ('GET', 'HEAD') and 'body' in case:
            raise ValueError(f'case {i}: GET/HEAD 요청에 body를 넣지 마세요')
        if 'name' in case and not isinstance(case['name'], str):
            raise ValueError(f'case {i}: name은 문자열이어야 합니다')
        if 'expect_json' in case and not isinstance(case['expect_json'], (dict, list)):
            raise ValueError(f'case {i}: expect_json은 JSON 객체나 배열이어야 합니다')
        result.append(case)
    return base, result


def has_path(value, dotted):
    cursor = value
    for key in dotted.split('.'):
        if isinstance(cursor, dict) and key in cursor:
            cursor = cursor[key]
        elif isinstance(cursor, list) and key.isdecimal() and int(key) < len(cursor):
            cursor = cursor[int(key)]
        else:
            return False
    return True


def subset(expected, actual):
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(k in actual and subset(v, actual[k]) for k, v in expected.items())
    return type(expected) is type(actual) and expected == actual


def execute(spec, timeout=5.0, allow_writes=False):
    if not (0 < timeout <= 30):
        raise ValueError('timeout은 0초 초과·30초 이하여야 합니다')
    base, cases = validate_spec(spec, allow_writes)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), RefuseRedirect)
    results = []
    for i, case in enumerate(cases, 1):
        method = case.get('method', 'GET')
        body = None
        headers = {}
        if 'body' in case:
            body = json.dumps(case['body']).encode('utf-8')
            headers['Content-Type'] = 'application/json'
        request = urllib.request.Request(base + case['path'], data=body, method=method, headers=headers)
        status, raw, err = None, b'', None
        try:
            try:
                response = opener.open(request, timeout=timeout)
            except urllib.error.HTTPError as exc:
                response = exc
            with response:
                status = response.status
                raw = response.read(MAX_RESPONSE + 1)
                if len(raw) > MAX_RESPONSE:
                    err = '응답 본문이 1MiB를 초과합니다'
        except (OSError, ValueError, urllib.error.URLError) as exc:
            err = f'HTTP 요청 실패: {type(exc).__name__}: {exc}'
        if err is None and status != case['expect_status']:
            err = f"상태 코드 불일치: 기대 {case['expect_status']}, 실제 {status}"
        if err is None and ('expect_json' in case or case.get('expect_json_fields')):
            try:
                actual = json.loads(raw.decode('utf-8'))
                if 'expect_json' in case and not subset(case['expect_json'], actual):
                    err = '예상 JSON 내용과 불일치'
                if err is None:
                    for name in case.get('expect_json_fields', []):
                        if not has_path(actual, name):
                            err = f'JSON 필드 누락: {name}'
                            break
            except (UnicodeError, ValueError):
                err = '응답이 유효한 JSON이 아닙니다'
        results.append({'name': case.get('name', f'case-{i}'), 'method': method,
                        'path': case['path'], 'expected_status': case['expect_status'],
                        'actual_status': status, 'passed': err is None, 'error': err})
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, help='검사할 엔드포인트 명세 JSON')
    parser.add_argument('--allow-writes', action='store_true', help='POST/PATCH/PUT/DELETE 호출 명시적 허용')
    parser.add_argument('--timeout', type=float, default=5.0)
    parser.add_argument('--format', choices=['text', 'json'], default='text')
    args = parser.parse_args(argv)
    try:
        spec = json.loads(Path(args.config).read_text(encoding='utf-8'))
        results = execute(spec, args.timeout, args.allow_writes)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.exit(2, f'설정 또는 실행 오류: {exc}\n')
    if args.format == 'json':
        print(json.dumps({'results': results, 'passed': sum(x['passed'] for x in results),
                          'failed': sum(not x['passed'] for x in results)}, ensure_ascii=False, indent=2))
    else:
        for x in results:
            print(f"[{'PASS' if x['passed'] else 'FAIL'}] {x['name']} {x['method']} {x['path']} "
                  f"(status {x['actual_status']}, expected {x['expected_status']})" +
                  (f" — {x['error']}" if x['error'] else ''))
        print(f"검사 {len(results)}개: 통과 {sum(x['passed'] for x in results)}, 실패 {sum(not x['passed'] for x in results)}")
    return 0 if all(x['passed'] for x in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
