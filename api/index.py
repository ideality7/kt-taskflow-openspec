import os
import random
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

from api.database import get_db, engine, Base
from api.models import User, Team, TeamMember, Task, Message

Base.metadata.create_all(bind=engine)

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-key-change-in-prod")
ALGORITHM = "HS256"
INVITE_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # I, O, 0, 1 제외
VALID_STATUSES = {"TODO", "DOING", "DONE"}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer()

app = FastAPI(title="TaskFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 유틸리티 ───────────────────────────────────────────────────────

def fmt_dt(dt: datetime) -> Optional[str]:
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"


def create_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def generate_invite_code() -> str:
    return (
        "".join(random.choices(INVITE_CHARS, k=4))
        + "-"
        + "".join(random.choices(INVITE_CHARS, k=4))
    )


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "msg": "인증이 필요합니다"},
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "msg": "인증이 필요합니다"},
        )
    return user


def require_member(team_id: int, user: User, db: Session) -> TeamMember:
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id, TeamMember.user_id == user.id
    ).first()
    if not member:
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "msg": "팀 멤버만 접근할 수 있습니다"},
        )
    return member


# ── Pydantic 스키마 ────────────────────────────────────────────────

class AuthReq(BaseModel):
    email: str
    password: str

class TeamCreateReq(BaseModel):
    name: str

class TeamJoinReq(BaseModel):
    invite_code: str

class TaskCreateReq(BaseModel):
    title: str

