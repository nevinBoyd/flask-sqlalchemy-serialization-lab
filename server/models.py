from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from marshmallow import Schema, fields, EXCLUDE


metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Review(db.Model):
       """
       Join table w/ attributes (Many-to-Many with payload)
       - Each Review belongs to ONE customer & ONE item
       """
       __tablename__ = 'reviews'

       id = db.Column(db.Integer, primary_key=True)
       comment = db.Column(db.String)

       # Foreign keys
       customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
       item_id = db.Column(db.Integer, db.ForeignKey('items.id'))

       # Relationships back to parents
       customer = db.relationship("Customer", back_populates="reviews")
       item = db.relationship("Item", back_populates="reviews")

       def __repr__(self):
           return f'<Review {self.id}, {self.comment}>'
       
class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

     # Customer has many reviews
    reviews = db.relationship("Review", back_populates="customer")

    # association proxy: customer.items → goes through reviews → item
    items = association_proxy("reviews", "item")

    def __repr__(self):
        return f'<Customer {self.id}, {self.name}>'


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)
    
     # Item has many reviews
    reviews = db.relationship("Review", back_populates="item")

    def __repr__(self):
        return f'<Item {self.id}, {self.name}, {self.price}>'
       
# SCHEMAS
# EXCLUDE ignores unexpected data when deserializing 

# Include related customer item, prevent nesting their own reviews into the serializer
class ReviewSchema(Schema):
   customer = fields.Nested("CustomerSchema", exclude=("reviews",))
   item = fields.Nested("ItemSchema", exclude=("reviews",)) 

   # Define allowed fields in JSON output
   class Meta:
       fields = ("id", "comment", "customer", "item")
       unknown = EXCLUDE

# Customer nests reviews, excludes review customer field, avoids infinite loop
class CustomerSchema(Schema):
    reviews = fields.Nested("ReviewSchema", many=True, exclude=("customer",))

    class Meta:
        fields = ("id", "name", "reviews")
        unknown = EXCLUDE

# Item nests reviews, excludes review item field, avoids infinite loop
class ItemSchema(Schema):
    reviews = fields.Nested("ReviewSchema", many=True, exclude=("item",))

    class Meta:
        fields = ("id", "name", "price", "reviews")
        unknown = EXCLUDE       
