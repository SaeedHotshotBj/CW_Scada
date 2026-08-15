from datetime import datetime, timedelta
from database.connection import get_connection


def initialize():
    conn = get_connection()
    c = conn.cursor()

    statements = [
        """IF OBJECT_ID('AccountantDaily','U') IS NULL CREATE TABLE AccountantDaily(ID INT IDENTITY PRIMARY KEY,RecordDate DATE NOT NULL,SalesAmount DECIMAL(18,2),PurchaseAmount DECIMAL(18,2),ProductionCost DECIMAL(18,2),Profit DECIMAL(18,2),MeterProduced DECIMAL(18,2))""",
        """IF OBJECT_ID('AccountantSales','U') IS NULL CREATE TABLE AccountantSales(ID INT IDENTITY PRIMARY KEY,SaleDate DATETIME NOT NULL,CustomerName NVARCHAR(200),ProductName NVARCHAR(200),Quantity DECIMAL(18,2),UnitPrice DECIMAL(18,2),TotalAmount DECIMAL(18,2),PaymentStatus NVARCHAR(50))""",
        """IF OBJECT_ID('AccountantPurchases','U') IS NULL CREATE TABLE AccountantPurchases(ID INT IDENTITY PRIMARY KEY,PurchaseDate DATETIME NOT NULL,SupplierName NVARCHAR(200),MaterialName NVARCHAR(200),Quantity DECIMAL(18,2),UnitPrice DECIMAL(18,2),TotalAmount DECIMAL(18,2),PaymentStatus NVARCHAR(50))""",
        """IF OBJECT_ID('AccountantProductionCost','U') IS NULL CREATE TABLE AccountantProductionCost(ID INT IDENTITY PRIMARY KEY,CostDate DATETIME NOT NULL,MachineName NVARCHAR(200),ProductName NVARCHAR(200),MaterialCost DECIMAL(18,2),ElectricityCost DECIMAL(18,2),LaborCost DECIMAL(18,2),MaintenanceCost DECIMAL(18,2),TotalCost DECIMAL(18,2))""",
        """IF OBJECT_ID('AccountantInventory','U') IS NULL CREATE TABLE AccountantInventory(ID INT IDENTITY PRIMARY KEY,ItemName NVARCHAR(200),Category NVARCHAR(100),Quantity DECIMAL(18,2),Unit NVARCHAR(50),UnitPrice DECIMAL(18,2),TotalValue DECIMAL(18,2),MinimumStock DECIMAL(18,2))""",
        """IF OBJECT_ID('AccountantReceivables','U') IS NULL CREATE TABLE AccountantReceivables(ID INT IDENTITY PRIMARY KEY,CustomerName NVARCHAR(200),InvoiceNumber NVARCHAR(100),InvoiceDate DATE,DueDate DATE,Amount DECIMAL(18,2),PaidAmount DECIMAL(18,2),RemainingAmount DECIMAL(18,2),Status NVARCHAR(50))""",
        """IF OBJECT_ID('AccountantPayables','U') IS NULL CREATE TABLE AccountantPayables(ID INT IDENTITY PRIMARY KEY,SupplierName NVARCHAR(200),InvoiceNumber NVARCHAR(100),InvoiceDate DATE,DueDate DATE,Amount DECIMAL(18,2),PaidAmount DECIMAL(18,2),RemainingAmount DECIMAL(18,2),Status NVARCHAR(50))""",
        """IF OBJECT_ID('AccountantCashFlow','U') IS NULL CREATE TABLE AccountantCashFlow(ID INT IDENTITY PRIMARY KEY,TransactionDate DATETIME,TransactionType NVARCHAR(50),Description NVARCHAR(300),Amount DECIMAL(18,2))"""
    ]
    for statement in statements:
        c.execute(statement)

    c.execute("SELECT COUNT(*) FROM AccountantDaily")
    daily_count = c.fetchone()[0]

    # Demo period: one complete Gregorian month (July 2026).
    # The web application converts these dates to Jalali for display/filtering.
    if daily_count < 31:
        tables = [
            'AccountantCashFlow', 'AccountantPayables', 'AccountantReceivables',
            'AccountantInventory', 'AccountantProductionCost',
            'AccountantPurchases', 'AccountantSales', 'AccountantDaily'
        ]
        for table in tables:
            c.execute(f'DELETE FROM {table}')

        customers = [
            'شرکت کابل پارس', 'صنایع برق آریا', 'پروژه نیرو گستر',
            'شرکت ساختمان شرق', 'تأسیسات نوین', 'پارس انرژی',
            'صنایع برق خاور', 'شرکت توسعه نیرو'
        ]
        products = [
            ('کابل قدرت 4x16', 850000, 1200),
            ('کابل قدرت 3x35', 1250000, 850),
            ('کابل افشان 4x6', 490000, 1800),
            ('سیم افشان 2.5', 310000, 2500),
            ('سیم ارت 16', 190000, 3000),
            ('کابل کنترل 4x2.5', 420000, 1600)
        ]
        suppliers = [
            ('مس ایران', 'مفتول مسی', 185000),
            ('پتروشیمی پارس', 'گرانول PVC', 145000),
            ('مواد عایق شرق', 'مواد عایق', 210000),
            ('فولاد مرکزی', 'قرقره فلزی', 850000),
            ('پارس پلیمر', 'مواد روکش', 175000),
            ('صنایع مس نوین', 'مفتول مسی نرم', 191000)
        ]
        machines = ['خط تولید شماره 1', 'خط تولید شماره 2', 'خط تولید شماره 3', 'خط تولید شماره 4']
        start = datetime(2026, 7, 1)

        for day in range(31):
            dt = start + timedelta(days=day)
            factor = 0.90 + ((day * 7) % 13) / 100
            sales_total = 0
            purchase_total = 0
            production_total = 0
            meters = 0

            # Three sales invoices every day.
            for n in range(3):
                customer = customers[(day + n) % len(customers)]
                product, base_price, base_qty = products[(day + n * 2) % len(products)]
                qty = round(base_qty * factor * (0.92 + n * 0.06), 2)
                price = round(base_price * (1 + ((day + n) % 5) * 0.012))
                total = round(qty * price)
                status = ['پرداخت شده', 'بخشی پرداخت شده', 'در انتظار پرداخت'][(day + n) % 3]
                sale_time = f'{8 + n * 3:02d}:{20 + (day * 3 + n * 10) % 35:02d}'
                c.execute(
                    "INSERT INTO AccountantSales(SaleDate,CustomerName,ProductName,Quantity,UnitPrice,TotalAmount,PaymentStatus) VALUES(?,?,?,?,?,?,?)",
                    (f'{dt:%Y-%m-%d} {sale_time}', customer, product, qty, price, total, status)
                )
                sales_total += total
                meters += qty

            # Two purchase invoices every day.
            for n in range(2):
                supplier, material, base_price = suppliers[(day + n) % len(suppliers)]
                qty = round((1800 + ((day * 173 + n * 420) % 2200)) * (0.92 + n * 0.08), 2)
                price = round(base_price * (1 + ((day + n) % 6) * 0.009))
                total = round(qty * price)
                status = ['پرداخت شده', 'بخشی پرداخت شده', 'در انتظار پرداخت'][(day + n + 1) % 3]
                purchase_time = f'{9 + n * 3:02d}:{10 + (day * 4 + n * 7) % 40:02d}'
                c.execute(
                    "INSERT INTO AccountantPurchases(PurchaseDate,SupplierName,MaterialName,Quantity,UnitPrice,TotalAmount,PaymentStatus) VALUES(?,?,?,?,?,?,?)",
                    (f'{dt:%Y-%m-%d} {purchase_time}', supplier, material, qty, price, total, status)
                )
                purchase_total += total

            # Three production-cost records per day.
            for n in range(3):
                machine = machines[(day + n) % len(machines)]
                product = products[(day + n) % len(products)][0]
                material_cost = round(sales_total * (0.19 + n * 0.018))
                electricity = round(sales_total * (0.025 + n * 0.003))
                labor = round(sales_total * (0.045 + n * 0.004))
                maintenance = round(sales_total * (0.012 + ((day + n) % 4) * 0.002))
                total_cost = material_cost + electricity + labor + maintenance
                c.execute(
                    "INSERT INTO AccountantProductionCost(CostDate,MachineName,ProductName,MaterialCost,ElectricityCost,LaborCost,MaintenanceCost,TotalCost) VALUES(?,?,?,?,?,?,?,?)",
                    (f'{dt:%Y-%m-%d}', machine, product, material_cost, electricity, labor, maintenance, total_cost)
                )
                production_total += total_cost

            profit = sales_total - production_total
            c.execute(
                "INSERT INTO AccountantDaily(RecordDate,SalesAmount,PurchaseAmount,ProductionCost,Profit,MeterProduced) VALUES(?,?,?,?,?,?)",
                (f'{dt:%Y-%m-%d}', sales_total, purchase_total, production_total, profit, round(meters))
            )

            # Three cash-flow transactions every day.
            receipt = round(sales_total * [0.35, 0.45, 0.55, 0.30][day % 4])
            material_payment = -round(purchase_total * [0.40, 0.55, 0.30][day % 3])
            salary_and_overhead = -round(production_total * 0.055)
            c.execute(
                "INSERT INTO AccountantCashFlow(TransactionDate,TransactionType,Description,Amount) VALUES(?,?,?,?)",
                (f'{dt:%Y-%m-%d} 11:00', 'دریافت', 'دریافت از مشتریان', receipt)
            )
            c.execute(
                "INSERT INTO AccountantCashFlow(TransactionDate,TransactionType,Description,Amount) VALUES(?,?,?,?)",
                (f'{dt:%Y-%m-%d} 14:00', 'پرداخت', 'پرداخت خرید مواد اولیه', material_payment)
            )
            c.execute(
                "INSERT INTO AccountantCashFlow(TransactionDate,TransactionType,Description,Amount) VALUES(?,?,?,?)",
                (f'{dt:%Y-%m-%d} 17:00', 'پرداخت', 'حقوق و هزینه های جاری تولید', salary_and_overhead)
            )

        # Inventory snapshot for the end of the demo month.
        inventory = [
            ('مفتول مسی', 'مواد اولیه', 9800, 'کیلوگرم', 192000, 3200),
            ('گرانول PVC', 'مواد اولیه', 5400, 'کیلوگرم', 149000, 1800),
            ('مواد عایق', 'مواد اولیه', 2700, 'کیلوگرم', 216000, 900),
            ('قرقره فلزی', 'بسته بندی', 240, 'عدد', 890000, 60),
            ('مواد روکش', 'مواد اولیه', 3100, 'کیلوگرم', 178000, 1000),
            ('کابل قدرت 4x16', 'محصول نهایی', 6200, 'متر', 860000, 1500),
            ('کابل قدرت 3x35', 'محصول نهایی', 4100, 'متر', 1270000, 1000),
            ('سیم افشان 2.5', 'محصول نهایی', 7600, 'متر', 318000, 2000)
        ]
        for row in inventory:
            item, category, quantity, unit, unit_price, minimum = row
            c.execute(
                "INSERT INTO AccountantInventory(ItemName,Category,Quantity,Unit,UnitPrice,TotalValue,MinimumStock) VALUES(?,?,?,?,?,?,?)",
                (item, category, quantity, unit, unit_price, round(quantity * unit_price), minimum)
            )

        # Receivable and payable aging examples.
        receivables = [
            ('شرکت کابل پارس', 'INV-1001', '2026-07-03', '2026-07-18', 1850000000, 1850000000),
            ('صنایع برق آریا', 'INV-1002', '2026-07-06', '2026-07-21', 1280000000, 700000000),
            ('پروژه نیرو گستر', 'INV-1003', '2026-07-09', '2026-07-24', 2140000000, 1200000000),
            ('شرکت ساختمان شرق', 'INV-1004', '2026-07-13', '2026-07-28', 980000000, 0),
            ('تأسیسات نوین', 'INV-1005', '2026-07-17', '2026-08-02', 1560000000, 600000000),
            ('پارس انرژی', 'INV-1006', '2026-07-22', '2026-08-07', 1730000000, 900000000),
            ('صنایع برق خاور', 'INV-1007', '2026-07-27', '2026-08-12', 1190000000, 0)
        ]
        for i, row in enumerate(receivables, 1):
            customer, invoice, invoice_date, due_date, amount, paid = row
            status = 'تسویه شده' if paid == amount else ('بخشی پرداخت شده' if paid else 'در انتظار پرداخت')
            c.execute(
                "INSERT INTO AccountantReceivables(CustomerName,InvoiceNumber,InvoiceDate,DueDate,Amount,PaidAmount,RemainingAmount,Status) VALUES(?,?,?,?,?,?,?,?)",
                (customer, invoice, invoice_date, due_date, amount, paid, amount - paid, status)
            )

        payables = [
            ('مس ایران', 'PUR-2001', '2026-07-02', '2026-07-17', 2250000000, 1500000000),
            ('پتروشیمی پارس', 'PUR-2002', '2026-07-05', '2026-07-20', 980000000, 980000000),
            ('مواد عایق شرق', 'PUR-2003', '2026-07-10', '2026-07-25', 720000000, 350000000),
            ('فولاد مرکزی', 'PUR-2004', '2026-07-14', '2026-07-30', 430000000, 0),
            ('پارس پلیمر', 'PUR-2005', '2026-07-19', '2026-08-03', 850000000, 400000000),
            ('صنایع مس نوین', 'PUR-2006', '2026-07-24', '2026-08-09', 1160000000, 0)
        ]
        for row in payables:
            supplier, invoice, invoice_date, due_date, amount, paid = row
            status = 'تسویه شده' if paid == amount else ('بخشی پرداخت شده' if paid else 'در انتظار پرداخت')
            c.execute(
                "INSERT INTO AccountantPayables(SupplierName,InvoiceNumber,InvoiceDate,DueDate,Amount,PaidAmount,RemainingAmount,Status) VALUES(?,?,?,?,?,?,?,?)",
                (supplier, invoice, invoice_date, due_date, amount, paid, amount - paid, status)
            )

    conn.commit()
    conn.close()
