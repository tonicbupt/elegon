$(document).ready(function() {
    $('input[name=appname]').blur(function() {
        var self = $(this),
        appname = self.val(),
        version = $('select[name=version]'),
        url = '/j/app/' + appname + '/';
        $.ajax({
            url: url,
            type: 'GET',
            success: function(r) {
                version.html(r.html);
                version.val('');
            },
        });
    });

    $('select[name=version]').change(function() {
        var self = $(this),
        appname = $('input[name=appname]').val(),
        version = self.val(),
        url = '/j/app/' + appname + '/version/' + version + '/';
        $.ajax({
            url: url,
            type: 'GET',
            success: function(r) {
                var entry = $('select[name=entrypoint]');
                var env = $('select[name=env]');
                entry.html(r.entrypoint);
                env.html(r.env);
            },
        });
    });

    $('select[name=group]').change(function() {
        var self = $(this),
        groupname = self.val(),
        url = '/j/group/' + groupname + '/pods/';
        $.ajax({
            url: url,
            type: 'GET',
            success: function(r) {
                var pod = $('select[name=pod]');
                pod.html(r.pod);
            },
        });
    });

    $('input[type=checkbox]').on('switchChange.bootstrapSwitch', function(e, s) {
        var self = $(this),
        id = self.data('id'),
        action = 'off';
        if (s) {
            action = 'on';
        } else {
            action = 'off';
        }
        url = '/j/crontab/' + id + '/' + action + '/';
        $.ajax({
            url: url,
            type: 'POST',
            success: function (r) {
                if (r.r) {
                    alert(r.msg);
                }
            },
        });
    });
});
