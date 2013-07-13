var AppViewModel = function(json) {
	var self = this;

	// data fields
	this.user = ko.observable({
		id: 0,
		username: null,
		is_logged_in: false
	});

	this.isLoaded = ko.observable(false);

	this.playlists = ko.observableArray();
	if(json) { self.addPlaylists(json.playlists); }

	// state
	this.stateTemplate = ko.observable('homepage-tmpl');
	this.stateData = ko.observable(self);

	// display helpers

	this.userLabel = ko.computed(function() {
		return self.user().username;
	});
	this.userIsLoggedIn = ko.computed(function() {
		return self.user().is_logged_in;
	});

    // activity feed
    var activities = new ActivityViewModel();
    this.latestActivity = activities.latestActivity;

	// functions
	this.clickLogo = function() {
		self.transition('homepage-tmpl', self);
	};
	this.clickUserLabel = function() {
		$("#user .user-label").fadeOut(150, function() {
			$("#user #user-login").fadeIn(150);
		});
	};

	this.addPlaylists = function(_playlists) {
		if(_playlists) {
			_.each(_playlists, function(playlist) {
				self.playlists.push(new PlaylistViewModel(playlist));
				console.log(self.playlists());
			});
		}
	};

	this.transition = function(template, data) {
		if(template == self.stateTemplate()) return;

		beforeTransition = self.stateData().beforeTransition;
		if(typeof beforeTransition === 'function') {
			beforeTransition();
		}
		$('#wrapper').slideUp(300, function() {
			self.stateTemplate('null-tmpl');
			self.stateData(data);
			self.stateTemplate(template);
		});
		$("#wrapper").slideDown(300);
	};

	this.clickLogin = function() {
		$.get('/login', function(data) {
            var url = data.login_url;
            if (url) {
                window.location = url;
            }
        });
	};
};
