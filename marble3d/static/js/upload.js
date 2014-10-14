$(document).ready(function () {

    var selector = '[role=uploadcare-uploader]';
    var widget = uploadcare.MultipleWidget(selector);

    widget.onChange(function (group) {
        if (!group) {
            return;
        }
        $.when.apply(null, group.files()).done(function () {
            // Store each image in the database
            $.each(arguments, function () {
                var fileInfo = this;
                console.log(fileInfo);

                $.ajax(store_image_url, {
                    type: "POST",
                    data: {
                        'image_url': fileInfo.cdnUrl,
                        'filename': fileInfo.name,
                        'csrfmiddlewaretoken': csrf_token
                    },
                    statusCode: {
                        400: function (response) {
                            addNotification('danger', 'the image was not saved - please make sure that job_id is correct and that crowdcafe.io is alive');
                        },
                        404: function (response) {
                            addNotification('danger', 'the image was not saved - please make sure that job_id is correct and that crowdcafe.io is alive');
                        },
                        500: function (response) {
                            addNotification('danger', 'the image was not saved - please make sure that job_id is correct and that crowdcafe.io is alive');
                        }
                    },
                    success: function (response) {
                        addNotification('success', 'image was saved');
                    }
                });
            });
        });

    });
});

function addNotification(type, message) {
    var alert_message = '<div class="alert alert-' + type + ' alert-dismissible" role="alert"> <button type="button" class="close" data-dismiss="alert"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button><strong>' + type + '!</strong> ' + message + '+ </div>';
    $('.notifications').append(alert_message);
}