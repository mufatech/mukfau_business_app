from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import app, db
from app.models.product import Product, Supply, Sale

@app.route('/admin/edit_products', methods=['GET'])
@login_required
def edit_products():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Items per page
    products = Product.query.paginate(page=page, per_page=per_page)
    # supplies = Supply.query.all()
    # products = Product.query.all()


    # Build products_with_supplies
    products_with_supplies = []
    for product in products.items:
        total_quantity = sum(supply.quantity for supply in product.supplies)  # Assuming Product.supplies relationship
        products_with_supplies.append({
            "product": product,
            "total_quantity": total_quantity,
        })
        
    # products_with_supplies = [
    #     {
    #         'product': product,
    #         'total_quantity': sum(supply.quantity for supply in product.supplies),
    #     }
    #     for product in products.items
    # ]
    return render_template('admin/edit_products.html', products_with_supplies=products_with_supplies, products=products)


@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    print(f"Attempting to delete product ID: {product_id}")
    if not product:
        return {"error": "Product not found."}, 404

    # Check for associated sales
    sales = Sale.query.filter_by(product_id=product_id).all()
    if sales:
        return {"error": "Cannot delete product. It has associated sales."}, 400

    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully', 'success')
    return redirect(url_for('edit_products'))