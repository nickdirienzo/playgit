var PlaylistViewModel = function(json) {
	var self = this;

	this.id = ko.observable(json.id);
	this.name = ko.observable(json.name);
	this.parent = ko.observable(json.parent);
	this.songs = ko.observableArray();

	this.owner = ko.observable(json.uid != appVM.user.id);
    this.username = ko.observable('');
    this.hasChanges = ko.observable(false);

    this.searchQuery = ko.observable("");
    this.searchTimeout = null;
    this.searchResults = ko.observableArray();
    this.pr = ko.observableArray(json.pull_requests || []);

    self.isLoading = ko.observable(true);
    $.get('/playlist/' + this.id(), function(data) {
        self.isLoading(false);
        self.songs(data.playlist.songs);
    });

    $.get('/user/' + json.uid, function(data) {
        self.username(data.username);
    });

	this.songsCount = ko.computed(function() {
		return self.songs().length;
	}, this);

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

	};

	this.deletePlaylist = function() {

	};

	this.removeSong = function(song) {
		self.songs.remove(song);
        self.hasChanges(true);
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
    	alert(self.id());
        $.ajax({
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'songs': self.songs() }),
            dataType: 'json',
            url: '/commit/' + self.id(),
            success: function(res) {
                if (res.success) {
                    self.hasChanges(false);
                }
            }
        });
    };

    this.fadeIn = function(elem) {
        if (elem.nodeType === 1) {
            $(elem).hide().slideDown();
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

