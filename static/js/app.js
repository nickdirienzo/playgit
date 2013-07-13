var playlist = {
	id: 3,
	name: "Test Playlist PETER",
	songs: [
		{ name: "Never Gonna Give You Up", artist: "Rick Astley", album: "Platnium Hits" },
		{ name: "Get Lucky", artist: "Daft Punk", album: "Random Access Memoeries" }
	],
	pr: [
		{ name: "PR 1", diff: [] }
	]
};
var playlist2 = {
	name: "Test Playlist 2",
	songs: [
		{ name: "Can't Hold Us", artist: "Macklemore", album: "The Heist" },
		{ name: "Fix You", artist: "Coldplay", album: "X&Y" }
	]
};

// var appVM = new AppViewModel({
	// playlists: [ playlist, playlist2 ]
// });

var appVM = new AppViewModel();

$.get('/user', function(data) {
	appVM.user(data);
	appVM.isLoaded(true);

	$.get("/playlists", function(data) {
		appVM.addPlaylists(data.playlists);

		if(window.location.hash.indexOf('playlist') == 1) {
			var targetPlaylist = appVM.findPlaylist(parseInt(getQueryVariable('id')));
			if(targetPlaylist) {
				appVM.transition('playlist-tmpl', targetPlaylist, true); 
			}
		}
	})
});

ko.applyBindings(appVM);

function getQueryVariable(variable) {
    var query = window.location.hash.substring(window.location.hash.indexOf('?') + 1);
    var vars = query.split('&');
    for (var i = 0; i < vars.length; i++) {
        var pair = vars[i].split('=');
        if (decodeURIComponent(pair[0]) == variable) {
            return decodeURIComponent(pair[1]);
        }
    }
}
