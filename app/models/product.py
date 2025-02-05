from app import db
from datetime import datetime
from sqlalchemy import Enum
from app import db
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


# # class Product(db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     name = db.Column(db.String(255), nullable=False)
# #     price = db.Column(db.Float, nullable=False)
# #     description = db.Column(db.String(255), nullable=False)
# #     stock = db.Column(db.Integer, default=0) # Auto-update
    
# #     supplies = db.relationship('Supply', back_populates='product', lazy='dynamic')
    
# #     expenses = db.relationship('Expenses', backref='product', lazy=True)

# #     def expenses_value(self):
# #         """Calculate the total expenses related to this product."""
# #         return db.session.query(db.func.sum(Expenses.amount)).filter(Expenses.product_id == self.id).scalar() or 0.0


# #     @property
# #     def latest_cost_per_unit(self):
# #         # Get the latest supply cost_per_unit
# #         latest_supply = db.session.query(Supply).filter(Supply.product_id == self.id).order_by(Supply.date.desc()).first()
# #         return latest_supply.cost_per_unit if latest_supply else 0.0
    
# #     def stock_value(self):
# #         """Calculate the stock value."""
# #         return self.stock * self.price

# #     def __str__(self):
# #         return self.name

# # class Supply(db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     date = db.Column(db.Date, nullable=False, default=datetime.utcnow)  # Automatically set to current date
# #     product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
# #     quantity = db.Column(db.Float, nullable=False, default=0.0)
# #     cost_per_unit = db.Column(db.Float, nullable=False, default=0.0)  # Ensure cost is never None
    
# #     product = db.relationship('Product', back_populates='supplies')
# #     #product = db.relationship('Product', backref='supplies')

# #     @property
# #     def supply_cost(self):
# #         return self.quantity * self.product.price
    
# #     def __str__(self):
# #         return f"Supply(id={self.id}, product_id={self.product_id}, quantity={self.quantity})"
    

# from app import db
# from datetime import datetime

# class Product(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255), nullable=False)
#     price = db.Column(db.Float, nullable=False)
#     description = db.Column(db.String(255), nullable=False)
#     stock = db.Column(db.Integer, default=0)

#     supplies = db.relationship('Supply', back_populates='product', lazy='dynamic')
#     expenses = db.relationship('Expenses', backref='product', lazy=True)

#     def expenses_value(self):
#         return db.session.query(db.func.sum(Expenses.amount)).filter(Expenses.product_id == self.id).scalar() or 0.0

#     @property
#     def latest_cost_per_unit(self):
#         latest_supply = db.session.query(Supply).filter(Supply.product_id == self.id).order_by(Supply.date.desc()).first()
#         return latest_supply.cost_per_unit if latest_supply else 0.0

#     def stock_value(self):
#         return self.stock * self.price

#     def __str__(self):
#         return self.name


# class Supply(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
#     product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
#     quantity = db.Column(db.Float, nullable=False, default=0.0)
#     cost_per_unit = db.Column(db.Float, nullable=False, default=0.0)

#     product = db.relationship('Product', back_populates='supplies')

#     @property
#     def supply_cost(self):
#         return self.quantity * self.cost_per_unit

#     def __str__(self):
#         return f"Supply(id={self.id}, product_id={self.product_id}, quantity={self.quantity})"

# class Sale(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     date = db.Column(db.Date, default=datetime.utcnow)  # Automatically sets the current date
#     customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
#     transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
#     product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='SET NULL'), nullable=True)
#     quantity_sold = db.Column(db.Float, nullable=False)
#     price = db.Column(db.Float, nullable=False)  # Ensures price is not optional
#     total_amount = db.Column(db.Float, nullable=False)  # Computed as quantity_sold * price
#     payment_method = db.Column(db.String(50), nullable=False)  # Payment method (e.g., cash, transferred)
#     status = db.Column(db.String(20), nullable=False, default='Pending')  # Sale status ('Pending', 'Completed')

#     # Relationships
#     customer = db.relationship('Customer', backref='sales')
#     transaction = db.relationship('Transaction', backref='sales')
#     product = db.relationship('Product', backref='sales')


   
#     @property
#     def sale_value(self):
#         if self.quantity_sold is None or self.price is None:
#             return 0  # Or any default value you prefer
#         return self.quantity_sold * self.product.price
    
#     def expenses_value(self):
#         return db.session.query(db.func.sum(Expenses.amount)).filter(Expenses.product_id == self.id).scalar() or 0.0

#         #return sum(expense.amount for expense in self.expenses)



# class Expenses(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     date = db.Column(db.Date, default=datetime.utcnow)
#     amount = db.Column(db.Float, nullable=False)
#     purpose = db.Column(db.String(255), nullable=False)
#     product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    

# # models.py
# class Transaction(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
#     customer = db.relationship('Customer', backref='transactions')
#     total_amount = db.Column(db.Float, nullable=False)
#     amount_paid = db.Column(db.Float, nullable=False, default=0.0)
#     balance = db.Column(db.Float, nullable=False)
#     status = db.Column(db.String(20), nullable=False, default="Pending")  # e.g., "Pending", "Completed"

    
#     customer = db.relationship('Customer', backref='transactions')

# class Customer(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     phone = db.Column(db.String(20), nullable=True)