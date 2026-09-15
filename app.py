from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Admin credentials supporting username, email, or phone number
ADMIN_CREDENTIALS = {
    'username': 'admin',
    'email': 'admin@cyber.com',
    'phone': '0712345678',
    'password': '1234'
}

# In-memory storage for client orders
client_orders = []

@app.route('/')
def home():
    if 'user' in session:
        return render_template('admin_dashboard.html', orders=client_orders, current_user=session['user'])
    else:
        return render_template('public_form.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        login_identifier = request.form.get('identifier').strip()
        password = request.form.get('password')
        
        if (login_identifier == ADMIN_CREDENTIALS['username'] or 
            login_identifier == ADMIN_CREDENTIALS['email'] or 
            login_identifier == ADMIN_CREDENTIALS['phone']):
            
            if password == ADMIN_CREDENTIALS['password']:
                session['user'] = login_identifier
                return redirect(url_for('home'))
            else:
                error = 'Incorrect Password!'
        else:
            error = 'Identifier (Username/Email/Phone) not recognized!'
            
    return render_template('login.html', error=error)

@app.route('/submit_order', methods=['POST'])
def submit_order():
    client_name = request.form.get('client_name')
    phone = request.form.get('phone')
    service = request.form.get('service')
    mpesa_code = request.form.get('mpesa_code')
    
    order_id = len(client_orders) + 1
    
    order_details = {
        'id': order_id,
        'client_name': client_name,
        'phone': phone,
        'service': service,
        'mpesa_code': mpesa_code.upper()
    }
    client_orders.append(order_details)
    return render_template('order_success.html', client_name=client_name)

@app.route('/receipt/<int:order_id>')
def view_receipt(order_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    order = next((o for o in client_orders if o['id'] == order_id), None)
    if not order:
        return "Receipt not found", 404
        
    return render_template('receipt.html', order=order)

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    current_pass = request.form.get('current_password')
    new_pass = request.form.get('new_password')
    
    if current_pass == ADMIN_CREDENTIALS['password']:
        ADMIN_CREDENTIALS['password'] = new_pass
        return redirect(url_for('home'))
    else:
        return "Current password incorrect!", 400

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
