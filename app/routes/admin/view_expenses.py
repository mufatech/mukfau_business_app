from flask import Flask, render_template, request, redirect, flash, url_for
from flask_login import login_required
from app import app, db
from app.models.product import Product, Expenses
from datetime import datetime

@app.route('/view_expenses')
@login_required
def view_expenses():
    page = request.args.get('page', 1, type=int)
    
    # Get filter dates if they exist
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Expenses.query.order_by(Expenses.date.desc())
    
    if start_date and end_date:
        query = query.filter(Expenses.date >= start_date, Expenses.date <= end_date)
    
    expenses_paginated = query.paginate(page=page, per_page=10)

    # Calculate the total expenses
    total_expenses_value = sum(expense.amount for expense in expenses_paginated.items)

    app.logger.info(f"Expenses retrieved: {[expense.id for expense in expenses_paginated.items]}")


    return render_template(
        'admin/view_expenses.html', 
        expenses=expenses_paginated.items,  # Pass the list of expenses
        pagination=expenses_paginated,     # Pass pagination object for navigation
        total_expenses_value=total_expenses_value,
        start_date=start_date,
        end_date=end_date
    )