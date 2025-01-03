from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import app, db
from app.models.product import Product, Supply
from datetime import datetime

@app.route('/edit-supply/<int:supply_id>', methods=['GET', 'POST'])
@login_required
def edit_supply(supply_id):
    supply = Supply.query.get_or_404(supply_id)
    product = Product.query.get_or_404(supply.product_id)

    if request.method == 'POST':
        try:
            # Parse and validate form data
            date = request.form.get('date')
            quantity = request.form.get('quantity')
            cost_per_unit = request.form.get('cost_per_unit')

            date = datetime.strptime(date, '%Y-%m-%d').date() if date else supply.date
            quantity = float(quantity)
            cost_per_unit = float(cost_per_unit)

            # Revert old stock update and apply new update
            product.stock -= supply.quantity
            if product.stock + quantity < 0:
                flash('Invalid operation: stock cannot go negative.', 'error')
                return redirect(url_for('edit_supply', supply_id=supply_id))
            product.stock += quantity

            # Update supply record
            supply.date = date
            supply.quantity = quantity
            supply.cost_per_unit = cost_per_unit

            db.session.commit()
            flash('Supply updated successfully!', 'success')
            return redirect(url_for('supply_report'))

        except (ValueError, TypeError):
            flash('Invalid input. Please check your data.', 'error')

    products = Product.query.all()  # Fetch products for dropdown if needed
    return render_template('admin/edit_supply.html', supply=supply, products=products)

@app.route('/delete-supply/<int:supply_id>', methods=['POST'])
@login_required
def delete_supply(supply_id):
    supply = Supply.query.get_or_404(supply_id)
    product = Product.query.get_or_404(supply.product_id)

    # Update stock before deleting supply
    product.stock -= supply.quantity
    if product.stock < 0:
        flash('Error: Stock cannot be negative.', 'error')
        return redirect(url_for('supply_report'))

    # Delete supply record
    db.session.delete(supply)
    db.session.commit()
    flash('Supply deleted successfully!', 'success')
    return redirect(url_for('supply_report'))




# from flask import render_template, request, redirect, url_for, flash
# from flask_login import login_required
# from app import app, db
# from app.models.product import Product, Supply
# import os
# from datetime import datetime

# @app.route('/edit-supply/<int:supply_id>', methods=['GET', 'POST'])
# def edit_supply(supply_id):
#     supply = Supply.query.get_or_404(supply_id)  # Fetch the supply record or show 404
#     if request.method == 'POST':
#         # Get form data
#         supply.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
#         supply.quantity = float(request.form.get('quantity'))
#         supply.cost_per_unit = float(request.form.get('cost_per_unit'))
#         # Parse date
#         if not date:
#             date = supply.date  # Use existing date if not provided
#         else:
#             date = datetime.strptime(date, '%Y-%m-%d').date()

#         # Validate quantity and cost_per_unit
#         quantity = float(quantity) if quantity and quantity.replace('.', '', 1).isdigit() else 0.0
#         cost_per_unit = float(cost_per_unit) if cost_per_unit and cost_per_unit.replace('.', '', 1).isdigit() else 0.0

#         # Update stock in Product model
#         product = Product.query.get_or_404(supply.product_id)
#         product.stock -= supply.quantity  # Revert old stock update
#         product.stock += quantity  # Apply new stock update

#         # Update supply record
#         supply.date = date
#         supply.quantity = quantity
#         supply.cost_per_unit = cost_per_unit

#         db.session.commit()
#         flash('Supply updated successfully!', 'success')
#         return redirect(url_for('supply_report'))

#     products = Product.query.all()  # For dropdown if necessary
#     return render_template('admin/edit_supply.html', supply=supply, products=products)


# @app.route('/delete-supply/<int:supply_id>', methods=['POST'])
# def delete_supply(supply_id):
#     supply = Supply.query.get_or_404(supply_id)  # Fetch the supply record
#     product = Product.query.get_or_404(supply.product_id)  # Get associated product

#     # Update stock before deleting supply
#     product.stock -= supply.quantity

#     # Delete supply record
#     db.session.delete(supply)
#     db.session.commit()
#     flash('Supply deleted successfully!', 'success')
#     return redirect(url_for('supply_report'))
