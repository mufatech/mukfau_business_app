from flask import  render_template, flash, redirect, url_for, request
from app import app, db
from app.models.product import Supply, Product, ProductSupply, ProductSupplyForm
from datetime import datetime
from math import ceil
from sqlalchemy import func, extract
import calendar
from sqlalchemy import extract


# Define how many items per page
ITEMS_PER_PAGE = 20
@app.route('/product_supplies', methods=['GET', 'POST'])
def product_supplies():
    search_query = request.args.get('search_query', '')
    date_filter = request.args.get('date_filter', '')
    selected_month = request.args.get('month_name', '')  # Avoid name conflict
    page = request.args.get('page', 1, type=int)

    query = ProductSupply.query.join(Product)
    total_profit_query = db.session.query(func.sum(ProductSupply.profit))

    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))

    if date_filter:
        query = query.filter(ProductSupply.supply_date == date_filter)
        total_profit_query = total_profit_query.filter(ProductSupply.supply_date == date_filter)

    # Filter by month name
    if selected_month:
        try:
            month_number = list(calendar.month_name).index(selected_month)
            query = query.filter(extract('month', ProductSupply.supply_date) == month_number)
            total_profit_query = total_profit_query.filter(extract('month', ProductSupply.supply_date) == month_number)
        except ValueError:
            flash("Invalid month name", "danger")

    query = query.order_by(ProductSupply.supply_date.desc())
    supplies_paginated = query.paginate(page=page, per_page=ITEMS_PER_PAGE, error_out=False)

    total_profit = total_profit_query.scalar() or 0

    return render_template(
        'admin/product_supplies.html',
        supplies=supplies_paginated.items,
        search_query=search_query,
        date_filter=date_filter,
        month_name=selected_month,
        pagination=supplies_paginated,
        total_profit=total_profit
    )

@app.route('/edit_product_supply/<int:supply_id>', methods=['GET', 'POST'])
def edit_product_supply(supply_id):
    supply = ProductSupply.query.get_or_404(supply_id)
    form = ProductSupplyForm(obj=supply)

    # Repopulate dropdown
    form.product_id.choices = [(product.id, product.name) for product in Product.query.all()]

    if form.validate_on_submit():
        supply.product_id = form.product_id.data
        supply.cost_price = form.cost_price.data
        supply.selling_price = form.selling_price.data
        supply.quantity_in_bags = form.quantity_in_bags.data
        supply.supply_date = form.supply_date.data

        db.session.commit()
        return redirect(url_for('product_supplies'))

    return render_template('admin/edit_product_supply.html', form=form, supply=supply)


@app.route('/delete_product_supply/<int:supply_id>', methods=['GET', 'POST'])
def delete_product_supply(supply_id):
    supply = ProductSupply.query.get_or_404(supply_id)
    db.session.delete(supply)
    db.session.commit()
    return redirect(url_for('product_supplies'))