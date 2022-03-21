$(document).ready(function () {
    if ($(window).width() < 1200) {
        $('#sidenav-tog0').on('click', function () {
            $('.overlay').removeClass('active');
            if (document.getElementById("sidenav-tog0")!=null) {
                document.getElementById("sidenav-tog0").hidden = true;
            }
            if (document.getElementById("sidenav-tog")!=null) {
                document.getElementById("sidenav-tog").hidden = false;
            }
            if (document.getElementById("collap_button")!=null) {
                document.getElementById("collap_button").hidden = false;
            }
        });

        $('#sidenav-tog, #collap_button').on('click', function () {
            $('.overlay').addClass('active');
            if (document.getElementById("sidenav-tog")!=null) {
                document.getElementById("sidenav-tog").hidden = true;
            }
            if (document.getElementById("sidenav-tog0")!=null) {
                document.getElementById("sidenav-tog0").hidden = false;
            }
            if (document.getElementById("collap_button")!=null) {
                document.getElementById("collap_button").hidden = true;
            }
        });
    }
});

if (document.URL == 'http://127.0.0.1:8000/fr/dashboard/') {
    $(document).ready(function () {
        $.ajax({
            type: "GET",
            url: "full_map",
            async: true,
            dataType: "json",
            contentType: "application/javascript; charset=utf8",
            complete: function (data) {
                let full_map = data.responseJSON['map'];
                $("div.child1").replaceWith(full_map);
                setTimeout(
                    function () {
                        $('div.child2').fadeOut('', function () {
                            $('div.child2').replaceWith();
                        });
                    }, 250);
            },
        });
    });
}



