# Lab: Flask-SQLAlchemy Serialization

## Scenario

You are building a simplified e-commerce backend that manages customers, 
the items they purchase, and the reviews they leave for products. To ensure 
your database is well-structured and your application can easily communicate 
with front-end or external systems, you need to correctly model the 
relationships between customers, items, and reviews, and then serialize this 
data into dictionaries or JSON-friendly formats.

To support this, you will need to use:
* SQLAlchemy models to define relationships and association proxies.
* Marshmallow schemas to serialize and structure the nested relational data.
* Recursion handling techniques to prevent infinite loops when serializing 
  relationships.

By the end of this lab, you should have a fully relational database and be 
able to serialize complex, nested relationships between customers, items, 
and reviews without errors.

## Tools & Resources

- [GitHub Repo](https://github.com/learn-co-curriculum/flask-sqlalchemy-serialization-lab)
- [Marshmallow Documentation](https://marshmallow.readthedocs.io/en/stable/)

## Setup

Fork and clone the lab repo.

Run `pipenv install` and `pipenv shell` .

```console
$ pipenv install
$ pipenv shell
```

Change into the `server` directory:

```console
$ cd server
```

The file `server/models.py` defines models named `Customer` and `Item`.

Run the following commands to create the tables for customers and items.

```console
$ flask db init
$ flask db migrate -m "initial migration"
$ flask db upgrade head
```

## Instructions

### Task 1: Define the Problem

Your application currently models customers and items, but there’s 
no direct way to track reviews that customers leave for the items 
they purchase. You also cannot yet serialize your data easily to 
share it via an API.

Specifically, you need to:
* Create a `Review` model to connect customers and items through their reviews.
* Allow a customer to access their reviewed items through an association proxy.
* Serialize models properly using Marshmallow to:
  * Flatten nested relationships.
  * Avoid recursion errors.
  * Control which fields are included or excluded during serialization.

Without solving these problems, it would be difficult to represent customer 
purchase histories, reviews, and item popularity in a structured, API-ready 
way.

### Task 2: Determine the Design

To solve this, the design will follow these steps:

1. Database Model Updates:
  * Create a `Review` model as a join table with `comment`, `customer_id`, and `item_id`.
  * Establish proper `back_populates` relationships between `Customer`, `Item`, and `Review`.
  * Add an association proxy to the `Customer` model so customers can easily access their items via reviews.

2. Serialization Strategy:
  * Create Marshmallow schemas for each model (`CustomerSchema`, `ItemSchema`, `ReviewSchema`).
  * Use `fields.Nested` to serialize relationships between models.
  * Exclude fields that could cause circular recursion:
    * In `CustomerSchema`, exclude items and reviews from nested outputs.
    * In `ItemSchema`, exclude reviews and customers from nested outputs.
    * In `ReviewSchema`, exclude item and customer from nested outputs.

3. Testing:
  * Create and seed the database with initial customers, items, and reviews.
  * Verify relationships using Flask shell.
  * Run unit tests to validate model relationships, association proxies, and serialization outputs.

Following this structure will ensure your data models are complete, your 
serialization is correct, and your application is robust against recursion errors.

### Task 3: Develop, Test, and Refine the Code

#### Step 1: Add Review and relationships with Customer and Item

![customer review item erd](/assets/sqlalchemy_lab_2_erd.png)

A customer can review an item that they purchased.

- A review **belongs to** an customer.
- A review **belongs to** an item.
- A customer **has many** items **through** reviews.
- An item **has many** customers **through** reviews.

Edit `server/models.py` to add a new model class named `Review` that inherits
from `db.Model`. Add the following attributes to the `Review` model:

- a string named `__tablename__` assigned to the value `'reviews'`.
- a column named `id` to store an integer that is the primary key.
- a column named `comment` to store a string.
- a column named `customer_id` that is a foreign key to the `'customers'` table.
- a column named `item_id` that is a foreign key to the `'items'` table.
- a relationship named `customer` that establishes a relationship with the
  `Customer` model. Assign the `back_populates` parameter to match the property
  name defined to the reciprocal relationship in `Customer`.
- a relationship named `item` that establishes a relationship with the `Item`
  model. Assign the `back_populates` parameter to match the property name
  defined to the reciprocal relationship in `Item`.

Edit the `Customer` model to add the following:

- a relationship named `reviews` that establishes a relationship with the
  `Review` model. Assign the `back_populates` parameter to match the property
  name defined to the reciprocal relationship in `Review`.

Edit the `Item` model to add the following:

- a relationship named `reviews` that establishes a relationship with the
  `Review` model. Assign the `back_populates` parameter to match the property
  name defined to the reciprocal relationship in `Review`.

Save `server/models.py`. Make sure you are in the `server` directory, then type
the following to perform a migration to add the new model:

```console
$ flask db migrate -m 'add review'
$ flask db upgrade head
```

Test the new `Review` model class and relationships:

```console
$ pytest testing/review_test.py
```

The 4 tests should pass. If not, update your `Review` model to pass the tests
before proceeding.

Run `server/seed.py` to add sample customers, items, and reviews to the
database.

```
$ python seed.py
```

Then use either Flask shell or SQLite Viewer to confirm the 3 tables are
populated with the seed data.

#### Step 2: Add Association Proxy

Given a customer, we might want to get a list of items they've reviewed.
Currently, you would need to iterate through the customer's reviews to get each
item. Try this in the Flask shell:

```py
>>> from models import *
>>> customer1 = Customer.query.filter_by(id=1).first()
>>> customer1
<Customer 1, Tal Yuri>
>>> items = [review.item for review in customer1.reviews]
>>> items
[<Item 1, Laptop Backpack, 49.99>, <Item 2, Insulated Coffee Mug, 9.99>]
>>>
```

Update `Customer` to add an association proxy named `items` to get a list of
items through the customer's `reviews` relationship.

Once you've defined the association proxy, you can easily get the items for a
customer as:

```py
>>> customer1.items
[<Item 1, Laptop Backpack, 49.99>, <Item 2, Insulated Coffee Mug, 9.99>]
```

Test the updated `Customer` model and association proxy:

```console
$ pytest testing/association_proxy_test.py
```

#### Step 3: Add Serialization

- Add schemas for `Customer`, `Item`, and `Reviews`.
- Schemas should serialize all columns including id, excepting any foreign keys.
- Use `fields.Nested` to include relationships.
- Add serialization rules to avoid errors involving recursion depth (be careful
  about tuple commas).
  - Customer(s) should exclude `items` and `reviews`
  - Item(s) should exclude `reviews` and `customers`
  - Review(s) should exclude `item` and `customer`

#### Step 4: Test and Refine Code

Test the serialized models:

```console
$ pytest testing/serialization_test.py
```

Run all tests to ensure they pass:

```console
$ pytest
```

#### Step 5: Commit and Push Git History

Once all tests are passing, commit and push your work using `git`.

### Task 4: Document and Maintain

Best Practice documentation steps:
* Add comments to the code to explain purpose and logic, clarifying intent and functionality of your code to other developers.
* Update README text to reflect the functionality of the application following https://makeareadme.com. 
  * Add screenshot of completed work included in Markdown in README.
* Delete any stale branches on GitHub
* Remove unnecessary/commented out code
* If needed, update git ignore to remove sensitive data

## Important Submission Note

Before you submit your solution, you need to save your progress with git.

1. Add your changes to the staging area by executing `git add .`.
2. Create a commit by executing `git commit -m "Your commit message"`.
3. Push your commits to GitHub by executing `git push origin main`.

CodeGrade will grade your lab using the same tests as are provided in the 
`testing/` directory.

---

## Developer Notes

Added Review model for Many-to-Many with payload between Customer & Item.
Implemented association_proxy:
- Customer.items → through reviews → item

Implemented Marshmallow schemas for serialization:
- Hide recursive inverse fields to prevent circular nesting
- Defined explicit fields + unknown = EXCLUDE

### Environment Fix

Ran into a **broken Pipfile** on clone — Flask dependency was malformed (`flask2.2.2` instead of `flask = "2.2.2"`).  
Because of that, Pipenv refused to install anything and virtualenv builds failed.

Solution (inside `server/` directory):

```
pipenv --rm 2>/dev/null || true
rm -rf ~/.local/share/virtualenvs/*serialization-lab*
pipenv --clear
pipenv install --skip-lock
pipenv shell

# Then install correct deps manually:
pip install \
  "flask==2.2.2" \
  "flask-migrate==3.1.0" \
  "flask-sqlalchemy==3.0.3" \
  "Werkzeug==2.2.2" \
  "pytest==7.1.3" \
  "importlib-metadata==6.0.0" \
  "importlib-resources==5.10.0" \
  "Faker==14.2.0" \
  "marshmallow==3.20.1"
```
