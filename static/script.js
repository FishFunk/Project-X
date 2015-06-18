// script.js

    // Create the app module
    var projectX = angular.module('projectX', ['ngRoute','angularFileUpload', 'ui.bootstrap', 'sprintf']);

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
                    sessionStorage.post = JSON.stringify(post)
                },
                getLivePost: function(){
                    if(!sessionStorage.post)
                    {
                        return null;
                    }
                    return JSON.parse(sessionStorage.post)
                },
                setNewPost: function(post){
                    sessionStorage.post = JSON.stringify(post)
                },
                getNewPost: function(){
                    if(!sessionStorage.post)
                    {
                        return null;
                    }
                    return JSON.parse(sessionStorage.post)
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

        .when('/previewPost', {
            templateUrl : 'static/partials/previewPost.html',
            controller : 'previewPostController'
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

        $scope.header = "";
        $scope.searchField = "";

        generateGreeting = function(){
            var msgs = [
                "Ahoy Matey!",
                "¡Hola Amigo!",
                "You've come to the right place!",
                "Let's find some good deals!",
                "Hello Friend!",
                "Fancy meeting you here. Come here often?"
            ];

            $scope.header = _.sample(msgs);
        };

        $scope.search = function() {
            sessionCache.setSearchText($scope.searchField);
        	dbService.search($scope.searchField)
            .success(function(data, status, headers, config)
            {
                if(data != null && data.length == 0)
                {
                    var msg = sprintf("Sorry... we didn't find any listings that match '%s'. Try phrasing your search differently or check back again later!", $scope.searchField);
                    bootbox.alert(msg);
                }
                else
                {
                    sessionCache.setSearchResults(data);
                    $location.path('/results');
                }
            })
            .error(function(data, status, headers, config)
            {});
        }

        generateGreeting();
    });

    // Create Post Controller
    projectX.controller('createPostController', function($scope, $location, $window, sessionCache){

        var reader = new FileReader();
        $scope.allFiles = [];

        $scope.init = function(){
            $scope.post = sessionCache.getNewPost();
            $scope.allFiles = $scope.post.photos;
        };

        $scope.init();

        reader.onload = function()
        {
            $scope.droppedFile[0].url = reader.result;
            $scope.allFiles.push($scope.droppedFile[0]);
            $scope.post.photos = $scope.allFiles;
            $scope.$apply();
        };

        $scope.$watch('droppedFile', function(){
            if($scope.droppedFile && $scope.droppedFile.length > 0)
            {
                reader.readAsDataURL($scope.droppedFile[0]);
            }
        });

        $scope.onPreview = function(){
            // TODO: Properly Verify Inputs
            if(!$scope.post.title || !$scope.post.location || !$scope.post.price ||
               !$scope.post.description || !$scope.post.email)
            {
                bootbox.alert("One or more required fields are empty.");
                return;
            }

            // TODO: Properly Verify Photos
            if($scope.post.photos.length < 1)
            {
                bootbox.alert("You must upload at least one image.");
            }

            sessionCache.setNewPost($scope.post);
            $location.path('/previewPost');
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
            $('.selectpicker').selectpicker();
            $scope.resultsMsg = sprintf("Good news! We found %s listings for", $scope.results.length);
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
            $('html,body').scrollTop(0);
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

    // Preview Controller
    projectX.controller('previewPostController', function($scope, $location, $http, sessionCache) {
        $scope.init = function() {
            $scope.post = sessionCache.getNewPost();
        };

        $scope.init();

        $scope.onSubmit = function() {
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
                console.info(data, status, headers, config);
            })
            .error(function(data, status, headers, config) {
                console.error(data, status, headers, config);
            });
        };

        $scope.onBack = function() {
            $location.path("/createPost");
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