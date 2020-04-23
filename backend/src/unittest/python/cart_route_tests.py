import os
import unittest
import jwt
from unittest.mock import patch
from app import app
from database import Database

class CartRouteTest(unittest.TestCase):

	def setUp(self):
		self.app = app.test_client()
		self.app.testing = True
		self.mock_db = patch("app.db")
		self.mock_db.start()
		self.username = "testuser"

		self.token = jwt.encode(
			{
				"username": self.username
			},
			app.config["SECRET_KEY"]
		)


	def tearDown(self):
		self.mock_db.stop()


	@patch("app.valid_order_data", return_value=False)
	def test_update_cart_with_invalid_cart(self, mocked_valid_order_data):

		result = self.app.post(
			"/api/carts", 
			json={"valid":False},
			headers={"Authorization": self.token}
			).data.decode()

		expected = '{"msg":"no/invalid json data or missing json content type header"}\n'

		self.assertEqual(result, expected)


	@patch("app.valid_order_data", return_value=True)
	def test_update_cart_with_valid_cart(self, mocked_valid_order_data):

		result = self.app.post(
			"/api/carts", 
			json={"valid":True},
			headers={"Authorization": self.token}
			).data.decode()
		expected = '{"msg":"successfuly updated cart"}\n'

		self.assertEqual(result, expected)

	@patch("app.db.get_cart", return_value= {"orderDetails": []})
	def test_get_cart_with_empty_user_cart(self, mocked_db_get_cart):

		result = self.app.get(
			"/api/carts",
			headers={"Authorization": self.token}
			).data.decode()

		expected = '{"orderDetails":[],"username":"testuser"}\n'

		self.assertEqual(result, expected)


if __name__ == '__main__':
	unittest.main()
