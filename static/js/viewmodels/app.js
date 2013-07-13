var AppViewModel = function(json) {
	var self = this;

	this.user = ko.observable({
		id: 1,
		username: "Guest"
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
		})
	};

	this.clickLogin = function() {
		$.post('/login', {
			username: self.userFormUsername(),
			password: self.userFormPassword()
		})
	};
};