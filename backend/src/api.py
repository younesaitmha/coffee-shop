from flask import Flask, jsonify, abort, request
from flask_cors import CORS
import json

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


# db_drop_and_create_all()

# ROUTES


# the endpoint GET /drinks. it's a public endpoint
@app.route('/drinks', methods=['GET'])
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


# endpoint GET /drinks-detail
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details(token):
    '''
        returns status code 200 and json {"success": True, "drinks": drinks} where drinks
        is the list of drinks or appropriate status code indicating reason for failure
            - it requires the 'get:drinks-detail' permission
            - it contains the drink.long() data representation
    '''

    drinks = Drink.query.order_by(Drink.id).all()
    drinks = [drink.long() for drink in drinks]
    if drinks is None:
        abort(404)
    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(token):
    '''
    POST /drinks
        it creates a new row in the drinks table
        it requires the 'post:drinks' permission
        it contains the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array
        containing only the newly created drink or appropriate status code indicating reason
        for failure
    '''
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)
    try:
        drink = Drink(title = title, recipe = json.dumps(recipe))
        drink.insert()
        return jsonify({
            "success": True,
            "drink": [drink.long()]
        })
    except:
        abort(422)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(token, drink_id):
    '''
    PATCH /drinks/<id>
        where <id> is the existing model id
        it responds with a 404 error if <id> is not found
        it updates the corresponding row for <id>
        it requires the 'patch:drinks' permission
        it contains the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array
        containing only the updated drink or appropriate status code indicating reason for
        failure
    '''
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink is None:
        abort(404)
    try:
        if title is not None:
            drink.title = title
        if recipe is not None:
            drink.recipe = json.dumps(recipe)
        drink.update()
        return jsonify({"success": True,
                        "drinks": [drink.long()]})
    except:
        abort(422)


'''
#TODO implement
        where <id> is the existing model id
        it responds with a 404 error if <id> is not found
        it deletes the corresponding row for <id>
        it requires the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of
        the deleted record or appropriate status code indicating reason for failure
'''


# endpoint DELETE /drinks/<int:id>
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token, drink_id):

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink is None:
        abort(404)
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


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Server error"
    }), 500

'''
#TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
