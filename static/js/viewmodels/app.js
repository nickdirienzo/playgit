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
	this.signOut = function() {
		$.get('/logout', function() {
			location.reload();
		});
	};

	this.newPlaylist = function() {
		var playlistName = window.prompt('New playlist name?');
        if (playlistName) {
            $.post('/create_playlist', {name: playlistName}, function() {
                self.reloadPlaylists();
            });
        }
	};

	// front end data
	this.addPlaylists = function(_playlists) {
		if(_playlists) {
			_.each(_playlists, function(playlist) {
				plvm = new PlaylistViewModel(playlist);
				self.playlists.push(plvm);
				plvm.refresh();
			});
		}
	};

	this.reloadPlaylists = function(callback) {
		$.get("/playlists", function(data) {
			appVM.playlists.removeAll();
			appVM.addPlaylists(data.playlists);
			if(typeof callback === 'function') {
				callback();
			}
		});
	};
	this.findPlaylist = function(id, callback) {
		toReturn = null;
		ko.utils.arrayForEach(self.playlists(), function(playlist) {
			if(playlist.id() == id) {
				toReturn = playlist;
				return false;
			}
		});

		if(toReturn == null) {
			$.get('/playlist' + id, function(data) {
				callback(new PlaylistViewModel(data.playlist));
			})
		} else {
			callback(toReturn);
		}
	};
	this.findPR = function(id, callback) {
		$.get('/pr/' + id, function(data) {
			callback(data);
		})
	};

	this.transition = function(template, data, noAnim) {
		if(template == self.stateTemplate() && data == self.stateData()) return;

		beforeTransition = self.stateData().beforeTransition;
		if(typeof beforeTransition === 'function') {
			beforeTransition();
		}

		setHash = data.setHash;
		if(typeof setHash === 'function') {
			setHash();
		} else {
			if(template == 'homepage-tmpl') {
				location.hash = "";
			} else {
				location.hash = template.substring(0, template.length-5);
			}
		}
	};
	this.afterRender = function() {
		if(self.stateTemplate() == 'playlist-tmpl') {
			self.stateData().refresh();
		}
	};
	this.reRender = function(template, data) {
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
