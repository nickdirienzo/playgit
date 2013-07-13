var AppViewModel = function(json) {
	var self = this;

	this.user = ko.observable({
		id: 0,
		username: null,
		is_logged_in: false
	});

	this.userFormUsername = ko.observable("");
	this.userFormPassword = ko.observable("");

	// data fields
	this.playlists = ko.observableArray();
	_.each(json.playlists, function(playlist) {
		self.playlists.push(new PlaylistViewModel(playlist));
	});

	// display helpers
	this.userLabel = ko.computed(function() {
		return self.user().username;
	});
	this.userIsLoggedIn = ko.computed(function() {
		return self.user().is_logged_in;
	});

	// functions
	this.clickUserLabel = function() {
		$("#user .user-label").fadeOut(150, function() {
			$("#user #user-login").fadeIn(150);	
		});
	};
	this.clickRegister = function() {
		$.post('/signup', {
			username: self.userFormUsername(),
			password: self.userFormPassword()
		});
	};

	this.clickLogin = function() {
		$.get('/login', function(data) {
            var url = data['login_url'];
            if (url) {
                window.location = url;
            }
        });
	};
};
