import os
import unittest
from unittest.mock import patch
from app import app
from database import Database

class AccountRouteTest(unittest.TestCase):

	def setUp(self):
		self.app = app.test_client()
		self.app.testing = True
		self.invalid_credentials = {"invalid":True}
		self.valid_credentials = {
			"username": "firstUser",
			"password": "p@55w0rd"
		}
		self.mock_db = patch("app.db")
		self.mock_db.start()


	def tearDown(self):
		self.mock_db.stop()


	def test_authenticate_user_with_missing_fields(self):
		result = self.app.post("/api/auth").data.decode()
		expected = '{"msg":"no/invalid json data or missing json content type header"}\n'
		
		self.assertEqual(result, expected)


	@patch("app.valid_credentials_data", return_value=False)
	def test_authenticate_user_invalid_credentials_data(self, mocked_valid_credentials_data):
		credentials = self.invalid_credentials

		result = self.app.post("/api/auth", json=credentials).data.decode()
		expected = '{"msg":"no/invalid json data or missing json content type header"}\n'
		
		self.assertEqual(result, expected)


	@patch("app.db.find_credentials", return_value=False)
	@patch("app.valid_credentials_data", return_value=True)
	def test_authenticate_user_with_credentials_not_found(self, mocked_valid_credentials_data, mocked_find_credentials):
		credentials = self.valid_credentials

		result = self.app.post("/api/auth", json=credentials).data.decode()
		
		self.assertIn("username or password is invalid", result)


	@patch("app.db.find_credentials", return_value=True)
	@patch("app.valid_credentials_data", return_value=True)
	def test_authenticate_user_with_credentials_found(self, mocked_valid_credentials_data, mocked_find_credentials):
		credentials = self.valid_credentials

		result = self.app.post("/api/auth", json=credentials).data.decode()
		
		self.assertIn("successfuly authenticated", result)


	def test_token_protected_with_no_authorization_headers(self):
		result = self.app.get("/protected").data.decode()

		self.assertIn("missing token", result)


	@patch("app.jwt.decode", side_effect=Exception)
	def test_token_protected_with_invalid_token(self, mocked_decode):
		result = self.app.get(
			"/protected",
			headers={"authorization": "token"}
			).data.decode()

		self.assertIn("invalid token", result)


	@patch("app.jwt.decode", side_effect=None)
	def test_token_protected_with_valid_token(self, mocked_decode):
		result = self.app.get(
			"/protected",
			headers={"authorization": "token"}
			).data.decode()

		self.assertIn("protected content", result)


if __name__ == '__main__':
	unittest.main()
