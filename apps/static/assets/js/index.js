$(document).ready(function () {
    if ($(window).width() < 1200) {
        $('#sidenav-tog0').on('click', function () {
            $('.overlay').removeClass('active');
            if (document.getElementById("sidenav-tog0") != null) {
                document.getElementById("sidenav-tog0").hidden = true;
            }
            if (document.getElementById("sidenav-tog") != null) {
                document.getElementById("sidenav-tog").hidden = false;
            }
            if (document.getElementById("collap_button") != null) {
                document.getElementById("collap_button").hidden = false;
            }
        });

        $('#sidenav-tog, #collap_button').on('click', function () {
            $('.overlay').addClass('active');
            if (document.getElementById("sidenav-tog") != null) {
                document.getElementById("sidenav-tog").hidden = true;
            }
            if (document.getElementById("sidenav-tog0") != null) {
                document.getElementById("sidenav-tog0").hidden = false;
            }
            if (document.getElementById("collap_button") != null) {
                document.getElementById("collap_button").hidden = true;
            }
        });
    }
});

const URL = document.URL
var lastfive = URL.substr(URL.length - 11)

if (lastfive.includes("/dashboard/")) {
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
};

if (document.URL.includes("/training/")) {
    $(document).ready(function () {
        var list_column_form = $("[id='id_column']");
        list_column_form[1].id = "id_column0";
        list_column_form[2].id = "id_column1";

        $("#id_column").change(function () {
            var x = $("#id_column option:selected").text();
            var i = $("#id_column").val();

            if (x == "DATE") {
                $("#id_column0").val("date");
                $("#date_form").css("display", "inline");
                $("#time_form").hide();
                $("#simple_search").hide();
                $("#simple_form_btn").hide();
                $("#date_form_btn").show();
                $("#time_form_btn").hide();
            }
            else if (x == "TIME") {
                $("#id_column1").val("time");
                $("#date_form").hide();
                $("#time_form").css("display", "inline");
                $("#simple_search").hide();
                $("#simple_form_btn").hide();
                $("#date_form_btn").hide();
                $("#time_form_btn").show();
            }
            else {
                $("#id_column").val(i);
                $("#date_form").hide();
                $("#time_form").hide();
                $("#simple_search").show();
                $("#simple_form_btn").show();
                $("#date_form_btn").hide();
                $("#time_form_btn").hide();
            }
        });
        $("#id_column0").change(function () {
            var y = $("#id_column0 option:selected").text();
            var j = $("#id_column0").val();
            if (y == "DATE") {
                $("#id_column0").val("date");
                $("#date_form").css("display", "inline");
                $("#time_form").hide();
                $("#simple_search").hide();
                $("#simple_form_btn").hide();
                $("#date_form_btn").show();
                $("#time_form_btn").hide();
            }
            else if (y == "TIME") {
                $("#id_column1").val("time");
                $("#date_form").hide();
                $("#time_form").css("display", "inline");
                $("#simple_search").hide();
                $("#simple_form_btn").hide();
                $("#date_form_btn").hide();
                $("#time_form_btn").show();
            }
            else {
                $("#id_column").val(j);
                $("#date_form").hide();
                $("#time_form").hide();
                $("#simple_search").show();
                $("#simple_form_btn").show();
                $("#date_form_btn").hide();
                $("#time_form_btn").hide();
            }
        });
        $("#id_column1").change(function () {
            var z = $("#id_column1 option:selected").text();
            var k = $("#id_column1").val();

            if (z == "DATE") {
                $("#id_column0").val("date");
                $("#date_form").css("display", "inline");
                $("#time_form").hide();
                $("#simple_search").hide();
                $("#simple_form_btn").hide();
                $("#date_form_btn").show();
                $("#time_form_btn").hide();
            }
            else if (z == "TIME") {
                $("#id_column1").val("time");
                $("#date_form").hide();
                $("#time_form").css("display", "inline");
                $("#simple_search").hide();
                $("#simple_form_btn").hide();
                $("#date_form_btn").hide();
                $("#time_form_btn").show();
            }
            else {
                $("#id_column").val(k);
                $("#date_form").hide();
                $("#time_form").hide();
                $("#simple_search").show();
                $("#simple_form_btn").show();
                $("#date_form_btn").hide();
                $("#time_form_btn").hide();
            }
        });        
    })
}