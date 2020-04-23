'use strict';

var application = angular
	.module("checkout", ["ngCookies"])
	.config(function($locationProvider) {
		$locationProvider.html5Mode({
			enabled: true,
			requireBase: true,
			rewriteLinks: false
		});
	});


application.controller("checkoutController", function($scope, $http, $window, $cookies) {

	$scope.address = {};

	$scope.categories = [];

	$scope.account = {
		"link" : "/login.html",
		"message" : "Login/Register"
	};

	$scope.cart = {
		"orderDetails" : []
	}

	$scope.order = {};

	$scope.user = undefined;

	$scope.initialize = function() {
		$scope.setUser();
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

			alert("must be logged in to checkout! redirecting to login page")

			$window.location.href = 'login.html';

		}
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

	$scope.sendOrder = function() {

		$scope.order.orderDetails = $scope.cart.orderDetails;
		$scope.order = {...$scope.order, ...$scope.address};

		console.log($scope.order);
		console.log("sending order");

		var token = $cookies.get("jwt");

		$http.post("/api/orders", $scope.order, {headers: {'Content-Type': 'application/json', 'Authorization': token}})
		.then(
			(response) => {
				alert("successfully created order, redirecting back to home page");
				$window.location.href = 'index.html';
			},
			(response) => {
				alert(response.data.msg);
			}
		);		

	}

});