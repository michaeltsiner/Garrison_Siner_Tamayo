import os
import unittest
import jwt
from unittest.mock import patch
from app import app
from database import Database

class OrderRouteTest(unittest.TestCase):

	def setUp(self):
		self.app = app.test_client()
		self.app.testing = True
		self.mock_db = patch("app.db")
		self.mock_db.start()

		self.token = jwt.encode(
			{
				"username": "testuser"
			},
			app.config["SECRET_KEY"]
		)


	def tearDown(self):
		self.mock_db.stop()


	@patch("app.valid_order_data", return_value=False)
	def test_send_order_with_invalid_order(self, mocked_valid_order_data):

		result = self.app.post(
			"/api/orders", 
			json={"valid":False},
			headers={"Authorization": self.token}
			).data.decode()

		expected = '{"msg":"no/invalid json data or missing json content type header"}\n'

		self.assertEqual(result, expected)


	@patch("app.valid_order_data", return_value=True)
	def test_send_order_with_valid_order(self, mocked_valid_order_data):

		result = self.app.post(
			"/api/orders", 
			json={"valid":True},
			headers={"Authorization": self.token}
			).data.decode()
		expected = '{"msg":"successfuly created order"}\n'

		self.assertEqual(result, expected)

	@patch("app.valid_order_data", return_value=True)
	@patch("app.db.address_is_valid", return_value=False)
	def test_send_order_with_invalid_address(self, mocked_address_is_valid, mocked_valid_order_data):

		result = self.app.post(
			"/api/orders", 
			json={"valid":False},
			headers={"Authorization": self.token}
			).data.decode()

		expected = '{"msg":"address is invalid"}\n'

		self.assertEqual(result, expected)

	@patch("app.db.get_user_orders", return_value=[])
	def test_get_orders(self, mocked_db_get_orders):

		result = self.app.get(
			"/api/users/testuser/orders",
			headers={"Authorization": self.token}
			).data.decode()

		expected = '[]\n'

		self.assertEqual(result, expected)

	def test_get_orders_unauthorized(self):

		result = self.app.get(
			"/api/users/admin/orders",
			headers={"Authorization": self.token}
			).data.decode()

		expected = '{"msg":"unauthorized"}\n'

		self.assertEqual(result, expected)


if __name__ == '__main__':
	unittest.main()
