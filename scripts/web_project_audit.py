#!/usr/bin/env python3
"""Read-only audit of a local web project's structure and run scripts."""
import argparse
import json
import os
from pathlib import Path

SKIP_DIRS = {'.git', 'node_modules', '.next', '.nuxt', '.svelte-kit', 'dist', 'build', 'coverage', '.venv', 'venv', '__pycache__', '.turbo'}
CANDIDATES = {'index.html', 'src/main.jsx', 'src/main.tsx', 'src/App.jsx', 'src/App.tsx',
              'app/page.tsx', 'app/page.jsx', 'pages/index.tsx', 'server.js', 'server.mjs',
              'src/index.ts', 'src/server.ts', 'app.py', 'main.py', 'requirements.txt'}
FRAMEWORKS = {'react', 'next', 'vue', 'nuxt', 'svelte', '@sveltejs/kit', 'vite',
              'express', 'fastify', 'astro', 'hono', 'playwright', 'vitest'}
LOCKFILES = {'package-lock.json': 'npm', 'pnpm-lock.yaml': 'pnpm', 'yarn.lock': 'yarn', 'bun.lock': 'bun', 'bun.lockb': 'bun'}
TEST_HINTS = ('.test.', '.spec.', 'test_', '_test.py')


def audit(root):
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError('프로젝트 폴더를 찾을 수 없습니다')
    paths = []
    packages = []
    scanned = 0
    truncated = False
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not (Path(current) / d).is_symlink())
        for filename in sorted(files):
            target = Path(current) / filename
            if target.is_symlink() or filename.startswith('.env') or filename == '.env':
                continue
            scanned += 1
            if scanned > 10000:
                truncated = True
                break
            rel = target.relative_to(root).as_posix()
            paths.append(rel)
            if filename == 'package.json' and len(packages) < 20:
                try:
                    package = json.loads(target.read_text(encoding='utf-8'))
                    if not isinstance(package, dict):
                        raise ValueError('package.json root must be object')
                    deps = set((package.get('dependencies') or {}).keys()) | set((package.get('devDependencies') or {}).keys())
                    scripts = package.get('scripts') or {}
                    packages.append({'path': rel, 'name': package.get('name', ''),
                                     'scripts': sorted(scripts) if isinstance(scripts, dict) else [],
                                     'frameworks': sorted(deps & FRAMEWORKS)})
                except (OSError, ValueError, AttributeError, TypeError) as exc:
                    packages.append({'path': rel, 'error': f'package.json 파싱 실패: {type(exc).__name__}'})
        if truncated:
            break
    file_set = set(paths)
    locks = sorted(k for k in LOCKFILES if k in file_set)
    entries = sorted(p for p in paths if p in CANDIDATES or p.split('/')[-1] in {'vite.config.js', 'vite.config.ts', 'next.config.js', 'next.config.mjs'})
    tests = sorted(p for p in paths if any(h in Path(p).name.lower() for h in TEST_HINTS))
    warnings = []
    if not packages and 'index.html' not in file_set and not any(x.endswith('/index.html') for x in paths):
        warnings.append('웹 프로젝트 진입점을 확인하지 못했습니다. 실제 README를 먼저 보세요.')
    if truncated:
        warnings.append('파일 10,000개를 넘겨 일부만 조사했습니다.')
    if len(locks) > 1:
        warnings.append('잠금 파일이 여러 개입니다. 제공 프로젝트에서 선택한 패키지 관리자를 확인하세요.')
    return {'root': str(root), 'files_scanned': len(paths), 'lockfiles': locks,
            'packages': packages, 'entrypoints': entries, 'tests': tests[:100],
            'test_count': len(tests), 'warnings': warnings}


def markdown(report):
    lines = [f"# 웹 프로젝트 구조 조사", "", f"- 폴더: `{report['root']}`",
             f"- 확인한 파일 수: {report['files_scanned']}",
             f"- 패키지 잠금 파일: {', '.join(report['lockfiles']) or '확인되지 않음'}", ""]
    for pkg in report['packages']:
        lines.extend([f"## {pkg['path']}", f"- 프레임워크·라이브러리: {', '.join(pkg.get('frameworks', [])) or '확인되지 않음'}",
                      f"- npm 스크립트 이름: {', '.join(pkg.get('scripts', [])) or '없음'}"])
        if 'error' in pkg:
            lines.append(f"- 경고: {pkg['error']}")
        lines.append('')
    lines.append('## 후보 진입점')
    lines.extend('- ' + p for p in report['entrypoints'])
    if not report['entrypoints']:
        lines.append('- 감지하지 못함')
    lines.extend(['', f"## 자동 테스트 후보 ({report['test_count']}개)"])
    lines.extend('- ' + p for p in report['tests'][:25])
    if report['test_count'] > 25:
        lines.append('- 나머지는 JSON 출력에서 확인')
    if report['warnings']:
        lines.extend(['', '## 주의', *('- ' + p for p in report['warnings'])])
    lines.extend(['', '**주의:** 읽기 전용 파일 조사 결과입니다. 서버 실행·테스트 통과·웹 화면 작동을 의미하지 않습니다.'])
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', help='조사할 실제 웹 프로젝트 폴더')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown')
    args = parser.parse_args(argv)
    try:
        result = audit(args.project)
    except (ValueError, OSError) as exc:
        parser.exit(2, f'오류: {exc}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.format == 'json' else markdown(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
