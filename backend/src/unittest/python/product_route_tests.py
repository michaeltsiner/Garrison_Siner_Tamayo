import os
import unittest
from unittest.mock import patch
from app import app
from database import Database

class ProductRouteTest(unittest.TestCase):

	sample_product = {
		"categoryID": 0,
		"description": "typing tool",
		"imageURL": "null",
		"name": "keyboard",
		"price": 1500,
		"productID": 1,
		"quantityAvailable": 50
	}

	def setUp(self):
		self.app = app.test_client()
		self.app.testing = True
		self.mock_db = patch("app.db")
		self.mock_db.start()

	def tearDown(self):
		self.mock_db.stop()

	@patch("app.db.get_products", return_value=[])
	def test_get_products_with_none_in_database(self, mocked_get_products):
		result = self.app.get("/api/products").data.decode()
		expected = '[]\n'
		
		self.assertEqual(result, expected)


	@patch("app.db.get_products", return_value=sample_product)
	def test_get_products_with_one_in_database(self, mocked_get_products):
		result = self.app.get("/api/products").data.decode()
		expected = '{"categoryID":0,"description":"typing tool","imageURL":"null","name":"keyboard","price":1500,"productID":1,"quantityAvailable":50}\n'
		
		self.assertEqual(result, expected)


if __name__ == '__main__':
	unittest.main()
