#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import os

# Set up the base directory and the database URI
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Initialize the Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

# Set up Flask-Migrate for database migrations
migrate = Migrate(app, db)

# Initialize SQLAlchemy and Flask-RESTful
db.init_app(app)
api = Api(app)

# Home route
@app.route("/")
def index():
    return "<h1>Code Challenge</h1>"

# Resource to handle all restaurants
class RestaurantListResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.to_dict() for restaurant in restaurants])

# Resource to handle a specific restaurant by ID
class RestaurantResource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get_or_404(id)
        return restaurant.to_dict(), 200

    def delete(self, id):
        restaurant = Restaurant.query.get_or_404(id)
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204

# Resource to handle all pizzas
class PizzaListResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict() for pizza in pizzas])

# Resource to create a restaurant-pizza association (RestaurantPizza)
class RestaurantPizzaResource(Resource):
    def post(self):
        data = request.get_json()
        
        try:
            # Price validation
            price = data.get('price')
            if not (1 <= price <= 30):
                raise ValueError("Price must be between 1 and 30")
                
            new_restaurant_pizza = RestaurantPizza(
                price=price,
                pizza_id=data['pizza_id'],
                restaurant_id=data['restaurant_id']
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            return new_restaurant_pizza.to_dict(), 201
        except ValueError as e:
            return {'error': str(e)}, 400

# Register resources with the API
api.add_resource(RestaurantListResource, '/restaurants')
api.add_resource(RestaurantResource, '/restaurants/<int:id>')
api.add_resource(PizzaListResource, '/pizzas')
api.add_resource(RestaurantPizzaResource, '/restaurant_pizzas')

# Run the app
if __name__ == "__main__":
    app.run(port=5555, debug=True)
