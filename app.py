from flask import Flask, redirect, request, session, render_template_string
from config import Config
from app.accounting import accounting
from app.reports import reports
from database.seed import initialize

app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(accounting)
app.register_blueprint(reports)

# =====================================================
# MASTER LOGIN
# Hardcoded master credentials for the system administrator.
# =====================================================
MASTER_USERNAME = "master"
MASTER_PASSWORD = "1234"


@app.route('/', methods=['GET'])
def index():
    if session.get('master_logged_in'):
        return redirect('/master/companies')
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if username == MASTER_USERNAME and password == MASTER_PASSWORD:
            session.clear()
            session['master_logged_in'] = True
            session['master_username'] = MASTER_USERNAME
            return redirect('/master/companies')

        error = 'نام کاربری یا رمز عبور صحیح نیست.'

    return render_template_string('''
<!doctype html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="utf-8">
    <title>ورود</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f3f4f6;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }
        .login-box {
            width: 360px;
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 8px 30px rgba(0,0,0,.10);
        }
        h2 { margin-top: 0; }
        input, button {
            width: 100%;
            box-sizing: border-box;
            padding: 12px;
            margin-top: 10px;
            border-radius: 7px;
            border: 1px solid #ddd;
        }
        button {
            background: #2563eb;
            color: white;
            border: 0;
            cursor: pointer;
        }
        .error { color: #dc2626; margin-top: 12px; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>ورود به سیستم</h2>
        <form method="post">
            <input type="text" name="username" placeholder="نام کاربری" required>
            <input type="password" name="password" placeholder="رمز عبور" required>
            <button type="submit">ورود</button>
        </form>
        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
''', error=error)


@app.route('/master/companies')
def master_companies():
    if not session.get('master_logged_in'):
        return redirect('/login')

    return render_template_string('''
<!doctype html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="utf-8">
    <title>Master - Companies</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f3f4f6;
            margin: 0;
            padding: 30px;
        }
        .panel {
            max-width: 1100px;
            margin: auto;
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 8px 30px rgba(0,0,0,.08);
        }
        .top {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        a {
            text-decoration: none;
            color: white;
            background: #dc2626;
            padding: 9px 16px;
            border-radius: 7px;
        }
    </style>
</head>
<body>
    <div class="panel">
        <div class="top">
            <h1>Master Companies Panel</h1>
            <a href="/master/logout">خروج</a>
        </div>
        <p>ورود Master با موفقیت انجام شد.</p>
        <p>این صفحه محل مدیریت شرکت‌ها خواهد بود.</p>
    </div>
</body>
</html>
''')


@app.route('/master/logout')
def master_logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    initialize()
    app.run(host='0.0.0.0', port=5000, debug=True)
