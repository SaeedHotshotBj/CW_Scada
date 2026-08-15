from flask import Blueprint, render_template, request
from database.queries import get_summary,get_sales,get_purchases,get_production_costs,get_inventory,get_receivables,get_payables,get_cashflow,get_profit_loss
import jdatetime

accounting=Blueprint('accounting',__name__,url_prefix='/accounting')

def jalali_to_gregorian(value):
    if not value:return None
    y,m,d=value.replace('/','-').split('-')
    return jdatetime.date(int(y),int(m),int(d)).togregorian()

def money(value):return "{:,.0f}".format(float(value or 0))

@accounting.app_template_filter('money')
def money_filter(value):return money(value)

@accounting.route('/')
def dashboard():
    start=request.args.get('start');end=request.args.get('end')
    return render_template('accounting/dashboard.html',summary=get_summary(jalali_to_gregorian(start),jalali_to_gregorian(end)),start=start or '',end=end or '')

@accounting.route('/sales')
def sales():
    start=request.args.get('start');end=request.args.get('end')
    return render_template('accounting/sales.html',rows=get_sales(jalali_to_gregorian(start),jalali_to_gregorian(end)),start=start or '',end=end or '')

@accounting.route('/purchases')
def purchases():
    start=request.args.get('start');end=request.args.get('end')
    return render_template('accounting/purchases.html',rows=get_purchases(jalali_to_gregorian(start),jalali_to_gregorian(end)),start=start or '',end=end or '')

@accounting.route('/production-cost')
def production_cost():
    start=request.args.get('start');end=request.args.get('end')
    return render_template('accounting/production_cost.html',rows=get_production_costs(jalali_to_gregorian(start),jalali_to_gregorian(end)),start=start or '',end=end or '')

@accounting.route('/inventory')
def inventory():return render_template('accounting/inventory.html',rows=get_inventory())
@accounting.route('/receivables')
def receivables():return render_template('accounting/receivables.html',rows=get_receivables())
@accounting.route('/payables')
def payables():return render_template('accounting/payables.html',rows=get_payables())

@accounting.route('/cashflow')
def cashflow():
    start=request.args.get('start');end=request.args.get('end')
    return render_template('accounting/cashflow.html',rows=get_cashflow(jalali_to_gregorian(start),jalali_to_gregorian(end)),start=start or '',end=end or '')

@accounting.route('/profit-loss')
def profit_loss():
    start=request.args.get('start');end=request.args.get('end')
    return render_template('accounting/profit_loss.html',result=get_profit_loss(jalali_to_gregorian(start),jalali_to_gregorian(end)),start=start or '',end=end or '')
