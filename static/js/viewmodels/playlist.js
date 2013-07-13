var PlaylistViewModel = function(json) {
	var self = this;

	this.id = ko.observable(json.id);
	this.name = ko.observable(json.name);
	this.parent = ko.observable(json.parent);
	this.songs = ko.observableArray();

	this.owner = ko.observable(json.uid != appVM.user.id); // TODO flip this
    this.username = ko.observable('');
    this.hasChanges = ko.observable(false);
    this.commitLabel = ko.observable("");

    this.searchQuery = ko.observable("");
    this.searchTimeout = null;
    this.searchResults = ko.observableArray();
    this.pr = ko.observableArray();
    this.noPullRequests = ko.computed(function() {
        return self.pr().length === 0;
    });

    this.history = ko.observableArray();
    this.refreshHistory = function() {
        $.get('/playlist/' + this.id() + '/log', function(data) {
            self.history(data.history);
        });
    };
    this.refreshHistory();

    this.isLoading = ko.observable(true);
    this.refresh = function() {
    	self.songs.removeAll();
    	self.pr.removeAll();
    	self.isLoading(true);

    	$.get('/playlist/' + this.id(), function(data) {
	        self.isLoading(false);
	        self.songs(data.playlist.songs);
	        _.each(data.playlist.pull_requests, function(pr) {
	        	self.pr.push(new PRModel(pr));
	        });
	        $('.playlist-song.added').removeClass('added');
	    });
	};

    $.get('/user/' + json.uid, function(data) {
        self.username(data.username);
    });

	this.songsCount = ko.computed(function() {
		return self.songs().length;
	}, this);

	this.background = ko.computed(function() {
		var background = "";
		for(var i = 0; i < 4; i ++) {
            var song = self.songs()[Math.floor(Math.random()*self.songs().length)];
			if(song) {
				background += '<img src="' + song.artwork_url + '" />';
			}
		}
		return background;
	});
	this.clickPlaylist = function() {
		appVM.transition('playlist-tmpl', self);
	};
	this.clickSearchResult = function(result) {
		self.songs.unshift({
			key: result.key,
			name: result.name,
			artist: result.artist,
			album: result.album,
            artwork_url: result.icon
		});

        self.hasChanges(true);
        self.commitLabel("Commit changes");

		$("#playlist-search-results").slideUp(300, function() {
			self.searchResults.removeAll();
			self.searchQuery('');
		});
	};

	this.clickFork = function() {
		$.get('/fork_playlist/' + json.id, function(data) {
			appVM.addPlaylists([data.playlist]);
			appVM.transition('playlist-tmpl', appVM.playlists()[appVM.playlists().length-1]);
		});
	};

	this.pullRequest = function() {
		$.get('/pr/' + self.id() + '/' + self.parent(), function(res) {
			appVM.transition('playlist-tmpl', appVM.findPlaylist(self.parent()));
        });
	};

	this.findPR = function(id) {
		toReturn = null;
		ko.utils.arrayForEach(self.pr(), function(pr) {
			if(pr.id() == id) {
				toReturn = pr;
				return false;
			}
		});
		return toReturn;
	}

	this.deletePlaylist = function() {

	};


	this.displayPullRequest = function(pr) {
		appVM.transition('pr-tmpl', pr);
	};


	this.removeSong = function(song) {
		self.songs.remove(song);
        self.hasChanges(true);
        self.commitLabel("Commit changes");
	};
	this.doSearch = function() {
		clearTimeout(self.searchTimeout);
		self.searchTimeout = setTimeout(function() {
			$.get('/search', {q: self.searchQuery}, function(data) {
				self.searchResults.removeAll();
				_.each(data.results, function(result) {
					self.searchResults.push(result);
				});
				$('#playlist-search-results').slideDown(300);
			});
		}, 300);
	};

    this.commitChanges = function() {
        self.commitLabel("Committing...");
        $.ajax({
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'songs': self.songs() }),
            dataType: 'json',
            url: '/commit/' + self.id(),
            success: function(res) {
                self.commitLabel("");
                if (res.commit) {
                    self.hasChanges(false);
                    self.refreshHistory();
                    $('.playlist-song.added').removeClass('added');
                }
            }
        });
    };

    this.fadeIn = function(elem) {
        if (elem.nodeType === 1) {
            $(elem).hide().addClass('added').slideDown();
        }
    };
    this.fadeOut = function(elem) {
        if (elem.nodeType === 1) {
            $(elem).slideUp();
        }
    };

	this.setHash = function() {
		location.hash = "#playlist?id=" + self.id();
	};

};

