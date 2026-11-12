from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__); app.config["SQLALCHEMY_DATABASE_URI"] = __import__("os").environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, nullable=False)
    channel = db.Column(db.String(20), default="in-app")
    message = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default="SENT")

@app.get("/health")
def health(): return jsonify(service="notification-service", status="healthy")

@app.post("/notifications")
def create_notification():
    d=request.get_json(silent=True) or {}
    try:
        n=Notification(user_id=int(d["user_id"]), order_id=int(d["order_id"]), channel=d.get("channel","in-app"), message=d["message"])
        db.session.add(n); db.session.commit()
        return jsonify(id=n.id,user_id=n.user_id,order_id=n.order_id,channel=n.channel,message=n.message,status=n.status),201
    except (KeyError,ValueError,TypeError):
        return jsonify(error="user_id, order_id and message are required"),400

@app.get("/notifications")
def list_notifications():
    uid=request.args.get("user_id",type=int)
    q=Notification.query.filter_by(user_id=uid) if uid else Notification.query
    return jsonify(notifications=[{"id":n.id,"user_id":n.user_id,"order_id":n.order_id,"channel":n.channel,"message":n.message,"status":n.status} for n in q.order_by(Notification.id.desc()).all()])

with app.app_context(): db.create_all()
