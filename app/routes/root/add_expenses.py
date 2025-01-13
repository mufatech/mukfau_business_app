from flask import Flask, render_template, request, redirect, flash, url_for
from app import app, db 
from app.models.product import Product, Expenses
from datetime import datetime

@app.route('/add-expenses', methods=['GET', 'POST'])
def add_expenses():
    if request.method == 'POST':
        try:
            date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
            amount = float(request.form.get('amount'))
            purpose = request.form.get('purpose')
            product_id = int(request.form.get('product_id'))
            
            # Retrieve the product
            product = Product.query.get(product_id)
            if not product or product.stock < amount:
                flash("Insufficient stock for the selected product.", "danger")
                return redirect(url_for('add_expenses'))
            
            # Deduct from product stock
            product.stock -= amount
            
            # Add expense
            expenses = Expenses(date=date, amount=amount, purpose=purpose, product_id=product_id)
            db.session.add(expenses)
            db.session.commit()

            flash("Expense recorded successfully!", "success")
            return redirect(url_for('add_expenses'))
    
        except ValueError:
            flash("Invalid input. Please check the data and try again.", "danger")
        except Exception as e:
                app.logger.error(f"Error adding expense: {str(e)}")
                flash("An unexpected error occurred. Please try again.", "danger")
        

    products = Product.query.all()
    today = datetime.utcnow().strftime('%Y-%m-%d')
    return render_template('root/expenses.html', products=products, today=today)

# @app.route('/expenses')
# def expenses():

#     page = request.args.get('page', 1, type=int)
#     expenses_paginated = Expenses.query.order_by(Expenses.date.desc()).paginate(page=page, per_page=10)
#   # Paginate the results

#     #expenses = Expenses.query.order_by(Expenses.date.desc()).all()
#     products = Product.query.all()
#     total_expenses_value = sum(product.total_expenses_value() for product in products)
#     return render_template('admin/view_expenses.html', expenses=expenses_paginated.items, pagination=expenses_paginated, total_expenses_value=total_expenses_value)