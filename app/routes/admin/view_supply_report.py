from flask import  render_template, redirect, url_for, request
from app import app, db
from app.models.product import Supply, Product, ProductSupply, ProductSupplyForm
from datetime import datetime
from math import ceil
from sqlalchemy import func, extract


# Define how many items per page
ITEMS_PER_PAGE = 20




@app.route('/supply-report', methods=['GET'])
def supply_report():
    # Optional filters for start and end dates
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Base query
    query = Supply.query
    
    # Apply date filters if provided
    if start_date:
        query = query.filter(Supply.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(Supply.date <= datetime.strptime(end_date, '%Y-%m-%d').date())

    # Fetch filtered supplies
    supplies = query.order_by(Supply.date.desc()).all()
    for supply in supplies:
    # Ensure values are not None (optional if DB constraints are correct)
        supply.quantity = supply.quantity or 0
        supply.cost_per_unit = supply.cost_per_unit or 0
    products = Product.query.all()
    total_stock_value = sum([product.stock_value() for product in products])
    
    return render_template('admin/supply_report.html', products=products, supplies=supplies, start_date=start_date, end_date=end_date, total_stock_value=total_stock_value)







