var ActivityViewModel = function() {
    var self = this;

    self.latestActivity = ko.observableArray();

    var fetchActivity = function() {
        $.get('/activity', function(data) {
            self.latestActivity(data.activity);
        });
    };

    window.setInterval(fetchActivity, 5000);
    fetchActivity();
};
