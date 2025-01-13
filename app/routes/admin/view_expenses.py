from flask import Flask, render_template, request, redirect, flash, url_for
from flask_login import login_required
from app import app, db
from app.models.product import Product, Expenses
from datetime import datetime

@app.route('/view_expenses', methods=['GET'])
@login_required
def view_expenses():        
    # Fetch date range from query parameters
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    # Check if start_date and end_date are received correctly
    print(f"Start Date: {start_date_str}, End Date: {end_date_str}")

    # Convert string dates to datetime objects if available, with error handling
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
    except ValueError:
        flash("Invalid date format. Please use YYYY-MM-DD.", "error")
        return redirect(url_for('view_expenses'))

    # Print the converted dates to see if they're correct
    print(f"Converted Start Date: {start_date}, Converted End Date: {end_date}")

    # Build query with optional date filtering
    query = Expenses.query
    if start_date and end_date:
        query = query.filter(Expenses.date.between(start_date, end_date))
    
    query = query.filter(Expenses.date.between(datetime(2025, 1, 3), datetime(2025, 1, 9)))
    print(str(query))  # Check the generated query

    # Fetch paginated results
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Expenses.date.desc()).paginate(page=page, per_page=20, error_out=False)

    # Calculate total expenses value
    total_expenses_value = db.session.query(db.func.sum(Expenses.amount)).filter(Expenses.date.between(start_date, end_date)).scalar() or 0.0

    return render_template(
        'admin/view_expenses.html',
        expenses=pagination.items,
        pagination=pagination,
        total_expenses_value=total_expenses_value,
        start_date=start_date.strftime('%Y-%m-%d') if start_date else '',
        end_date=end_date.strftime('%Y-%m-%d') if end_date else ''
    )

@app.route('/expenses')
def expenses():

    page = request.args.get('page', 1, type=int)
    expenses_paginated = Expenses.query.order_by(Expenses.date.desc()).paginate(page=page, per_page=10)
  # Paginate the results

    #expenses = Expenses.query.order_by(Expenses.date.desc()).all()
    products = Product.query.all()
    total_expenses_value = sum(product.total_expenses_value() for product in products)
    return render_template('admin/view_expenses.html', expenses=expenses_paginated.items, pagination=expenses_paginated, total_expenses_value=total_expenses_value)

# @app.route('/expenses')
# def expenses():

#     page = request.args.get('page', 1, type=int)
#     expenses_paginated = Expenses.query.order_by(Expenses.date.desc()).paginate(page=page, per_page=10)
#   # Paginate the results

#     #expenses = Expenses.query.order_by(Expenses.date.desc()).all()
#     products = Product.query.all()
#     total_expenses_value = sum(product.total_expenses_value() for product in products)
#     return render_template('admin/view_expenses.html', expenses=expenses_paginated.items, pagination=expenses_paginated, total_expenses_value=total_expenses_value)
