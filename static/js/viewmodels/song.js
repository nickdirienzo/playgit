var SongViewModel = function(json, playlist) {
	var self = this;

	this.id = ko.observable(json.id);
	this.name = ko.observable(json.name);
	this.artist = ko.observable(json.artist);
	this.album = ko.observable(json.album);

	// not observable. 
	this.playlist = playlist;

	// functions
	this.removeSong = function() {
		self.playlist.removeSong(self);
	}
};

