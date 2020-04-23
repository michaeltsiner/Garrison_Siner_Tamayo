import os
import unittest
from unittest.mock import patch
from app import app
from database import Database

class CategoryRouteTest(unittest.TestCase):

	sample_category = {
		"categoryName": "tool"
	}

	def setUp(self):
		self.app = app.test_client()
		self.app.testing = True
		self.mock_db = patch("app.db")
		self.mock_db.start()

	def tearDown(self):
		self.mock_db.stop()

	@patch("app.db.get_categories", return_value=[])
	def test_get_categories_with_none_in_database(self, mocked_get_products):
		result = self.app.get("/api/categories").data.decode()
		expected = '[]\n'
		
		self.assertEqual(result, expected)


	@patch("app.db.get_categories", return_value=sample_category)
	def test_get_products_with_one_in_database(self, mocked_get_products):
		result = self.app.get("/api/categories").data.decode()
		expected = '{"categoryName":"tool"}\n'
		
		self.assertEqual(result, expected)


if __name__ == '__main__':
	unittest.main()
