from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models.product import Transaction

@app.route('/transactions')
def view_transactions():

    # Get the current page number from the query string, default to page 1
    page = request.args.get('page', 1, type=int)
    
    # Query the transactions with pagination, 15 items per page
    transactions = Transaction.query.paginate(page=page, per_page=20)
    #transactions = Transaction.query.all()  # Fetch all transactions
    return render_template('root/view_transactions.html', transactions=transactions)
