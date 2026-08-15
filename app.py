from flask import Flask,redirect
from config import Config
from app.accounting import accounting
from app.reports import reports
from database.seed import initialize

app=Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(accounting)
app.register_blueprint(reports)

@app.route('/')
def index():return redirect('/accounting/')

if __name__=='__main__':
    initialize()
    app.run(host='0.0.0.0',port=5000,debug=True)
