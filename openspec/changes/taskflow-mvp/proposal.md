## Why

소규모 팀(3~5인)이 업무 진행 상황을 한 화면에서 추적할 수 있는 도구가 없어 슬랙·스프레드시트를 병행하는 비효율이 발생한다. TaskFlow MVP는 칸반 보드와 실시간(폴링) 채팅을 단일 화면에 통합해 이 문제를 해결한다.

## What Changes

- 회원가입·로그인·JWT 발급·비밀번호 bcrypt 해시 처리 신규 구현
- 팀 생성·초대코드 발급·합류·멤버 목록 기능 신규 구현
- TODO / DOING / DONE 3컬럼 칸반 보드(태스크 추가·상태 이동·삭제) 신규 구현
- 팀 단위 채팅 송수신(5초 폴링, 발신자·시각 표시) 신규 구현
- 로컬 SQLite + 배포 Neon(Vercel Storage) 이중 DB 환경 구성
- Vercel(FE+BE 일체형) 자동 배포 파이프라인 구성

## Capabilities

### New Capabilities

- `user-auth`: 회원가입, 로그인, JWT 발급, bcrypt 비밀번호 해시, 로그아웃 (Auth 4개 API)
- `team-management`: 팀 생성, 초대코드 발급·합류, 멤버 목록 조회 (Team 4개 API)
- `kanban-tasks`: TODO/DOING/DONE 3컬럼 태스크 CRUD 및 상태 이동 (Task 6개 API)
- `team-chat`: 팀 채팅 송수신, 5초 폴링, 발신자·시각 표시 (Chat 4개 API)
- `deployment`: FastAPI StaticFiles 일체형 로컬 실행 + Vercel 배포 + Neon DB 연결

### Modified Capabilities

## Impact

- **Backend**: FastAPI (Python) — 18개 REST API 엔드포인트, SQLAlchemy ORM, bcrypt, python-jose
- **Frontend**: Vanilla JS + Tailwind CSS — 4개 화면(로그인, 팀 선택, 칸반, 채팅), StaticFiles 서빙
- **DB**: 로컬 SQLite ↔ 배포 Neon(PostgreSQL), SQLAlchemy로 양쪽 호환 (4테이블: users, teams, tasks, messages)
- **배포**: Vercel(FE+BE) + Vercel Storage Neon Pooled 자동 주입
- **외부 의존성**: python-jose(JWT), passlib[bcrypt], sqlalchemy, fastapi, uvicorn
