from flask import Blueprint, render_template, redirect, url_for, request
from app import app, db
from app.models import Sale, Product, Transaction
from datetime import datetime

#main = Blueprint('main', __name__)

@app.route('/sales-report', methods=['GET'])
def sales_report():
    # Optional filters for start and end dates
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Base query
    query = Sale.query

    # Apply date filters if provided
    if start_date:
        query = query.filter(Sale.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(Sale.date <= datetime.strptime(end_date, '%Y-%m-%d').date())

    # Fetch filtered sales
    sales = query.order_by(Sale.date.desc()).all()

    # Preload transaction data (if needed)
    for sale in sales:
        sale.transaction = Transaction.query.get(sale.transaction_id)

    products = Product.query.all()
    total_stock_value = sum([product.stock_value() for product in products])
    # Pass the sales data and date filters to the template
    return render_template('admin/sales_report.html', sales=sales, start_date=start_date, end_date=end_date, total_stock_value=total_stock_value, transaction=sale.transaction)
