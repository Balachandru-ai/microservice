from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__); app.config["SQLALCHEMY_DATABASE_URI"] = __import__("os").environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    description = db.Column(db.String(500), default="")
    category = db.Column(db.String(80), default="General")
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)

def as_dict(p): return {"id":p.id,"name":p.name,"description":p.description,"category":p.category,"price":p.price,"stock":p.stock}

@app.get("/health")
def health(): return jsonify(service="product-service", status="healthy")

@app.get("/")
@app.get("/products")
def products():
    q = request.args.get("q", "")
    rows = Product.query.filter(Product.name.ilike(f"%{q}%")).order_by(Product.id).all() if q else Product.query.order_by(Product.id).all()
    return jsonify(products=[as_dict(p) for p in rows])

@app.get("/products/<int:pid>")
def product(pid):
    p = db.session.get(Product, pid)
    return (jsonify(as_dict(p)), 200) if p else (jsonify(error="Product not found"), 404)

@app.post("/products")
def create_product():
    d = request.get_json(silent=True) or {}
    try:
        p = Product(name=d["name"], description=d.get("description",""), category=d.get("category","General"), price=float(d["price"]), stock=int(d.get("stock",0)))
        if p.price < 0 or p.stock < 0: raise ValueError()
        db.session.add(p); db.session.commit()
        return jsonify(as_dict(p)), 201
    except (KeyError, ValueError, TypeError):
        return jsonify(error="Valid name, price and non-negative stock are required"), 400

@app.put("/products/<int:pid>")
def update_product(pid):
    p = db.session.get(Product, pid)
    if not p: return jsonify(error="Product not found"), 404
    d = request.get_json(silent=True) or {}
    for key in ("name","description","category","price","stock"):
        if key in d: setattr(p, key, d[key])
    db.session.commit(); return jsonify(as_dict(p))

@app.delete("/products/<int:pid>")
def delete_product(pid):
    p = db.session.get(Product, pid)
    if not p: return jsonify(error="Product not found"), 404
    db.session.delete(p); db.session.commit(); return jsonify(message="Deleted")

@app.post("/products/<int:pid>/reserve")
def reserve(pid):
    p = db.session.get(Product, pid); qty = int((request.get_json(silent=True) or {}).get("quantity", 1))
    if not p: return jsonify(error="Product not found"), 404
    if qty < 1 or p.stock < qty: return jsonify(error="Insufficient stock"), 409
    p.stock -= qty; db.session.commit(); return jsonify(as_dict(p))

@app.post("/products/<int:pid>/restock")
def restock(pid):
    p = db.session.get(Product, pid); qty = int((request.get_json(silent=True) or {}).get("quantity", 1))
    if not p or qty < 1: return jsonify(error="Invalid product or quantity"), 400
    p.stock += qty; db.session.commit(); return jsonify(as_dict(p))

with app.app_context():
    db.create_all()
    if Product.query.count() == 0:
        db.session.add_all([Product(name="Laptop",description="14-inch everyday laptop",category="Electronics",price=64999,stock=12), Product(name="Wireless Mouse",description="Ergonomic wireless mouse",category="Accessories",price=899,stock=40), Product(name="Mechanical Keyboard",description="RGB mechanical keyboard",category="Accessories",price=2499,stock=25), Product(name="Headphones",description="Over-ear headphones",category="Audio",price=3999,stock=18)])
        db.session.commit()
