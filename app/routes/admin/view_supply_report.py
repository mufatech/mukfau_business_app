from flask import  render_template, redirect, url_for, request
from app import app, db
from app.models import Supply, Product
from datetime import datetime



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
    
    products = Product.query.all()
    total_stock_value = sum([product.stock_value() for product in products])
    
    return render_template('admin/supply_report.html', products=products, supplies=supplies, start_date=start_date, end_date=end_date, total_stock_value=total_stock_value)
