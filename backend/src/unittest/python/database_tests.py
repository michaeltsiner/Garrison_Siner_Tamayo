import unittest
from database import Database
import os

class DatabaseTest(unittest.TestCase):

	def setUp(self):
		self.db = Database("test.db")
		self.account = {
			"username": "firstUser",
			"password": "p@55w0rd",
			"email": "name@email.com",
			"firstName": "john",
			"lastName": "smith",
			"phoneNumber": "123-456-7890"
		}
		self.db.initialize_database()


	def tearDown(self):
		os.remove("test.db")


	def test_account_exists_with_nonexisting_account(self):
		self.assertFalse(self.db.account_exists("someAccountThatsNotReal"))


	def test_account_exists_with_existing_account(self):
		account = self.account

		self.db.add_customer(account)
		self.assertTrue(self.db.account_exists(account["username"]))


	def test_add_customer(self):
		account = self.account

		self.db.add_customer(account)
		
		self.assertTrue(self.db.account_exists(account["username"]))


	def test_find_credentials_with_non_existing_credentials(self):
		credentials = self.account
		
		self.assertFalse(self.db.find_credentials(credentials))


	def test_find_credentials_with_non_existing_credentials(self):
		credentials = self.account
		self.db.add_customer(self.account)

		self.assertTrue(self.db.find_credentials(credentials))


	def test_get_role_with_admin_account(self):
		self.assertEqual("admin", self.db.get_role("admin"))


	def test_get_role_with_customer_account(self):
		account = self.account
		self.db.add_customer(account)
		
		self.assertEqual("customer", self.db.get_role("firstUser"))


	def test_get_products_with_no_products_in_database(self):
		result = self.db.get_products()
		expected = []
		
		self.assertEqual(result, expected)

	def test_get_categories_with_no_products_in_database(self):
		result = self.db.get_categories()
		expected = []
		
		self.assertEqual(result, expected)

# TODO add tests for add_category, add_product

	def test_add_order_with_one_order(self):
		self.db.add_customer(self.account)
		self.db.add_category("food")
		sample_product = {
			"categoryID": 1,
			"name" : "apple",
			"description": "edible fruit",
			"imageURL" : None,
			"price" : 100,
			"quantityAvailable" : 50
		}
		self.db.add_product(sample_product)

		order = {
			"username": "firstUser",
			"orderDetails": [
				{
					"productID": 1,
					"quantity": 2
				}
			]
		}

		result = self.db.add_order(order)
		
		self.assertIsNone(result)


	def test_update_cart_with_no_previous_cart(self):
		self.db.add_customer(self.account)
		sample_cart = {
			"username": "firstUser",
			"orderDetails": [
				{
					"productID": 1,
					"quantity": 2
				}
			]
		}

		expected = {
			"orderDetails": [
				{
					"productID": 1,
					"quantity": 2
				}
			]
		}

		self.db.update_cart(sample_cart)

		result = self.db.get_cart("firstUser")

		self.assertEqual(expected, result)


	def test_update_cart_with_previous_cart(self):
		self.db.add_customer(self.account)
		sample_cart = {
			"username": "firstUser",
			"orderDetails": [
				{
					"productID": 1,
					"quantity": 2
				}
			]
		}

		self.db.update_cart(sample_cart)

		sample_cart_2 = {
			"username": "firstUser",
			"orderDetails": [
				{
					"productID": 3,
					"quantity": 7
				}
			]
		}

		self.db.update_cart(sample_cart_2)

		expected = {
			"orderDetails": [
				{
					"productID": 3,
					"quantity": 7
				}
			]
		}

		result = self.db.get_cart("firstUser")

		self.assertEqual(expected, result)


	def test_get_cart_with_no_previous_cart(self):
		self.db.add_customer(self.account)
		
		result = self.db.get_cart(self.account["username"])
		expected = {'orderDetails': []}

		self.assertEqual(expected, result)


	def test_get_cart_with_previous_cart(self):
		self.db.add_customer(self.account)
		

		sample_cart= {
			"username": "firstUser",
			"orderDetails": [
				{
					"productID": 1,
					"quantity": 2
				}
			]
		}

		self.db.update_cart(sample_cart)

		expected = {
			"orderDetails": [
				{
					"productID": 1,
					"quantity": 2
				}
			]
		}

		result = self.db.get_cart(self.account["username"])

		self.assertEqual(expected, result)


	def test_get_user_orders_empty(self):
		self.db.add_customer(self.account)

		result = self.db.get_user_orders("firstUser")
		expected = []

		self.assertEqual(expected, result)

	def test_get_user_orders_one_order(self):
		self.db.add_customer(self.account)

		self.db.add_category("food")
		sample_product = {
			"categoryID": 1,
			"name" : "apple",
			"description": "edible fruit",
			"imageURL" : None,
			"price" : 100,
			"quantityAvailable" : 50
		}
		self.db.add_product(sample_product)

		sample_order = {
			"username": "firstUser",
			"orderDetails": [
				{
					"productID": 1,
					"quantity": 2
				}
			]
		}

		self.db.add_order(sample_order)

		result = self.db.get_user_orders("firstUser")

		# remove date ordered otherwise can't compare result and expected result
		del result[0]["dateOrdered"]

		expected = [
			{
				'orderID': 1,
				'accountID': 2,
				'billingAddress': None,
				'billingCity': None,
				'billingPostalCode': None,
				'billingState': None,
				'items': [
					{
						'description': 'edible fruit',
						'name': 'apple',
						'orderDetailID': 1,
						'orderID': 1,
						'price': 100,
						'productID': 1,
						'quantity': 2
					}
				],
				'shippingAddress': None,
				'shippingCity': None,
				'shippingCost': 0,
				'shippingPostalCode': None,
				'shippingState': None,
				'taxCost': 16,
				'totalCost': 216
				}
		]

		self.assertEqual(expected, result)


if __name__ == '__main__':
	unittest.main()
