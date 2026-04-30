from flask import (Blueprint, render_template, request,
                   redirect, url_for, session, jsonify)
from ..models import db, Packaging, DEPARTMENTS
from datetime import date, datetime
from functools import wraps

packaging_bp = Blueprint('packaging', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@packaging_bp.route('/packaging', methods=['GET', 'POST'])
@login_required
def packaging():
    error = None
    success = None
    if request.method == 'POST':
        try:
            record = Packaging(
                department=request.form['department'],
                product=request.form['product'],
                total_packed=float(request.form['total_packed']),
                date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
                entered_by=session.get('username'),
                sync_status='synced',
            )
            db.session.add(record)
            db.session.commit()
            success = f"Saved! {record.product} – Packed: {record.total_packed}"
        except Exception as e:
            error = f"Error saving record: {str(e)}"
    dept = session.get('department') if session.get('role') == 'worker' else None
    query = Packaging.query
    if dept:
        query = query.filter_by(department=dept)
    records = query.order_by(Packaging.created_at.desc()).limit(20).all()
    return render_template('packaging.html',
                           records=records,
                           departments=DEPARTMENTS,
                           today=str(date.today()),
                           error=error,
                           success=success,
                           worker_dept=dept)

@packaging_bp.route('/packaging/delete/<int:record_id>', methods=['POST'])
@login_required
def delete_packaging(record_id):
    record = Packaging.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('packaging.packaging'))
