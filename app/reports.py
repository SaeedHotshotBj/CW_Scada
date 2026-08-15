from flask import Blueprint, render_template, request
from database.queries import get_summary
from app.jalali import jalali_to_gregorian

reports = Blueprint('reports', __name__, url_prefix='/reports')


@reports.route('/')
def index():
    start = request.args.get('start', '').strip()
    end = request.args.get('end', '').strip()
    return render_template(
        'accounting/report.html',
        summary=get_summary(jalali_to_gregorian(start), jalali_to_gregorian(end)),
        start=start,
        end=end,
    )
