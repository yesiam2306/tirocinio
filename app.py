from flask import Flask, Blueprint, request, jsonify, make_response, abort
from IPy import IP
import time
import sqlite3
import ipaddress
import random
import string

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False #this is cause otherwise JSON's labels are sorted alphabetically

import settings
from Endpoints.apiEndpoint import ns_endpoint
from Restplus import api


def configure_app(flask_app):
    flask_app.config['SERVER_NAME'] = settings.FLASK_SERVER_NAME
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP


def initialize_app(flask_app):
    configure_app(flask_app)
    blueprint = Blueprint('api', __name__, url_prefix='/flaskAPI')
    api.init_app(blueprint)
    api.add_namespace(ns_endpoint)

    flask_app.register_blueprint(blueprint)


#this function transform a row of a database in a dictionary type data
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


#this function generates a random string with letters, numbers and symbols.
#it's useful for the script key
def get_random_key(length):
    key_characters = string.ascii_letters + string.digits + string.punctuation
    # it's better to remove special characters
    key_characters = key_characters.replace("\"", "")
    key_characters = key_characters.replace("\'", "")
    key_characters = key_characters.replace("`", "")
    #it adds a random character from an array with all letters, symbol and numbers
    key = ''.join(random.choice(key_characters) for i in range(length))
    return key

# it's used to check if an IP has the correct format
def checkIP(ip, port):
    try:
        IP(ip)
        if port > 65535 or port < 0:
            return False
        return True
    except ValueError:
        return False

#-------------------------------------HANDLERS--------------------------------------------#

# this handles the errors for missing parameters
@app.errorhandler(400)
def bad_request(error):
    if not request.json:
        parameter = 's' # to print the plural (Missing input parameterS)
    elif not 'username' in request.json:
        parameter = ' [\'username\']'
    elif not 'ip_address' in request.json:
        parameter = ' [\'ip_address\']'
    status = 'STATUS.BAD_REQUEST'
    code = 400
    message = 'Missing input parameter{}'.format(parameter)
    return make_response(jsonify(
                            {
                                'status' : status,
                                'code' : code,
                                'message' : message
                            }), 400)

# this handles errors for incorrect format
@app.errorhandler(401)
def input_format(error):
    status = 'STATUS.INPUT_FORMAT_ERROR'
    code = 401
    message = 'Incorrect input parameter'
    return make_response(jsonify(
                            {
                                'status' : status,
                                'code' : code,
                                'message' : message
                            }), 401)

# this is for missing data errors
@app.errorhandler(404)
def not_found(error):
    status = 'STATUS.NOT_FOUND'
    code = 402
    message = 'Data not found'
    return make_response(jsonify(
                            {
                                'status' : status,
                                'code' : code,
                                'message' : message
                            }), 402)

# this handle the case when someone is trying to insert the same IP twice
@app.errorhandler(403)
def not_allowed(error):
    status = 'STATUS.NOT_ALLOWED'
    code = 403
    message = 'Operation not allowed, you\'re trying to ask for same IP two times'
    return make_response(jsonify(
                            {
                                'status' : status,
                                'code' : code,
                                'message' : message
                            }), 403)


# this handle the case when someone is trying to insert different IP addresses more than three times
# in three days
@app.errorhandler(409)
def conflict(error):
    status = 'STATUS.CONFLICT'
    code = 409
    message = 'Too many tries. Try again in 3 days'
    return make_response(jsonify(
                            {
                                'status' : status,
                                'code' : code,
                                'message' : message
                            }), 409)

#----------------------------------------------------------------------------------------------------#

@app.route('/api/v1.0/verifiedIP', methods=['GET'])
def api_all():

    status = 'STATUS.OK'
    code = 200
    message = 'Request Accepted'

    if not request.json or not 'username' in request.json:
        abort(400)

    username = request.json['username']
    if type(username) != unicode or len(username) > 25:
        abort(401)

    #establishes a connection with the database
    conn = sqlite3.connect('HTTP01_challenge_db.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    query = "SELECT * FROM IP_addresses WHERE username = {}".format(username)
    #saves all rows in a dictionary named all_ip
    all_ip = cur.execute(query).fetchall()

    if not all_ip:
        abort(404)

    return jsonify({'status' : status,
                    'code' : code,
                    'message' : message,
                    'data' : all_ip})


@app.route('/api/v1.0/newIP', methods=['POST'])
def api_post():

    if not request.json or 'ip_address' not in request.json or 'username' not in request.json:
        abort(400)

    status = 'STATUS.OK'
    code = 200
    message = 'Request Accepted'

    username = request.json['username']
    if type(username) != str or len(username) > 25:
        abort(401)

    ip_address = request.json['ip_address']
    iport = ip_address.split(":")
    ip_address = iport[0]
    port = int(iport[1])
    if not checkIP(ip_address, port):
        abort(401)

    conn = sqlite3.connect('HTTP01_challenge_db.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    #it is getting the list of all ip addresses registered by the user 'user'
    query = "SELECT * FROM IP_addresses WHERE username = '{}'".format(username)
    all_ip = cur.execute(query).fetchall()
    print(all_ip)
    if all_ip and ip_address in all_ip:
        abort(403)

    #with another query it controls if there are more than three tries in three days
    results = cur.execute("SELECT * " \
                        "FROM IP_addresses " \
                        "WHERE username = '{}'" \
                          "AND datetime(creation, '+3 day') > datetime('now')".format(username)).fetchall()
    if request and len(results) >= 3:
        abort(409)

    #setting for data values
    trusted = False
    verification_date = ''
    key = get_random_key(25)

    #they are inserted into an array to be passed to cur.executemany
    values = [(
        ip_address,
        username,
        trusted,
        verification_date,
        key,
    )]
    conn = sqlite3.connect('HTTP01_challenge_db.db')
    cur = conn.cursor()
    cur.executemany("INSERT INTO `IP_addresses` VALUES (?,?,?,DATETIME('now'),?,?)", values)
    conn.commit()
    conn.close()

    return jsonify({'status': status,
                    'code': code,
                    'message': message,
                    'data': key})


if __name__ == '__main__':
#    initialize_app(app)
    app.run(debug= settings.FLASK_DEBUG)
