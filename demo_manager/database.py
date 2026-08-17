import pyodbc

SERVER = 'localhost'
DATABASE = 'CW_SCADA'
DRIVER = 'ODBC Driver 11 for SQL Server'


def connection():
    return pyodbc.connect(f'DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;')


def init_db():
    conn = connection(); cur = conn.cursor()
    cur.execute('''
    IF OBJECT_ID('dbo.ManagerProductPrices','U') IS NULL
    CREATE TABLE dbo.ManagerProductPrices(
        ID INT IDENTITY(1,1) PRIMARY KEY,
        ProductName NVARCHAR(200) NOT NULL UNIQUE,
        WeightPrice DECIMAL(18,2) NOT NULL DEFAULT 0,
        MeterPrice DECIMAL(18,2) NOT NULL DEFAULT 0,
        UpdatedAt DATETIME2 NOT NULL DEFAULT SYSDATETIME()
    )
    ''')
    cur.execute('''
    INSERT INTO dbo.ManagerProductPrices(ProductName,WeightPrice,MeterPrice)
    SELECT p.ProductName,100000,1000
    FROM (SELECT DISTINCT ProductName FROM dbo.production WHERE ProductName IS NOT NULL) p
    WHERE NOT EXISTS (SELECT 1 FROM dbo.ManagerProductPrices m WHERE m.ProductName=p.ProductName)
    ''')
    conn.commit(); conn.close()


def get_products():
    conn=connection(); cur=conn.cursor()
    cur.execute('SELECT DISTINCT ProductName FROM dbo.production WHERE ProductName IS NOT NULL ORDER BY ProductName')
    rows=[r[0] for r in cur.fetchall()]; conn.close(); return rows


def _jalali_to_gregorian(value):
    if not value: return None
    try:
        from jalali import jalali_to_gregorian
        return jalali_to_gregorian(value)
    except Exception: return None


def get_manager_rows(start='', end='', product=''):
    conn=connection(); cur=conn.cursor()
    sql='''SELECT p.ProductionTime,p.ProductName,p.Quantity,p.MeterProduced,
                  ISNULL(m.WeightPrice,0),ISNULL(m.MeterPrice,0)
           FROM dbo.production p
           LEFT JOIN dbo.ManagerProductPrices m ON m.ProductName=p.ProductName
           WHERE 1=1'''
    params=[]
    gs=_jalali_to_gregorian(start); ge=_jalali_to_gregorian(end)
    if gs: sql+=' AND p.ProductionTime >= ?'; params.append(gs)
    if ge: sql+=' AND p.ProductionTime < DATEADD(day,1,?)'; params.append(ge)
    if product: sql+=' AND p.ProductName = ?'; params.append(product)
    sql+=' ORDER BY p.ProductionTime DESC,p.ProductionID DESC'
    try: cur.execute(sql,params); raw=cur.fetchall()
    except Exception as exc:
        conn.close(); return empty(f'خطا در خواندن dbo.production: {exc}')
    result=[]; sw=sm=swa=sma=total=0
    from jalali import gregorian_to_jalali
    for dt,pn,w,m,wp,mp in raw:
        w=float(w or 0); m=float(m or 0); wp=float(wp or 0); mp=float(mp or 0)
        wa=w*wp; ma=m*mp; ta=wa+ma
        result.append({'date':gregorian_to_jalali(dt),'product':pn or 'بدون محصول','weight':w,'weight_price':wp,'weight_amount':wa,'meters':m,'meter_price':mp,'meter_amount':ma,'total':ta})
        sw+=w; sm+=m; swa+=wa; sma+=ma; total+=ta
    conn.close()
    return {'rows':result,'summary':{'weight':sw,'meters':sm,'weight_amount':swa,'meter_amount':sma,'total':total},'message':''}


def empty(message):
    return {'rows':[],'summary':{'weight':0,'meters':0,'weight_amount':0,'meter_amount':0,'total':0},'message':message}
