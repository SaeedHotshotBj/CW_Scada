from database.connection import get_connection


def get_summary(start_date=None, end_date=None):
    conn = get_connection(); cursor = conn.cursor()
    query = """SELECT ISNULL(SUM(SalesAmount),0), ISNULL(SUM(PurchaseAmount),0), ISNULL(SUM(ProductionCost),0), ISNULL(SUM(Profit),0), ISNULL(SUM(MeterProduced),0) FROM AccountantDaily WHERE 1=1"""
    params=[]
    if start_date: query += " AND RecordDate >= ?"; params.append(start_date)
    if end_date: query += " AND RecordDate <= ?"; params.append(end_date)
    cursor.execute(query, params); row=cursor.fetchone(); conn.close()
    return {"sales":float(row[0] or 0),"purchases":float(row[1] or 0),"production_cost":float(row[2] or 0),"profit":float(row[3] or 0),"meters":float(row[4] or 0)}


def _rows(query, params=None):
    conn=get_connection(); cursor=conn.cursor(); cursor.execute(query, params or []); rows=cursor.fetchall(); conn.close(); return rows


def get_sales(start_date=None,end_date=None):
    q="SELECT SaleDate,CustomerName,ProductName,Quantity,UnitPrice,TotalAmount,PaymentStatus FROM AccountantSales WHERE 1=1"; p=[]
    if start_date:q+=" AND SaleDate >= ?";p.append(start_date)
    if end_date:q+=" AND SaleDate <= ?";p.append(end_date)
    return _rows(q+=" ORDER BY SaleDate DESC",p)


def get_purchases(start_date=None,end_date=None):
    q="SELECT PurchaseDate,SupplierName,MaterialName,Quantity,UnitPrice,TotalAmount,PaymentStatus FROM AccountantPurchases WHERE 1=1";p=[]
    if start_date:q+=" AND PurchaseDate >= ?";p.append(start_date)
    if end_date:q+=" AND PurchaseDate <= ?";p.append(end_date)
    return _rows(q+=" ORDER BY PurchaseDate DESC",p)


def get_production_costs(start_date=None,end_date=None):
    q="SELECT CostDate,MachineName,ProductName,MaterialCost,ElectricityCost,LaborCost,MaintenanceCost,TotalCost FROM AccountantProductionCost WHERE 1=1";p=[]
    if start_date:q+=" AND CostDate >= ?";p.append(start_date)
    if end_date:q+=" AND CostDate <= ?";p.append(end_date)
    return _rows(q+=" ORDER BY CostDate DESC",p)


def get_inventory(): return _rows("SELECT ItemName,Category,Quantity,Unit,UnitPrice,TotalValue,MinimumStock FROM AccountantInventory ORDER BY Category,ItemName")
def get_receivables(): return _rows("SELECT CustomerName,InvoiceNumber,InvoiceDate,DueDate,Amount,PaidAmount,RemainingAmount,Status FROM AccountantReceivables ORDER BY DueDate")
def get_payables(): return _rows("SELECT SupplierName,InvoiceNumber,InvoiceDate,DueDate,Amount,PaidAmount,RemainingAmount,Status FROM AccountantPayables ORDER BY DueDate")


def get_cashflow(start_date=None,end_date=None):
    q="SELECT TransactionDate,TransactionType,Description,Amount FROM AccountantCashFlow WHERE 1=1";p=[]
    if start_date:q+=" AND TransactionDate >= ?";p.append(start_date)
    if end_date:q+=" AND TransactionDate <= ?";p.append(end_date)
    return _rows(q+=" ORDER BY TransactionDate DESC",p)


def get_profit_loss(start_date=None,end_date=None):
    s=get_summary(start_date,end_date); gross=s["sales"]-s["production_cost"]
    return {"sales":s["sales"],"production_cost":s["production_cost"],"gross_profit":gross,"purchases":s["purchases"],"net_profit":s["profit"]}
