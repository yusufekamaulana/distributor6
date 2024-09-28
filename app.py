from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'distributor6'
app.secret_key = 'your_secret_key'
mysql = MySQL(app) 

@app.route('/')
def landing_page():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Both email and password are required!', 'danger')
            return redirect(url_for('login_page'))

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[3], password):  # user[3] is the hashed password
            session['user_id'] = user[0]  # Store user ID in session
            session['nama_lengkap'] = user[2]
            flash('Login successful!', 'success')
            return redirect(url_for('home_page'))
        else:
            flash('Login failed. Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        nama_lengkap = request.form.get('nama_lengkap')
        email = request.form.get('email')
        password = request.form.get('password')

        if not nama_lengkap or not email or not password:
            flash('All fields are required!', 'danger')
            return redirect(url_for('register_page'))

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cur.fetchone()

        if existing_user:
            flash('Email already registered. Please log in.', 'warning')
            return redirect(url_for('login_page'))

        hashed_password = generate_password_hash(password)
        cur.execute("INSERT INTO users (email, nama_lengkap, password) VALUES (%s, %s, %s)", 
                    (email, nama_lengkap, hashed_password))
        mysql.connection.commit()
        cur.close()

        flash('Registration successful! You can log in now.', 'success')
        return redirect(url_for('login_page'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('landing_page'))

@app.route('/home')
def home_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
