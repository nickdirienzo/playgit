var PlaylistViewModel = function(json) {
	var self = this;

	this.id = ko.observable(json.id);
	this.name = ko.observable(json.name);
	this.parent = ko.observable(json.parent);
	this.songs = ko.observableArray();
	_.each(json.songs, function(song) {
		self.songs.push(new SongViewModel(song,self));
	});

	this.songsCount = ko.computed(function() {
		return this.songs().length;
	}, this);

	this.clickPlaylist = function() {
		appVM.transition('playlist-tmpl', self);
	};

	this.removeSong = function(song) {
		self.songs.remove(song);
	}
};

