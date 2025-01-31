from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import app, db
from app.models.product import Product, Supply, Sale
from datetime import datetime

@app.route('/')
def index():
    return redirect(url_for('stock_balance'))

@app.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form.get('description', '')

        # Check if the product already exists
        existing_product = Product.query.filter_by(name=name).first()
        if existing_product:
            flash('Product already exists!', 'error')
            return redirect(url_for('add_product'))

        # Add the new product
        product = Product(name=name, price=price, description=description)
        db.session.add(product)
        db.session.commit()

         # Now create the corresponding supply entry
        supply_quantity = float(request.form.get('quantity', '0.0'))  # Assume this is the initial quantity

        supply = Supply(
            product_id=product.id,  # Link supply to the created product
            quantity=supply_quantity
        )


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

        # Calculate supply cost
        supply_cost = quantity * cost_per_unit
        
        # Get the product and update stock
        product = Product.query.get_or_404(product_id)
        product.stock += quantity  # Update stock

        # Create the supply record
        supply = Supply(product_id=product_id, quantity=quantity, cost_per_unit=product.price, date=date)
        
        # Add and commit the supply record
        db.session.add(supply)
        db.session.commit()
        
        flash('Supply added successfully!', 'success')
        return redirect(url_for('supply_report'))
        
        # Fetch all products for the form
    products = Product.query.all()
    return render_template('admin/add_supply.html', products=products, supply_cost=supply_cost)

def supply_cost(self):
        return self.quantity * self.cost_per_unit


@app.route('/stock-balance')
def stock_balance():
    products = Product.query.all()
    #sale = Sale.query.all()

    # Get the page number from the query parameters (default to 1 if not provided)
    page = request.args.get('page', 1, type=int)

    # Fetch the products with pagination
    paginated_products = Product.query.paginate(page=page, per_page=15, error_out=False)

    # Calculate stock value for all products
    all_products = Product.query.all()  # Fetch all products (not paginated)
    total_stock_value = sum([product.stock_value() for product in all_products])
    return render_template('admin/stock_balance.html', products=paginated_products, total_stock_value=total_stock_value, current_page=page  # Pass current page info for conditional rendering
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
