var SongViewModel = function(json, playlist) {
	var self = this;

	this.key = ko.observable(json.key);
	this.name = ko.observable(json.name);
	this.artist = ko.observable(json.artist);
	this.album = ko.observable(json.album);

	// not observable. 
	this.playlist = playlist;

	// functions
	this.removeSong = function() {
		self.playlist.removeSong(self);
	}

	this.toJSON = function() {
		return {
			key: self.key(),
			name: self.name(),
			artist: self.artist(),
			album: self.album()
		};
	}
};

