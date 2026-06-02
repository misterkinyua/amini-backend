"""
Amini Platform · Backend API
Flask + SQLAlchemy  (SQLite by default — swap one env var for MySQL)

Default DB  : sqlite:///amini.db
MySQL switch: set DATABASE_URL=mysql+pymysql://user:pass@localhost/amini
"""

import os, json, secrets, hashlib
from datetime import datetime
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, or_
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:3456", "http://127.0.0.1:3456"], supports_credentials=True)

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///amini.db")
engine       = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base         = declarative_base()


# ── MODELS ────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"
    id                  = Column(String(60),  primary_key=True)
    email               = Column(String(255), unique=True, nullable=False)
    password            = Column(String(255), nullable=False)
    role                = Column(String(20),  nullable=False)
    name                = Column(String(255))
    title               = Column(String(255))
    location            = Column(String(255))
    bio                 = Column(Text)
    avatar              = Column(String(10))
    identity_verified   = Column(Boolean, default=False)
    subscription        = Column(String(50),  default="free")
    billing_cycle       = Column(String(20))
    ubuntu_score        = Column(Integer, default=0)
    profile_views_count = Column(Integer, default=0)
    joined              = Column(String(20))
    markets             = Column(Text)   # JSON array
    skills              = Column(Text)   # JSON array
    work_visas          = Column(Text)   # JSON array
    other_markets       = Column(Text)   # JSON array
    vouch_ids           = Column(Text)   # JSON array
    salary_range        = Column(String(120))
    resume_name         = Column(String(255))
    self_vouch_duration = Column(Integer)
    self_vouch_saved_at = Column(String(50))
    # HR-only
    company             = Column(String(255))
    company_size        = Column(String(50))
    company_location    = Column(String(255))
    lookups_used        = Column(Integer, default=0)
    lookups_limit       = Column(Integer, default=20)
    created_at          = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id, "email": self.email, "role": self.role,
            "name": self.name, "title": self.title, "location": self.location,
            "bio": self.bio, "avatar": self.avatar,
            "identity_verified": self.identity_verified,
            "subscription": self.subscription, "billing_cycle": self.billing_cycle,
            "ubuntu_score": self.ubuntu_score or 0,
            "profile_views": self.profile_views_count or 0,
            "joined": self.joined,
            "markets":       json.loads(self.markets      or "[]"),
            "skills":        json.loads(self.skills       or "[]"),
            "work_visas":    json.loads(self.work_visas   or "[]"),
            "other_markets": json.loads(self.other_markets or "[]"),
            "vouch_ids":     json.loads(self.vouch_ids    or "[]"),
            "salary_range": self.salary_range,
            "resume_name": self.resume_name,
            "self_vouch_duration": self.self_vouch_duration,
            "self_vouch_saved_at": self.self_vouch_saved_at,
            "company": self.company, "company_size": self.company_size,
            "company_location": self.company_location,
            "lookups_used": self.lookups_used or 0,
            "lookups_limit": self.lookups_limit or 20,
        }


class Vouch(Base):
    __tablename__ = "vouches"
    id               = Column(String(60),  primary_key=True)
    candidate_id     = Column(String(60),  ForeignKey("users.id"))
    witness_name     = Column(String(255))
    witness_role     = Column(String(255))
    witness_initials = Column(String(10))
    witness_color    = Column(String(20))
    context          = Column(String(50))
    status           = Column(String(20))
    weight           = Column(Float, default=0)
    duration         = Column(Integer)
    media_url        = Column(Text)
    quote            = Column(Text)
    created_at       = Column(String(20))

    def to_dict(self):
        return {
            "id": self.id, "candidate_id": self.candidate_id,
            "witness_name": self.witness_name, "witness_role": self.witness_role,
            "witness_initials": self.witness_initials, "witness_color": self.witness_color,
            "context": self.context, "status": self.status,
            "weight": self.weight, "duration": self.duration,
            "media_url": self.media_url, "quote": self.quote,
            "created_at": self.created_at,
        }


class Message(Base):
    __tablename__ = "messages"
    id                   = Column(String(60),  primary_key=True)
    from_id              = Column(String(60),  ForeignKey("users.id"))
    from_name            = Column(String(255))
    from_company         = Column(String(255))
    to_witness           = Column(String(255))
    about_candidate_id   = Column(String(60))
    about_candidate_name = Column(String(255))
    body                 = Column(Text)
    reply                = Column(Text)
    status               = Column(String(20), default="sent")
    created_at           = Column(String(30))
    replied_at           = Column(String(30))

    def to_dict(self):
        return {
            "id": self.id, "from_id": self.from_id,
            "from_name": self.from_name, "from_company": self.from_company,
            "to_witness": self.to_witness,
            "about_candidate_id": self.about_candidate_id,
            "about_candidate_name": self.about_candidate_name,
            "body": self.body, "reply": self.reply,
            "status": self.status, "created_at": self.created_at,
            "replied_at": self.replied_at,
        }


