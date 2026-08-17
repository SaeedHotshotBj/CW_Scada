from flask import Flask, render_template, request, jsonify
from database import init_db, get_manager_rows, get_products

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.get('/api/products')
def products():
    return jsonify(get_products())

@app.get('/api/manager_data')
def manager_data():
    start = request.args.get('start', '').strip()
    end = request.args.get('end', '').strip()
    product = request.args.get('product', '').strip()
    return jsonify(get_manager_rows(start, end, product))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001, debug=True)
