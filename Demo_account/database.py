import os
import pyodbc

SERVER = os.getenv("SCADA_SQL_SERVER", r"DESKTOP-2UBRA9H\WINCC")
DATABASE = os.getenv("SCADA_SQL_DATABASE", "CW_SCADA")
DRIVER = os.getenv("SCADA_SQL_DRIVER", "ODBC Driver 11 for SQL Server")


def connection():
    return pyodbc.connect(
        f"DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;"
    )


def init_db():
    conn = connection()
    cur = conn.cursor()
    cur.execute("""
    IF OBJECT_ID('DemoAccountTransactions','U') IS NULL
    CREATE TABLE DemoAccountTransactions(
        ID INT IDENTITY(1,1) PRIMARY KEY,
        RecordDate DATE NOT NULL,
        CustomerName NVARCHAR(200) NOT NULL,
        ProductName NVARCHAR(200) NOT NULL,
        Weight DECIMAL(18,3) NOT NULL DEFAULT 0,
        WeightPrice DECIMAL(18,2) NOT NULL DEFAULT 0,
        WeightAmount AS (Weight * WeightPrice) PERSISTED,
        Meters DECIMAL(18,3) NOT NULL DEFAULT 0,
        MeterPrice DECIMAL(18,2) NOT NULL DEFAULT 0,
        MeterAmount AS (Meters * MeterPrice) PERSISTED,
        TotalAmount AS ((Weight * WeightPrice) + (Meters * MeterPrice)) PERSISTED,
        Description NVARCHAR(500) NULL,
        CreatedAt DATETIME2 NOT NULL DEFAULT SYSDATETIME()
    )
    """)
    conn.commit()
    conn.close()


def query_rows(start, end, product="", customer=""):
    conn = connection()
    cur = conn.cursor()
    sql = """SELECT ID,RecordDate,CustomerName,ProductName,Weight,WeightPrice,WeightAmount,
                     Meters,MeterPrice,MeterAmount,TotalAmount,Description
              FROM DemoAccountTransactions WHERE 1=1"""
    params = []
    if start:
        from jalali import jalali_to_gregorian
        sql += " AND RecordDate >= ?"
        params.append(jalali_to_gregorian(start))
    if end:
        from jalali import jalali_to_gregorian
        sql += " AND RecordDate <= ?"
        params.append(jalali_to_gregorian(end))
    if product:
        sql += " AND ProductName = ?"
        params.append(product)
    if customer:
        sql += " AND CustomerName LIKE ?"
        params.append(f"%{customer}%")
    sql += " ORDER BY RecordDate DESC, ID DESC"
    cur.execute(sql, params)
    columns = [c[0] for c in cur.description]
    rows = [dict(zip(columns, row)) for row in cur.fetchall()]
    conn.close()
    return rows


def insert_transaction(record_date, customer, product, weight, weight_price, meters, meter_price, description):
    conn = connection()
    cur = conn.cursor()
    cur.execute("""INSERT INTO DemoAccountTransactions
        (RecordDate,CustomerName,ProductName,Weight,WeightPrice,Meters,MeterPrice,Description)
        VALUES (?,?,?,?,?,?,?,?)""",
        record_date, customer, product, weight, weight_price, meters, meter_price, description)
    conn.commit()
    conn.close()
