# user-auth Specification

## Purpose
TBD - created by archiving change taskflow-mvp. Update Purpose after archive.
## Requirements
### Requirement: 회원가입
시스템은 이메일·비밀번호로 신규 사용자를 등록하고, 성공 시 JWT access token을 반환해야 한다(SHALL).
- 비밀번호는 bcrypt로 해시 저장해야 한다(MUST).
- 이미 존재하는 이메일은 409 Conflict를 반환해야 한다(SHALL).

#### Scenario: 정상 회원가입
- **WHEN** POST /auth/signup {email, password} 요청
- **THEN** HTTP 201, {token: "<JWT>", user: {id, email}} 반환

#### Scenario: 중복 이메일 가입 시도
- **WHEN** 이미 존재하는 이메일로 POST /auth/signup
- **THEN** HTTP 409, {code: "EMAIL_EXISTS", msg: "이미 사용 중인 이메일입니다"} 반환

### Requirement: 로그인
시스템은 이메일·비밀번호를 검증하고 JWT access token을 발급해야 한다(SHALL).
- JWT 만료는 24시간이며, 갱신(refresh) 없다(MUST).
- 잘못된 인증정보는 401 Unauthorized를 반환해야 한다(SHALL).

#### Scenario: 정상 로그인
- **WHEN** POST /auth/login {email, password} 요청
- **THEN** HTTP 200, {token: "<JWT>", user: {id, email}} 반환

#### Scenario: 잘못된 비밀번호
- **WHEN** 존재하는 이메일에 틀린 비밀번호로 POST /auth/login
- **THEN** HTTP 401, {code: "INVALID_CREDENTIALS", msg: "이메일 또는 비밀번호가 올바르지 않습니다"} 반환

### Requirement: 내 정보 조회
시스템은 유효한 JWT를 가진 사용자의 정보를 반환해야 한다(SHALL).
- Authorization: Bearer <token> 헤더가 없거나 만료된 경우 401을 반환해야 한다(MUST).

#### Scenario: 정상 조회
- **WHEN** 유효한 JWT로 GET /auth/me 요청
- **THEN** HTTP 200, {id, email, created_at} 반환

#### Scenario: 토큰 없음
- **WHEN** Authorization 헤더 없이 GET /auth/me 요청
- **THEN** HTTP 401, {code: "UNAUTHORIZED", msg: "인증이 필요합니다"} 반환

### Requirement: 로그아웃
시스템은 로그아웃 요청을 수락하고 클라이언트가 토큰을 폐기하도록 안내해야 한다(SHALL).
- 서버 측 토큰 블랙리스트 없음. 클라이언트 localStorage 삭제로 처리(MUST).

#### Scenario: 정상 로그아웃
- **WHEN** 유효한 JWT로 POST /auth/logout 요청
- **THEN** HTTP 200, {msg: "로그아웃 되었습니다"} 반환

### Requirement: 프론트엔드 라우트 보호
클라이언트는 인증이 필요한 페이지 접근 시 JWT 유무를 확인하고, 없으면 로그인 페이지로 리다이렉트해야 한다(SHALL).
- 보호 대상 페이지: teams.html, kanban.html, chat.html(MUST).
- 각 페이지 최상단 JS에서 localStorage의 JWT를 확인한다(MUST).
- JWT가 없으면 즉시 index.html(로그인)로 리다이렉트해야 한다(MUST).
- API 호출 결과 401을 받은 경우에도 index.html로 리다이렉트해야 한다(MUST).

#### Scenario: 미인증 상태로 보호 페이지 직접 접근
- **WHEN** localStorage에 JWT 없이 /kanban.html 직접 URL 입력
- **THEN** 즉시 /index.html로 리다이렉트, 칸반 화면 노출 안 됨

#### Scenario: 만료 토큰으로 API 호출
- **WHEN** 만료된 JWT로 GET /teams 호출 시 서버가 401 반환
- **THEN** 클라이언트가 localStorage JWT 삭제 후 /index.html로 리다이렉트

