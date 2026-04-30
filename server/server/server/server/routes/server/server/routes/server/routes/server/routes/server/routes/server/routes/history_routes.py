from flask import (Blueprint, render_template, request,
                   redirect, url_for, session)
from ..models import db, Production, Packaging, Giveaway, DEPARTMENTS
from datetime import date
from functools import wraps

history_bp = Blueprint('history', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@history_bp.route('/history')
@login_required
def history():
    tab = request.args.get('tab', 'production')
    dept_filter = request.args.get('dept', '')
    date_filter = request.args.get('date', '')
    if session.get('role') == 'worker':
        dept_filter = session.get('department', '')
    records = []
    if tab == 'production':
        q = Production.query
        if dept_filter: q = q.filter_by(department=dept_filter)
        if date_filter:
            try:
                q = q.filter_by(date=date.fromisoformat(date_filter))
            except ValueError:
                pass
        records = q.order_by(Production.created_at.desc()).limit(50).all()
    elif tab == 'packaging':
        q = Packaging.query
        if dept_filter: q = q.filter_by(department=dept_filter)
        if date_filter:
            try:
                q = q.filter_by(date=date.fromisoformat(date_filter))
            except ValueError:
                pass
        records = q.order_by(Packaging.created_at.desc()).limit(50).all()
    elif tab == 'giveaway':
        q = Giveaway.query
        if dept_filter: q = q.filter_by(department=dept_filter)
        if date_filter:
            try:
                q = q.filter_by(date=date.fromisoformat(date_filter))
            except ValueError:
                pass
        records = q.order_by(Giveaway.created_at.desc()).limit(50).all()
    return render_template('history.html',
                           records=records,
                           tab=tab,
                           departments=list(DEPARTMENTS.keys()),
                           dept_filter=dept_filter,
                           date_filter=date_filter)

@history_bp.route('/history/delete/<string:tab>/<int:record_id>', methods=['POST'])
@login_required
def delete_record(tab, record_id):
    if tab == 'production':
        r = Production.query.get_or_404(record_id)
    elif tab == 'packaging':
        r = Packaging.query.get_or_404(record_id)
    elif tab == 'giveaway':
        r = Giveaway.query.get_or_404(record_id)
    else:
        return redirect(url_for('history.history'))
    db.session.delete(r)
    db.session.commit()
    return redirect(url_for('history.history', tab=tab))
