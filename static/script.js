// script.js

    // Create the app module
    var projectX = angular.module('projectX', ['ngRoute', 'ui.bootstrap', 'sprintf']);

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

    projectX.factory('utils', function($http){
        return {
            isNumeric: function(value){
                return !isNaN(parseFloat(value)) && isFinite(value);
            },
            isValidEmail: function(email){
                var pattern = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
                return pattern.test(email);
            },
            getLocation: function(){
                window.navigator.geolocation.getCurrentPosition(function(pos){
                  console.log(pos);
                  $http.get('http://maps.googleapis.com/maps/api/geocode/json?latlng='+pos.coords.latitude+','+pos.coords.longitude+'&sensor=true')
                  .then(function(res){
                    console.log(res.data);
                  });
                })
            },
            isBrowserCompatible: function(){
                return (typeof(Storage) !== "undefined" && 
                        typeof(navigator.geolocation) !== "undefined");
            }
        };
    });

    // Session cache service
    projectX.factory('sessionCache', function(utils){
        
        if(!utils.isBrowserCompatible())
        {
            bootbox.alert("Sorry, your browser does not support features our app needs!");
            return;
        }
        else
        {
            var newPostPhotos;

            return {
                setSearchText: function(value){
                    sessionStorage.searchText = value;
                },
                getSearchText: function(){
                    return sessionStorage.searchText ? sessionStorage.searchText : "";
                },
                setSearchResults: function(data){
                    sessionStorage.searchResults = JSON.stringify(data);
                },
                getSearchResults: function(){
                    return sessionStorage.searchResults ? JSON.parse(sessionStorage.searchResults) : [];
                },
                setLivePost: function(post){
                    sessionStorage.livePost = JSON.stringify(post);
                },
                getLivePost: function(){
                    return sessionStorage.livePost ? JSON.parse(sessionStorage.livePost) : null;
                },
                setNewPost: function(post){
                    if(!post)
                    {
                        sessionStorage.removeItem("newPost");
                        return;
                    }
                    newPostPhotos = post.photos ? post.photos : [];
                    post.photos = null;
                    sessionStorage.newPost = JSON.stringify(post);
                },
                getNewPost: function(){
                    if(!sessionStorage.newPost)
                    {
                        return null;
                    }

                    var post = JSON.parse(sessionStorage.newPost);
                    post.photos = newPostPhotos ? newPostPhotos : [];
                    return post;
                },
                addFavorite: function(post){
                    if(post == null)
                    {
                        return;
                    }

                    var favorites = sessionStorage.favorites ? JSON.parse(sessionStorage.favorites) : [];
                    var addCondition = _.find(favorites, function(p){ return p.guid == post.guid }) == null;

                    if(addCondition)
                    {
                        favorites.push(post);
                        sessionStorage.favorites = JSON.stringify(favorites);
                    }
                },
                getFavorites: function(){
                    return  sessionStorage.favorites ? JSON.parse(sessionStorage.favorites) : [];
                },
                flagPost: function(guid){
                    if(!guid)
                    {
                        return;
                    }
                    var flagged = sessionStorage.flaggedPosts ? JSON.parse(sessionStorage.flaggedPosts) : [];
                    flagged.push(guid);
                    sessionStorage.flaggedPosts = JSON.stringify(flagged);
                },
                didFlagPost: function(guid){
                    var flagged = sessionStorage.flaggedPosts ? JSON.parse(sessionStorage.flaggedPosts) : [];
                    var target = _.find(flagged, function(g){ return g == guid });
                    return target != null;
                }
            }
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
    projectX.config(function($routeProvider, $locationProvider) {
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

        // Create page
        .when('/createPost', {
            templateUrl : 'static/partials/createPost.html',
            controller : 'createPostController'
        })

        .when('/edit/:post_guid', {
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

        .when('/previewPost/:post_guid?', {
            templateUrl : 'static/partials/previewPost.html',
            controller : 'previewPostController'
        })

        .when('/favorites', {
            templateUrl : 'static/partials/favorites.html',
            controller : 'favoritesController'
        })

        .when('/about', {
            templateUrl : 'static/partials/about.html',
            controller : 'aboutController'
        })

        .when('/tips', {
            templateUrl : 'static/partials/tips.html',
            controller : 'tipsController'
        })

        // Default to home
        .otherwise({
            redirectTo:'/'
        });
    });

//*********** Controllers **************//

    // Main/Home Page Controller
    projectX.controller('mainController', function($scope, $location, $http, dbService, sessionCache, utils) {
        
        generateGreeting = function(){
            var msgs = [
                "Ahoy Matey!",
                "¡Hola Amigo!",
                "You've come to the right place!",
                "Let's find some good deals!",
                "Hello Friend!",
                "Fancy meeting you here...",
                "Come here often?"
            ];

            $scope.header = _.sample(msgs);
        };

        $scope.init = function(){
            $("#post-nav-btn").show();
            generateGreeting();
            if(!utils.isBrowserCompatible())
            {
                bootbox.alert("Sorry, your browser does not support features that we require.");
            }
        };

        $scope.init();

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
            {
                console.error(data, status, headers, config);
            });
        }
    });

    // Create Post Controller
    projectX.controller('createPostController', 
        function($scope, $location, $window, sessionCache, utils, $routeParams, $http){

        var reader = new FileReader();
        var dropperFile = {};

        $scope.editModeEnabled = $routeParams.post_guid != null;

        $scope.init = function(){
            if($scope.editModeEnabled)
            {
                var editPath = sprintf("/edit/%s", $routeParams.post_guid);
                $http({
                    url: editPath,
                    method:'POST',
                    dataType: 'JSON',
                    headers: {'Content-Type': 'application/json'}
                })
                .success(function(data, status, headers, config) 
                {
                    console.info(data, status, headers, config);
                    data.photos = _.map(data.photos, function(url){
                        return {url: url};
                    });
                    _.first(data.photos).isMain = true;

                    $scope.post = data;
                })
                .error(function(data, status, headers, config) 
                {
                    console.error(data, status, headers, config);
                    bootbox.alert("There was a problem navigating to that URL.");
                    $location.path("/")
                });
            }
            else
            {
                var newPost = sessionCache.getNewPost();
                $scope.post = (newPost) ? newPost : {};
                $scope.post.photos = ($scope.post.photos) ? $scope.post.photos : [];

            }
            $(".form-control").on("focus", function(){
                $(this).removeClass("bad-input");
            });
            $("#post-nav-btn").hide();
        };

        $scope.init();

        reader.onload = function()
        {
            droppedFile.url = reader.result;
            if($scope.post.photos.length == 0)
            {
                droppedFile.isMain = true;
            }
            $scope.post.photos.push(droppedFile);
            $scope.$apply();
        };

        $scope.onSelectFile = function() {
            if($scope.post.photos.length == 8)
            {
                bootbox.alert("Woah there tiger! You can upload a maximum of 8 images, so choose wisely!")
                return;
            }
            $("input#file-input").click();
        };

        $scope.onFileSelected = function(files) {
            droppedFile = files[0];
            reader.readAsDataURL(files[0]);
        };

        $scope.onStarPhoto = function(photo) {
            _.each($scope.post.photos, function(p){p.isMain = false});
            photo.isMain = true;
        };

        $scope.onDeletePhoto = function(photo) {
            $scope.post.photos = _.reject($scope.post.photos, function(p){return p == photo});
            if($scope.post.photos.length == 1)
            {
                $scope.post.photos[0].isMain = true;
            }
        };

        $scope.onPreview = function(){
            if(!$scope.post)
            {
                $("form-control").addClass("bad-input");
                return;
            }

            $("form-control").removeClass("bad-input");

            var problemCount = 0;
            var message = "Oh no! There are some problems with your post.<BR><BR>"
            // TODO: Properly Verify Inputs
            if(!$scope.post.title)
            {
                problemCount++;
                $("input#title").addClass("bad-input");
                message+=sprintf("%s. The 'Title' field can not be empty.<BR>", problemCount);
            }
            if(!$scope.post.zip || !utils.isNumeric($scope.post.zip) || $scope.post.length > 9)
            {
                problemCount++;
                $("input#zip").addClass("bad-input");
                message+=sprintf("%s. Please enter a valid zip code.<BR>", problemCount);
            } 
            if(!$scope.post.price || !utils.isNumeric($scope.post.price))
            {
                problemCount++;
                $("input#price").addClass("bad-input");
                message+=sprintf("%s. Please enter a valid price value.<BR>", problemCount);
            }
            if(!$scope.post.desc)
            {
                problemCount++;
                $("textarea#desc").addClass("bad-input");
                message+=sprintf("%s. 'Description' is a required field.<BR>", problemCount);
            }
            if(!$scope.post.email || !utils.isValidEmail($scope.post.email))
            {
                problemCount++;
                $("input#email").addClass("bad-input");
                message+=sprintf("%s. Please enter a valid email address.<BR>", problemCount);
            }
            if(!$scope.post.photos || $scope.post.photos.length < 1)
            {
                problemCount++;
                message+=sprintf("%s. We require that you upload at least one relevant image for your ad.<BR>", problemCount);
            }

            if(problemCount > 0)
            {
                bootbox.alert(message);
                return;
            }

            sessionCache.setNewPost($scope.post);
            var path = $scope.editModeEnabled ? sprintf("/previewPost/%s", $routeParams.post_guid) : "/previewPost"
            $location.path(path);
        };

        $scope.onCancel = function(){
            bootbox.dialog({
              message: "Any information you've entered will be lost.",
              title: "Are you sure you want to cancel?",
              buttons: {
                danger: {
                  label: "Nevermind!",
                  className: "btn-danger",
                  callback: function(){}
                },
                main: {
                  label: "Duh, I know what I'm doing.",
                  className: "btn-primary",
                  callback: function() {
                    sessionCache.setNewPost(null);
                    $location.path("/");
                    $scope.$apply();
                  }
                }
              }
            });
        };

        $scope.onDelete = function(){
            bootbox.confirm("Are you sure you want to delete this post forever?", 
                function(isConfirmed) 
                {                
                    if (isConfirmed) 
                    {
                        var json = JSON.stringify({guid: $routeParams.post_guid});
                        $http({
                            url: "/delete_post",
                            method:'POST',
                            dataType: 'JSON',
                            headers: {'Content-Type': 'application/json'},
                            data: json
                        })
                        .success(function(data, status, headers, config) 
                        {
                            console.info(data, status, headers, config);
                            bootbox.alert("The deed is done.");
                            $location.path("/");                        
                        })
                        .error(function(data, status, headers, config) 
                        {
                            console.error(data, status, headers, config);
                        });
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
            $scope.resultsMsg = sprintf("Good news! We found %s listing%s for", 
                $scope.results.length,
                ($scope.results.length > 1 ? "s" : ""));
            $("#post-nav-btn").show();
        };

        $scope.init();

        $scope.onLoadPost = function(post){
            sessionCache.setLivePost(post);
            $location.path("/livePost");
        };

    });


    // Live/Active Post Controller
    projectX.controller('livePostController', function($scope, $http, $window, sessionCache) {
        $scope.init = function(){
            $('html,body').scrollTop(0);
            $scope.post = sessionCache.getLivePost();
            $scope.isFavBtnDisabled = _.find(sessionCache.getFavorites(), function(p)
                    { return p.guid == $scope.post.guid }) != null;
            $scope.isFlagBtnDisabled = sessionCache.didFlagPost($scope.post.guid);
            $scope.favBtnText = ($scope.isFavBtnDisabled) ? "Favorited!" : "Add to Favorites";
            $("#post-nav-btn").show();
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

        $scope.onFlag = function(){
            var json = JSON.stringify({guid: $scope.post.guid});
            $http({
                url:'/flag_post',
                method:'POST',
                dataType: 'JSON',
                data: json,
                headers: {'Content-Type': 'application/json'}
            })
            .success(function(data, status, headers, config) 
            {
                $scope.isFlagBtnDisabled = true;
                sessionCache.flagPost($scope.post.guid);
                bootbox.alert("Post has been flagged! Thanks for keeping an eye on things.");
                console.info(data, status, headers, config);
            })
            .error(function(data, status, headers, config) 
            {
                console.error(data, status, headers, config);
            });
        };
    });

    // Preview Controller
    projectX.controller('previewPostController', function($scope, $location, $http, sessionCache, $routeParams) {

        $scope.init = function() {
            $scope.editModeEnabled = $routeParams.post_guid != null
            $scope.post = sessionCache.getNewPost();
            $scope.post.photos = [_.find($scope.post.photos, function(p){return p.isMain})]
            .concat(_.filter($scope.post.photos, function(p){return !p.isMain}));
            $("#post-nav-btn").hide();
        };

        $scope.init();

        $scope.onSubmit = function() {
            _.each($scope.post.photos, function(p){
                p.base64 = p.url.replace("data:image/jpeg;base64,", "");
            });
            var json = JSON.stringify($scope.post);
            var path = $scope.editModeEnabled ? "/update" : "/upload";
            $http({
                url: path,
                method:'POST',
                dataType: 'JSON',
                data: json,
                headers: {'Content-Type': 'application/json'}
            })
            .success(function(data, status, headers, config) 
            {
                bootbox.alert("Woohoo! Your post has been added. Check your email for confirmation.");
                console.info(data, status, headers, config);
                sessionCache.setNewPost(null);
                $location.path("/");
            })
            .error(function(data, status, headers, config) 
            {
                console.error(data, status, headers, config);
            });
        };

        $scope.onBack = function() {
            var path = $scope.editModeEnabled ? sprintf("/edit/%s", $routeParams.post_guid) : "/createPost";
            $location.path(path);
        };
    });

    // Favorites Controller
    projectX.controller('favoritesController', function($scope, $location, $window, sessionCache) {
        $scope.init = function(){
            $scope.favorites = sessionCache.getFavorites();
            if($scope.favorites.length == 0)
            {
                bootbox.alert("You don't have any favorites yet!");
                $window.history.back();
            }
            $("#post-nav-btn").show();
        };

        $scope.init();

        $scope.onLoadPost = function(post){
            sessionCache.setLivePost(post);
            $location.path("/livePost");
        };
    });

    // Tips Page Controller
    projectX.controller('tipsController', function() {
        $("#post-nav-btn").show();
    });

    // About Page Controller
    projectX.controller('aboutController', function() {
        $("#post-nav-btn").show();
    });



