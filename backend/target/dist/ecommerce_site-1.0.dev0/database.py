import sqlite3
from hashlib import sha256
from urllib.request import urlopen
import urllib.parse
from math import floor


class Database(object):
	database_uri = None

	def __init__(self, database_uri):
		self.database_uri = database_uri

	def account_exists(self, username):
		conn = sqlite3.connect(self.database_uri, check_same_thread=False)
		c = conn.cursor()

		c.execute('''
			SELECT * FROM Accounts WHERE username = ?;
		''', (username,))

		result = c.fetchone()

		conn.commit()
		conn.close()

		return result is not None

	def address_is_valid(self, address):  # pragma: no cover
		request_xml = f'''
			<?xml version="1.0"?>
			<AddressValidateRequest USERID="657UNIVE7805">
				<Revision>1</Revision>
				<Address ID="0">
					<Address1></Address1>
					<Address2>{address["street"]}</Address2>
					<City>{address["city"]}</City>
					<State>{address["state"]}</State>
					<Zip5>{address["zip"]}</Zip5>
					<Zip4></Zip4>
				</Address>
			</AddressValidateRequest>
		'''

		api_endpoint = "http://production.shippingapis.com/ShippingAPI.dll?API=Verify&XML="

		with urlopen(api_endpoint + urllib.parse.quote(request_xml)) as response:
			response_xml = response.read().decode().upper()

			if "</Error>" in response_xml:
				return False
			elif f'<Address2>{address["street"]}</Address2>'.upper() not in response_xml:
				return False
			elif f'<City>{address["city"]}</City>'.upper() not in response_xml:
				return False
			elif f'<State>{address["state"]}</State>'.upper() not in response_xml:
				return False
			elif f'<Zip5>{address["zip"]}</Zip5>'.upper() not in response_xml:
				return False
			else:
				return True

	def find_credentials(self, credentials):
		conn = sqlite3.connect(self.database_uri, check_same_thread=False)
		c = conn.cursor()

		username = credentials.get("username")
		password = sha256(credentials.get("password").encode()).hexdigest()

		c.execute('''
			SELECT * FROM Accounts WHERE username = ? and password = ?;
		''', (username, password,))

		result = c.fetchone()

		conn.commit()
		conn.close()

		return result is not None

	def get_role(self, username):
		conn = sqlite3.connect(self.database_uri, check_same_thread=False)
		c = conn.cursor()

		c.execute('''
			SELECT * FROM Admins
			JOIN Accounts
			ON Admins.accountID = Accounts.accountID
			WHERE username = ?;
		''', (username,))

		if c.fetchone() is not None:
			conn.commit()
			conn.close()
			return "admin"
		else:
			conn.commit()
			conn.close()
			return "customer"

	def get_products(self):
		conn = sqlite3.connect(self.database_uri, check_same_thread=False)
		c = conn.cursor()

		c.execute('''
			SELECT * FROM Products;
		''')

		column_names = next(zip(*c.description))
		product_rows = c.fetchall()

		products = [dict(zip(column_names, product_values)) for product_values in product_rows]

		conn.commit()
		conn.close()

		return products

	def get_categories(self):
		conn = sqlite3.connect(self.database_uri, check_same_thread=False)
		c = conn.cursor()

		c.execute('''
			SELECT * FROM Categories;
		''')

		column_names = next(zip(*c.description))
		category_rows = c.fetchall()

		categories = [dict(zip(column_names, category_values)) for category_values in category_rows]

		conn.commit()
		conn.close()

		return categories

	def get_user_orders(self, username):
		conn = sqlite3.connect(self.database_uri, check_same_thread=False)
		c = conn.cursor()

		c.execute('''
			SELECT *
			FROM Orders
			WHERE accountID = (SELECT accountID
				FROM Accounts
				WHERE username = ?);
		''', (username,))

		column_names = next(zip(*c.description))
		order_rows = c.fetchall()

		orders = [dict(zip(column_names, order_values)) for order_values in order_rows]

		order_ids = [order["orderID"] for order in orders]

		for index, order_id in enumerate(order_ids):
			c.execute('''
				SELECT *
				FROM OrderDetails
				WHERE orderID = ?;
			''', (order_id,))

			item_column_names = next(zip(*c.description))
			item_rows = c.fetchall()

			items = [dict(zip(item_column_names, item_values)) for item_values in item_rows]

			orders[index]["items"] = items

		conn.commit()
		conn.close()
		return orders

	def add_category(self, category_name):
		conn = sqlite3.connect(self.database_uri, check_same_thread=False)
		c = conn.cursor()

		c.execute('''
			INSERT INTO Categories(categoryName)
			VALUES(?);
		''', (category_name,))

		conn.commit()
		conn.close()

	def add_product(self, product):
		conn = sqlite3.connect(self.database_uri, check_same_thread=False)
		c = conn.cursor()

		product_details = [
			product.get("categoryID"),
			product.get("name"),
			product.get("description"),
			product.get("imageURL"),
			product.get("price"),
			product.get("quantityAvailable"),
		]

		# TODO verify category id exists

		c.execute('''
			INSERT INTO Products(
			categoryID,
			name,
			description,
			imageURL,
			price,
			quantityAvailable
			)
			VALUES(?,?,?,?,?,?);
		''', product_details)

		conn.commit()
		conn.close()

	# TODO this whole function could probably be enhanced/made more efficient using some more advanced sql
	def add_order(self, order):
		conn = sqlite3.connect(self.database_uri, check_same_thread=False)
		c = conn.cursor()

		username = order["username"]

		c.execute('''
			SELECT accountID FROM Accounts WHERE username = ?;
		''', (username,))

		account_id = c.fetchone()

		c.execute('''
			SELECT
			billingAddress,
			billingCity,
			billingState,
			billingPostalCode,
			shippingAddress,
			shippingCity,
			shippingState,
			shippingPostalCode
			FROM Customers WHERE accountID = ?;
		''', account_id)

		account_shipping_and_billing = (
			order.get("street"),
			order.get("city"),
			order.get("state"),
			order.get("zip"),
			order.get("street"),
			order.get("city"),
			order.get("state"),
			order.get("zip"),
		)

		account_details = (account_id + account_shipping_and_billing)

		# TODO verify user billingAddress and shippingAddress exist

		# TODO verify each product exists and that there is enough to fulfill order

		# create order entry
		c.execute('''
			INSERT INTO Orders
			(
				accountID,
				dateOrdered,
				billingAddress,
				billingCity,
				billingState,
				billingPostalCode,
				shippingAddress,
				shippingCity,
				shippingState,
				shippingPostalCode,
				taxCost,
				shippingCost,
				totalCost
			)
			VALUES (?, DATETIME("now"), ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0);
		''', account_details)

		order_id = c.lastrowid

		orderDetails = [
			(order_id, orderDetail["quantity"], orderDetail["productID"])
			for orderDetail in order["orderDetails"]
		]

		# add orderlines
		c.executemany('''
			INSERT INTO OrderDetails
			(
			orderID,
			productID,
			name,
			description,
			price,
			quantity
			)
			SELECT ?, productID, name, description, price, ?
			FROM Products WHERE productID = ?;
			''', orderDetails)

		# update order price info
		# get sum of price of all products in order
		c.execute('''
			SELECT SUM(price * quantity)
			FROM OrderDetails
			WHERE orderID = ?;
		''', (order_id,))

		order_product_sum = c.fetchone()[0]

		tax_rate = 0.0825

		tax_cost = floor(order_product_sum * tax_rate)

		total_cost = floor(order_product_sum + tax_cost)

		shipping_cost = 0  # free shipping

		c.execute('''
			UPDATE Orders
			SET
			taxCost = ?,
			shippingCost = ?,
			totalCost = ?
			WHERE orderID = ?;
		''', (tax_cost, shipping_cost, total_cost, order_id,))

		conn.commit()
		conn.close()

	def get_cart(self, username):

		conn = sqlite3.connect(self.database_uri, check_same_thread=False)
		c = conn.cursor()

		c.execute('''
			SELECT cartID
			FROM Customers
			WHERE accountID = (
				SELECT accountID
				FROM Accounts
				WHERE username = ?
			);
		''', (username,))

		cart_id = c.fetchone()

		cart_id = cart_id[0] if cart_id is not None else None

		if cart_id is None:
			# create cart
			c.execute('''
				INSERT INTO Carts(accountID)
				SELECT accountID
				FROM Accounts
				WHERE username = ?;
			''', (username,))
			cart_id = c.lastrowid

			# update customer cart id
			c.execute('''
				UPDATE Customers
				SET cartID = ?
				WHERE accountID = (
					SELECT accountID
					FROM Accounts
					WHERE username = ?
				);
			''', (cart_id, username,))

		c.execute('''
			SELECT productID, quantity FROM CartDetails
			WHERE cartID = ?;
			''', (cart_id,))

		column_names = next(zip(*c.description))

		cart_detail_rows = c.fetchall()

		cart = {"orderDetails": [dict(zip(column_names, cart_detail)) for cart_detail in cart_detail_rows]}
		conn.commit()
		conn.close()
		return cart

	def update_cart(self, cart):
		# get account id, and cart id
		conn = sqlite3.connect(self.database_uri, check_same_thread=False)
		c = conn.cursor()

		username = cart["username"]

		c.execute('''
			SELECT accountID FROM Accounts WHERE username = ?;
		''', (username,))

		account_id = c.fetchone()

		c.execute('''
			SELECT cartID FROM Customers WHERE accountID = ?;
		''', account_id)

		cart_id = c.fetchone()[0]

		if cart_id is None:
			# create cart
			c.execute('''
				INSERT INTO Carts(accountID)
				VALUES(?);
			''', account_id)
			cart_id = c.lastrowid

			# update customer cart id
			c.execute('''
				UPDATE Customers
				SET cartID = ?
				WHERE accountID = ?;
			''', (cart_id, account_id[0],))

		cartDetails = [
			(cart_id, cartDetail["productID"], cartDetail["quantity"])
			for cartDetail in cart["orderDetails"]
		]

		# delete previous cart details
		c.execute('''
			DELETE FROM CartDetails
			WHERE cartID = ?;
		''', (cart_id,))

		# TODO verify cart details exist

		# insert cart details
		c.executemany('''
			INSERT INTO CartDetails
			(
			cartID,
			productID,
			quantity
			)
			VALUES(?,?,?);
		''', cartDetails)

		# insert cart items
		conn.commit()
		conn.close()

	def add_customer(self, account):
		conn = sqlite3.connect(self.database_uri, check_same_thread=False)
		c = conn.cursor()

		account_details = [
			account.get("username"),
			sha256(account.get("password").encode()).hexdigest(),
			account.get("firstName"),
			account.get("middleInitial"),
			account.get("lastName"),
			account.get("phoneNumber"),
			account.get("email"),
		]

		c.execute('''
			INSERT INTO Accounts
			(username, password, firstName, middleInitial, lastName, phoneNumber, email)
			VALUES (?,?,?,?,?,?,?);
		''', account_details)

		c.execute('''
			INSERT INTO Customers (accountID)
			SELECT accountID FROM Accounts WHERE username = ?;
		''', (account_details[0],))

		conn.commit()
		conn.close()

	def create_accounts_table(self):
		conn = sqlite3.connect(self.database_uri, check_same_thread=False)
		c = conn.cursor()

		c.execute('''
			CREATE TABLE IF NOT EXISTS Accounts (
				accountID INTEGER NOT NULL PRIMARY KEY UNIQUE,
				username TEXT NOT NULL UNIQUE,
				password TEXT NOT NULL,
				firstName TEXT NOT NULL,
				middleInitial TEXT,
				lastName TEXT NOT NULL,
				phoneNumber TEXT,
				email TEXT NOT NULL
			);
		''')

		admin_account = [
			"admin",
			sha256(b"password").hexdigest(),
			"admin",
			"i",
			"strator",
			"1234567890",
			"admin@ecommerce.com"
		]

		# create initial admin account
		c.execute('''
			INSERT INTO Accounts
			(username, password, firstName, middleInitial, lastName, phoneNumber, email)
			VALUES(?, ?, ?, ?, ?, ?, ?);
		''', admin_account)
		conn.commit()
		conn.close()

	def create_admins_table(self):
		conn = sqlite3.connect(self.database_uri, check_same_thread=False)
		c = conn.cursor()

		c.execute('''
			CREATE TABLE IF NOT EXISTS Admins (
				accountID INTEGER NOT NULL PRIMARY KEY,
				FOREIGN KEY(accountID) REFERENCES Accounts(accountID)
				ON DELETE CASCADE
			);
		''')

		# insert initial admin account to admin table
		c.execute('''
			INSERT INTO Admins(accountID)
			SELECT accountID
			FROM Accounts WHERE username = "admin";
		''')
		conn.commit()
		conn.close()

	def create_customers_table(self):
		conn = sqlite3.connect(self.database_uri, check_same_thread=False)
		c = conn.cursor()

		c.execute('''
			CREATE TABLE IF NOT EXISTS Customers (
				accountID INTEGER NOT NULL PRIMARY KEY,
				billingAddress TEXT,
				billingCity TEXT,
				billingState TEXT,
				billingPostalCode TEXT,
				shippingAddress TEXT,
				shippingCity TEXT,
				shippingState TEXT,
				shippingPostalCode TEXT,
				accountCreationDate TEXT,
				cartID TEXT,
				FOREIGN KEY(accountID) REFERENCES Accounts(accountID)
				ON DELETE CASCADE
			);
		''')
		conn.commit()
		conn.close()

	def create_categories_table(self):
		conn = sqlite3.connect(self.database_uri, check_same_thread=False)
		c = conn.cursor()

		c.execute('''
			CREATE TABLE IF NOT EXISTS Categories (
				categoryID INTEGER NOT NULL PRIMARY KEY,
				categoryName TEXT
			);
		''')
		conn.commit()
		conn.close()

	def create_products_table(self):
		conn = sqlite3.connect(self.database_uri, check_same_thread=False)
		c = conn.cursor()

		c.execute('''
			CREATE TABLE IF NOT EXISTS Products (
				productID INTEGER NOT NULL PRIMARY KEY,
				categoryID INTEGER,
				name TEXT,
				description TEXT,
				imageURL TEXT,
				price INTEGER,
				quantityAvailable INTEGER,
				FOREIGN KEY(categoryID) REFERENCES Categories(categoryID)
				ON DELETE CASCADE
			);
		''')
		conn.commit()
		conn.close()

	def create_orders_table(self):
		conn = sqlite3.connect(self.database_uri, check_same_thread=False)
		c = conn.cursor()

		c.execute('''
			CREATE TABLE IF NOT EXISTS Orders (
				orderID INTEGER NOT NULL PRIMARY KEY,
				accountID INTEGER,
				dateOrdered DATETIME,
				billingAddress TEXT,
				billingCity TEXT,
				billingState TEXT,
				billingPostalCode TEXT,
				shippingAddress TEXT,
				shippingCity TEXT,
				shippingState TEXT,
				shippingPostalCode TEXT,
				taxCost INTEGER,
				shippingCost INTEGER,
				totalCost INTEGER,
				FOREIGN KEY(accountID) REFERENCES Accounts(accountID)
				ON DELETE CASCADE
			);
		''')
		conn.commit()
		conn.close()

	def create_order_details_table(self):
		conn = sqlite3.connect(self.database_uri, check_same_thread=False)
		c = conn.cursor()

		c.execute('''
			CREATE TABLE IF NOT EXISTS OrderDetails (
				orderDetailID INTEGER NOT NULL PRIMARY KEY,
				orderID INTEGER,
				productID INTEGER,
				name TEXT,
				description TEXT,
				price INTEGER,
				quantity INTEGER
			);
		''')
		conn.commit()
		conn.close()

	def create_carts_table(self):
		conn = sqlite3.connect(self.database_uri, check_same_thread=False)
		c = conn.cursor()

		c.execute('''
			CREATE TABLE IF NOT EXISTS Carts (
				cartID INTEGER NOT NULL PRIMARY KEY,
				accountID INTEGER,
				FOREIGN KEY(accountID) REFERENCES Accounts(accountID)
				ON DELETE CASCADE
			);
		''')
		conn.commit()
		conn.close()

	def create_cart_details_table(self):
		conn = sqlite3.connect(self.database_uri, check_same_thread=False)
		c = conn.cursor()

		c.execute('''
			CREATE TABLE IF NOT EXISTS CartDetails (
				cartDetailID INTEGER NOT NULL PRIMARY KEY,
				cartID INTEGER,
				productID INTEGER,
				quantity INTEGER,
				FOREIGN KEY(cartID) REFERENCES Carts(cartID)
				ON DELETE CASCADE,
				FOREIGN KEY(productID) REFERENCES Products(productID)
				ON DELETE CASCADE
			);
		''')
		conn.commit()
		conn.close()

	def initialize_database(self):
		self.create_accounts_table()
		self.create_admins_table()
		self.create_customers_table()
		self.create_categories_table()
		self.create_products_table()
		self.create_orders_table()
		self.create_order_details_table()
		self.create_carts_table()
		self.create_cart_details_table()
