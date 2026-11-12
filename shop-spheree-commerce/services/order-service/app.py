import os, requests
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
app=Flask(__name__); app.config["SQLALCHEMY_DATABASE_URI"]=os.environ["DATABASE_URL"]; app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
db=SQLAlchemy(app)
PRODUCT=os.getenv("PRODUCT_SERVICE_URL","http://localhost:5002")
PAYMENT=os.getenv("PAYMENT_SERVICE_URL","http://localhost:5004")
NOTIFY=os.getenv("NOTIFICATION_SERVICE_URL","http://localhost:5005")

class Order(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,nullable=False)
    product_id=db.Column(db.Integer,nullable=False)
    product_name=db.Column(db.String(140),nullable=False)
    quantity=db.Column(db.Integer,nullable=False)
    amount=db.Column(db.Float,nullable=False)
    status=db.Column(db.String(30),nullable=False)
    payment_transaction=db.Column(db.String(50))

def out(o): return {"id":o.id,"user_id":o.user_id,"product_id":o.product_id,"product_name":o.product_name,"quantity":o.quantity,"amount":o.amount,"status":o.status,"payment_transaction":o.payment_transaction}

@app.get("/health")
def health(): return jsonify(service="order-service",status="healthy")

@app.post("/orders")
def create_order():
    d=request.get_json(silent=True) or {}
    try:
        uid=int(d["user_id"]); pid=int(d["product_id"]); qty=int(d["quantity"])
        if uid<1 or qty<1: raise ValueError()
    except (KeyError,ValueError,TypeError): return jsonify(error="user_id, product_id and positive quantity are required"),400
    try:
        pr=requests.get(f"{PRODUCT}/products/{pid}",timeout=5)
        if pr.status_code != 200: return jsonify(error="Product not found"),404
        product=pr.json()
        reserve=requests.post(f"{PRODUCT}/products/{pid}/reserve",json={"quantity":qty},timeout=5)
        if reserve.status_code != 200: return jsonify(error=reserve.json().get("error","Could not reserve stock")),409
        amount=round(float(product["price"])*qty,2)
        order=Order(user_id=uid,product_id=pid,product_name=product["name"],quantity=qty,amount=amount,status="PAYMENT_PENDING")
        db.session.add(order); db.session.commit()
        try:
            payment=requests.post(f"{PAYMENT}/payments",json={"order_id":order.id,"user_id":uid,"amount":amount,"method":d.get("payment_method","DEMO")},timeout=8)
            payment.raise_for_status(); p=payment.json()
            order.payment_transaction=p["transaction_id"]; order.status="CONFIRMED" if p["status"]=="SUCCESS" else "PAYMENT_FAILED"
        except requests.RequestException:
            order.status="PAYMENT_PENDING"
            db.session.commit()
            return jsonify(order=out(order),warning="Payment service unavailable; order remains pending"),202
        db.session.commit()
        message=f"Order #{order.id} {order.status.lower().replace('_',' ')}. Amount: {amount:.2f}."
        try: requests.post(f"{NOTIFY}/notifications",json={"user_id":uid,"order_id":order.id,"message":message},timeout=5)
        except requests.RequestException: pass
        return jsonify(order=out(order),payment=p),201 if order.status=="CONFIRMED" else 402
    except requests.RequestException:
        return jsonify(error="A dependent service is unavailable"),503

@app.get("/orders")
def list_orders():
    uid=request.args.get("user_id",type=int)
    q=Order.query.filter_by(user_id=uid) if uid else Order.query
    return jsonify(orders=[out(o) for o in q.order_by(Order.id.desc()).all()])

@app.get("/orders/<int:oid>")
def get_order(oid):
    o=db.session.get(Order,oid)
    return (jsonify(out(o)),200) if o else (jsonify(error="Order not found"),404)

with app.app_context(): db.create_all()
