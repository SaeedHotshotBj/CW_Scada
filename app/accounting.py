from flask import Blueprint, render_template, request
from database.queries import (
    get_summary, get_sales, get_purchases, get_production_costs,
    get_inventory, get_receivables, get_payables, get_cashflow,
    get_profit_loss,
)
from app.jalali import jalali_to_gregorian, to_jalali

accounting = Blueprint('accounting', __name__, url_prefix='/accounting')


def money(value):
    return "{:,.0f}".format(float(value or 0))


@accounting.app_template_filter('money')
def money_filter(value):
    return money(value)


@accounting.app_template_filter('jalali')
def jalali_filter(value):
    return to_jalali(value)


def date_range():
    start = request.args.get('start', '').strip()
    end = request.args.get('end', '').strip()
    return start, end, jalali_to_gregorian(start), jalali_to_gregorian(end)


@accounting.route('/')
def dashboard():
    start, end, start_g, end_g = date_range()
    return render_template(
        'accounting/dashboard.html',
        summary=get_summary(start_g, end_g), start=start, end=end
    )


@accounting.route('/sales')
def sales():
    start, end, start_g, end_g = date_range()
    return render_template(
        'accounting/sales.html', rows=get_sales(start_g, end_g), start=start, end=end
    )


@accounting.route('/purchases')
def purchases():
    start, end, start_g, end_g = date_range()
    return render_template(
        'accounting/purchases.html', rows=get_purchases(start_g, end_g), start=start, end=end
    )


@accounting.route('/production-cost')
def production_cost():
    start, end, start_g, end_g = date_range()
    return render_template(
        'accounting/production_cost.html',
        rows=get_production_costs(start_g, end_g), start=start, end=end
    )


@accounting.route('/inventory')
def inventory():
    return render_template('accounting/inventory.html', rows=get_inventory())


@accounting.route('/receivables')
def receivables():
    return render_template('accounting/receivables.html', rows=get_receivables())


@accounting.route('/payables')
def payables():
    return render_template('accounting/payables.html', rows=get_payables())


@accounting.route('/cashflow')
def cashflow():
    start, end, start_g, end_g = date_range()
    return render_template(
        'accounting/cashflow.html', rows=get_cashflow(start_g, end_g), start=start, end=end
    )


@accounting.route('/profit-loss')
def profit_loss():
    start, end, start_g, end_g = date_range()
    return render_template(
        'accounting/profit_loss.html',
        result=get_profit_loss(start_g, end_g), start=start, end=end
    )
