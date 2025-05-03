from flask import render_template
from flask_login import login_required, current_user
from app import app, db
from app.models.product import Product, Supply, Sale

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # Querying the database for metrics
    total_products = Product.query.count()
    total_sales = Sale.query.count()
    total_supplies = Supply.query.count()

    # Calculate total revenue and supply costs (if applicable)
    
    total_revenue = db.session.query(db.func.sum(Sale.sale_value)).scalar() or 0
    # Corrected: compute in Python
    total_supply_cost = sum(
        (s.quantity or 0) * (s.cost_per_unit or 0)
        for s in Supply.query.all()
    )
    #total_supply_cost = db.session.query(db.func.sum(Supply.supply_cost)).scalar() or 0

    # Pass the data to the template
    return render_template(
        'admin/dashboard.html',
        admin_email=current_user.email,
        total_products=total_products,
        total_sales=total_sales,
        total_supplies=total_supplies,
        total_revenue=total_revenue,
        total_supply_cost=total_supply_cost
    )


# from flask import render_template
# from flask_login import login_required, current_user
# from app import app
# from app.models.product import Product, Supply, Sale

# # Admin dashboard route
# @app.route('/admin/dashboard')
# @login_required
# def admin_dashboard():
#     # Pass the current user's email to the template
#     return render_template('admin/dashboard.html', admin_email=current_user.email)

# # Add product route
# @app.route('/add-product')
# @login_required
# def add_product():
#     return render_template('add_product.html')

# # Record sale route
# @app.route('/record-sale')
# @login_required
# def record_sale():
#     return render_template('record_sale.html')

# # Stock balance route
# @app.route('/stock-balance')
# @login_required
# def stock_balance():
#     # Logic to calculate and display stock balance can be added here
#     return render_template('stock_balance.html')

# # Supply report route
# @app.route('/supply-report')
# @login_required
# def supply_report():
#     # Logic for supply report can be added here
#     return render_template('supply_report.html')

# # Sales report route
# @app.route('/sales-report')
# @login_required
# def sales_report():
#     # Logic for sales report can be added here
#     return render_template('sales_report.html')
