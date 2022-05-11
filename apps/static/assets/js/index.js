//Global script
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

// Training.html script
if (document.URL.includes("/training/")) {
    $(document).ready(function () {
        var list_column_form = $("[id='id_column']");
        list_column_form[1].id = "id_column0";
        list_column_form[2].id = "id_column1";

        $("#id_column").change(function () {
            var x = $("#id_column option:selected").text();
            var i = $("#id_column").val();

            if (x == "DEPARTMENT" || x == "DÉPARTEMENT") {
                $("#id_column0").val("department");
                $("#department_form").css("display", "inline");
                $("#commune_form").hide();
                $("#simple_search").hide();
                $("#simple_form_btn").hide();
                $("#department_form_btn").show();
                $("#commune_form_btn").hide();
            }
            else if (x == "COMMUNE") {
                $("#id_column1").val("commune");
                $("#department_form").hide();
                $("#commune_form").css("display", "inline");
                $("#simple_search").hide();
                $("#simple_form_btn").hide();
                $("#department_form_btn").hide();
                $("#commune_form_btn").show();
            }
            else {
                $("#id_column").val(i);
                $("#department_form").hide();
                $("#commune_form").hide();
                $("#simple_search").show();
                $("#simple_form_btn").show();
                $("#department_form_btn").hide();
                $("#commune_form_btn").hide();
            }
        });
        $("#id_column0").change(function () {
            var y = $("#id_column0 option:selected").text();
            var j = $("#id_column0").val();
            if (y == "DEPARTMENT" || y == "DÉPARTEMENT") {
                $("#id_column0").val("department");
                $("#department_form").css("display", "inline");
                $("#commune_form").hide();
                $("#simple_search").hide();
                $("#simple_form_btn").hide();
                $("#department_form_btn").show();
                $("#commune_form_btn").hide();
            }
            else if (y == "COMMUNE") {
                $("#id_column1").val("commune");
                $("#department_form").hide();
                $("#commune_form").css("display", "inline");
                $("#simple_search").hide();
                $("#simple_form_btn").hide();
                $("#department_form_btn").hide();
                $("#commune_form_btn").show();
            }
            else {
                $("#id_column").val(j);
                $("#department_form").hide();
                $("#commune_form").hide();
                $("#simple_search").show();
                $("#simple_form_btn").show();
                $("#department_form_btn").hide();
                $("#commune_form_btn").hide();
            }
        });
        $("#id_column1").change(function () {
            var z = $("#id_column1 option:selected").text();
            var k = $("#id_column1").val();

            if (z == "DEPARTMENT" || z == "DÉPARTEMENT") {
                $("#id_column0").val("department");
                $("#department_form").css("display", "inline");
                $("#commune_form").hide();
                $("#simple_search").hide();
                $("#simple_form_btn").hide();
                $("#department_form_btn").show();
                $("#commune_form_btn").hide();
            }
            else if (z == "COMMUNE") {
                $("#id_column1").val("commune");
                $("#department_form").hide();
                $("#commune_form").css("display", "inline");
                $("#simple_search").hide();
                $("#simple_form_btn").hide();
                $("#department_form_btn").hide();
                $("#commune_form_btn").show();
            }
            else {
                $("#id_column").val(k);
                $("#department_form").hide();
                $("#commune_form").hide();
                $("#simple_search").show();
                $("#simple_form_btn").show();
                $("#department_form_btn").hide();
                $("#commune_form_btn").hide();
            }
        });
    })
}
