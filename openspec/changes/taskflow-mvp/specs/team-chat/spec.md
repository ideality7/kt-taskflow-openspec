## ADDED Requirements

### Requirement: 채팅 메시지 전송
팀 소속 사용자는 팀 채팅방에 메시지를 전송할 수 있어야 한다(SHALL).
- 메시지는 최대 1000자로 제한해야 한다(MUST).
- 발신자 ID와 전송 시각(ISO 8601)이 저장되어야 한다(MUST).

#### Scenario: 정상 메시지 전송
- **WHEN** POST /teams/{id}/messages {content: "안녕하세요"} 요청
- **THEN** HTTP 201, {id, team_id, user_id, content, created_at: "2024-01-01T09:00:00Z"} 반환

#### Scenario: 1000자 초과 메시지
- **WHEN** 1001자 content로 POST /teams/{id}/messages 요청
- **THEN** HTTP 422, {code: "VALIDATION_ERROR", msg: "메시지는 1000자 이하여야 합니다"} 반환

#### Scenario: 빈 메시지
- **WHEN** content: "" 로 POST /teams/{id}/messages 요청
- **THEN** HTTP 422, {code: "VALIDATION_ERROR", msg: "메시지를 입력해주세요"} 반환

### Requirement: 채팅 메시지 목록 조회 (폴링)
팀 소속 사용자는 특정 시각 이후의 메시지만 조회할 수 있어야 한다(SHALL).
- since 쿼리 파라미터(ISO 8601)가 없을 경우 전체 메시지를 반환해야 한다(SHALL).
- 클라이언트는 5초마다 since=<마지막 메시지 created_at>으로 폴링해야 한다(MUST).

#### Scenario: 전체 메시지 조회
- **WHEN** GET /teams/{id}/messages 요청 (since 없음)
- **THEN** HTTP 200, [{id, team_id, user_id, content, created_at}] 오래된 순 정렬 반환

#### Scenario: since 이후 메시지만 조회
- **WHEN** GET /teams/{id}/messages?since=2024-01-01T09:00:00Z 요청
- **THEN** HTTP 200, since 이후에 생성된 메시지만 반환 (없으면 [])

### Requirement: 채팅 메시지 단건 조회
팀 소속 사용자는 특정 메시지를 ID로 조회할 수 있어야 한다(SHALL).

#### Scenario: 정상 조회
- **WHEN** GET /messages/{id} 요청
- **THEN** HTTP 200, {id, team_id, user_id, content, created_at} 반환

#### Scenario: 존재하지 않는 메시지
- **WHEN** 존재하지 않는 ID로 GET /messages/{id} 요청
- **THEN** HTTP 404, {code: "NOT_FOUND", msg: "메시지를 찾을 수 없습니다"} 반환

### Requirement: 채팅 메시지 삭제
팀 소속 사용자는 메시지를 삭제할 수 있어야 한다(SHALL).

#### Scenario: 정상 삭제
- **WHEN** DELETE /messages/{id} 요청
- **THEN** HTTP 200, {msg: "메시지가 삭제되었습니다"} 반환
