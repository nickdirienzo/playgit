var playlist = {
	name: "Test Playlist",
	songs: [
		{ name: "Never Gonna Give You Up", artist: "Rick Astley", album: "Platnium Hits" },
		{ name: "Get Lucky", artist: "Daft Punk", album: "Random Access Memoeries" }
	]
};
var playlist2 = {
	name: "Test Playlist 2",
	songs: [
		{ name: "Can't Hold Us", artist: "Macklemore", album: "The Heist" },
		{ name: "Fix You", artist: "Coldplay", album: "X&Y" }
	]
};

var appVM = new AppViewModel({
	playlists: [ playlist, playlist2 ]
});

$.get('/user', function(data) {
	appVM.user(data);
	appVM.isLoaded(true)
});

ko.applyBindings(appVM);