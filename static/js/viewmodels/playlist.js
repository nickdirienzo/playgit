var PlaylistViewModel = {
	id: ko.observable("123ABC"),
	uid: ko.observable(1),
	name: ko.observable("Test Playlist"),
	parent: ko.observable("123AB"),
	songs: ko.observableArray([
		{ name: "Never Gonna Give You Up", artist: "Rick Astley", album: "Platnium Hits" },
		{ name: "Get Lucky", artist: "Daft Punk", album: "Random Access Memoeries" }
	]),
	songsCount: function() {
		return self.songs.length
	}
}