class VouchRequest(Base):
    __tablename__ = "vouch_requests"
    id             = Column(String(60), primary_key=True)
    candidate_id   = Column(String(60), ForeignKey("users.id"))
    witness_email  = Column(String(255))
    witness_name   = Column(String(255))
    status         = Column(String(20), default="sent")
    created_at     = Column(String(30))

    def to_dict(self):
        return {
            "id": self.id, "candidate_id": self.candidate_id,
            "witness_email": self.witness_email, "witness_name": self.witness_name,
            "status": self.status, "created_at": self.created_at,
        }


class Pipeline(Base):
    __tablename__ = "pipeline"
    id           = Column(String(60), primary_key=True)
    hr_id        = Column(String(60), ForeignKey("users.id"))
    candidate_id = Column(String(60), ForeignKey("users.id"))
    stage        = Column(String(50))
    added_at     = Column(String(30))

    def to_dict(self):
        return {
            "id": self.id, "hr_id": self.hr_id,
            "candidate_id": self.candidate_id,
            "stage": self.stage, "added_at": self.added_at,
        }


class ProfileView(Base):
    __tablename__ = "profile_views"
    id           = Column(String(60), primary_key=True)
    candidate_id = Column(String(60), ForeignKey("users.id"))
    hr_id        = Column(String(60), ForeignKey("users.id"))
    hr_name      = Column(String(255))
    hr_initials  = Column(String(10))
    hr_color     = Column(String(20))
    hr_company   = Column(String(255))
    hr_title     = Column(String(255))
    viewed_at    = Column(String(40))
    read         = Column(Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id, "candidate_id": self.candidate_id,
            "hr_id": self.hr_id, "hr_name": self.hr_name,
            "hr_initials": self.hr_initials, "hr_color": self.hr_color,
            "hr_company": self.hr_company, "hr_title": self.hr_title,
            "viewed_at": self.viewed_at, "read": self.read,
        }


class AuthToken(Base):
    __tablename__ = "auth_tokens"
    token      = Column(String(128), primary_key=True)
    user_id    = Column(String(60), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)


# ── HELPERS ───────────────────────────────────────────────────────────────────

def get_db():
    if "db" not in g:
        g.db = SessionLocal()
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db: db.close()

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def current_user(db):
    token = request.headers.get("X-Auth-Token")
    if not token: return None
    row = db.get(AuthToken, token)
    if not row: return None
    return db.get(User, row.user_id)

def ok(data={}, code=200):
    return jsonify(data), code

def err(msg, code=400):
    return jsonify({"error": msg}), code


# ── AUTH ──────────────────────────────────────────────────────────────────────

@app.route("/api/auth/login", methods=["POST"])
def login():
    db   = get_db()
    data = request.json or {}
    user = db.query(User).filter_by(email=data.get("email","")).first()
    if not user or user.password != hash_pw(data.get("password","")):
        return err("Invalid email or password", 401)
    token = secrets.token_hex(32)
    db.add(AuthToken(token=token, user_id=user.id))
    db.commit()
    return ok({"token": token, "user": user.to_dict()})

@app.route("/api/auth/logout", methods=["POST"])
def logout():
    db    = get_db()
    token = request.headers.get("X-Auth-Token","")
    db.query(AuthToken).filter_by(token=token).delete()
    db.commit()
    return ok({"ok": True})


# ── USERS ─────────────────────────────────────────────────────────────────────

@app.route("/api/users", methods=["GET"])
def list_users():
    db    = get_db()
    role  = request.args.get("role")
    query = db.query(User)
    if role: query = query.filter_by(role=role)
    return ok([u.to_dict() for u in query.all()])

@app.route("/api/users", methods=["POST"])
def create_user():
    db   = get_db()
    data = request.json or {}
    if db.query(User).filter_by(email=data.get("email","")).first():
        return err("Email already registered", 409)
    uid  = data.get("id") or (data.get("role","u") + "-" + secrets.token_hex(6))
    user = User(
        id=uid, email=data["email"], password=hash_pw(data["password"]),
        role=data.get("role","candidate"), name=data.get("name",""),
        title=data.get("title",""), location=data.get("location",""),
        bio=data.get("bio",""), avatar=data.get("avatar","??"),
        joined=data.get("joined", datetime.utcnow().strftime("%Y-%m-%d")),
        markets=json.dumps(data.get("markets",[])),
        skills=json.dumps(data.get("skills",[])),
        work_visas=json.dumps(data.get("work_visas",[])),
        vouch_ids=json.dumps(data.get("vouch_ids",[])),
        company=data.get("company",""), company_size=data.get("company_size",""),
        lookups_limit=data.get("lookups_limit",20),
    )
    db.add(user); db.commit()
    return ok(user.to_dict(), 201)

