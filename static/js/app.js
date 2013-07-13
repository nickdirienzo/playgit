var appVM = new AppViewModel();
$(window).hashchange(function() {
	console.log("hash change");
	if(window.location.hash.indexOf('playlist') == 1) {
		var targetPlaylist = appVM.findPlaylist(parseInt(getQueryVariable('id')));
		if(targetPlaylist) {
			appVM.reRender('playlist-tmpl', targetPlaylist); 
		}
	} else {
		appVM.reRender('homepage-tmpl', appVM);
	}
});

$.get('/user', function(data) {
	appVM.user(data);
	appVM.isLoaded(true);

	$.get("/playlists", function(data) {
		appVM.addPlaylists(data.playlists);
		$(window).hashchange();
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
