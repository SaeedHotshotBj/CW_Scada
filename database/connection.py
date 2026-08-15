import pyodbc
from config import Config

def get_connection():
    return pyodbc.connect(Config.CONNECTION_STRING)
