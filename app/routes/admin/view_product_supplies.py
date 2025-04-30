from flask import  render_template, redirect, url_for, request
from app import app, db
from app.models.product import Supply, Product, ProductSupply
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
