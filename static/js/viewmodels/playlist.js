var PlaylistViewModel = function(json) {
	var self = this;

	this.id = ko.observable(json.id);
	this.name = ko.observable(json.name);
	this.parent = ko.observable(json.parent);
	this.songs = ko.observableArray();

    this.searchQuery = ko.observable("");
    this.searchTimeout = null;
    this.searchResults = ko.observableArray();
    this.pr = ko.observableArray(json.pr || []);

    $.get('/playlist/' + this.id(), function(data) {
        self.songs(data.songs);
    });

	this.songsCount = ko.computed(function() {
		return this.songs().length;
	}, this);

	this.clickPlaylist = function() {
		appVM.transition('playlist-tmpl', self);
	};
	this.clickSearchResult = function(result) {
		self.songs.push(new SongViewModel({
			key: result.key,
			name: result.name,
			artist: result.artist,
			album: result.album
		}));

		$("#playlist-search-results").slideUp(300, function() {
			self.searchResults.removeAll();
			self.searchQuery('');
		});
	};

	this.removeSong = function(song) {
		self.songs.remove(song);
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

	this.beforeTransition = function() {
		songs = [];
		ko.utils.arrayForEach(self.songs(), function(item) {
			songs.push(item);
		});
		console.log(JSON.stringify(songs));
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

