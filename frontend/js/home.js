'use strict';

var application = angular
	.module("home", ["ngCookies"])
	.config(function($locationProvider) {
		$locationProvider.html5Mode({
			enabled: true,
			requireBase: true,
			rewriteLinks: false
		});
	});


application.controller("homeController", function($scope, $http, $window, $cookies) {

	$scope.categories = [];

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
		$scope.setCategories();
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

	$scope.numberOfCartItems = function() {
		var count = 0;

		$scope.cart.orderDetails.forEach(cartItem => count += cartItem.quantity);

		return count;
	}

	$scope.setCategories = function() {
		$http.get("/api/categories")
		.then(
			(response) => {
				$scope.categories = response.data;
			},
			(error) => {
				console.log(error);
			}
		);
	}

	$scope.viewCategoryProducts = function(category) {
		$window.location.href = "products.html?categoryID=" + category.categoryID;
	}

	$scope.signOut = function() {
		$cookies.remove("jwt");
		$cookies.remove("cart");
		alert("signing out!");
		$window.location.href = 'index.html';
	}

});