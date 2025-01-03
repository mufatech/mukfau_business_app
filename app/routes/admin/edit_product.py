from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import app, db
from app.models.product import Product, Supply
import os

# UPLOAD_FOLDER = 'app/static/admin/uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

# def save_file(file):
#     if file and allowed_file(file.filename):
#         filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
#         file.save(filename)
#         return filename.replace('app/static/', '')  # Store path relative to static folder
#     return None

@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    #print(f"Product Quantity: {product.quantity}")  # Debug line
    # Create the supply record
    supply = Supply.query.filter_by(product_id=product_id).first()
        
    if not supply:
        # Handle case when no supply record is found
        flash('No supply record found for this product', 'warning')

    if request.method == 'POST':
        product.name = request.form.get('name').strip()
        product.price = float(request.form.get('price'))
        product.quantity = float(request.form.get('quantity'))
        product.description = request.form.get('description')
        
         # If the supply exists, update it
        if supply:
            supply.product_id = product_id  # Ensure product_id is set
            # Optionally, update supply fields like quantity if needed
            supply.quantity = float(request.form.get('quantity', 0))

        
        db.session.commit()
        flash('Product updated successfully', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/edit_product.html', product=product, supply=supply)
