import unittest
from data_validator import valid_account_data, valid_credentials_data, valid_order_data

class DataValidatorTest(unittest.TestCase):

	def test_valid_account_data_with_schema_unmatched(self):
		account = {"username":"test"}
		
		self.assertFalse(valid_account_data(account))


	def test_valid_account_data_with_schema_matched(self):
		account = {
			"username": "firstUser",
			"password": "p@55w0rd",
			"email": "name@email.com",
			"firstName": "john",
			"middleInitial": "m",
			"lastName": "smith",
			"phoneNumber": "123-456-7890"
		}

		self.assertTrue(valid_account_data(account))


	def test_valid_credentials_data_with_schema_unmatched(self):
		credentials = {"username":"test"}
		
		self.assertFalse(valid_credentials_data(credentials))


	def test_valid_credentials_data_with_schema_matched(self):
		credentials = {
			"username": "firstUser",
			"password": "p@55w0rd",
		}

		self.assertTrue(valid_credentials_data(credentials))


	def test_valid_order_data_with_schema_unmatched(self):
		order = {
			"orderDetails": [
				{
					"quantity": 1
				}
			]
		}
		
		self.assertFalse(valid_order_data(order))


	def test_valid_order_data_with_schema_matched(self):
		order = {
			"orderDetails": [
				{
					"quantity": 1,
					"productID": 0
				},
				{
					"quantity": 2,
					"productID": 3
				}
			]
		}
		
		self.assertTrue(valid_order_data(order))

if __name__ == '__main__':
	unittest.main()
