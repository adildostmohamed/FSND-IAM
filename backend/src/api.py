import os
import sys
from flask import Flask, request, jsonify, abort, make_response
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
    GET /drinks
    returns status code 200 and json
    {"success": True, "drinks": drinks}
    where drinks is the list of drinks
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.order_by(Drink.id).all()
    drinks = list(map(lambda x: x.short(), drinks))
    return jsonify({
        'success': True,
        'drinks': drinks
    })


'''
    GET /drinks-detail
    returns status code 200 and json
    {"success": True, "drinks": drinks}
    where drinks is the list of drinks
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth("get:drinks-detail")
def get_drinks_detail(token):
    drinks = Drink.query.order_by(Drink.id).all()
    drinks = list(map(lambda x: x.long(), drinks))
    return jsonify({
        'success': True,
        'drinks': drinks
    })


'''
    POST /drinks
    returns status code 200 and json
    {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
'''
@app.route('/drinks', methods=['POST'])
@requires_auth("post:drinks")
def create_drink(token):
    drink_data = request.get_json()
    if drink_data is None:
        abort(400)
    else:
        drink = Drink(title=drink_data['title'], recipe=json.dumps(
            drink_data['recipe']))
        drink.insert()
        drinks = []
        new_drink_data = drink.long()
        drinks.append(new_drink_data)
        drinks_response = {
            "success": True,
            "drinks": drinks
        }
        return make_response(jsonify(drinks_response), 200)


'''
    PATCH /drinks/<id>
    returns status code 200 and json
    {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth("patch:drinks")
def update_drink(token, id):
    drink_data = request.get_json()
    if drink_data is None:
        abort(400)
    else:
        drink = Drink.query.get(id)
        if drink is None:
            abort(404)
        if 'title' in drink_data:
            drink.title = drink_data['title']
        if 'recipe' in drink_data:
            drink.recipe = json.dumps(drink_data['recipe'])
        drink.update()
        drinks = []
        updated_drink_data = drink.long()
        drinks.append(updated_drink_data)
        drinks_response = {
            "success": True,
            "drinks": drinks
        }
        return make_response(jsonify(drinks_response), 200)


'''
    DELETE /drinks/<id>
    returns status code 200 and json
    {"success": True, "delete": id}
    where id is the id of the deleted record

'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth("delete:drinks")
def delete_drink(token, id):
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)
    else:
        drink.delete()
        drinks_response = {
            "success": True,
            "delete": id
        }
        return make_response(jsonify(drinks_response), 200)


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(500)
def internal_server(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify(error.error), error.status_code
