import os
import unittest
from unittest.mock import patch
from app import app
from database import Database

class AccountRouteTest(unittest.TestCase):

	def setUp(self):
		self.app = app.test_client()
		self.app.testing = True
		self.invalid_account = {"invalid":True}
		self.valid_account = {
			"username": "firstUser",
			"password": "p@55w0rd",
			"email": "name@email.com",
			"firstName": "john",
			"middleInitial": "m",
			"lastName": "smith",
			"phoneNumber": "123-456-7890"
		}
		self.mock_db = patch("app.db")
		self.mock_db.start()


	def tearDown(self):
		self.mock_db.stop()


	def test_create_customer_account_with_missing_fields(self):
		result = self.app.post("/api/users").data.decode()
		expected = '{"msg":"no/invalid json data or missing json content type header"}\n'
		
		self.assertEqual(result, expected)


	@patch("app.valid_account_data", return_value=False)
	def test_create_customer_account_with_invalid_account_data(self, mocked_valid_account_data):
		account = self.invalid_account

		result = self.app.post("/api/users", json=account).data.decode()
		expected = '{"msg":"no/invalid json data or missing json content type header"}\n'
		
		self.assertEqual(result, expected)


	@patch("app.valid_account_data", return_value=True)
	@patch("app.db.account_exists", return_value=True)
	def test_create_customer_account_but_username_is_taken(self, mocked_account_exists, mocked_valid_account_data):
		account = self.valid_account

		result = self.app.post("/api/users", json=account).data.decode()
		expected = '{"msg":"could not create account, username taken"}\n'

		self.assertEqual(result, expected)


	@patch("app.valid_account_data", return_value=True)
	@patch("app.db.account_exists", return_value=False)
	def test_create_customer_account_succesfully(self, mocked_account_exists, mocked_valid_account_data):
		account = self.valid_account

		result = self.app.post("/api/users", json=account).data.decode()
		expected = '{"msg":"account created"}\n'

		self.assertEqual(result, expected)


	def test_static_page(self):
		result = self.app.get("/").data.decode()
		self.assertIn("html", result)


if __name__ == '__main__':
	unittest.main()
