'use strict';

var application = angular.module("registration", ["ngCookies"]);

application.controller("registrationController", function($scope, $http, $window, $cookies) {

	$scope.user = {};
	$scope.cart = {};

	$scope.submitRegistration = function() {
		console.log($scope.user);

		if ($scope.user.password != $scope.user.confirmedPassword) {
			alert("Passwords don't match");
		}else {
			$http.post("/api/users", $scope.user, {headers: {'Content-Type': 'application/json'}})
			.then(
				(response) => {

					var token = undefined;

					$http.post("/api/auth", $scope.user, {headers: {'Content-Type': 'application/json'}})
					.then(
						(authResponse) => {
							token = $cookies.get("jwt");
						},
						(authError) => {
							alert(authError.data.msg);
						}
					).finally(() => {
						if ($cookies.get("cart") != undefined) {
							$scope.cart =  JSON.parse($cookies.get("cart"));

							$http.post("/api/carts", $scope.cart, {headers: {'Authorization': token}})
							.then(
								(cartResponse) => {
									console.log(response);
									console.log("updated cart");
								},
								(cartError) => {
									console.log(cartError);
								}
							).finally(() => {
								alert("account successfully created!, redirecting back to home page");
								$window.location.href = 'index.html';
							});

						}else{
							alert("account successfully created!, redirecting back to home page");
							$window.location.href = 'index.html';	
						}

					});

				},
				(response) => {
					alert(response.data.msg);
				});
		}
	}

});