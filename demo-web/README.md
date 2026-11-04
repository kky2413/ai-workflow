# 범용 웹 개발 연습 예제 — Node.js 표준 라이브러리만 사용

**과제 제출물이 아닌 독립 연습 샘플**입니다. 기존 프로젝트가 있다면 실제 README와 코드를 우선하세요. 이 폴더를 기존 프로젝트 위에 통째로 복사하지 마세요.

## 연습할 기능

- 모바일 대응 화면에서 항목 생성·조회·수정·삭제·완료 변경·검색
- 사용자 클릭 → fetch → Node HTTP API → 로컬 JSON 파일 저장 → 화면 갱신
- 입력 오류·서버 장애 표시, HTTP 상태 코드, 키보드 포커스와 기본 접근성
- Node 기본 테스트로 실제 HTTP 호출과 파일 저장까지 검증

## 설치 없이 실행

Node.js 20 이상이 이미 설치된 경우:

~~~sh
cd demo-web
node --version
npm run dev
~~~

브라우저에서 http://127.0.0.1:3000 을 엽니다. 별도 터미널에서 테스트합니다.

~~~sh
npm test
python3 ../scripts/web_api_check.py --config api-check.example.json
~~~

웹 실행과 npm test에는 **Python이 필요하지 않습니다.** Python은 추가 API 검사 도구에만 필요합니다. npm install도 필요하지 않습니다.

플랫폼 미리보기에서 허용될 때만 HOST·PORT를 실제 환경에 맞춰 지정합니다.

Bash:
~~~sh
HOST=0.0.0.0 PORT=3000 npm run dev
~~~

PowerShell:
~~~powershell
$env:HOST = '0.0.0.0'; $env:PORT = '3000'; npm run dev
~~~

0.0.0.0은 외부 네트워크에도 노출될 수 있으므로 개인 PC에서는 기본값 127.0.0.1을 권장합니다. 외부 배포를 위한 공개 서비스가 아닙니다.

## 구성과 API

| 파일 | 역할 |
| --- | --- |
| server.mjs | HTTP 라우트·요청 입력 제한·정적 파일 제공 |
| store.mjs | CRUD·입력 검증·로컬 JSON 저장 |
| public/index.html | 폼·검색·목록·수정 대화창·상태 안내 |
| public/styles.css | 데스크톱·모바일 화면과 포커스 스타일 |
| public/app.js | 실제 API 요청·화면 동기화·오류 알림 |
| tests/server.test.mjs | HTTP·CRUD·파일 저장·잘못된 입력 테스트 |
| api-check.example.json | GET API 3개 검사 설정 |

| 메서드 | 경로 | 기능 |
| --- | --- | --- |
| GET | /api/health | 서버 상태 |
| GET | /api/items | 저장된 항목 조회 |
| POST | /api/items | title 문자열 항목 추가 |
| PATCH | /api/items/:id | title 수정 또는 done 상태 변경 |
| DELETE | /api/items/:id | 삭제 |

저장 파일은 **demo-web/data/items.json**입니다. 프로그램이 추가·수정·삭제를 수행하면 생성됩니다. 공개 저장소에 실사용자 데이터를 저장하지 마세요.

## 직접 확인할 화면 7가지

1. 항목을 추가하고 새로고침 후 유지되는지
2. 수정한 제목을 서버에서 다시 읽어 확인할 수 있는지
3. 완료/완료 취소 후 전체·진행 중·완료 개수가 맞는지
4. 검색으로 목록이 필터링되는지
5. 삭제 후 다시 조회해도 해당 항목이 없는지
6. 빈 제목·서버 중단 상황에서 오류가 적절한지
7. 좁은 화면에서 버튼을 누를 수 있고 키보드로 조작할 수 있는지

**테스트 통과와 시각적 UI 검증을 구분해야 합니다.** 실제 화면은 사용자가 직접 열고 조작하기 전까지 미검증 상태입니다.

## 명확한 한계

- 계정·인증·권한·감사 로그·동시 수정 충돌 처리·실서비스 보안·DB 백업이 없습니다.
- JSON 파일 단일 프로세스 저장 예제입니다. 여러 서버/사용자가 동시에 쓰는 운영 환경에는 적합하지 않습니다.
- 일시적인 클라우드 실행 환경에서 파일 저장의 영구성은 보장되지 않습니다.
- 특정 업무의 규칙·계산·실제 API 데이터가 포함돼 있지 않습니다. **사이트 예제 자체가 실제 과제 답안은 아닙니다.**
- 외부 API·CDN·유료 모델·패키지 설치가 필요하지 않습니다.

[웹 과제 시작](../docs/WEB_START_HERE.md) · [검증 절차](../docs/WEB_TESTING.md)
