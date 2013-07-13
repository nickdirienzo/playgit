var PlaylistViewModel = function(json) {
	var self = this;

	this.id = ko.observable(json.id);
	this.name = ko.observable(json.name);
	this.parent = ko.observable(json.parent);
	this.songs = ko.observableArray();
	_.each(json.songs, function(song) {
		self.songs.push(new SongViewModel(song,self));
	});
	this.owner = ko.observable(json.uid != appVM.user.id);

	this.songsCount = ko.computed(function() {
		return json.id;
		//return this.songs().length;
	}, this);

	this.clickPlaylist = function() {
		appVM.transition('playlist-tmpl', self);
	};

	this.clickFork = function() {
		$.get('/fork_playlist/' + json.id, function(data) {
			appVM.addPlaylists([data.playlist]);
			console.log(appVM.playlists().length-1);
			appVM.transition('playlist-tmpl', appVM.playlists()[appVM.playlists().length-1]);
		});
	};

	this.pullRequest = function() {

	};

	this.deletePlaylist = function() {

	};

	this.removeSong = function(song) {
		self.songs.remove(song);
	}

	this.beforeTransition = function() {
		songs = [];
		ko.utils.arrayForEach(self.songs(), function(item) {
			songs.push(item.toJSON());
		})
		console.log(JSON.stringify(songs));
	}
};

