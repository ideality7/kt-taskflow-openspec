## Context

TaskFlow MVP는 소규모 팀(3~5인)을 위한 칸반+채팅 통합 웹앱이다. 기존 도구가 없는 그린필드 프로젝트이며, 2일(Day 2) 내 완성이 목표다. 한국어 사용자만 대상으로 하며, 팀당 최대 5명·동시 접속 50명 이내를 전제한다.

기술 제약: 무료 티어(Vercel Hobby + Neon Free) 한도 내에서 운영해야 하므로 마이크로서비스·WebSocket·테스트 자동화는 범위 외다.

## Goals / Non-Goals

**Goals:**
- FastAPI 단일 서버에서 정적 파일(Vanilla JS+Tailwind)과 REST API를 함께 서빙
- 로컬은 SQLite, 배포는 Neon(PostgreSQL)으로 SQLAlchemy로 양쪽 호환
- JWT(24h 만료, 갱신 없음) + bcrypt로 인증·보안 처리
- 18개 REST API 엔드포인트 정확히 구현 (Auth 4 + Team 4 + Task 6 + Chat 4)
- Vercel 배포 시 FE+BE 일체형으로 한 번에 배포

**Non-Goals:**
- WebSocket 실시간 메시지 (5초 폴링으로 대체)
- 이메일·SMS·푸시 알림
- 파일 첨부, 전문 검색
- 페이지별 권한 세분화, 다국어, 테스트 자동화

## Decisions

### 1. FastAPI StaticFiles 일체형 구조

**결정**: FastAPI 한 프로세스에서 `/api/*` REST + `StaticFiles`로 Vanilla JS 서빙  
**이유**: Vercel의 FE+BE 분리 배포 복잡도를 제거하고 Day 2 내 완성 가능성을 높임. Next.js 등 프레임워크 도입 시 학습 비용 발생.  
**대안**: FE Vercel Static + BE Vercel Functions 분리 → CORS 설정 복잡, 빌드 파이프라인 이중화

### 2. SQLAlchemy + 환경변수 DB URL 전환

**결정**: `DATABASE_URL` 환경변수로 로컬(sqlite:///./taskflow.db) ↔ Neon(postgresql://...) 전환  
**이유**: 코드 변경 없이 로컬/배포 환경 전환 가능. SQLAlchemy가 SQLite·PostgreSQL 양쪽 지원.  
**대안**: 환경별 별도 코드 분기 → 유지보수 부담

### 3. JWT 24h 단일 토큰, 갱신 없음

**결정**: access token만 발급, refresh token·갱신 API 없음  
**이유**: MVP 범위 내 단순성 우선. 24h 만료 후 재로그인 허용 가능.  
**대안**: refresh token → 구현 복잡도 증가, Day 2 범위 초과

### 4. 채팅 5초 폴링

**결정**: `GET /teams/{id}/messages?since=<ISO>` 를 클라이언트 setInterval(5000)으로 호출  
**이유**: WebSocket 인프라 설정·비용 없이 실시간에 준하는 UX 제공. Free 티어에서 안정적.  
**대안**: WebSocket → Vercel Free에서 지속 연결 유지 불안정

### 5. 초대코드 신뢰 모델

**결정**: 초대코드(XXXX-XXXX 형식) 소지자는 인증 없이 팀 합류 가능  
**이유**: MVP 단순 온보딩 우선. 코드 유출 위험은 Out of Scope로 명시.  
**대안**: 이메일 초대 → 이메일 서버 필요, 범위 초과

## Risks / Trade-offs

- [SQLite 동시성] SQLite는 동시 쓰기 잠금 발생 → 로컬 개발 전용으로만 사용, 배포는 반드시 Neon
- [JWT localStorage] XSS 취약 가능성 → MVP 전제(신뢰 환경)로 명시, httpOnly cookie는 범위 외
- [5초 폴링 부하] 50명 동시 접속 시 초당 10 req/s → Neon Free 연결 한도(~10) 초과 가능 → connection pool size=1 설정으로 완화
- [Vercel Free 타임아웃] 300s 제한 → FastAPI cold start 포함해도 충분
