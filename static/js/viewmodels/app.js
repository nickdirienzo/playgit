var AppViewModel = function(json) {
	var self = this;

	this.user = ko.observable({
		id: 1,
		username: "Guest"
	});

	this.userLoginUsername = ko.observable("");
	this.userLoginPassword = ko.observable("");

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
	this.clickRegister = function() {};

	this.submitLogin = function(formElement) {
		debugger
		$.post('/login', {
			username: self.userLoginUsername(),
			password: self.userLoginPassword()
		})
	};
};