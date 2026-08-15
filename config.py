class Config:
    SECRET_KEY = "DEMO_ACCOUNTANT_SECRET_KEY"
    SQL_SERVER = r"."
    SQL_DATABASE = "CW_SCADA"
    SQL_DRIVER = "ODBC Driver 11 for SQL Server"
    CONNECTION_STRING = (
        f"DRIVER={{{SQL_DRIVER}}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        "Trusted_Connection=yes;"
    )
