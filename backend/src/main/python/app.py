import jwt
import json
import datetime
import base64
from functools import wraps
from flask import Flask, request, make_response, jsonify, send_from_directory
from flask_cors import CORS
from database import Database
from data_validator import valid_account_data, valid_credentials_data, valid_order_data

app = Flask(__name__)
app.config["SECRET_KEY"] = "SOMESUPERSECUREKEY"
CORS(app)

db = Database("src/main/python/database.db")


def token_protected(f):
	@wraps(f)
	def authenticate_token(*args, **kwargs):
		token = request.headers.get("Authorization")
		if token is not None:
			try:
				jwt.decode(token, app.config["SECRET_KEY"])
			except Exception as e:
				print(e)
				return jsonify({"msg": "invalid token"}), 403
		else:
			return jsonify({"msg": "missing token"}), 400
		return f(*args, **kwargs)

	return authenticate_token


# disable cacheing of static files, this is temporary only to help with development
@app.after_request
def add_header(r):
	r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
	r.headers["Pragma"] = "no-cache"
	r.headers["Expires"] = "0"
	r.headers["Cache-Control"] = "public, max-age=0"
	return r


# send static files
@app.route("/", defaults={"filename": "index.html"})
@app.route("/<path:filename>")
def send_static(filename):
	return send_from_directory("../../../../frontend", filename)


# temporary route used only for testing the token_protected decorator
@app.route("/protected")
@token_protected
def protected():
	return "protected content"


@app.route("/api/carts", methods=["POST"])
@token_protected
def update_cart():
	cart = request.json
	if cart and valid_order_data(cart):  # valid cart data is the same as valid order data
		token_body = json.loads(base64.b64decode(request.headers.get("Authorization").split(".")[1] + "==").decode())
		cart["username"] = token_body["username"]
		# TODO handle error
		db.update_cart(cart)
		return jsonify({"msg": "successfuly updated cart"})
	else:
		return jsonify({"msg": "no/invalid json data or missing json content type header"}), 400


@app.route("/api/carts", methods=["GET"])
@token_protected
def get_cart():
	token_body = json.loads(base64.b64decode(request.headers.get("Authorization").split(".")[1] + "==").decode())
	username = token_body["username"]
	cart = db.get_cart(username)
	cart["username"] = username
	return jsonify(cart)


@app.route("/api/orders", methods=["GET"])
@token_protected
def get_all_orders():  # pragma: no cover
	token_body = json.loads(base64.b64decode(request.headers.get("Authorization").split(".")[1] + "==").decode())
	role = token_body["role"]

	if role == "admin":
		placed_orders = db.get_all_orders()
		return jsonify(placed_orders)
	else:
		return jsonify({"msg": "unauthorized"}), 401


@app.route("/api/users/<username>/orders", methods=["GET"])
@token_protected
def get_orders(username):
	token_body = json.loads(base64.b64decode(request.headers.get("Authorization").split(".")[1] + "==").decode())
	request_username = token_body["username"]

	if request_username != username:
		return jsonify({"msg": "unauthorized"}), 401
	else:
		user_orders = db.get_user_orders(request_username)
		return jsonify(user_orders)


@app.route("/api/orders", methods=["POST"])
@token_protected
def add_order():
	order = request.json
	if order and valid_order_data(order):
		token_body = json.loads(base64.b64decode(request.headers.get("Authorization").split(".")[1] + "==").decode())
		order["username"] = token_body["username"]

		if db.address_is_valid(order):
			# TODO handle error
			db.add_order(order)
			empty_cart = {"username": order["username"], "orderDetails": []}
			db.update_cart(empty_cart)
			return jsonify({"msg": "successfuly created order"})
		else:
			return jsonify({"msg": "address is invalid"}), 400

	else:
		return jsonify({"msg": "no/invalid json data or missing json content type header"}), 400


@app.route("/api/categories", methods=["POST"])
@token_protected
def add_category():  # pragma: no cover
	token_body = json.loads(base64.b64decode(request.headers.get("Authorization").split(".")[1] + "==").decode())
	role = token_body["role"]

	if role == "admin":
		db.add_category(request.json["name"])
		return jsonify({"msg": "successfuly created category"})
	else:
		return jsonify({"msg": "unauthorized"}), 401


@app.route("/api/products", methods=["POST"])
@token_protected
def add_product():  # pragma: no cover
	token_body = json.loads(base64.b64decode(request.headers.get("Authorization").split(".")[1] + "==").decode())
	role = token_body["role"]

	if role == "admin":
		product = request.json
		print(product)
		db.add_product(product)
		return jsonify({"msg": "successfuly created product"})
	else:
		return jsonify({"msg": "unauthorized"}), 401


@app.route("/api/products", methods=["GET"])
def get_products():
	products = db.get_products()

	return jsonify(products)


@app.route("/api/categories", methods=["GET"])
def get_categories():
	categories = db.get_categories()
	return jsonify(categories)


@app.route("/api/auth", methods=["POST"])
def authenticate_user():
	credentials = request.json
	if credentials and valid_credentials_data(credentials):
		if db.find_credentials(credentials):
			token = jwt.encode(
				{
					"username": credentials["username"],
					"role": str(db.get_role(credentials["username"])),
					"exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
				},
				app.config["SECRET_KEY"]
			)
			response = make_response(jsonify({"msg": "successfuly authenticated", "jwt": token.decode()}))
			response.set_cookie("jwt", token.decode())
			return response
		else:
			return jsonify({"msg": "username or password is invalid"}), 401
	else:
		return jsonify({"msg": "no/invalid json data or missing json content type header"}), 400


@app.route("/api/users", methods=["POST"])
def create_customer_account():
	account = request.json
	if account and valid_account_data(account):
		if not db.account_exists(account["username"]):
			db.add_customer(account)
			return jsonify({"msg": "account created"})
		else:
			return jsonify({"msg": "could not create account, username taken"}), 409
	else:
		return jsonify({"msg": "no/invalid json data or missing json content type header"}), 400
