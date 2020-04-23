import sqlite3
from hashlib import sha256


class Database(object):
	database_uri = None
	conn = None

	def __init__(self, database_uri):
		self.database_uri = database_uri

	def open_connection(self):
		self.conn = sqlite3.connect(self.database_uri, check_same_thread=False)

	def close_connection(self):
		self.conn.close()

	def account_exists(self, username):
		c = self.conn.cursor()

		c.execute('''
			SELECT * FROM Accounts WHERE username = ?;
		''', (username,))

		return c.fetchone() is not None

	def find_credentials(self, credentials):
		c = self.conn.cursor()

		username = credentials.get("username")
		password = sha256(credentials.get("password").encode()).hexdigest()

		c.execute('''
			SELECT * FROM Accounts WHERE username = ? and password = ?;
		''', (username, password,))

		return c.fetchone() is not None

	def get_role(self, username):
		c = self.conn.cursor()

		c.execute('''
			SELECT * FROM Admins
			JOIN Accounts
			ON Admins.accountID = Accounts.accountID
			WHERE username = ?;
		''', (username,))

		if c.fetchone() is not None:
			return "admin"
		else:
			return "customer"

	def get_products(self):
		c = self.conn.cursor()

		c.execute('''
			SELECT * FROM Products;
		''')

		column_names = next(zip(*c.description))
		product_rows = c.fetchall()

		products = [dict(zip(column_names, product_values)) for product_values in product_rows]

		return products

	def add_category(self, category_name):
		c = self.conn.cursor()

		c.execute('''
			INSERT INTO Categories(categoryName)
			VALUES(?);
		''', (category_name,))

		self.conn.commit()

	def add_product(self, product):
		c = self.conn.cursor()

		product_details = [
			product.get("categoryID"),
			product.get("name"),
			product.get("description"),
			product.get("imageURL"),
			product.get("price"),
			product.get("quantityAvailable"),
		]

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

		self.conn.commit()

	# TODO this whole function could probably be enhanced/made more efficient using some more advanced sql
	def add_order(self, order):
		c = self.conn.cursor()

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

		account_shipping_and_billing = c.fetchone()

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

		tax_cost = int(order_product_sum * tax_rate)

		total_cost = order_product_sum + tax_cost

		shipping_cost = 0  # free shipping

		c.execute('''
			UPDATE Orders
			SET
			taxCost = ?,
			shippingCost = ?,
			totalCost = ?
			WHERE orderID = ?;
		''', (tax_cost, shipping_cost, total_cost, order_id,))

		self.conn.commit()

	def update_cart(self, cart):
		# get account id, and cart id
		c = self.conn.cursor()

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
			(cart_id, cartDetail["quantity"], cartDetail["productID"])
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
		self.conn.commit()

	def add_customer(self, account):
		c = self.conn.cursor()

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

		self.conn.commit()

	def create_accounts_table(self):
		c = self.conn.cursor()

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

	def create_admins_table(self):
		c = self.conn.cursor()

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

	def create_customers_table(self):
		c = self.conn.cursor()

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

	def create_categories_table(self):
		c = self.conn.cursor()

		c.execute('''
			CREATE TABLE IF NOT EXISTS Categories (
				categoryID INTEGER NOT NULL PRIMARY KEY,
				categoryName TEXT
			);
		''')

	def create_products_table(self):
		c = self.conn.cursor()

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

	def create_orders_table(self):
		c = self.conn.cursor()

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

	def create_order_details_table(self):
		c = self.conn.cursor()

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

	def create_carts_table(self):
		c = self.conn.cursor()

		c.execute('''
			CREATE TABLE IF NOT EXISTS Carts (
				cartID INTEGER NOT NULL PRIMARY KEY,
				accountID INTEGER,
				FOREIGN KEY(accountID) REFERENCES Accounts(accountID)
				ON DELETE CASCADE
			);
		''')

	def create_cart_details_table(self):
		c = self.conn.cursor()

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
		self.conn.commit()
