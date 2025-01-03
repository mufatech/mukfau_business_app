from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models.product import Product, Supply, Transaction
import os

@app.route('/edit_transaction/<int:transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)

    if request.method == 'POST':
        amount_paid = float(request.form.get('amount_paid'))
        transaction.amount_paid = amount_paid
        transaction.balance = transaction.total_amount - amount_paid
        transaction.status = "Completed" if transaction.balance == 0 else "Pending"

        db.session.commit()
        flash("Transaction updated successfully!", "success")
        return redirect(url_for('sales_page'))

    return render_template('edit_transaction.html', transaction=transaction)
