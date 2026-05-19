## 1. 프로젝트 초기 설정

- [ ] 1.1 FastAPI 프로젝트 디렉토리 구조 생성 (backend/, frontend/static/)
- [ ] 1.2 requirements.txt 작성 (fastapi, uvicorn, sqlalchemy, passlib[bcrypt], python-jose, python-dotenv)
- [ ] 1.3 .env 파일 생성 (DATABASE_URL, JWT_SECRET_KEY)
- [ ] 1.4 SQLAlchemy Base 및 engine 설정 (DATABASE_URL 환경변수로 SQLite↔Neon 전환)
- [ ] 1.5 4개 DB 모델 정의 (users, teams, tasks, messages)
- [ ] 1.6 main.py에 FastAPI 앱 생성 + StaticFiles 마운트 + CORS 설정

## 2. 인증 API (Auth 4개)

- [ ] 2.1 POST /auth/signup — 회원가입, bcrypt 해시, JWT 발급, 201 반환
- [ ] 2.2 POST /auth/login — 이메일·비밀번호 검증, JWT 발급, 200 반환
- [ ] 2.3 GET /auth/me — JWT 검증 의존성(get_current_user) 구현 및 사용자 정보 반환
- [ ] 2.4 POST /auth/logout — 200 반환 (클라이언트 측 토큰 삭제 안내)

## 3. 팀 API (Team 4개)

- [ ] 3.1 POST /teams — 팀 생성, 초대코드(XXXX-XXXX) 자동 발급, 201 반환
- [ ] 3.2 GET /teams — 내 소속 팀 목록 반환
- [ ] 3.3 POST /teams/join — 초대코드로 팀 합류, 중복 합류 409 처리
- [ ] 3.4 GET /teams/{id}/members — 팀 멤버 목록 반환, 비소속 403 처리

## 4. 칸반 태스크 API (Task 6개)

- [ ] 4.1 POST /teams/{id}/tasks — 태스크 생성, 초기 상태 TODO, 201 반환
- [ ] 4.2 GET /teams/{id}/tasks — 팀 전체 태스크 목록 반환
- [ ] 4.3 GET /tasks/{id} — 태스크 단건 조회, 404 처리
- [ ] 4.4 PUT /tasks/{id} status 변경 — TODO/DOING/DONE 유효성 검사 포함
- [ ] 4.5 PUT /tasks/{id} title 수정 — 제목 변경
- [ ] 4.6 DELETE /tasks/{id} — 태스크 삭제, 404 처리

## 5. 채팅 API (Chat 4개)

- [ ] 5.1 POST /teams/{id}/messages — 메시지 전송, 1000자 제한, 201 반환
- [ ] 5.2 GET /teams/{id}/messages?since= — since 파라미터 기반 폴링, ISO 8601 필터링
- [ ] 5.3 GET /messages/{id} — 메시지 단건 조회, 404 처리
- [ ] 5.4 DELETE /messages/{id} — 메시지 삭제

## 6. 프론트엔드 4개 화면 (Vanilla JS + Tailwind)

- [ ] 6.1 로그인 화면 (index.html) — 이메일·비밀번호 입력, 로그인·회원가입 버튼, JWT localStorage 저장
- [ ] 6.2 팀 선택 화면 (teams.html) — 내 팀 목록, 팀 만들기, 초대코드 입력·합류 버튼
- [ ] 6.3 칸반 화면 (kanban.html) — TODO/DOING/DONE 3컬럼, 태스크 카드, 드래그&드롭 상태 이동
- [ ] 6.4 채팅 화면 (chat.html) — 메시지 리스트, 발신자+시각 표시, 입력창, 5초 setInterval 폴링
- [ ] 6.5 공통 JS 모듈 (api.js) — fetch 래퍼, JWT Authorization 헤더 자동 주입, 에러 처리

## 7. 배포 설정

- [ ] 7.1 vercel.json 작성 — Python 런타임, FastAPI 엔트리포인트 설정
- [ ] 7.2 Vercel 환경변수 설정 — DATABASE_URL(Neon Pooled), JWT_SECRET_KEY
- [ ] 7.3 Neon DB 연결 확인 및 테이블 초기화 (배포 후 /docs에서 API 동작 검증)
- [ ] 7.4 vercel deploy --prod 실행 및 5분 이내 배포 완료 확인
