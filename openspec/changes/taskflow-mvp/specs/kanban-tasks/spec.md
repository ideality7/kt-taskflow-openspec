## ADDED Requirements

### Requirement: 태스크 생성
팀 소속 사용자는 해당 팀에 태스크를 추가할 수 있어야 한다(SHALL).
- 최초 상태는 반드시 TODO여야 한다(MUST).
- 생성자 ID가 creator_id로 저장되어야 한다(MUST).

#### Scenario: 정상 태스크 생성
- **WHEN** POST /teams/{id}/tasks {title: "API 설계"} 요청
- **THEN** HTTP 201, {id, team_id, title, status: "TODO", creator_id} 반환

#### Scenario: 제목 미입력
- **WHEN** POST /teams/{id}/tasks {title: ""} 요청
- **THEN** HTTP 422, {code: "VALIDATION_ERROR", msg: "태스크 제목을 입력해주세요"} 반환

### Requirement: 태스크 목록 조회
팀 소속 사용자는 해당 팀의 모든 태스크를 조회할 수 있어야 한다(SHALL).

#### Scenario: 태스크 목록 조회
- **WHEN** GET /teams/{id}/tasks 요청
- **THEN** HTTP 200, [{id, team_id, title, status, creator_id}] 배열 반환 (TODO/DOING/DONE 전체)

### Requirement: 태스크 상태 변경
팀 소속 사용자는 태스크를 TODO → DOING → DONE 중 임의 상태로 이동할 수 있어야 한다(SHALL).
- 유효한 상태값은 TODO, DOING, DONE 세 가지뿐이다(MUST).

#### Scenario: 상태 변경 성공
- **WHEN** PUT /tasks/{id} {status: "DOING"} 요청
- **THEN** HTTP 200, {id, title, status: "DOING", team_id, creator_id} 반환

#### Scenario: 유효하지 않은 상태값
- **WHEN** PUT /tasks/{id} {status: "INVALID"} 요청
- **THEN** HTTP 422, {code: "VALIDATION_ERROR", msg: "상태는 TODO, DOING, DONE 중 하나여야 합니다"} 반환

### Requirement: 태스크 제목 수정
팀 소속 사용자는 태스크 제목을 수정할 수 있어야 한다(SHALL).

#### Scenario: 제목 수정 성공
- **WHEN** PUT /tasks/{id} {title: "수정된 제목"} 요청
- **THEN** HTTP 200, {id, title: "수정된 제목", status, team_id, creator_id} 반환

### Requirement: 태스크 단건 조회
팀 소속 사용자는 특정 태스크를 ID로 조회할 수 있어야 한다(SHALL).

#### Scenario: 정상 조회
- **WHEN** GET /tasks/{id} 요청
- **THEN** HTTP 200, {id, team_id, title, status, creator_id} 반환

#### Scenario: 존재하지 않는 태스크
- **WHEN** 존재하지 않는 ID로 GET /tasks/{id} 요청
- **THEN** HTTP 404, {code: "NOT_FOUND", msg: "태스크를 찾을 수 없습니다"} 반환

### Requirement: 태스크 삭제
팀 소속 사용자는 태스크를 삭제할 수 있어야 한다(SHALL).

#### Scenario: 정상 삭제
- **WHEN** DELETE /tasks/{id} 요청
- **THEN** HTTP 200, {msg: "태스크가 삭제되었습니다"} 반환

#### Scenario: 존재하지 않는 태스크 삭제
- **WHEN** 존재하지 않는 ID로 DELETE /tasks/{id} 요청
- **THEN** HTTP 404, {code: "NOT_FOUND", msg: "태스크를 찾을 수 없습니다"} 반환
