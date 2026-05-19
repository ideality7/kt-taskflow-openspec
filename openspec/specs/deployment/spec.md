# deployment Specification

## Purpose
TBD - created by archiving change taskflow-mvp. Update Purpose after archive.
## Requirements
### Requirement: 로컬 일체형 실행
시스템은 로컬 환경에서 FastAPI 단일 프로세스로 FE(StaticFiles)+BE(REST API)를 동시에 서빙해야 한다(SHALL).
- DB는 SQLite(./taskflow.db)를 사용해야 한다(MUST).
- `uvicorn main:app --reload` 한 명령으로 실행 가능해야 한다(MUST).

#### Scenario: 로컬 서버 기동
- **WHEN** uvicorn main:app --reload 실행
- **THEN** http://localhost:8000 에서 Vanilla JS 프론트엔드 접근 가능, /api/* 엔드포인트 응답 정상

#### Scenario: 로컬 DB 초기화
- **WHEN** 서버 최초 기동
- **THEN** taskflow.db 파일 자동 생성, 4개 테이블(users, teams, tasks, messages) 자동 마이그레이션

### Requirement: Vercel 배포 (FE+BE 일체형)
시스템은 Vercel에 FastAPI 앱 전체를 단일 배포로 올릴 수 있어야 한다(SHALL).
- vercel.json 또는 vercel.ts로 Python 런타임 설정을 해야 한다(MUST).
- 배포 완료까지 5분 이내여야 한다(MUST).

#### Scenario: Vercel 배포 성공
- **WHEN** vercel deploy --prod 실행
- **THEN** 5분 이내에 https://<project>.vercel.app 에서 앱 접근 가능

### Requirement: Neon PostgreSQL 연결 (배포 환경)
배포 환경에서 시스템은 Vercel Storage Neon의 Pooled Connection URL을 사용해야 한다(SHALL).
- DATABASE_URL 환경변수로 DB URL을 주입받아야 한다(MUST).
- SQLAlchemy가 SQLite ↔ PostgreSQL 전환을 코드 변경 없이 처리해야 한다(MUST).

#### Scenario: 환경변수로 DB 전환
- **WHEN** DATABASE_URL=postgresql://... 환경변수 설정 후 서버 기동
- **THEN** Neon DB에 연결되어 모든 API 정상 동작

#### Scenario: 환경변수 미설정 시 SQLite 폴백
- **WHEN** DATABASE_URL 환경변수 없음
- **THEN** 로컬 sqlite:///./taskflow.db 사용