@app.route("/api/users/<uid>", methods=["GET"])
def get_user(uid):
    db   = get_db()
    user = db.get(User, uid)
    if not user: return err("Not found", 404)
    return ok(user.to_dict())

@app.route("/api/users/<uid>", methods=["PUT"])
def update_user(uid):
    db   = get_db()
    user = db.get(User, uid)
    if not user: return err("Not found", 404)
    data       = request.json or {}
    json_fields = {"markets","skills","work_visas","other_markets","vouch_ids"}
    protected   = {"id","email","password","role","created_at"}
    for k, v in data.items():
        if k in protected: continue
        setattr(user, k, json.dumps(v) if k in json_fields else v)
    db.commit()
    return ok(user.to_dict())

@app.route("/api/users/<uid>", methods=["DELETE"])
def delete_user(uid):
    db   = get_db()
    user = db.get(User, uid)
    if not user: return err("Not found", 404)
    db.delete(user); db.commit()
    return ok({"deleted": uid})


# ── VOUCHES ───────────────────────────────────────────────────────────────────

@app.route("/api/vouches", methods=["GET"])
def list_vouches():
    db  = get_db()
    cid = request.args.get("candidate_id")
    q   = db.query(Vouch)
    if cid: q = q.filter_by(candidate_id=cid)
    return ok([v.to_dict() for v in q.all()])

@app.route("/api/vouches/<vid>", methods=["PUT"])
def update_vouch(vid):
    db    = get_db()
    vouch = db.get(Vouch, vid)
    if not vouch: return err("Not found", 404)
    data  = request.json or {}
    for k, v in data.items():
        if k != "id": setattr(vouch, k, v)
    db.commit()
    return ok(vouch.to_dict())


# ── MESSAGES ──────────────────────────────────────────────────────────────────

@app.route("/api/messages", methods=["GET"])
def list_messages():
    db  = get_db()
    uid = request.args.get("user_id")
    q   = db.query(Message)
    if uid: q = q.filter(or_(Message.from_id==uid, Message.about_candidate_id==uid))
    return ok([m.to_dict() for m in q.all()])

@app.route("/api/messages", methods=["POST"])
def add_message():
    db   = get_db()
    data = request.json or {}
    msg  = Message(
        id=data.get("id","msg-"+secrets.token_hex(8)),
        from_id=data.get("from_id"), from_name=data.get("from_name",""),
        from_company=data.get("from_company",""),
        to_witness=data.get("to_witness",""),
        about_candidate_id=data.get("about_candidate_id"),
        about_candidate_name=data.get("about_candidate_name",""),
        body=data.get("body",""), status=data.get("status","sent"),
        created_at=data.get("created_at", datetime.utcnow().isoformat()),
    )
    db.add(msg); db.commit()
    return ok(msg.to_dict(), 201)

@app.route("/api/messages/<mid>", methods=["PUT"])
def update_message(mid):
    db  = get_db()
    msg = db.get(Message, mid)
    if not msg: return err("Not found", 404)
    data = request.json or {}
    for k, v in data.items():
        if k != "id": setattr(msg, k, v)
    db.commit()
    return ok(msg.to_dict())


# ── VOUCH REQUESTS ────────────────────────────────────────────────────────────

@app.route("/api/vouch_requests", methods=["GET"])
def list_vouch_requests():
    db  = get_db()
    cid = request.args.get("candidate_id")
    q   = db.query(VouchRequest)
    if cid: q = q.filter_by(candidate_id=cid)
    return ok([r.to_dict() for r in q.all()])

@app.route("/api/vouch_requests", methods=["POST"])
def add_vouch_request():
    db   = get_db()
    data = request.json or {}
    req  = VouchRequest(
        id=data.get("id","vr-"+secrets.token_hex(6)),
        candidate_id=data.get("candidate_id"),
        witness_email=data.get("witness_email",""),
        witness_name=data.get("witness_name",""),
        status=data.get("status","sent"),
        created_at=data.get("created_at", datetime.utcnow().isoformat()),
    )
    db.add(req); db.commit()
    return ok(req.to_dict(), 201)


# ── PIPELINE ──────────────────────────────────────────────────────────────────

@app.route("/api/pipeline", methods=["GET"])
def list_pipeline():
    db    = get_db()
    hr_id = request.args.get("hr_id")
    q     = db.query(Pipeline)
    if hr_id: q = q.filter_by(hr_id=hr_id)
    return ok([p.to_dict() for p in q.all()])

