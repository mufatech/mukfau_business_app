from flask import Flask, render_template, request, redirect, flash, url_for
from flask_login import login_required
from app import app, db
from app.models.product import Product, Expenses
from datetime import datetime

@app.route('/view_expenses', methods=['GET'])
@login_required
def view_expenses():
    try:
        # Fetch date range from query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Validate and parse dates
        try:
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
            return redirect(url_for('view_expenses'))

        # Build query with optional date filtering
        query = Expenses.query
        if start_date and end_date:
            query = query.filter(Expenses.date.between(start_date, end_date))

        # Fetch paginated results
        page = request.args.get('page', 1, type=int)
        pagination = query.paginate(page=page, per_page=10, error_out=False)

        # Calculate total expenses value
        total_expenses_value = sum(float(exp.amount for exp in pagination.items))

        return render_template(
            'admin/view_expenses.html',
            expenses=pagination.items,
            pagination=pagination,
            total_expenses_value=total_expenses_value,
            start_date=start_date.strftime('%Y-%m-%d') if start_date else '',
            end_date=end_date.strftime('%Y-%m-%d') if end_date else ''
        )

    except Exception as e:
        app.logger.error(f"Error fetching expenses: {str(e)}")
        flash("An error occurred while fetching expenses. Please try again.", "danger")
        return redirect(url_for('view_expenses'))

def expenses_value(self):
        return db.session.query(db.func.sum(Expenses.amount)).filter(Expenses.product_id == self.id).scalar() or 0.0

# from flask import Flask, render_template, request, redirect, flash, url_for
# from flask_login import login_required
# from app import app, db 
# from app.models.product import Product, Expenses
# from datetime import datetime


# @app.route('/admin/view_expenses', methods=['GET'])
# @login_required
# def view_expenses():
#     # Fetch expenses with optional filtering by date range
#     start_date = request.args.get('start_date')
#     end_date = request.args.get('end_date')
#     query = Expenses.query

#     if start_date and end_date:
#         query = query.filter(Expenses.date.between(start_date, end_date))

#     expenses = query.all()
#     total_expenses_value = sum(exp.amount for exp in expenses)

#     # Pagination setup
#     page = request.args.get('page', 1, type=int)
#     pagination = query.paginate(page=page, per_page=10)

#     return render_template(
#         'admin/view_expenses.html',

#         expenses=pagination.items,
#         pagination=pagination,
#         total_expenses_value=total_expenses_value,
#         start_date=start_date,
#         end_date=end_date,
#     )
