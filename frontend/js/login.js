var application = angular.module("login", ["ngCookies"]);

application.controller("loginController", function($scope, $http, $window, $cookies) {

	$scope.user = {};

	$scope.authenticate = function() {
		$http.post("/api/auth", $scope.user, {headers: {'Content-Type': 'application/json'}})
		.then(
			(response) => {
				token = $cookies.get("jwt");
		
				if (token == undefined){
					console.log("missing token");
					$window.location.href = 'index.html';
				}else{
					tokenBody = JSON.parse(atob(token.split(".")[1]));

					alert("successfully authenticated!, redirecting to your home page");
					
					if (tokenBody.role == "admin"){
						$window.location.href = 'admin.html';
					}else{
						$window.location.href = 'index.html';
					}
					
				}
			},
			(response) => {
				alert(response.data.msg);
			}
		);
	}

});