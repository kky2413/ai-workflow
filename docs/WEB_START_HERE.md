# 웹사이트 과제 — 가장 먼저 읽을 안내

**이 문서만 먼저 확인하고, 필요한 자료로 이동하세요.** 실제 과제 README와 기존 코드가 항상 우선입니다.

## 30초 선택표

| 실제 상황 | 먼저 할 일 | 관련 자료 |
| --- | --- | --- |
| 기존 React/Vite/Next/Vue 프로젝트 | 현재 프레임워크·실행 명령·화면·API·데이터 확인 후 기존 스택 유지 | [실전 절차](WEB_APP_PLAYBOOK.md) |
| 이미 있는 웹사이트가 고장 남 | 오류 재현 → 최소 수정 → 회귀 검증 | [웹 검증](WEB_TESTING.md) |
| 빈 폴더에서 새 웹사이트 작성 | 필수 사용자 행동·저장 규칙을 확인하고 가장 작은 완성 흐름 구현 | [Node 연습 예제](../demo-web/README.md) |
| 알고리즘·스케줄링을 웹으로 제공 | 실제 계산·제약조건·해의 유효성부터 만들고 API와 UI에 연결 | [실전 절차](WEB_APP_PLAYBOOK.md) |
| Node는 있고 Python은 없음 | 실제 package.json 스크립트와 node --test 활용 | [검증](WEB_TESTING.md) |

## 실제 프로젝트에서 먼저 볼 것

Bash:
~~~sh
pwd
ls -la
cat README.md
node --version
npm --version
~~~

PowerShell:
~~~powershell
Get-Location
Get-ChildItem -Force
Get-Content README.md
node --version
npm --version
~~~

package.json이 있다면 **그 파일의 scripts**를 확인하고 실제 프로젝트에 정의된 명령만 선택합니다. Python이 이미 설치돼 있다면 읽기 전용 구조 조사:

~~~sh
python3 /참고폴더/ai-workflow/scripts/web_project_audit.py /실제/프로젝트/폴더
~~~

Python이 없으면 무리하게 설치하지 말고 Codex의 파일 탐색과 기존 Node 도구를 사용하세요.

## 첫 Codex 요청

> 실제 과제 README와 현재 웹 프로젝트의 진입점, 프레임워크, 실행 스크립트, 화면 목록, API, 저장 방식과 필수 사용자 행동을 분석해 주세요. 실제 입력→처리/저장→화면 출력까지 이어지는 가장 작은 기능을 제안하고 검증 방법을 설명해 주세요. 아직 수정하지 말고, 참고 키트 전체를 복사하거나 기존 스택을 교체하지 마세요.

## 제출 전 5문항

1. 실제 서버가 켜지고 제공된 브라우저 미리보기에서 열리는가?
2. 필수 버튼·입력은 실제 처리·저장·화면 갱신과 연결되는가?
3. 새로고침·잘못된 입력·데이터 없음·서버 오류를 확인했는가?
4. 출력 경로·파일 형식·실제 업무 값이 README와 일치하는가?
5. 실행한 테스트와 **본인이 직접 확인한 UI**를 구분해 기록했는가?

[웹 개발 절차](WEB_APP_PLAYBOOK.md) · [검증](WEB_TESTING.md) · [Codex 프롬프트](WEB_PROMPTS.md)
