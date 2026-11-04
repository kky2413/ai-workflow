# 처음 시작하기 — 어느 자료를 읽어야 할까요?

**답은 하나입니다. 실제 과제의 README부터 확인하세요.** 이 저장소는 참고용입니다.

## 1. 실제 폴더와 실행 환경 확인

Bash/일반 터미널:

~~~sh
pwd
ls -la
cat README.md
~~~

Windows PowerShell:

~~~powershell
Get-Location
Get-ChildItem -Force
Get-Content README.md
~~~

현재 위치가 **실제 과제 루트**인지 확인하고 필수 파일명, 저장 경로, 구현·검증 조건을 적습니다. 이미 있는 package.json, requirements.txt, 테스트, API를 먼저 살펴봅니다.

## 2. 목적에 맞게 딱 하나부터 선택

| 상황 | 읽을 문서 | 관련 도구 |
| --- | --- | --- |
| 데이터·보고서 | [업무별 절차](WORKFLOWS.md) | `data_profile.py`, `join_audit.py`, `quality_report.py` |
| 웹사이트·API | [웹 개발](WEB_APP_PLAYBOOK.md) | `web_project_audit.py`, `web_api_check.py` |
| 결과 검증 | [웹 검증](WEB_TESTING.md) 또는 실제 프로젝트 테스트 | `verify_outputs.py` 등 |
| Codex 지시 | [프롬프트 예시](PROMPT_EXAMPLES.md) | 필요한 질문 하나만 사용 |
| 실행 명령·제약 | [도구 목록](TOOL_CATALOG.md) | 각 도구의 --help |

**Python이 없어도 Node/React 프로젝트는 해당 프로젝트에 준비된 명령으로 작업할 수 있습니다.** 모든 도구를 실행하거나 패키지를 설치할 필요는 없습니다.

## 3. 필요할 때만 별도 폴더에 Clone

~~~sh
git clone --depth 1 https://github.com/kky2413/ai-workflow.git ai-workflow-reference
~~~

프로젝트 폴더와 분리해 보관합니다. 참고용 AGENTS.md·Skill이 다른 작업 폴더에 자동 적용된다고 가정하지 마세요.

## 4. Codex에 첫 요청

> 현재 실제 프로젝트 README와 기존 코드를 읽고 목표·필수 기능·입력 자료·결과 경로·검증 방법을 정리해 주세요. 모호한 업무 기준은 질문으로 분리하고, 가장 작은 정상 동작부터 만들 계획을 제시하세요. 아직 코드는 수정하지 마세요. 참고 키트 전체를 복사하거나 설치하지 마세요.

## 5. 완료 기준

- 요구사항에 맞는 **실제 입력 → 처리 → 출력**이 존재하는가?
- 정상·경계·오류 사례를 **실제로 실행**했는가?
- 예상값과 실제 결과를 비교했는가?
- 웹은 사람이 실제 화면을 열어 필수 버튼·새로고침을 확인했는가?
- 테스트 성공과 미검증 항목을 구분했는가?

간단한 기록이 필요하면 [작업 계획](templates/TASK_PLAN.md), [데이터 계약](templates/DATA_CONTRACT.md), [최종 점검](templates/FINAL_CHECK.md) 중 필요한 것만 사용하세요.
