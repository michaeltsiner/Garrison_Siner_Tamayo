'use strict';

var application = angular
	.module("cart", ["ngCookies"])
	.config(function($locationProvider) {
		$locationProvider.html5Mode({
			enabled: true,
			requireBase: true,
			rewriteLinks: false
		});
	});


application.controller("cartController", function($scope, $http, $window, $cookies) {

	$scope.categories = [];

	$scope.account = {
		"link" : "/login.html",
		"message" : "Login/Register"
	};

	$scope.cart = {
		"orderDetails" : []
	}

	$scope.products = [];

	$scope.cartItems = [];

	$scope.user = undefined;

	$scope.initialize = function() {
		$scope.setUser();
		$scope.setProducts()

	}


	$scope.userIsAuthenticated = function() {
		var token = $cookies.get("jwt");

		if(token == undefined) {
			return false;
		}else{
			$scope.user = JSON.parse(atob(token.split(".")[1]));

			return true;			
		}
	}

	$scope.numberOfCartItems = function() {
		var count = 0;

		$scope.cart.orderDetails.forEach(cartItem => count += cartItem.quantity);

		return count;
	}

	$scope.setUser = function(){
		if ($scope.userIsAuthenticated()) {
			$scope.account = {
				"link" : "/account.html",
				"message" : "My Account"
			};

			var token = $cookies.get("jwt");

			$http.get("/api/carts", {headers: {'Authorization': token}})
			.then(
				(response) => {
					$cookies.put("cart", JSON.stringify(response.data));
					$scope.cart =  JSON.parse($cookies.get("cart"));
				},
				(error) => {
					console.log(error);
				}
			);

		}else {
			if ($cookies.get("cart") == undefined) {
				$cookies.put("cart", JSON.stringify($scope.cart));
			}

			$scope.cart = JSON.parse($cookies.get("cart"));
		}
	}

	$scope.setProducts = function() {
		$http.get("/api/products")
		.then(
			(response) => {
				$scope.products = response.data

				for (var i = $scope.cart.orderDetails.length - 1; i >= 0; i--) {
					var product = $scope.products
						.filter(product => { 
							return product.productID == $scope.cart.orderDetails[i].productID;
						})[0];

					$scope.cart.orderDetails[i] = {...$scope.cart.orderDetails[i], ...product};
				}
			},
			(error) => {
				console.log(error);
			}
		);
	}

	$scope.reduceQuantity = function(productID) {
		for (var i = $scope.cart.orderDetails.length - 1; i >= 0; i--) {
			if ($scope.cart.orderDetails[i].productID == productID && $scope.cart.orderDetails[i].quantity != 0) {
				$scope.cart.orderDetails[i].quantity -= 1;
			}
		}

		$cookies.put("cart", JSON.stringify($scope.cart));

		if ($scope.userIsAuthenticated()) {
			var token = $cookies.get("jwt");

			$http.post("/api/carts", $scope.cart, {headers: {'Authorization': token}})
			.then(
				(response) => {
					console.log(response);
					console.log("updated cart");
				},
				(error) => {
					console.log(error);
				}
			);
		}else{
			console.log("not authenticated");
		}
	}

	$scope.addQuantity = function(productID) {
		for (var i = $scope.cart.orderDetails.length - 1; i >= 0; i--) {
			if ($scope.cart.orderDetails[i].productID == productID) {
				$scope.cart.orderDetails[i].quantity += 1;
			}
		}

		$cookies.put("cart", JSON.stringify($scope.cart));

		if ($scope.userIsAuthenticated()) {
			var token = $cookies.get("jwt");

			$http.post("/api/carts", $scope.cart, {headers: {'Authorization': token}})
			.then(
				(response) => {
					console.log(response);
					console.log("updated cart");
				},
				(error) => {
					console.log(error);
				}
			);
		}else{
			console.log("not authenticated");
		}
	}

	$scope.cartTax = function() {
		return Math.floor($scope.cartTotal() * 0.0825);
	}

	$scope.cartTotal = function() {
		var total = 0;
		$scope.cart.orderDetails.forEach(product => total += product.price * product.quantity);
		return total;
	}

	$scope.total = function() {
		return $scope.cartTotal() + $scope.cartTax();
	}

	$scope.goToCheckout = function(category) {
		if ($scope.numberOfCartItems() == 0) {
			alert("can't checkout with 0 items");
		}else{
			$window.location.href = "checkout.html";
		}
	}


	$scope.signOut = function() {
		$cookies.remove("jwt");
		$cookies.remove("cart");
		alert("signing out!");
		$window.location.href = 'index.html';
	}

});