// script.js

    // Create the app module
    var projectX = angular.module('projectX', ['ngRoute','angularFileUpload', 'ui-rangeSlider', 'ui.bootstrap']);

    // Database service
    projectX.factory('dbService', function ($http){
        return {
            search: function(searchText){
                var json = JSON.stringify({searchVal: searchText});
                return $http({
                    url:'/search',
                    method:'POST',
                    data: json,
                    headers: {'Content-Type': 'application/json'}
                });
            }
        };
    });

    // Session cache service
    projectX.factory('sessionCache', function(){
        
        if(typeof(Storage) !== "undefined")
        {
            return {
                setSearchResults: function(data){
                    sessionStorage.searchResults = JSON.stringify(data);
                },
                setSearchText: function(value){
                    sessionStorage.searchText = value;
                },
                getSearchResults: function(){
                    if(!sessionStorage.searchResults)
                    {
                        return [];
                    }
                    return JSON.parse(sessionStorage.searchResults);
                },
                getSearchText: function(){
                    if(!sessionStorage.searchText)
                    {
                        return "";
                    }
                    return sessionStorage.searchText;
                },
                setLivePost: function(post){
                    sessionStorage.livePost = JSON.stringify(post)
                },
                getLivePost: function(){
                    if(!sessionStorage.livePost)
                    {
                        return null;
                    }
                    return JSON.parse(sessionStorage.livePost)
                },
                addFavorite: function(post){
                    if(post == null)
                    {
                        return;
                    }

                    var favorites = (sessionStorage.favorites == null) ? [] : JSON.parse(sessionStorage.favorites);
                    var addCondition = _.find(favorites, function(p){ return p.Guid == post.Guid }) == null;

                    if(addCondition)
                    {
                        favorites.push(post);
                        sessionStorage.favorites = JSON.stringify(favorites);
                    }
                },
                getFavorites: function(){
                    if(!sessionStorage.favorites)
                    {
                        return [];
                    }
                    return JSON.parse(sessionStorage.favorites);
                }
            };
        }
        else
        {
            alert("Bummer! This browser does not \
                support features this app requires!");
        }
    });

    // Enter action directive
    projectX.directive('ngEnter', function () {
        return function (scope, element, attrs) {
            element.bind("keydown keypress", function (event) {
                if(event.which === 13) {
                    scope.$apply(function (){
                        scope.$eval(attrs.ngEnter);
                    });

                    event.preventDefault();
                }
            });
        };
    });

    // configure routes
    projectX.config(function($routeProvider) {
        $routeProvider
        
        // Home page
        .when('/', {
            templateUrl : 'static/partials/home.html',
            controller : 'mainController'
        })

        // About page
        .when('/about', {
            templateUrl : 'static/partials/about.html',
            controller : 'aboutController'
        })

        // Contact page
        .when('/contact', {
            templateUrl : 'static/partials/contact.html',
            controller : 'contactController'
        })

        // Create page
        .when('/createPost', {
            templateUrl : 'static/partials/createPost.html',
            controller : 'createPostController'
        })

        // Results page
        .when('/results', {
            templateUrl : 'static/partials/results.html',
            controller : 'resultsController'
        })

        .when('/livePost', {
            templateUrl : 'static/partials/livePost.html',
            controller : 'livePostController'
        })

        .when('/favorites', {
            templateUrl : 'static/partials/favorites.html',
            controller : 'favoritesController'
        })

        // Default to home
        .otherwise({
            redirectTo:'/'
        });
    });

//*********** Controllers **************//

    // Main/Home Page Controller
    projectX.controller('mainController', function($scope, $location, $http, dbService, sessionCache) {

        $scope.header = 'Hello there!';
        $scope.searchField = "";
        
        $scope.search = function() {
            sessionCache.setSearchText($scope.searchField);
        	dbService.search($scope.searchField)
            .success(function(data, status, headers, config)
            {
                sessionCache.setSearchResults(data);
                $location.path('/results');
            })
            .error(function(data, status, headers, config)
            {});
        }
    });

    // Create Post Controller
    projectX.controller('createPostController', function($scope, $location, $http, $window){

        var reader = new FileReader();
        $scope.allFiles = [];

        reader.onload = function(){
            $scope.droppedFile[0].url = reader.result;
            $scope.allFiles.push($scope.droppedFile[0]);
            $scope.$apply();
        };

        $scope.$watch('droppedFile', function(){
            if($scope.droppedFile && $scope.droppedFile.length > 0){
                reader.readAsDataURL($scope.droppedFile[0]);
            }
        });

        $scope.upload = function(files){
            if($scope.allFiles && $scope.allFiles.length > 0)
            {
                //alert(JSON.stringify(allFiles));
            }
            $scope.post.photos = $scope.allFiles;
            var json = JSON.stringify($scope.post);
            $http({
                url:'/upload',
                method:'POST',
                dataType: 'JSON',
                data: json,
                headers: {'Content-Type': 'application/json'}
            })
            .success(function(data, status, headers, config) 
            {
            })
            .error(function(data, status, headers, config) {});
        };

        $scope.onCancel = function(){
            bootbox.confirm("Are you sure you want to cancel? Any information you've entered will be lost.", 
                function(confirm){
                    if(confirm)
                    {
                        $window.history.back();
                    }
            });
        };
    });

    // Results View CONTROLLER
    projectX.controller('resultsController', function($scope, $location, dbService, sessionCache) {
        $scope.init = function(){
            $scope.searchVal = sessionCache.getSearchText();
            $scope.results = sessionCache.getSearchResults();
            $scope.distanceRange = 25;
        };

        $scope.init();

        $scope.onLoadPost = function(post){
            sessionCache.setLivePost(post);
            $location.path("/livePost");
        };

    });


    // Live/Active Post Controller
    projectX.controller('livePostController', function($scope, $window, sessionCache) {
        $scope.init = function(){
            $scope.post = sessionCache.getLivePost();
            var slides = $scope.post.Photos;
            $scope.addSlide = function(){
                // Populate slides here
            };

            $scope.isFavBtnDisabled = _.find(sessionCache.getFavorites(), function(p)
                    { return p.Guid == $scope.post.Guid }) != null;
            
            $scope.favBtnText = ($scope.isFavBtnDisabled) ? "Favorited!" : "Add to Favorites";
        };

        $scope.init();

        $scope.onBack = function(){
            $window.history.back();
        };

        $scope.onAddFavorite = function(){
            sessionCache.addFavorite($scope.post);
            $scope.isFavBtnDisabled = true;
            $scope.favBtnText = "Favorited!"
        };
    });

    // Favorites Controller
    projectX.controller('favoritesController', function($scope, $location, $window, sessionCache) {
        $scope.init = function(){
            $scope.favorites = sessionCache.getFavorites();
        };

        $scope.init();

        $scope.onLoadPost = function(post){
            sessionCache.setLivePost(post);
            $location.path("/livePost");
        };
    });

    // About Page Controller
    projectX.controller('aboutController', function($scope) {
        $scope.message = 'I am an about page!';
    });

    // Contact Page Controller
    projectX.controller('contactController', function($scope) {
        $scope.message = 'We love to hear your feedback.';
    });