@app.route("/api/pipeline", methods=["POST"])
def add_pipeline():
    db   = get_db()
    data = request.json or {}
    item = Pipeline(
        id=data.get("id","pl-"+secrets.token_hex(6)),
        hr_id=data.get("hr_id"), candidate_id=data.get("candidate_id"),
        stage=data.get("stage","Shortlisted"),
        added_at=data.get("added_at", datetime.utcnow().strftime("%Y-%m-%d")),
    )
    db.add(item); db.commit()
    return ok(item.to_dict(), 201)

@app.route("/api/pipeline/<pid>", methods=["PUT"])
def update_pipeline(pid):
    db   = get_db()
    item = db.get(Pipeline, pid)
    if not item: return err("Not found", 404)
    data = request.json or {}
    for k, v in data.items():
        if k != "id": setattr(item, k, v)
    db.commit()
    return ok(item.to_dict())

@app.route("/api/pipeline/<pid>", methods=["DELETE"])
def delete_pipeline(pid):
    db   = get_db()
    item = db.get(Pipeline, pid)
    if not item: return err("Not found", 404)
    db.delete(item); db.commit()
    return ok({"deleted": pid})


# ── PROFILE VIEWS ─────────────────────────────────────────────────────────────

@app.route("/api/profile_views", methods=["GET"])
def list_profile_views():
    db  = get_db()
    cid = request.args.get("candidate_id")
    q   = db.query(ProfileView)
    if cid: q = q.filter_by(candidate_id=cid)
    return ok([v.to_dict() for v in q.all()])

@app.route("/api/profile_views", methods=["POST"])
def add_profile_view():
    db   = get_db()
    data = request.json or {}
    pv   = ProfileView(
        id=data.get("id","pv-"+secrets.token_hex(6)),
        candidate_id=data.get("candidate_id"),
        hr_id=data.get("hr_id"),
        hr_name=data.get("hr_name",""), hr_initials=data.get("hr_initials",""),
        hr_color=data.get("hr_color","#065F46"),
        hr_company=data.get("hr_company",""), hr_title=data.get("hr_title",""),
        viewed_at=data.get("viewed_at", datetime.utcnow().isoformat()),
        read=data.get("read", False),
    )
    db.add(pv)
    # bump candidate's profile_views_count
    cand = db.get(User, data.get("candidate_id"))
    if cand: cand.profile_views_count = (cand.profile_views_count or 0) + 1
    db.commit()
    return ok(pv.to_dict(), 201)

@app.route("/api/profile_views/<pvid>", methods=["PUT"])
def update_profile_view(pvid):
    db = get_db()
    pv = db.get(ProfileView, pvid)
    if not pv: return err("Not found", 404)
    data = request.json or {}
    for k, v in data.items():
        if k != "id": setattr(pv, k, v)
    db.commit()
    return ok(pv.to_dict())


# ── STATS ─────────────────────────────────────────────────────────────────────

@app.route("/api/stats", methods=["GET"])
def stats():
    db = get_db()
    candidates     = db.query(User).filter_by(role="candidate").all()
    hrs            = db.query(User).filter_by(role="hr").all()
    total_vouches  = db.query(Vouch).count()
    verified       = db.query(Vouch).filter_by(status="verified").count()
    pending        = db.query(Vouch).filter_by(status="pending").count()
    total_msgs     = db.query(Message).count()
    replied_msgs   = db.query(Message).filter_by(status="replied").count()
    scores         = [c.ubuntu_score for c in candidates if c.ubuntu_score]
    avg_score      = round(sum(scores)/len(scores)) if scores else 0
    return ok({
        "total_candidates": len(candidates),
        "total_hr_partners": len(hrs),
        "total_vouches": total_vouches,
        "verified_vouches": verified,
        "avg_ubuntu_score": avg_score,
        "pending_vouches": pending,
        "messages_sent": total_msgs,
        "messages_replied": replied_msgs,
    })


# ── FULL SYNC (initial data load for the frontend cache) ─────────────────────

@app.route("/api/sync", methods=["GET"])
def sync():
    """One-shot endpoint: returns everything the frontend needs to bootstrap."""
    db = get_db()
    return ok({
        "users":          [u.to_dict() for u in db.query(User).all()],
        "vouches":        [v.to_dict() for v in db.query(Vouch).all()],
        "messages":       [m.to_dict() for m in db.query(Message).all()],
        "vouch_requests": [r.to_dict() for r in db.query(VouchRequest).all()],
        "pipeline":       [p.to_dict() for p in db.query(Pipeline).all()],
        "profile_views":  [v.to_dict() for v in db.query(ProfileView).all()],
    })


# ── BOOTSTRAP ─────────────────────────────────────────────────────────────────

def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    app.run(debug=True, port=5001, host="0.0.0.0")
