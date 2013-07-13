var PRModel = function(json) {
	var self = this;

	this.id = ko.observable(json.id);
	this.child = ko.observable(appVM.findPlaylist(json.child_pid));
	this.child_uid = ko.observable(json.child_uid);
	this.parent = ko.observable(appVM.findPlaylist(json.parent_pid));
	this.parent_uid = ko.observable(json.parent_uid);
	this.diff = ko.observableArray();

	this.isLoading = true; 

};

