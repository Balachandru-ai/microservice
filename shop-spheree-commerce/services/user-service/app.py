import os, datetime, jwt
from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
SECRET = os.environ.get("JWT_SECRET", "local-demo-secret-change-me")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@example.com").lower()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="customer", nullable=False)

def token_for(user):
    return jwt.encode({"sub": str(user.id), "email": user.email, "role": user.role,
                       "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=12)}, SECRET, algorithm="HS256")

@app.get("/health")
def health(): return jsonify(service="user-service", status="healthy")

@app.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    name, email, password = data.get("name", "").strip(), data.get("email", "").strip().lower(), data.get("password", "")
    if not name or "@" not in email or len(password) < 8:
        return jsonify(error="Name, valid email and password (8+ characters) are required"), 400
    if User.query.filter_by(email=email).first(): return jsonify(error="Email already registered"), 409
    role = "admin" if email == ADMIN_EMAIL else "customer"
    user = User(name=name, email=email, password_hash=generate_password_hash(password), role=role)
    db.session.add(user); db.session.commit()
    return jsonify(token=token_for(user), user={"id": user.id, "name": user.name, "email": user.email, "role": user.role}), 201

@app.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    user = User.query.filter_by(email=data.get("email", "").lower()).first()
    if not user or not check_password_hash(user.password_hash, data.get("password", "")):
        return jsonify(error="Invalid email or password"), 401
    return jsonify(token=token_for(user), user={"id": user.id, "name": user.name, "email": user.email, "role": user.role})

@app.get("/me")
def me():
    auth = request.headers.get("Authorization", "")
    try:
        payload = jwt.decode(auth.removeprefix("Bearer ").strip(), SECRET, algorithms=["HS256"])
        user = db.session.get(User, int(payload["sub"]))
        if not user: raise ValueError()
        return jsonify(id=user.id, name=user.name, email=user.email, role=user.role)
    except Exception:
        return jsonify(error="Unauthorized"), 401

with app.app_context(): db.create_all()
