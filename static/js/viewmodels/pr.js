var PRModel = function(json) {
	var self = this;

	this.id = ko.observable(json.id);
	this.child = ko.observable(null);
	this.child_uid = ko.observable(json.child_uid);
	this.child_username = ko.observable(json.child_username);
	this.child_icon = ko.observable(json.child_icon);
	this.parent = ko.observable(null);
	this.parent_uid = ko.observable(json.parent_uid);
	this.requested_on = ko.observable(json.requested_on);
	this.accepted_on = ko.observable(json.accepted_on)

	this.diff = ko.observable('');
	this.isLoading = ko.observable(true);

	appVM.findPlaylist(json.child_pid, function(playlist) {
		self.child(playlist);
	})	
	appVM.findPlaylist(json.parent_pid, function(playlist) {
		self.parent(playlist);
	})	

	$.get('/diff/' + self.child().id() + '/' + self.parent().id(), function(data) {
		self.isLoading(false);
		self.diff(data.diff);
	});

	this.childName = ko.computed(function() {
		return self.child().username() + '/' + self.child().name() + ' to';
	})
	this.parentName = ko.computed(function() {
		return self.parent().username() + '/' + self.parent().name();
	})

	this.acceptPR = function() {
		$.get('/pr/' + self.parent().id() + '/' + self.child().id() + '/accept', function() {
			appVM.transition('playlist-tmpl', self.parent());
		});
	};

	this.setHash = function() {
		location.hash = "#pr?id=" + self.id();
	};

	this.isAccepted = ko.computed(function() {
		return self.accepted_on() != null;
	});

};

