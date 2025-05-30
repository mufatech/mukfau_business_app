from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import app, db
from app.models.product import Product, Supply, Sale, Transaction, ProductSupply, ProductSupplyForm
from datetime import datetime
from sqlalchemy import func, and_
from sqlalchemy.orm import aliased



@app.route('/')
def index():
    return redirect(url_for('stock_balance'))

@app.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        # price = float(request.form['price'])
        description = request.form.get('description', '')

        # Check if the product already exists
        existing_product = Product.query.filter_by(name=name).first()
        if existing_product:
            flash('Product already exists!', 'error')
            return redirect(url_for('add_product'))

        # Add the new product
        product = Product(name=name,  description=description)
        db.session.add(product)
        db.session.commit()

         # Set all NULL stock values to 0.0
        Product.query.filter(Product.stock == None).update({Product.stock: 0.0})
        db.session.commit()

         # Now create the corresponding supply entry
        supply_quantity = float(request.form.get('quantity', '0.0'))  # Assume this is the initial quantity
        cost_per_unit = float(request.form.get('cost_per_unit', '0.0'))

        supply = Supply(
            product_id=product.id,  # Link supply to the created product
            quantity=supply_quantity,
            cost_per_unit=cost_per_unit,
            date=datetime.utcnow().date()
        )

        db.session.add(supply)  # ✅ Save to DB
        db.session.commit()


        flash('Product added successfully!', 'success')
        return redirect(url_for('stock_balance'))

    return render_template('admin/add_product.html')

@app.route('/add-supply', methods=['GET', 'POST'])
def add_supply():
    if request.method == 'POST':
        # Get form data
        date = request.form.get('date')
        product_id = int(request.form['product_id'])
        quantity = request.form.get('quantity', '0.0')  # Default to '0.0' if missing
        cost_per_unit = request.form.get('cost_per_unit', '0.0')  # Default value for cost_per_unit
        
        # Parse date from form input
        if not date:
            date = datetime.utcnow().date()  # Default to today if no date provided
        else:
            date = datetime.strptime(date, '%Y-%m-%d').date()

        # Validate quantity and cost_per_unit
        quantity = float(quantity) if quantity and quantity.replace('.', '', 1).isdigit() else 0.0
        cost_per_unit = float(cost_per_unit) if cost_per_unit and cost_per_unit.replace('.', '', 1).isdigit() else 0.0

        #Calculate supply cost
        #supply_cost = quantity * cost_per_unit
        
        # Get the product and update stock
        product = Product.query.get_or_404(product_id)
        product.stock = product.stock or 0.0  # Fallback in case it's None
        product.stock += quantity  # Update stock

        # Create the supply record
        supply = Supply(product_id=product_id, quantity=quantity, cost_per_unit=cost_per_unit, date=date)
        
        # Add and commit the supply record
        db.session.add(supply)
        db.session.commit()
        
        flash('Supply added successfully!', 'success')
        return redirect(url_for('supply_report'))
        
        # Fetch all products for the form
    products = Product.query.all()
    return render_template('admin/add_supply.html', products=products)

def supply_cost(self):
        return self.quantity * self.cost_per_unit


@app.route('/stock-balance')
def stock_balance():
    # Total sales value (sum of all sales)
    total_sales_value = db.session.query(db.func.sum(Transaction.total_amount)).scalar() or 0.0

    # Total balance to be paid (sum of all unpaid balances)
    total_pending_balance = db.session.query(db.func.sum(Transaction.balance)).filter(Transaction.status == "Pending").scalar() or 0.0

    products = Product.query.all()
    #sale = Sale.query.all()

    # Get the page number from the query parameters (default to 1 if not provided)
    page = request.args.get('page', 1, type=int)

    # Fetch the products with pagination
    paginated_products = Product.query.paginate(page=page, per_page=20, error_out=False)

    # Calculate stock value for all products
    all_products = Product.query.all()  # Fetch all products (not paginated)
    total_stock_value = sum(
        (product.latest_cost_per_unit or 0.0) * (product.stock or 0.0)
        for product in products
    )
    # total_stock_value = sum([product.stock_value() for product in all_products])
    return render_template('admin/stock_balance.html', products=paginated_products, total_stock_value=total_stock_value, current_page=page,
        total_sales_value=total_sales_value,
        total_pending_balance=total_pending_balance # Pass current page info for conditional rendering
    )

