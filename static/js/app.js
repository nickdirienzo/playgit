playlist = {
	name: "Test Playlist",
	songs: [
		{ name: "Never Gonna Give You Up", artist: "Rick Astley", album: "Platnium Hits" },
		{ name: "Get Lucky", artist: "Daft Punk", album: "Random Access Memoeries" }
	]
};

appVM = new AppViewModel({
	playlists: [ playlist, playlist ]
})

ko.applyBindings(appVM);