from jsonschema import validate
from jsonschema.exceptions import ValidationError

account_schema = {
	"type": "object",
	"required": [
		"username",
		"password",
		"email",
		"firstName",
		"lastName"
	],
	"properties": {
		"username": {
			"type": "string"
		},
		"password": {
			"type": "string"
		},
		"email": {
			"type": "string",
			"format": "email"
		},
		"firstName": {
			"type": "string"
		},
		"middleInitial": {
			"type": "string"
		},
		"lastName": {
			"type": "string"
		},
		"phoneNumber": {
			"type": "string"
		}
	}
}

credentials_schema = {
	"type": "object",
	"required": [
		"username",
		"password"
	],
	"properties": {
		"username": {
			"type": "string"
		},
		"password": {
			"type": "string"
		}
	}
}

order_schema = {
	"type": "object",
	"required": [
		"orderDetails"
	],
	"properties": {
		"orderDetails": {
			"type": "array",
			"items": {
				"type": "object",
				"required": [
					"productID",
					"quantity"
				],
				"properties": {
					"productID": {
						"type": "number"
					},
					"quantity": {
						"type": "number"
					}
				}
			}
		}
	}
}


def valid_credentials_data(credentials):
	try:
		validate(instance=credentials, schema=credentials_schema)
		return True
	except ValidationError:
		return False


def valid_account_data(account):
	try:
		validate(instance=account, schema=account_schema)
		return True
	except ValidationError:
		return False


def valid_order_data(order):
	try:
		validate(instance=order, schema=order_schema)
		return True
	except ValidationError:
		return False
