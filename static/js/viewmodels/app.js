var AppViewModel = function(json) {
	var self = this;

	this.playlists = ko.observableArray();
	_.each(json.playlists, function(playlist) {
		self.playlists.push(new PlaylistViewModel(playlist));
	});
};