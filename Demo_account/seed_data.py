from datetime import date, timedelta
from database import connection


def seed_fake_data():
    conn = connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM DemoAccountTransactions")
    if cur.fetchone()[0] > 0:
        conn.close()
        return
    customers = ["شرکت سیم و کابل پارس", "صنایع کابل آریا", "بازرگانی برق گستر", "شرکت توزیع نیروی شرق", "پروژه ساختمانی نوین"]
    products = [("کابل چهار در یک افشان",185000),("کابل سه در دو و نیم افشان",225000),("سیم افشان یک و نیم",210000),("سیم افشان دو و نیم",205000),("کابل کنترل چهار رشته",165000),("کابل قدرت چهار در شش",310000)]
    rows=[]
    start=date(2026,7,1)
    for day in range(31):
        d=start+timedelta(days=day)
        for n in range(3):
            customer=customers[(day+n)%len(customers)]
            product,base=products[(day*3+n)%len(products)]
            weight=round(120+((day*37+n*83)%880),3)
            meters=round(800+((day*113+n*257)%6200),3)
            weight_price=base+((day+n)%5)*2500
            meter_price=1800+((day*7+n*13)%12)*150
            rows.append((d,customer,product,weight,weight_price,meters,meter_price,"فاکتور آزمایشی فروش و تولید"))
    cur.fast_executemany=True
    cur.executemany("""INSERT INTO DemoAccountTransactions
    (RecordDate,CustomerName,ProductName,Weight,WeightPrice,Meters,MeterPrice,Description)
    VALUES (?,?,?,?,?,?,?,?)""", rows)
    conn.commit()
    conn.close()
