'use strict';

var application = angular
	.module("account", ["ngCookies"])
	.config(function($locationProvider) {
		$locationProvider.html5Mode({
			enabled: true,
			requireBase: true,
			rewriteLinks: false
		});
	});

application.controller("accountController", function($scope, $http, $window, $cookies, $location) {

	$scope.orders = [];

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
		$scope.setOrders();
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

	$scope.setOrders = function() {
		console.log($scope.user);

		var token = $cookies.get("jwt");

		$http.get("/api/users/" + $scope.user.username + "/orders", {headers: {'Authorization': token}})
		.then(
			(response) => {
				$scope.orders = response.data;
				console.log(response);
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

	$scope.signOut = function() {
		$cookies.remove("jwt");
		$cookies.remove("cart");
		alert("signing out!");
		$window.location.href = 'index.html';
	}

});