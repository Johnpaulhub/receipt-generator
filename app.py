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
