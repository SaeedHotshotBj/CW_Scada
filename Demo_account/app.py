from flask import Flask, render_template, request, redirect, url_for, flash
from database import init_db, query_rows, insert_transaction
from jalali import jalali_to_gregorian, gregorian_to_jalali

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "cw-scada-demo-account"


def date_to_gregorian(value):
    if not value:
        return None
    return jalali_to_gregorian(value)


@app.route("/")
def index():
    return redirect(url_for("accounting"))


@app.route("/accounting")
def accounting():
    start = request.args.get("start", "")
    end = request.args.get("end", "")
    product = request.args.get("product", "")
    customer = request.args.get("customer", "")
    rows = query_rows(start, end, product, customer)
    totals = {
        "weight": sum(float(r["Weight"]) for r in rows),
        "meters": sum(float(r["Meters"]) for r in rows),
        "weight_amount": sum(float(r["WeightAmount"]) for r in rows),
        "meter_amount": sum(float(r["MeterAmount"]) for r in rows),
        "total": sum(float(r["TotalAmount"]) for r in rows),
    }
    products = sorted({r["ProductName"] for r in rows})
    return render_template("index.html", rows=rows, totals=totals, products=products,
                           start=start, end=end, product=product, customer=customer)


@app.post("/accounting/add")
def add():
    try:
        data = request.form
        insert_transaction(
            date_to_gregorian(data.get("date")), data.get("customer", ""),
            data.get("product", ""), float(data.get("weight") or 0),
            float(data.get("weight_price") or 0), float(data.get("meters") or 0),
            float(data.get("meter_price") or 0), data.get("description", "")
        )
        flash("رکورد با موفقیت ثبت شد.", "success")
    except Exception as exc:
        flash(f"خطا در ثبت اطلاعات: {exc}", "danger")
    return redirect(url_for("accounting"))


@app.template_filter("jalali")
def jalali_filter(value):
    return gregorian_to_jalali(value) if value else ""


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
