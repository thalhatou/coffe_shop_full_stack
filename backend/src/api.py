#from crypt import methods
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from  database.models import db_drop_and_create_all, setup_db, Drink
from  auth.auth import AuthError, requires_auth, get_token_auth_header

app = Flask(__name__)
setup_db(app)
CORS(app)


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
#db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def drinks():
    if request.method == 'GET':
        all_drinks= Drink.query.all()
        
        data = [drink.short() for drink in all_drinks]
        return jsonify({"success":True, "drinks":data})
    if request.method =='POST':
        title = request.get_json()["title"]
        recipe = request.get_json()['recipe']
        drink = Drink(title=title, recipe=recipe)
        drink.insert()
        return jsonify({"success":True, "drinks":drink.short()})


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth("get:drinks-detail")
def drinks_details():
   
    return jsonify({
            'success':
            True,
            'drinks': [drink.long() for drink in Drink.query.all()]
        })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
# A decorator that requires authentication for the post:drinks endpoint.
@requires_auth('post:drinks')
def post_drinks(data=""):
    title = request.get_json()["title"]
    recipe = json.dumps(request.get_json()["recipe"])
    drink = Drink(title=title, recipe=recipe)
    drink.insert()
    return jsonify({"success":True, "drinks":drink.short()})
'''
{       "recipe": [
                {
                    "color": "blue",
                    "parts": 1
                }
            ],
            "title": "Coca"
        }

'''

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
# This is a decorator that requires authentication for the patch:drinks endpoint.
@requires_auth('patch:drinks')
def modify_drinks(payload, id):
    title = request.get_json()["title"]
    recipe = json.dumps(request.get_json()['recipe'])
    drink = Drink.query.filter_by(id=id).first()
    if not drink: 
        return jsonify({"response":"not found"})
    drink.title = title
    drink.recipe = recipe
    drink.update()
    return jsonify({"success":True, "drinks":drink.short()})


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
# This is a decorator that requires authentication for the delete:drinks endpoint.
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    data = str(request).split('/')
   # This is a way to get the id of the drink to be deleted.
    drink_id = int(data[len(data)-1].split(' ')[0].replace("'", ""))
    try:
      
        drink = Drink.query.filter_by(id=drink_id).first()
        drink.delete()
        return jsonify({"success":True, "delete":id})
    except:
        return jsonify({"response":"not found"})
    
  
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


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

@app.errorhandler(401)
def unautorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden you dont have permission to access at this resources"
    }), 403



@app.errorhandler(405)
def allowing(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method Not allowed"
    }), 405

@app.errorhandler(500)
def internalerrors(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal errors"
    }), 500



'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def error_404(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404




'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def authentify_error(erreur):
    return jsonify({
        "success": False,
        "error": erreur.status_code,
        "message": erreur.error['description']
    }), erreur.status_code


 

