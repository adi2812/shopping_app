import imp
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(150), unique = True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    address = db.Column(db.String(150))
    cart = db.relationship('Cart',uselist=False, cascade='all, delete-orphan')

class Cart(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    product_id = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ordered_on = db.Column(db.DateTime(timezone=True),default = func.now())


class Category(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    image = db.Column(db.String(200), default="image.jpg")
    name = db.Column(db.String(20),unique=True)
    products = db.relationship("Product",backref='category', cascade='all, delete-orphan')



class Product(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20))
    price = db.Column(db.Integer)
    brand = db.Column(db.String(20))
    qty = db.Column(db.Integer)
    description = db.Column(db.String(300))
    image = db.Column(db.String(200), default="image.jpg")
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))


class Orders(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    product_id = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ordered_on = db.Column(db.DateTime(timezone=True),default = func.now())
    order_accepted = db.Column(db.Boolean, unique=False, default=False)
    order_dispatched = db.Column(db.Boolean, unique=False, default=False)
    order_delivered = db.Column(db.Boolean, unique=False, default=False)