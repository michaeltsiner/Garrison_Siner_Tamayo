'use strict';

var application = angular
	.module("admin", ["ngCookies"])
	.config(function($locationProvider) {
		$locationProvider.html5Mode({
			enabled: true,
			requireBase: true,
			rewriteLinks: false
		});
	});


application.controller("adminController", function($scope, $http, $window, $cookies) {

	$scope.user = undefined;
	$scope.action = "viewOrders";
	$scope.newCategory = {};
	$scope.newProduct = {};
	$scope.orders = [];
	$scope.categories = [];

	$scope.initialize = function() {
		$scope.userIsAuthenticated();
		$scope.setCategories();
	}

	$scope.getAllOrders = function() {
		var token = $cookies.get("jwt");
		$http.get("/api/orders", {headers: {'Authorization': token}})
		.then(
			(response) => {
				$scope.orders =  response.data;
			},
			(error) => {
				console.log(error);
			}
		);
		console.log($scope.orders);
	}

	$scope.addCategory = function() {
		var token = $cookies.get("jwt");
		$http.post("/api/categories", $scope.newCategory, {headers: {'Authorization': token}})
		.then(
			(response) => {
				console.log(response);
				alert("added category!");
			},
			(error) => {
				console.log(error);
			}
		);
	}

	$scope.addProduct = function() {
		console.log("adding product");
		console.log($scope.newProduct);
		var token = $cookies.get("jwt");
		$http.post("/api/products", $scope.newProduct, {headers: {'Authorization': token}})
		.then(
			(response) => {
				console.log(response);
				alert("added product!");
			},
			(error) => {
				console.log(error);
			}
		);
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

});