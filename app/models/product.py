from app import db
from datetime import datetime
from sqlalchemy import Enum
from app import db
from flask_wtf import FlaskForm
from wtforms import SelectField, FloatField, IntegerField, DateField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from sqlalchemy import UniqueConstraint

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    stock = db.Column(db.Integer, default=0)

    supplies = db.relationship('Supply', back_populates='product', lazy='dynamic')
    expenses = db.relationship('Expenses', back_populates='product')

    def total_expenses_value(self):
        # This method calculates the total expenses for this product
        return db.session.query(db.func.sum(Expenses.amount)).filter(Expenses.product_id == self.id).scalar() or 0.0
    
    @property
    def latest_cost_per_unit(self):
        latest_supply = db.session.query(Supply).filter(Supply.product_id == self.id).order_by(Supply.date.desc()).first()
        return latest_supply.cost_per_unit if latest_supply else 0.0

    def stock_value(self):
        return self.stock * self.price

    def __str__(self):
        return self.name


class Supply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    quantity = db.Column(db.Float, nullable=False, default=0.0)
    cost_per_unit = db.Column(db.Float, nullable=False, default=0.0)

    product = db.relationship('Product', back_populates='supplies')

    supply_cost = db.Column(db.Float)

    def __str__(self):
        return f"Supply(id={self.id}, product_id={self.product_id}, quantity={self.quantity})"

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='SET NULL'), nullable=True)
    quantity_sold = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')

    sale_value = db.Column(db.Float)

    customer = db.relationship('Customer', backref='sales')
    transaction = db.relationship('Transaction', backref='sales')
    product = db.relationship('Product', backref='sales')

    # Ensure no duplicate transaction-product pair
    __table_args__ = (UniqueConstraint('transaction_id', 'product_id', name='unique_transaction_product'),)

class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    amount = db.Column(db.Float, nullable=False)
    purpose = db.Column(db.String(255), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', back_populates='expenses')
    product = db.relationship('Product', backref='expense_records')
    def __repr__(self):
        return f'<Expense {self.purpose} - {self.amount}>'
    
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship('Customer', backref='transactions')
    total_amount = db.Column(db.Float, nullable=False)
    amount_paid = db.Column(db.Float, nullable=False, default=0.0)
    balance = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending")
    transaction_ref = db.Column(db.String(50), unique=True, index=True, nullable=True)  # Unique reference

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)


class ProductSupply(db.Model):
    __tablename__ = 'product_supplies'  # <-- clear database table name

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    cost_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    quantity_in_bags = db.Column(db.Integer, nullable=False)
    supply_date = db.Column(db.Date, nullable=False)

    product = db.relationship('Product', backref=db.backref('product_supplies', lazy=True))

    # Calculated fields
    total_cost = db.Column(db.Float, nullable=False, default=0)
    total_revenue = db.Column(db.Float, nullable=False, default=0)
    profit = db.Column(db.Float, nullable=False, default=0)
    
#     @property
#     def total_cost(self):
#         return self.cost_price * self.quantity_in_bags

#     @property
#     def total_revenue(self):
#         return self.selling_price * self.quantity_in_bags

#     @property
#     def profit(self):
#         return self.total_revenue - self.total_cost

#     def __repr__(self):
#         return f'<ProductSupply {self.product.name} - {self.quantity_in_bags} bags>'


class ProductSupplyForm(FlaskForm):
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    cost_price = FloatField('Cost Price (per bag)', validators=[DataRequired()])
    selling_price = FloatField('Selling Price (per bag)', validators=[DataRequired()])
    quantity_in_bags = IntegerField('Quantity in Bags', validators=[DataRequired()])
    supply_date = DateField('Supply Date', validators=[DataRequired()])
    submit = SubmitField('Add Supply')
