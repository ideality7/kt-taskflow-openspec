## ADDED Requirements

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
