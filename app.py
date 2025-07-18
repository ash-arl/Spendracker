from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, time
import psycopg2
import qrcode
import base64
from io import BytesIO
from hashids import Hashids
from flask import jsonify


app = Flask(__name__)

conn = psycopg2.connect(database = "transactionDB", user = "postgres", password="asharl", host = "localhost", port = "5432")
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS transactions (
            id serial primary key, 
            randid varchar(24), 
            amount NUMERIC(10,2), 
            transaction_type varchar(1), 
            category varchar(50), 
            date_created date, 
            time_created time);''')
conn.commit()
cur.close()
conn.close()

def crypticIdCreator(amount: int, date_created: int, time_created: int, transaction_type: str) -> str:
    type_digit = 1 if transaction_type == 'i' else 0
    to_encode = int(f"{amount}{date_created}{time_created}{type_digit}")
    
    hashids = Hashids(salt="q9vpD23yqp9vaKL43p9ayt", min_length=24)
    encoded = hashids.encode(to_encode)
    
    return encoded

# def decodeCrypticId(crypt_id: str):
#     hashids = Hashids(salt="q9vpD23yqp9vaKL43p9ayt", min_length=24)
#     decoded = hashids.decode(crypt_id)
#     if len(decoded) != 4:
#         raise ValueError("Invalid encoded ID")
    
#     amount_cents, date_digits, time_digits, type_digit = decoded
#     return {
#         "amount": amount_cents / 100,
#         "date": str(date_digits),
#         "time": str(time_digits),
#         "type": "i" if type_digit == 1 else "e"
#     }

#Home route
@app.route('/')
def index():
  conn = psycopg2.connect(database = "transactionDB", user = "postgres", password = "asharl", host = "localhost", port = "5432")
  cur = conn.cursor()
  cur.execute('''SELECT * FROM transactions''')
  transactions = cur.fetchall()

  cur.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE transaction_type ='i'")
  total_income = cur.fetchone()[0]

  cur.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE transaction_type ='e'")
  total_spend = cur.fetchone()[0]

  net_total = total_income - total_spend

  cur.close()
  conn.close()

  spendLabel = [row[5].strftime('%d %b %Y') for row in transactions if row[3] == 'e']
  dataSpend = [row[2] for row in transactions if row[3] == 'e']

  earnLabel = [row[5].strftime('%d %b %Y') for row in transactions if row[3] == 'i']
  dataEarn = [row[2] for row in transactions if row[3] == 'i']

  return render_template('index.html', transactions=transactions,
                        total_income= total_income,
                        total_spend = total_spend,
                        net_total = net_total,
                        spendLabel = spendLabel, 
                        dataSpend = dataSpend,
                        earnLabel = earnLabel,
                        dataEarn = dataEarn)
  
#New transaction creation
@app.route('/create',methods=['POST'])
def create():
  conn = psycopg2.connect(database = "transactionDB", user = "postgres", password = "asharl", host = "localhost",port = "5432")
  cur = conn.cursor()

  amount = float(request.form['amount'])
  transaction_type = request.form['transaction_type']
  category = request.form['category']
  date_created = request.form['date_created']

  date_only = datetime.strptime(date_created, "%Y-%m-%d").date()
  time_only = datetime.now().replace(microsecond=0).time()

  amountdigits = int(amount*100)
  date_digits = int(date_only.strftime('%Y%m%d'))
  time_digits = int(time_only.strftime('%H%M%S'))

  crypt_id = crypticIdCreator(amountdigits,date_digits,time_digits, transaction_type)

  cur.execute('''INSERT INTO transactions (randid, amount, transaction_type, category, date_created, time_created) VALUES (%s, %s, %s, %s, %s, %s)''',(crypt_id, amount, transaction_type, category, date_only, time_only))

  conn.commit()
  cur.close()
  conn.close()

  return redirect(url_for('index'))

@app.route('/qr/<int:txn_id>')
def get_qr(txn_id):
    conn = psycopg2.connect(database="transactionDB", user="postgres", password="asharl", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT * FROM transactions WHERE id = %s", (txn_id,))
    txn = cur.fetchone()
    cur.close()
    conn.close()

    if not txn:
      return "Transaction not found", 404

    # Generate QR data string
    qr_data = (f"Transaction ID: {txn[0]}\n"
               f"Amount: ₹{txn[2]}\n"
               f"Type: {'Income' if txn[3] == 'i' else 'Expenditure'}\n"
               f"Date: {txn[5]}\n"
               f"Time: {txn[6]}\n"
               f"Unique Transaction Id: f{txn[1]}")

    qr = qrcode.make(qr_data)
    buf = BytesIO()
    qr.save(buf, format='PNG')
    base64_img = base64.b64encode(buf.getvalue()).decode('utf-8')

    # Return base64 image string as data URI
    return f"data:image/png;base64,{base64_img}"

from flask import jsonify

@app.route('/edit/<int:txn_id>', methods=['POST'])
def edit_transaction(txn_id):
    data = request.get_json()
    conn = psycopg2.connect(database="transactionDB", user="postgres", password="asharl", host="localhost", port="5432")
    cur = conn.cursor()

    cur.execute("""
        UPDATE transactions 
        SET amount = %s, transaction_type = %s, category = %s, date_created = %s
        WHERE id = %s
    """, (
        data["amount"], data["transaction_type"], data["category"], data["date_created"], txn_id
    ))

    conn.commit()
    cur.close()
    conn.close()

    return "", 204


@app.route('/delete/<int:txn_id>', methods=['DELETE'])
def delete_transaction(txn_id):
    conn = psycopg2.connect(database="transactionDB", user="postgres", password="asharl", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("DELETE FROM transactions WHERE id = %s", (txn_id,))
    conn.commit()
    cur.close()
    conn.close()
    return '', 204



if __name__ == "__main__":
  app.run(debug=True)


