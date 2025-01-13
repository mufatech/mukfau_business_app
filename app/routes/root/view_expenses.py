# from flask import Flask, render_template, request, redirect, flash, url_for
# from app import app, db
# from app.models.product import Product, Expenses
# from datetime import datetime

# @app.route('/view-expenses')
# def view_expenses():
#     expenses = Expenses.query.order_by(Expenses.date.desc()).all()
#     return render_template('root/view_expenses.html', expenses=expenses)
