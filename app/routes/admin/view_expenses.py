from flask import Flask, render_template, request, redirect, flash, url_for
from flask_login import login_required
from app import app, db
from app.models.product import Product, Expenses
from datetime import datetime

@app.route('/view_expenses', methods=['GET'])
@login_required

def view_expenses():
    page = request.args.get('page', 1, type=int)
    expenses_paginated = Expenses.query.order_by(Expenses.date.desc()).paginate(page=page, per_page=10)
    

    
    # Calculate the total expenses value
    total_expenses_value = sum(expense.amount for expense in Expenses.query.all())

    #total_expenses_value = db.session.query(db.func.sum(Expenses.amount)).scalar() or 0
    
    return render_template('admin/view_expenses.html', expenses=expenses_paginated.items, pagination=expenses_paginated, total_expenses_value=total_expenses_value)
