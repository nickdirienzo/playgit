var PlaylistViewModel = function(json) {
	this.id = ko.observable(json.id);
	this.name = ko.observable(json.name);
	this.parent = ko.observable(json.parent);
	this.songs = ko.observableArray(json.songs);

	this.songsCount = ko.computed(function() {
		return this.songs().length;
	}, this);
};

