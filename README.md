# AI Workflow — 분석 · 웹 개발 · 검증

**낯선 프로젝트를 분석하고, 필요한 기능을 구현하고, 실제 결과를 검증할 때 선택해 사용하는 작은 도구 모음**입니다. 특정 과제의 정답이나 완성 프로젝트가 아닙니다.

**처음에는 [START_HERE.md](docs/START_HERE.md) 하나만 읽으세요.** 실제 과제의 README·운영 규칙·기존 코드가 이 저장소보다 우선합니다.

## 목적별 바로 가기

| 실제 해야 하는 일 | 먼저 볼 문서 | 필요한 경우만 실행 |
| --- | --- | --- |
| 처음 받은 프로젝트 파악 | [처음 시작](docs/START_HERE.md) | `inventory.py`, `environment_check.py` |
| CSV·JSON 분석·연결·보고서 | [업무별 절차](docs/WORKFLOWS.md) | `data_profile.py`, `join_audit.py`, `quality_report.py` |
| 웹사이트 제작·기존 코드 수정 | [웹 개발 가이드](docs/WEB_APP_PLAYBOOK.md) | `web_project_audit.py`, `web_api_check.py` |
| 실행·API·화면 검증 | [웹 검증](docs/WEB_TESTING.md) | 기존 프로젝트 테스트, 실제 브라우저 |
| Codex에게 일 맡기기 | [프롬프트 예시](docs/PROMPT_EXAMPLES.md) | 현재 과제에 맞는 요청만 선택 |
| 개별 명령어 보기 | [도구 목록](docs/TOOL_CATALOG.md) | 필요한 도구 하나만 사용 |

추가 참고: [데이터 정확성](docs/DATA_INTEGRITY.md), [보고서 설정](docs/REPORT_GUIDE.md), [Codex 명령어](docs/CODEX_COMMANDS.md), [안전 수칙](docs/SAFE_USE.md), [공개 참고 자료](docs/WEB_UPSTREAM_RESEARCH.md).

## 구성

~~~text
ai-workflow/
├─ README.md       여기서 시작
├─ AGENTS.md       이 저장소 안에서만 적용되는 작업 원칙
├─ scripts/        독립형 Python 도구 14개 (공통 모듈 포함)
├─ tests/          도구 검증용 Python 테스트
├─ docs/           짧은 안내서와 선택형 기록 양식
└─ skills/         필요할 때 직접 읽는 선택형 Codex 절차서
~~~

**React 앱·완성형 웹사이트를 제공하거나 과제 프로젝트를 자동 생성하지 않습니다.** 실제 웹사이트는 주어진 프로젝트와 요구사항에 맞춰 구현해야 합니다.

## 사용 예시

실제 프로젝트와 다른 폴더에 Clone한 뒤 필요한 도구만 참고합니다.

~~~sh
git clone --depth 1 https://github.com/kky2413/ai-workflow.git ai-workflow-reference
python3 ai-workflow-reference/scripts/environment_check.py
python3 -m unittest discover -s ai-workflow-reference/tests -v
~~~

Windows에서는 `python` 명령을 사용할 수 있습니다. **Python이 없으면 무리하게 설치하거나 우회하지 마세요.** Codex의 파일 읽기와 기존 프로젝트 실행 명령을 우선합니다. 이 저장소의 테스트 통과는 실제 과제의 완성·정확성을 증명하지 않습니다.

## 지켜야 할 원칙

- 실제 프로젝트 README와 제출 경로가 최우선. 참고 저장소 전체를 과제에 복사하지 않습니다.
- 확인되지 않은 기준·정답·결과를 만들지 않고, 원본 데이터를 보존합니다.
- **구현 → 실제 실행 → 기대값과 비교 → 실패 수정 → 재검증**을 반복합니다.
- AI 사용·외부 네트워크·설치·브라우저 자동화는 **해당 작업 환경의 허용 범위**를 따릅니다.
- 실자료, 비밀 키, 과제 산출물을 이 공개 저장소로 Push하지 않습니다.
