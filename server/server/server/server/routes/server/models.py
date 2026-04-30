from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()

DEPARTMENTS = {
    "Mandazi": ["Plain Mandazi", "Jam Mandazi", "Coconut Mandazi", "Sugar Mandazi"],
    "Bread": ["Sandwich", "Ubwadesa", "Ibipande", "Boris"],
    "Cakes": ["Vanilla Cake", "Chocolate Cake", "Fruit Cake", "Wedding Cake"],
    "Bagne": ["Classic Bagne", "Butter Bagne", "Sesame Bagne"],
}

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

class Production(db.Model):
    __tablename__ = 'production'
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(50), nullable=False)
    product = db.Column(db.String(100), nullable=False)
    sack_number = db.Column(db.Integer, nullable=False)
    input_qty = db.Column(db.Float, nullable=False)
    output_qty = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    entered_by = db.Column(db.String(50))
    sync_status = db.Column(db.String(20), default='synced')
    created_at = db.Column(db.DateTime, default=datetime.now)

class Packaging(db.Model):
    __tablename__ = 'packaging'
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(50), nullable=False)
    product = db.Column(db.String(100), nullable=False)
    total_packed = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    entered_by = db.Column(db.String(50))
    sync_status = db.Column(db.String(20), default='synced')
    created_at = db.Column(db.DateTime, default=datetime.now)

class Giveaway(db.Model):
    __tablename__ = 'giveaway'
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(50), nullable=False)
    product = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(200))
    date = db.Column(db.Date, nullable=False, default=date.today)
    entered_by = db.Column(db.String(50))
    sync_status = db.Column(db.String(20), default='synced')
    created_at = db.Column(db.DateTime, default=datetime.now)

def create_default_users():
    if User.query.count() == 0:
        users = [
            User(username='manager', password='manager123',
                 full_name='Bakery Manager', role='manager'),
            User(username='mandazi', password='mandazi123',
                 full_name='Mandazi Worker', role='worker',
                 department='Mandazi'),
            User(username='bread', password='bread123',
                 full_name='Bread Worker', role='worker',
                 department='Bread'),
            User(username='cakes', password='cakes123',
                 full_name='Cakes Worker', role='worker',
                 department='Cakes'),
            User(username='bagne', password='bagne123',
                 full_name='Bagne Worker', role='worker',
                 department='Bagne'),
        ]
        for user in users:
            db.session.add(user)
        db.session.commit()

def get_reconciliation(department=None, record_date=None):
    prod_query = Production.query
    pack_query = Packaging.query
    give_query = Giveaway.query

    if department:
        prod_query = prod_query.filter_by(department=department)
        pack_query = pack_query.filter_by(department=department)
        give_query = give_query.filter_by(department=department)

    if record_date:
        prod_query = prod_query.filter_by(date=record_date)
        pack_query = pack_query.filter_by(date=record_date)
        give_query = give_query.filter_by(date=record_date)

    products = {}
    for r in prod_query.all():
        key = (r.department, r.product)
        if key not in products:
            products[key] = {'department': r.department, 'product': r.product,
                             'produced': 0, 'packed': 0, 'giveaway': 0}
        products[key]['produced'] += r.output_qty

    for r in pack_query.all():
        key = (r.department, r.product)
        if key not in products:
            products[key] = {'department': r.department, 'product': r.product,
                             'produced': 0, 'packed': 0, 'giveaway': 0}
        products[key]['packed'] += r.total_packed

    for r in give_query.all():
        key = (r.department, r.product)
        if key not in products:
            products[key] = {'department': r.department, 'product': r.product,
                             'produced': 0, 'packed': 0, 'giveaway': 0}
        products[key]['giveaway'] += r.quantity

    results = []
    for key, p in products.items():
        produced = p['produced']
        packed = p['packed']
        giveaway = p['giveaway']
        real_loss = max(0, produced - packed - giveaway)
        efficiency = round((packed / produced * 100), 1) if produced > 0 else 0.0
        results.append({
            'department': p['department'], 'product': p['product'],
            'produced': round(produced, 1), 'packed': round(packed, 1),
            'giveaway': round(giveaway, 1), 'real_loss': round(real_loss, 1),
            'efficiency': efficiency,
        })
    return results

def get_summary_totals(department=None, record_date=None):
    results = get_reconciliation(department, record_date)
    total_produced = sum(r['produced'] for r in results)
    total_packed = sum(r['packed'] for r in results)
    total_giveaway = sum(r['giveaway'] for r in results)
    total_loss = sum(r['real_loss'] for r in results)
    efficiency = round((total_packed / total_produced * 100), 1) if total_produced > 0 else 0.0
    return {
        'produced': round(total_produced, 1),
        'packed': round(total_packed, 1),
        'giveaway': round(total_giveaway, 1),
        'loss': round(total_loss, 1),
        'efficiency': efficiency,
    }
