from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import app, db
from app.models.product import Product, Supply, Sale, Customer, Transaction
from datetime import datetime
import uuid


@app.route('/record-sale', methods=['GET', 'POST'])
def record_sale():
    if request.method == 'POST':
        date = request.form.get('date')
        customer_name = request.form.get('customer_name')
        product_ids = request.form.getlist('product_id[]')
        quantities_sold = request.form.getlist('quantity_sold[]')
        prices = request.form.getlist('price[]')
        amount_paid_str = request.form.get('amount_paid')
        payment_method = request.form.get('payment_method')

        if not customer_name or not product_ids or not quantities_sold or not prices or not amount_paid_str:
            flash("All fields are required!", "error")
            return redirect(url_for('record_sale'))

        try:
            amount_paid = float(amount_paid_str)
        except ValueError:
            flash("Invalid amount paid.", "error")
            return redirect(url_for('record_sale'))

        # Calculate total amount and balance
        total_amount = sum(float(q) * float(p) for q, p in zip(quantities_sold, prices))
        balance = total_amount - amount_paid
        status = "Pending" if balance > 0 else "Completed"

        # Ensure the customer exists
        customer = Customer.query.filter_by(name=customer_name).first()
        if not customer:
            customer = Customer(name=customer_name)
            db.session.add(customer)
            db.session.commit()

        # Generate unique transaction reference
        transaction_ref = f"{customer.id}-{date}-{total_amount}"

        # Check for duplicate transactions
        existing_transaction = Transaction.query.filter_by(transaction_ref=transaction_ref).first()
        if existing_transaction:
            flash('Duplicate transaction detected. Sale not recorded.', 'error')
            return redirect(url_for('record_sale'))

        # **🔹 Stock Validation: Ensure all products have enough stock before modifying stock**
        for product_id, quantity_sold in zip(product_ids, quantities_sold):
            product = Product.query.get(int(product_id))
            if not product or product.stock < float(quantity_sold):
                flash(f"Insufficient stock for {product.name}!", "error")
                return redirect(url_for('record_sale'))

        # Save transaction
        transaction = Transaction(
            date=date,
            customer_id=customer.id, 
            total_amount=total_amount, 
            amount_paid=amount_paid, 
            balance=balance, 
            status=status,
            transaction_ref=transaction_ref
        )
        db.session.add(transaction)
        db.session.commit()

        # **🔹 Deduct stock after validation**
        for product_id, quantity_sold, price in zip(product_ids, quantities_sold, prices):
            product = Product.query.get(int(product_id))
            quantity_sold = float(quantity_sold)
            price = float(price)

            sale = Sale(
                customer_id=customer.id,
                transaction_id=transaction.id, 
                product_id=product.id, 
                quantity_sold=quantity_sold,
                price=price, 
                total_amount=quantity_sold * price,
                payment_method=payment_method
            )
            product.stock -= quantity_sold
            db.session.add(sale)
            db.session.add(product)

        db.session.commit()

        flash('Sale recorded successfully!', 'success')
        return redirect(url_for('record_sale'))

    products = Product.query.all()
    return render_template('root/record_sale.html', products=products)


@app.route('/sales-report/<int:customer_id>', methods=['GET'])
def customer_sales_report(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    sales = Sale.query.filter_by(customer_id=customer.id).all()
    return render_template('root/customer_sales_report.html', customer=customer, sales=sales)


@app.route('/transaction/<int:transaction_id>', methods=['GET'])
def transaction_details(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    customer = Customer.query.get_or_404(transaction.customer_id)
    sales = Sale.query.filter_by(transaction_id=transaction_id).all()

    return render_template('root/transaction_details.html', transaction=transaction, customer=customer, sales=sales)


def sale_value(self):
        if self.quantity_sold is None or self.price is None:
            return 0
        return self.quantity_sold * self.price
