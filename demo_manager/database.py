import pyodbc

SERVER = '.'
DATABASE = 'CW_SCADA'
DRIVER = 'ODBC Driver 11 for SQL Server'


def connection():
    return pyodbc.connect(
        f'DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'
    )


def init_db():
    conn = connection()
    cur = conn.cursor()
    cur.execute('''
    IF OBJECT_ID('ManagerProductPrices','U') IS NULL
    CREATE TABLE ManagerProductPrices(
        ID INT IDENTITY(1,1) PRIMARY KEY,
        ProductName NVARCHAR(200) NOT NULL UNIQUE,
        WeightPrice DECIMAL(18,2) NOT NULL DEFAULT 0,
        MeterPrice DECIMAL(18,2) NOT NULL DEFAULT 0,
        UpdatedAt DATETIME2 NOT NULL DEFAULT SYSDATETIME()
    )
    ''')
    conn.commit()
    conn.close()


def get_products():
    conn = connection()
    cur = conn.cursor()
    cur.execute('SELECT ProductName FROM ManagerProductPrices ORDER BY ProductName')
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return rows


def _jalali_to_gregorian(value):
    if not value:
        return None
    try:
        from jalali import jalali_to_gregorian
        return jalali_to_gregorian(value)
    except Exception:
        return None


def get_manager_rows(start='', end='', product=''):
    conn = connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.name
        FROM sys.columns c
        INNER JOIN sys.tables t ON c.object_id=t.object_id
        WHERE t.name='TrendLog'
        ORDER BY c.column_id
    """)
    columns = [r[0] for r in cur.fetchall()]
    if not columns:
        conn.close()
        return {'rows': [], 'summary': {'weight': 0, 'meters': 0, 'weight_amount': 0, 'meter_amount': 0, 'total': 0}, 'message': 'جدول TrendLog پیدا نشد.'}

    def pick(names):
        exact = {c.lower(): c for c in columns}
        for name in names:
            if name.lower() in exact:
                return exact[name.lower()]
        for col in columns:
            if any(name.lower() in col.lower() for name in names):
                return col
        return None

    ts = pick(['Timestamp', 'RecordDate', 'Date', 'CreatedAt'])
    weight = pick(['Weight', 'وزن', 'WeightValue'])
    meters = pick(['Meters', 'Meter', 'متراژ', 'MeterValue', 'MeterProduced'])
    pname = pick(['ProductName', 'Product', 'نوع محصول', 'ProductType'])

    if not ts or (not weight and not meters):
        conn.close()
        return {'rows': [], 'summary': {'weight': 0, 'meters': 0, 'weight_amount': 0, 'meter_amount': 0, 'total': 0}, 'message': 'ستون‌های تاریخ/وزن/متراژ در TrendLog پیدا نشدند.'}

    weight_sql = f'[{weight}]' if weight else '0'
    meters_sql = f'[{meters}]' if meters else '0'
    product_sql = f'[{pname}]' if pname else "''"
    sql = f'SELECT [{ts}], {weight_sql} AS WeightValue, {meters_sql} AS MeterValue, {product_sql} AS ProductName FROM TrendLog WHERE 1=1'
    params = []
    gs = _jalali_to_gregorian(start)
    ge = _jalali_to_gregorian(end)
    if gs:
        sql += f' AND [{ts}] >= ?'
        params.append(gs)
    if ge:
        sql += f' AND [{ts}] < DATEADD(day,1,?)'
        params.append(ge)
    if product and pname:
        sql += f' AND [{pname}] = ?'
        params.append(product)
    sql += f' ORDER BY [{ts}] DESC'

    try:
        cur.execute(sql, params)
        raw = cur.fetchall()
        cur.execute('SELECT ProductName, WeightPrice, MeterPrice FROM ManagerProductPrices')
        prices = {r[0]: (float(r[1]), float(r[2])) for r in cur.fetchall()}
    except Exception as exc:
        conn.close()
        return {'rows': [], 'summary': {'weight': 0, 'meters': 0, 'weight_amount': 0, 'meter_amount': 0, 'total': 0}, 'message': f'خطا در خواندن اطلاعات: {exc}'}

    result = []
    sw = sm = swa = sma = total = 0
    for dt, w, m, pn in raw:
        w = float(w or 0)
        m = float(m or 0)
        pn = pn or 'بدون محصول'
        wp, mp = prices.get(pn, (0, 0))
        wa = w * wp
        ma = m * mp
        ta = wa + ma
        result.append({
            'date': dt.strftime('%Y-%m-%d %H:%M') if hasattr(dt, 'strftime') else str(dt),
            'product': pn,
            'weight': w,
            'weight_price': wp,
            'weight_amount': wa,
            'meters': m,
            'meter_price': mp,
            'meter_amount': ma,
            'total': ta
        })
        sw += w
        sm += m
        swa += wa
        sma += ma
        total += ta

    conn.close()
    return {'rows': result, 'summary': {'weight': sw, 'meters': sm, 'weight_amount': swa, 'meter_amount': sma, 'total': total}, 'message': ''}
