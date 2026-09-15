import io
import random
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for session management

# Demo user credentials
USER_DATA = {'admin': '1234'}


@app.route('/')
def home():
  if 'username' not in session:
    return redirect(url_for('login'))
  return render_template('index.html', user=session['username'])


@app.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':
    username = request.form.get('username')
    password = request.form.get('password')

    if username in USER_DATA and USER_DATA[username] == password:
      session['username'] = username
      return redirect(url_for('home'))
    else:
      error = 'Invalid Username or Password!'

  return render_template('login.html', error=error)


@app.route('/logout')
def logout():
  session.pop('username', None)
  return redirect(url_for('login'))


@app.route('/generate', methods=['POST'])
def generate():
  if 'username' not in session:
    return redirect(url_for('login'))

  business_name = request.form.get('business_name')
  phone = request.form.get('phone')
  customer = request.form.get('customer')
  item = request.form.get('item')
  price = request.form.get('price')
  quantity = request.form.get('quantity')

  try:
    total = float(price) * int(quantity)
  except ValueError:
    total = 0.0

  receipt_data = {
      'business_name': business_name,
      'phone': phone,
      'customer': customer,
      'item': item,
      'price': price,
      'quantity': quantity,
      'total': f'{total:,.2f}',
  }

  return render_template(
      'index.html', receipt=receipt_data, user=session['username']
  )


@app.route('/download', methods=['POST'])
def download_pdf():
  if 'username' not in session:
    return redirect(url_for('login'))

  business_name = request.form.get('business_name')
  phone = request.form.get('phone')
  customer = request.form.get('customer')
  item = request.form.get('item')
  price = request.form.get('price')
  quantity = request.form.get('quantity')

  try:
    total = float(price) * int(quantity)
  except ValueError:
    total = 0.0

  receipt_no = f'REC-{random.randint(1000, 9999)}'

  buffer = io.BytesIO()
  doc = SimpleDocTemplate(buffer, pagesize=letter)
  styles = getSampleStyleSheet()
  story = []

  story.append(Paragraph(f'<b>{business_name.upper()}</b>', styles['Title']))
  story.append(Paragraph(f'Phone: {phone}', styles['Normal']))
  story.append(Paragraph(f'Receipt No: {receipt_no}', styles['Normal']))
  story.append(Paragraph(f'Customer: {customer}', styles['Normal']))
  story.append(Spacer(1, 15))

  data = [
      ['Item Description', 'Qty', 'Unit Price', 'Total Amount'],
      [item, quantity, f'KSh {float(price):,.2f}', f'KSh {total:,.2f}'],
  ]

  table = Table(data, colWidths=[200, 50, 100, 100])
  table.setStyle(
      TableStyle([
          ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
          ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
          ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
          ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
          ('GRID', (0, 0), (-1, -1), 1, colors.black),
      ])
  )

  story.append(table)
  story.append(Spacer(1, 20))
  story.append(
      Paragraph('<b>Thank you for your business!</b>', styles['Normal'])
  )

  doc.build(story)
  buffer.seek(0)

  return send_file(
      buffer,
      as_attachment=True,
      download_name=f'Receipt_{receipt_no}.pdf',
      mimetype='application/pdf',
  )


if __name__ == '__main__':
  app.run(debug=True, host='127.0.0.1', port=5000)