class TaskUpdateReq(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None

class MessageCreateReq(BaseModel):
    content: str


# ── Auth ───────────────────────────────────────────────────────────

@app.post("/auth/signup", status_code=201)
def signup(req: AuthReq, db: Session = Depends(get_db)):
    if not req.email or not req.password:
        raise HTTPException(
            status_code=422,
            detail={"code": "VALIDATION_ERROR", "msg": "이메일과 비밀번호를 입력해주세요"},
        )
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(
            status_code=409,
            detail={"code": "EMAIL_EXISTS", "msg": "이미 사용 중인 이메일입니다"},
        )
    user = User(email=req.email, password_hash=pwd_context.hash(req.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"token": create_token(user.id), "user": {"id": user.id, "email": user.email}}


@app.post("/auth/login")
def login(req: AuthReq, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not pwd_context.verify(req.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail={"code": "INVALID_CREDENTIALS", "msg": "이메일 또는 비밀번호가 올바르지 않습니다"},
        )
    return {"token": create_token(user.id), "user": {"id": user.id, "email": user.email}}


@app.get("/auth/me")
def me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "created_at": fmt_dt(current_user.created_at)}


@app.post("/auth/logout")
def logout(current_user: User = Depends(get_current_user)):
    return {"msg": "로그아웃 되었습니다"}


# ── Team ───────────────────────────────────────────────────────────

@app.post("/teams", status_code=201)
def create_team(
    req: TeamCreateReq,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not req.name or not req.name.strip():
        raise HTTPException(
            status_code=422,
            detail={"code": "VALIDATION_ERROR", "msg": "팀명을 입력해주세요"},
        )
    for _ in range(10):
        code = generate_invite_code()
        if not db.query(Team).filter(Team.invite_code == code).first():
            break
    team = Team(name=req.name.strip(), invite_code=code, owner_id=current_user.id)
    db.add(team)
    db.flush()
    db.add(TeamMember(team_id=team.id, user_id=current_user.id))
    db.commit()
    db.refresh(team)
    return {"id": team.id, "name": team.name, "invite_code": team.invite_code, "owner_id": team.owner_id}


@app.get("/teams")
def list_teams(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    memberships = db.query(TeamMember).filter(TeamMember.user_id == current_user.id).all()
    result = []
    for m in memberships:
        t = db.query(Team).filter(Team.id == m.team_id).first()
        if t:
            result.append({"id": t.id, "name": t.name, "invite_code": t.invite_code, "owner_id": t.owner_id})
    return result


@app.post("/teams/join")
def join_team(
    req: TeamJoinReq,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    code = req.invite_code.upper()
    team = db.query(Team).filter(Team.invite_code == code).first()
    if not team:
        raise HTTPException(
            status_code=404,
            detail={"code": "TEAM_NOT_FOUND", "msg": "유효하지 않은 초대코드입니다"},
        )
    if db.query(TeamMember).filter(TeamMember.team_id == team.id, TeamMember.user_id == current_user.id).first():
        raise HTTPException(
            status_code=409,
            detail={"code": "ALREADY_MEMBER", "msg": "이미 합류한 팀입니다"},
        )
    db.add(TeamMember(team_id=team.id, user_id=current_user.id))
    db.commit()
    return {"id": team.id, "name": team.name, "invite_code": team.invite_code, "owner_id": team.owner_id}


@app.get("/teams/{team_id}/members")
def list_members(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_member(team_id, current_user, db)
    members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
    result = []
    for m in members:
        u = db.query(User).filter(User.id == m.user_id).first()
        if u:
            result.append({"id": u.id, "email": u.email})
    return result


# ── Task ───────────────────────────────────────────────────────────

@app.post("/teams/{team_id}/tasks", status_code=201)
def create_task(
    team_id: int,
    req: TaskCreateReq,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_member(team_id, current_user, db)
    if not req.title or not req.title.strip():
        raise HTTPException(
            status_code=422,
            detail={"code": "VALIDATION_ERROR", "msg": "태스크 제목을 입력해주세요"},
        )
    task = Task(team_id=team_id, title=req.title.strip(), status="TODO", creator_id=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return {"id": task.id, "team_id": task.team_id, "title": task.title, "status": task.status, "creator_id": task.creator_id}


@app.get("/teams/{team_id}/tasks")
def list_tasks(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_member(team_id, current_user, db)
    tasks = db.query(Task).filter(Task.team_id == team_id).all()
    return [{"id": t.id, "team_id": t.team_id, "title": t.title, "status": t.status, "creator_id": t.creator_id} for t in tasks]


@app.get("/tasks/{task_id}")
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "msg": "태스크를 찾을 수 없습니다"})
    require_member(task.team_id, current_user, db)
    return {"id": task.id, "team_id": task.team_id, "title": task.title, "status": task.status, "creator_id": task.creator_id}


@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    req: TaskUpdateReq,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "msg": "태스크를 찾을 수 없습니다"})
    require_member(task.team_id, current_user, db)
    if req.status is not None:
        if req.status not in VALID_STATUSES:
            raise HTTPException(
                status_code=422,
                detail={"code": "VALIDATION_ERROR", "msg": "상태는 TODO, DOING, DONE 중 하나여야 합니다"},
            )
        task.status = req.status
    if req.title is not None:
        if not req.title.strip():
            raise HTTPException(
                status_code=422,
                detail={"code": "VALIDATION_ERROR", "msg": "태스크 제목을 입력해주세요"},
            )
        task.title = req.title.strip()
    db.commit()
    db.refresh(task)
    return {"id": task.id, "team_id": task.team_id, "title": task.title, "status": task.status, "creator_id": task.creator_id}


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "msg": "태스크를 찾을 수 없습니다"})
    require_member(task.team_id, current_user, db)
    db.delete(task)
    db.commit()
    return {"msg": "태스크가 삭제되었습니다"}


# ── Message ────────────────────────────────────────────────────────

@app.post("/teams/{team_id}/messages", status_code=201)
def create_message(
    team_id: int,
    req: MessageCreateReq,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_member(team_id, current_user, db)
    if not req.content or not req.content.strip():
        raise HTTPException(
            status_code=422,
            detail={"code": "VALIDATION_ERROR", "msg": "메시지를 입력해주세요"},
        )
    if len(req.content) > 1000:
        raise HTTPException(
            status_code=422,
            detail={"code": "VALIDATION_ERROR", "msg": "메시지는 1000자 이하여야 합니다"},
        )
    msg = Message(team_id=team_id, user_id=current_user.id, content=req.content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return {"id": msg.id, "team_id": msg.team_id, "user_id": msg.user_id, "content": msg.content, "created_at": fmt_dt(msg.created_at)}


@app.get("/teams/{team_id}/messages")
def list_messages(
    team_id: int,
    since: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_member(team_id, current_user, db)
    query = db.query(Message).filter(Message.team_id == team_id)
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00")).replace(tzinfo=None)
            query = query.filter(Message.created_at > since_dt)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail={"code": "VALIDATION_ERROR", "msg": "since는 ISO 8601 형식이어야 합니다"},
            )
    messages = query.order_by(Message.created_at.asc()).all()
    return [
        {"id": m.id, "team_id": m.team_id, "user_id": m.user_id, "content": m.content, "created_at": fmt_dt(m.created_at)}
        for m in messages
    ]


@app.get("/messages/{message_id}")
def get_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "msg": "메시지를 찾을 수 없습니다"})
    require_member(msg.team_id, current_user, db)
    return {"id": msg.id, "team_id": msg.team_id, "user_id": msg.user_id, "content": msg.content, "created_at": fmt_dt(msg.created_at)}


@app.delete("/messages/{message_id}")
def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "msg": "메시지를 찾을 수 없습니다"})
    require_member(msg.team_id, current_user, db)
    db.delete(msg)
    db.commit()
    return {"msg": "메시지가 삭제되었습니다"}


# ── 로컬 정적 파일 서빙 (Vercel 환경 제외) ────────────────────────
if not os.environ.get("VERCEL"):
    _static = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
    if os.path.exists(_static):
        app.mount("/", StaticFiles(directory=_static, html=True), name="static")
