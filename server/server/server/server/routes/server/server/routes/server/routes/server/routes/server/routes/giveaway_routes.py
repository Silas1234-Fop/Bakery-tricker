from flask import (Blueprint, render_template, request,
                   redirect, url_for, session, jsonify)
from ..models import db, Giveaway, DEPARTMENTS
from datetime import date, datetime
from functools import wraps

giveaway_bp = Blueprint('giveaway', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@giveaway_bp.route('/giveaway', methods=['GET', 'POST'])
@login_required
def giveaway():
    error = None
    success = None
    if request.method == 'POST':
        try:
            record = Giveaway(
                department=request.form['department'],
                product=request.form['product'],
                quantity=float(request.form['quantity']),
                reason=request.form.get('reason', ''),
                date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
                entered_by=session.get('username'),
                sync_status='synced',
            )
            db.session.add(record)
            db.session.commit()
            success = f"Saved! {record.product} – Quantity: {record.quantity}"
        except Exception as e:
            error = f"Error saving record: {str(e)}"
    dept = session.get('department') if session.get('role') == 'worker' else None
    query = Giveaway.query
    if dept:
        query = query.filter_by(department=dept)
    records = query.order_by(Giveaway.created_at.desc()).limit(20).all()
    return render_template('giveaway.html',
                           records=records,
                           departments=DEPARTMENTS,
                           today=str(date.today()),
                           error=error,
                           success=success,
                           worker_dept=dept)

@giveaway_bp.route('/giveaway/delete/<int:record_id>', methods=['POST'])
@login_required
def delete_giveaway(record_id):
    record = Giveaway.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('giveaway.giveaway'))
