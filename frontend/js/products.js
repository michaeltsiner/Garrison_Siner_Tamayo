'use strict';

var application = angular
	.module("products", ["ngCookies"])
	.config(function($locationProvider) {
		$locationProvider.html5Mode({
			enabled: true,
			requireBase: true,
			rewriteLinks: false
		});
	});

application.controller("productsController", function($scope, $http, $window, $cookies, $location) {

	$scope.products = [];

	$scope.account = {
		"link" : "/login.html",
		"message" : "Login/Register"
	};

	$scope.cart = {
		"orderDetails" : []
	}

	$scope.user = undefined;

	$scope.initialize = function() {
		$scope.setUser();
		$scope.setProducts();
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

				if ($location.search().categoryID != undefined) {
					$scope.products = response.data
						.filter((product) => { 
							return product.categoryID == $location.search().categoryID;
						});
				}

			},
			(error) => {
				console.log(error);
			}
		);
	}

	$scope.numberOfCartItems = function() {
		var count = 0;

		$scope.cart.orderDetails.forEach(cartItem => count += cartItem.quantity);

		return count;
	}

	$scope.addToCart = function(product) {
		var item = {
			"productID" : product.productID,
			"quantity" : 1 
		};

		var itemInCart = false;


		for(var i in $scope.cart.orderDetails) {
			console.log(i);
			if ($scope.cart.orderDetails[i].productID == item.productID) {
				$scope.cart.orderDetails[i].quantity += 1;
				itemInCart = true;
				break;
			}
		}

		if (!itemInCart) {
			$scope.cart.orderDetails.push(item);
		}

		$cookies.put("cart", JSON.stringify($scope.cart));

		console.log("adding to cart");

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

		console.log($scope.cart);

		console.log($scope.numberOfCartItems());

	}


	$scope.signOut = function() {
		$cookies.remove("jwt");
		$cookies.remove("cart");
		alert("signing out!");
		$window.location.href = 'index.html';
	}

});