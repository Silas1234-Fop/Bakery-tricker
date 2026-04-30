from flask import (Blueprint, render_template, session,
                   redirect, url_for, jsonify, request)
from ..models import get_reconciliation, get_summary_totals
from datetime import date
from functools import wraps

dashboard_bp = Blueprint('dashboard', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    dept = None
    if session.get('role') == 'worker':
        dept = session.get('department')
    results = get_reconciliation(
        department=dept, record_date=date.today())
    totals = get_summary_totals(
        department=dept, record_date=date.today())
    return render_template('dashboard.html',
                           results=results,
                           totals=totals,
                           today=date.today().strftime('%B %d, %Y'),
                           departments_list=list(
                               set(r['department'] for r in results)))
