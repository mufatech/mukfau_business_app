from flask import  render_template, redirect, url_for, request
from app import app, db
from app.models.product import Supply, Product, ProductSupply, ProductSupplyForm
from datetime import datetime
from math import ceil
from sqlalchemy import func, extract


# Define how many items per page
ITEMS_PER_PAGE = 20
@app.route('/product_supplies', methods=['GET', 'POST'])
def product_supplies():
    search_query = request.args.get('search_query', '')
    date_filter = request.args.get('date_filter', '')
    month_filter = request.args.get('month_filter', '')
    page = request.args.get('page', 1, type=int)

    query = ProductSupply.query.join(Product)

    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))
    elif date_filter:
        query = query.filter(ProductSupply.supply_date == date_filter)
    elif month_filter:
         # Use extract instead of MySQL-specific func.date_format
        year, month = map(int, month_filter.split('-'))
        query = query.filter(
            extract('year', ProductSupply.supply_date) == year,
            extract('month', ProductSupply.supply_date) == month
        )
    # Now we can safely apply order and pagination
    query = query.order_by(ProductSupply.supply_date.desc())
    supplies_paginated = query.paginate(page=page, per_page=ITEMS_PER_PAGE, error_out=False)

    # Calculate total profit from the paginated items
    total_profit = db.session.query(func.sum(ProductSupply.profit)).filter(
        ProductSupply.id.in_([s.id for s in supplies_paginated.items])
    ).scalar()

    return render_template(
        'admin/product_supplies.html',
        supplies=supplies_paginated.items,
        search_query=search_query,
        date_filter=date_filter,
        month_filter=month_filter,
        pagination=supplies_paginated,
        total_profit=total_profit or 0
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