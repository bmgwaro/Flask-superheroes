#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'


# GET /heroes
@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()  
    heroes_data = [{"id": hero.id, "name": hero.name, "super_name": hero.super_name} for hero in heroes]
    return jsonify(heroes_data)

# GET /heroes/:id
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):
    hero = Hero.query.get(id) 
    if hero:
        hero_data = {
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name,
            "hero_powers": []  # Placeholder for hero powers 
        }
        return jsonify(hero_data)
    return jsonify({"error": "Hero not found"}), 404

# GET /powers
@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()  
    powers_data = [{"id": power.id, "name": power.name, "description": power.description} for power in powers]
    return jsonify(powers_data)

# GET /powers/:id
@app.route('/powers/<int:id>', methods=['GET'])
def get_power_by_id(id):
    power = Power.query.get(id)  
    if power:
        power_data = {
            "id": power.id,
            "name": power.name,
            "description": power.description
        }
        return jsonify(power_data)
    return jsonify({"error": "Power not found"}), 404

# PATCH /powers/:id
@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)  
    if not power:
        return jsonify({"error": "Power not found"}), 404
    
    data = request.get_json()
    description = data.get("description")

    # description must not be empty
    if not description:
        return jsonify({"errors": ["validation errors"]}), 400

    power.description = description
    db.session.commit()  
    return jsonify({
        "id": power.id,
        "name": power.name,
        "description": power.description
    })

# POST /hero_powers
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()
    hero_id = data.get("hero_id")
    power_id = data.get("power_id")
    strength = data.get("strength")

    hero = Hero.query.get(hero_id)
    power = Power.query.get(power_id)

    # Validate hero and power exist in the database
    if not hero or not power:
        return jsonify({"errors": ["validation errors"]}), 400

    valid_strengths = ["Strong", "Weak", "Average"]
    if strength not in valid_strengths:
        return jsonify({"errors": ["validation errors"]}), 400

    # Create a new HeroPower
    new_hero_power = HeroPower(hero_id=hero_id, power_id=power_id, strength=strength)
    db.session.add(new_hero_power)
    db.session.commit()

    return jsonify({
        "id": new_hero_power.id,
        "hero_id": hero_id,
        "power_id": power_id,
        "strength": strength,
        "hero": {"id": hero.id, "name": hero.name, "super_name": hero.super_name},
        "power": {"id": power.id, "name": power.name, "description": power.description}
    })


if __name__ == '__main__':
    app.run(port=5555, debug=True)
