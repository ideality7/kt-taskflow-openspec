## ADDED Requirements

### Requirement: 팀 생성
인증된 사용자는 팀을 생성하고, 시스템은 유일한 초대코드를 자동 발급해야 한다(SHALL).
- 생성자는 자동으로 해당 팀의 owner가 된다(MUST).
- 초대코드 형식: 대문자 영문(A-Z) + 숫자(2-9) 4자 + 하이픈 + 4자, 총 9자(XXXX-XXXX)(MUST).
- 혼동 문자(I, O, 0, 1)는 초대코드에 사용하지 않아야 한다(MUST).
- 초대코드는 대소문자 구분 없이 처리해야 한다(SHALL). 입력값을 대문자로 정규화한다.
- 초대코드는 DB 내 유일해야 하며, 충돌 시 재생성한다(MUST).

#### Scenario: 정상 팀 생성
- **WHEN** POST /teams {name: "개발팀"} 요청
- **THEN** HTTP 201, {id, name, invite_code: "ABCD-2345", owner_id} 반환 (I/O/0/1 미포함)

#### Scenario: 소문자 초대코드 입력 허용
- **WHEN** POST /teams/join {invite_code: "abcd-2345"} 요청 (소문자)
- **THEN** 대문자 "ABCD-2345"로 정규화되어 팀 합류 성공

#### Scenario: 팀명 미입력
- **WHEN** POST /teams {name: ""} 요청
- **THEN** HTTP 422, {code: "VALIDATION_ERROR", msg: "팀명을 입력해주세요"} 반환

### Requirement: 내 팀 목록 조회
인증된 사용자는 자신이 속한 팀 목록을 조회할 수 있어야 한다(SHALL).

#### Scenario: 팀 목록 조회
- **WHEN** GET /teams 요청
- **THEN** HTTP 200, [{id, name, invite_code, owner_id}] 배열 반환 (소속 팀만)

#### Scenario: 소속 팀 없음
- **WHEN** 아직 팀에 속하지 않은 사용자가 GET /teams 요청
- **THEN** HTTP 200, [] 빈 배열 반환

### Requirement: 초대코드로 팀 합류
사용자는 초대코드를 입력해 팀에 합류할 수 있어야 한다(SHALL).
- 이미 합류한 팀에 재가입 시도 시 409를 반환해야 한다(SHALL).
- 유효하지 않은 초대코드는 404를 반환해야 한다(SHALL).

#### Scenario: 정상 합류
- **WHEN** POST /teams/join {invite_code: "ABCD-1234"} 요청
- **THEN** HTTP 200, {id, name, invite_code, owner_id} 반환

#### Scenario: 존재하지 않는 초대코드
- **WHEN** POST /teams/join {invite_code: "ZZZZ-9999"} 요청
- **THEN** HTTP 404, {code: "TEAM_NOT_FOUND", msg: "유효하지 않은 초대코드입니다"} 반환

#### Scenario: 이미 합류한 팀
- **WHEN** 이미 속한 팀의 초대코드로 POST /teams/join
- **THEN** HTTP 409, {code: "ALREADY_MEMBER", msg: "이미 합류한 팀입니다"} 반환

### Requirement: 팀 멤버 목록 조회
팀 소속 사용자는 해당 팀의 멤버 목록을 조회할 수 있어야 한다(SHALL).
- 팀 비소속 사용자의 접근은 403을 반환해야 한다(MUST).

#### Scenario: 정상 조회
- **WHEN** 팀 소속 사용자가 GET /teams/{id}/members 요청
- **THEN** HTTP 200, [{id, email}] 배열 반환

#### Scenario: 비소속 사용자 접근
- **WHEN** 팀 미소속 사용자가 GET /teams/{id}/members 요청
- **THEN** HTTP 403, {code: "FORBIDDEN", msg: "팀 멤버만 접근할 수 있습니다"} 반환
