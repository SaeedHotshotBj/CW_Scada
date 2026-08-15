from flask import Blueprint,render_template,request
from database.queries import get_summary
import jdatetime

reports=Blueprint('reports',__name__,url_prefix='/reports')

def convert_date(value):
    if not value:return None
    y,m,d=value.replace('/','-').split('-')
    return jdatetime.date(int(y),int(m),int(d)).togregorian()

@reports.route('/')
def index():
    start=request.args.get('start');end=request.args.get('end')
    return render_template('accounting/report.html',summary=get_summary(convert_date(start),convert_date(end)),start=start or '',end=end or '')
