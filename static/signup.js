var usernameavlbl = false;
var passequal = false;

function DoPrevent(e) {
    e.preventDefault();
    e.stopPropagation();
}


function checkpass() {
    var pasel = $('input[name="confpassword"]');
    var pass = $('input[name="password"]').val();
    var confpass = pasel.val();
    if (pass === confpass) {
        passequal = true;
        pasel.popover('hide');
    } else {
        pasel.popover(
            {
                trigger: 'manual',
                title: 'Error',
                content: "Password and its confirmation are not equal",
                placement: 'right'
            }
        );
        pasel.popover('show');
        passequal = false;
    }
}

function checkuser(username) {
    var usrel = $('input[name="username"]');
    $.ajax('/checkuser?username=' + username, {
            success: function (data, status, xhr) {   // success callback function
                if (data === 'true') {
                    usrel.popover('hide');
                    usernameavlbl = true;
                } else {
                    usrel.popover(
                        {
                            trigger: 'manual',
                            title: 'Error',
                            content: "Username is already taken",
                            placement: 'right'
                        }
                    );
                    usrel.popover('show');
                    usernameavlbl = false;
                }
            }
        }
    )
}

function checksub() {
    if (usernameavlbl && passequal)
        $("form").off('click', DoPrevent);
    else
        $("form").on('click', DoPrevent);

}

function checksubprof() {
    var pasel = $('input[name="confpassword"]');
    var pass = $('input[name="password"]').val();
    var confpass = pasel.val();
    if (pass === confpass) {
        passequal = true;
    }
    if (passequal)
        $("form").off('click', DoPrevent);
    else
        $("form").on('click', DoPrevent);
}
