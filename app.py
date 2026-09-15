from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

ADMIN_CREDENTIALS = {
    'username': 'admin',
    'email': 'admin@cyber.com',
    'phone': '0712345678',
    'password': '1234'
}

client_orders = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_order():
    client_name = request.form.get('client_name')
    phone = request.form.get('phone')
    service = request.form.get('service')
    mpesa_code = request.form.get('mpesa_code')
    
    order_id = len(client_orders) + 1
    order = {
        'id': order_id,
        'client_name': client_name,
        'phone': phone,
        'service': service,
        'mpesa_code': mpesa_code
    }
    client_orders.append(order)
    return render_template('order_success.html', client_name=client_name)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')
        
        valid_user = (
            identifier == ADMIN_CREDENTIALS['username'] or 
            identifier == ADMIN_CREDENTIALS['email'] or 
            identifier == ADMIN_CREDENTIALS['phone']
        )
        
        if valid_user and password == ADMIN_CREDENTIALS['password']:
            session['admin_logged_in'] = True
            session['admin_user'] = ADMIN_CREDENTIALS['username']
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Invalid credentials. Please try again.'
            
    return render_template('login.html', error=error)

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html', orders=client_orders, current_user=session.get('admin_user'))

@app.route('/receipt/<int:order_id>')
def receipt(order_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    
    order = next((o for o in client_orders if o['id'] == order_id), None)
    if not order:
        return "Receipt not found", 404
        
    return render_template('receipt.html', order=order)

@app.route('/change_password', methods=['POST'])
def change_password():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
        
    current_pass = request.form.get('current_password')
    new_pass = request.form.get('new_password')
    
    if current_pass == ADMIN_CREDENTIALS['password']:
        ADMIN_CREDENTIALS['password'] = new_pass
        return redirect(url_for('admin_dashboard'))
    else:
        return "Current password incorrect", 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