@app.route('/profit')
def profit():

    # Optional filters for start and end dates
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')


    # Pagination parameters
    page = request.args.get('page', 1, type=int)  # Current page number, default is 1
    per_page = 30  # Number of items per page

    # Base query
    query = Sale.query

    # Apply date filters if provided
    if start_date:
        query = query.filter(Sale.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(Sale.date <= datetime.strptime(end_date, '%Y-%m-%d').date())

    # Fetch filtered sales
    #sales = query.order_by(Sale.date.desc()).all()
    paginated_sales = query.order_by(Sale.date.desc()).paginate(page=page, per_page=per_page)

   

    # Calculate profits for all paginated sales
    #sales = Sale.query.all()
    profits = []
    total_profit = 0
   

    for sale in paginated_sales.items:
        # Get the cost per unit for the product from the Supply model
        supply = Supply.query.filter_by(product_id=sale.product_id).first()
        if supply:
            cost_price = supply.cost_per_unit
            profit = (sale.price - supply.cost_per_unit) * sale.quantity_sold
            total_profit += profit
            profits.append({
                'date': sale.date,
                'product': sale.product,
                'quantity_sold': sale.quantity_sold,
                'selling_price': sale.price,
                'cost_price': supply.cost_per_unit,
                'profit': profit,
            })

            products = Product.query.all()
            
    return render_template('admin/profit.html', products=products, total_profit=total_profit, profits=profits, pagination=paginated_sales)



@app.route('/all-profits')
def all_profits():
    # Optional filters for start and end dates
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Pagination parameters
    page = request.args.get('page', 1, type=int)  # Current page number, default is 1
    per_page = 20  # Number of items per page

    # Base query to fetch all sales
    query = Sale.query

    # Apply date filters if provided
    if start_date:
        query = query.filter(Sale.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(Sale.date <= datetime.strptime(end_date, '%Y-%m-%d').date())

    # Fetch all sales based on the query
    all_sales = query.order_by(Sale.date.desc()).all()
    #paginated_sales = query.order_by(Sale.date.desc()).all()

    # Initialize profit calculations
    #profits = []
    total_profit = 0

    for sale in all_sales:
        # Fetch the corresponding product cost from the Supply table
        supply = Supply.query.filter_by(product_id=sale.product_id).first()
        if supply:
            #cost_price = supply.cost_per_unit
            total_profit += (sale.price - supply.cost_per_unit) * sale.quantity_sold
            #total_profit += profit

    # Fetch paginated sales for display
    paginated_sales = query.order_by(Sale.date.desc()).paginate(page=page, per_page=per_page)     
            # Calculate profits for the current page's sales
    profits = []
    for sale in paginated_sales.items:
        supply = Supply.query.filter_by(product_id=sale.product_id).first()
        if supply:
            profit = (sale.price - supply.cost_per_unit) * sale.quantity_sold
            profits.append({
                'date': sale.date,
                'product': sale.product,
                'quantity_sold': sale.quantity_sold,
                'selling_price': sale.price,
                'cost_price': supply.cost_per_unit,
                'profit': profit,
            })

    products = Product.query.all()

    return render_template(
        'admin/all_profits.html',
        products=products,
        total_profit=total_profit,  # Total profit across all pages
        profits=profits,           # Profits for the current page's sales
        pagination=paginated_sales  # Pagination object

    )


@app.route('/add_product_supply', methods=['GET', 'POST'])
def add_product_supply():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        cost_price = float(request.form.get('cost_price'))
        selling_price = float(request.form.get('selling_price'))
        quantity_in_bags = float(request.form.get('quantity_in_bags'))
        supply_date = request.form.get('supply_date')

        # Compute derived values
        total_cost = cost_price * quantity_in_bags
        total_revenue = selling_price * quantity_in_bags
        profit = total_revenue - total_cost

        new_supply = ProductSupply(
            product_id=product_id,
            cost_price=cost_price,
            selling_price=selling_price,
            quantity_in_bags=quantity_in_bags,
            supply_date=datetime.strptime(supply_date, "%Y-%m-%d"),
            total_cost=total_cost,
            total_revenue=total_revenue,
            profit=profit
        )
        db.session.add(new_supply)
        db.session.commit()

        flash('Product supply added successfully.', 'success')
        return redirect(url_for('product_supplies'))

    products = Product.query.all()
    return render_template('admin/add_product_supply.html', products=products)

