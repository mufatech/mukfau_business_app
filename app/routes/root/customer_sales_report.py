from flask import Flask, render_template, request, redirect, flash, url_for
from app import app, db 
from app.models.product import Customer, Sale
from datetime import datetime

@app.route('/sales-report/<int:customer_id>', methods=['GET'])
def customer_sales_report(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    sales = Sale.query.filter_by(customer_id=customer.id).all()
    return render_template('root/customer_sales_report.html', customer=customer, sales=sales)



