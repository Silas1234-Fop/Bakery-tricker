from flask import (Blueprint, render_template, request,
                   redirect, url_for, session, jsonify)
from ..models import db, Production, DEPARTMENTS
from datetime import date, datetime
from functools import wraps

production_bp = Blueprint('production', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@production_bp.route('/production', methods=['GET', 'POST'])
@login_required
def production():
    error = None
    success = None
    if request.method == 'POST':
        try:
            record = Production(
                department=request.form['department'],
                product=request.form['product'],
                sack_number=int(request.form['sack_number']),
                input_qty=float(request.form['input_qty']),
                output_qty=float(request.form['output_qty']),
                date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
                entered_by=session.get('username'),
                sync_status='synced',
            )
            db.session.add(record)
            db.session.commit()
            success = f"Saved! {record.product} – Output: {record.output_qty}"
        except Exception as e:
            error = f"Error saving record: {str(e)}"
    dept = session.get('department') if session.get('role') == 'worker' else None
    query = Production.query
    if dept:
        query = query.filter_by(department=dept)
    records = query.order_by(Production.created_at.desc()).limit(20).all()
    return render_template('production.html',
                           records=records,
                           departments=DEPARTMENTS,
                           today=str(date.today()),
                           error=error,
                           success=success,
                           worker_dept=dept)

@production_bp.route('/production/delete/<int:record_id>', methods=['POST'])
@login_required
def delete_production(record_id):
    record = Production.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('production.production'))
