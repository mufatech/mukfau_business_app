from flask import Flask, render_template, request, redirect, flash, url_for
from app import app, db
from app.models.product import Product, Expenses
from datetime import datetime

@app.route('/add-expenses', methods=['GET', 'POST'])
def add_expenses():
    expenses = []  # Ensure expenses is always defined

    if request.method == 'POST':
        try:
            # Get form data
            date_str = request.form.get('date')
            date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()
            product_id = request.form.get('product_id')
            amount = float(request.form.get('amount'))
            purpose = request.form.get('purpose')

            # Validate inputs
            if not purpose or not product_id:
                flash("All fields are required.", "danger")
                return redirect(url_for('add_expenses'))

            if amount <= 0:
                flash("Amount must be greater than zero.", "danger")
                return redirect(url_for('add_expenses'))

            # Retrieve the product
            product = Product.query.get(product_id)
            if not product:
                flash("Selected product does not exist.", "danger")
                return redirect(url_for('add_expenses'))

            if product.stock < amount:
                flash("Insufficient stock for the selected product.", "danger")
                return redirect(url_for('add_expenses'))

            # Deduct from product stock
            product.stock -= amount

            # Add expense
            new_expense = Expenses(date=date, amount=amount, purpose=purpose, product_id=product_id)
            db.session.add(new_expense)
            db.session.commit()

            flash("Expense recorded successfully!", "success")
            return redirect(url_for('add_expenses'))

        except ValueError:
            flash("Invalid input. Please check your data.", "danger")
        except Exception as e:
            app.logger.error(f"Error adding expense: {str(e)}")
            flash("An unexpected error occurred. Please try again.", "danger")

    # GET request: Fetch existing expenses
    expenses = Expenses.query.order_by(Expenses.date.desc()).all()
    products = Product.query.all()
    today = datetime.utcnow().strftime('%Y-%m-%d')

    return render_template('root/expenses.html', products=products, today=today, expenses=expenses)
