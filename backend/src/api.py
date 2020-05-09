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
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        drinks = list(map(lambda x: x.short(), drinks))
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        print(sys.exc_info())
        abort(500)


'''
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth("get:drinks-detail")
def get_drinks_detail(token):
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        drinks = list(map(lambda x: x.long(), drinks))
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        print(sys.exc_info())
        abort(500)


'''
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth("post:drinks")
def create_drink(token):
    drink_data = request.get_json()
    if drink_data is None:
        abort(400)
    try:
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
    except:
        print(sys.exc_info())
        abort(500)


'''
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth("patch:drinks")
def update_drink(token, id):
    drink_data = request.get_json()
    if drink_data is None:
        abort(400)
    try:
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

    except:
        print(sys.exc_info())
        abort(500)


'''
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth("delete:drinks")
def delete_drink(token, id):
    try:
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
    except:
        print(sys.exc_info())
        abort(500)


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
