import uuid
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__); app.config["SQLALCHEMY_DATABASE_URI"] = __import__("os").environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(50), unique=True, nullable=False)
    order_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(20), nullable=False)

@app.get("/health")
def health(): return jsonify(service="payment-service", status="healthy")

@app.post("/payments")
def pay():
    d = request.get_json(silent=True) or {}
    try:
        amount=float(d["amount"]); order_id=int(d["order_id"]); user_id=int(d["user_id"])
        method=d.get("method","demo").strip()
        if amount <= 0 or not method: raise ValueError()
    except (KeyError, ValueError, TypeError):
        return jsonify(error="Valid order_id, user_id, amount and method are required"), 400
    status = "DECLINED" if method.upper() == "DECLINE" else "SUCCESS"
    p=Payment(transaction_id="SIM-"+uuid.uuid4().hex[:12].upper(), order_id=order_id, user_id=user_id, amount=amount, method=method, status=status)
    db.session.add(p); db.session.commit()
    return jsonify(id=p.id, transaction_id=p.transaction_id, order_id=p.order_id, amount=p.amount, method=p.method, status=p.status), 201

@app.get("/payments")
def list_payments():
    return jsonify(payments=[{"id":p.id,"transaction_id":p.transaction_id,"order_id":p.order_id,"amount":p.amount,"method":p.method,"status":p.status} for p in Payment.query.order_by(Payment.id.desc()).all()])

with app.app_context(): db.create_all()
