import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
#TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMITTED ON FIRST RUN
!! Running this function will add one
'''
# db_drop_and_create_all()

# ROUTES


# the endpoint GET /drinks. it's a public endpoint
@app.route('drinks', methods=['GET'])
def get_drinks():
    """ returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks or appropriate status code
        indicating reason for failure
    """

    drinks = Drink.query.order_by(Drink.id).all()
    drinks = [drink.short() for drink in drinks]
    if drinks is None:
        abort(404)
    return jsonify({
        "success": True,
        "drinks": drinks
    }), 200


'''
#TODO
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

# endpoint GET /drinks-detail
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details(token):
    drinks = Drink.query.order_by(Drink.id).all()
    drinks = [drink.long() for drink in drinks]
    if drinks is None:
        abort(404)
    return jsonify({
        "success": True,
        "drinks": drinks
    })


'''
#TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
def create_drink():
    pass


'''
#TODO implement endpoint
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
def patch_drink():
    pass


'''
#TODO implement
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

# endpoint DELETE /drinks/<int:id>
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token, drink_id):

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink is None:
        abort(404)
    else:
        try:
            drink.delete()
            return jsonify({
                "success": True,
                "delete": drink_id
            })
        except Exception:
            abort(422)

# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404



'''
#TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
