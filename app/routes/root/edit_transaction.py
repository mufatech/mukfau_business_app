from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models.product import Product, Supply, Transaction
import os

# @app.route('/edit_transaction/<int:transaction_id>', methods=['GET', 'POST'])
# def edit_transaction(transaction_id):
#     transaction = Transaction.query.get_or_404(transaction_id)

#     # Check if the transaction is pending
#     if transaction.status != "Pending":
#         flash("Only pending transactions can be edited.", "danger")
#         return redirect(url_for('view_transactions'))
    
#     if request.method == 'POST':
#         transaction.total_amount = float(request.form.get('total_amount'))
#         transaction.amount_paid = float(request.form.get('amount_paid'))
#         transaction.balance = transaction.total_amount - transaction.amount_paid
#         transaction.status = "Completed" if transaction.balance == 0 else "Pending"

#         db.session.commit()
#         flash("Transaction updated successfully!", "success")
#         return redirect(url_for('view_transactions'))

#     return render_template('root/edit_transaction.html', transaction=transaction)

@app.route('/edit_transaction/<int:transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)

    # Check if the transaction is pending
    if transaction.status != "Pending":
        flash("Only pending transactions can be edited.", "danger")
        return redirect(url_for('view_transactions'))
    
    if request.method == 'POST':
        # Get updated values from the form
        transaction.customer_name = request.form.get('customer_name')
        transaction.product_id = request.form.get('product_id')
        transaction.total_amount = float(request.form.get('total_amount'))
        transaction.amount_paid = float(request.form.get('amount_paid'))
        transaction.balance = transaction.total_amount - transaction.amount_paid
        transaction.status = "Completed" if transaction.balance == 0 else "Pending"

        # Ensure product exists
        product = Product.query.get(transaction.product_id)
        if not product:
            flash("Selected product does not exist.", "danger")
            return redirect(url_for('edit_transaction', transaction_id=transaction.id))

        db.session.commit()
        flash("Transaction updated successfully!", "success")
        return redirect(url_for('view_transactions'))

    # Fetch all products for dropdown selection
    products = Product.query.all()

    return render_template('root/edit_transaction.html', transaction=transaction, products=products)

