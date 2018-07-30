var wildType = ["wild_type", "mutated", ""];
var assayType = ["functional", "binding", "phenotypic", ""];
var assayFormat = ["biochemical", "cell_based", "cell_free", "physiochemical", "tissue", "organism_based", ""];
var assaySubtype = ["binding_saturation", "binding_reversible", "binding_irreversible", "enzyme_activity", "process", "reporter_gene", "signalling", "uptake", "viability", ""];
var inhibitorType = ["competitive_inhibitor", "non_competitive_inhibitor", "allosteric_inhibitor", ""];
var detectionTech = ["fluoresecence", "luminescence", "spectrophotometry", "radiometry", "microscopy", "label_free_technology", "fluorescence_polarization", "TRF", "TR_FRET", "AlphaScreen", "qPCR", "termal_shift", ""];
var EMA = ["activation", "cytotoxocity", "growth_inhibition", "inhibition", "inverse_agonist", ""];


$(document).ready(function () {



        // using jQuery
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');
    
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
         }
    });

    $('.search').find("input").keypress(function (b) {
        if (b.which == 10 || b.which == 13) {
            $('.search').find('a')[0].click();
        }
    });

    // $("#logout").on('click', function (e) {

    //     e.preventDefault();

    //     $.ajax({
    //         url: "/GUI/Login.aspx/logout", // url for login
    //         type: "POST",
    //         dataType: "json",
    //         contentType: "application/json",
    //         success: function (status) {

    //             location.reload();
    //         }


    //     });
        
    // });
    //$('#Form1').validator();
    $("#login-modal form").validator().on('submit', function (e) {

        
        if (!e.isDefaultPrevented()) {
            e.preventDefault();
            var data = { "userid": $("#userid").val(), "pass": $("#password").val() };

            $.ajax({
                url: "/GUI/Login.aspx/validateuser", // url for login
                type: "POST",
                data: JSON.stringify(data),
                dataType: "json",
                contentType: "application/json",
                success: function (status) {
                    if (status.d != "") {
                        location.reload();
                    } else {
                        $('#login-modal .error').show();
                        shakeForm('#login-modal');
                    }

                }


            });
        }
    });


    $('#feedback_form').validator().on('submit', function (e) {
       
        if (!e.isDefaultPrevented()) {
            e.preventDefault();
            $.ajax({
                type: 'POST',
                dataType: "json",
                contentType: "application/json",
                url: '/feedback/create/',
                data: JSON.stringify({ "email": $('#email').val(), "institution": $('#organization').val(), "comment": $('#comment').val(), "subject": $('#subject').val() }),

                success: function () {
                    alertify.success('Thank you! for your feedback');
                    $("#feedback-form").modal('hide');
                }
            });
        } 
    });
});

function shakeForm(element) {
    var l = 20;
    for (var i = 0; i < 10; i++)
        $(element).animate({
            'margin-left': "+=" + (l = -l) + 'px',
            'margin-right': "-=" + l + 'px'
        }, 50);

}
function SearchText() {   // function for for autosuggest, use weblink incase of hosted application else use local host
    $(".autosuggest").autocomplete({
        source: function (request, response) {

            var textbox = parseInt(document.getElementById('txtSearchClient').value.length);
           
            if (textbox >= 3) {
             
                $.ajax({
                    type: "POST",
                    contentType: "application/json; charset=utf-8",
                    //url: "https://drugtargetcommons.fimm.fi/Home.aspx/GetAutoCompleteData",
                    url: "/autosuggest/",

                    data: JSON.stringify({'suggestedtext': document.getElementById('txtSearchClient').value }),

                    dataType: "json",
                    success: function (data) {
                        isSelected = true;
                        response(data);
                    },
                    error: function (xhr, status, error) {
                        //alert("Error is : " + status + "-" + xhr.status + "-" + xhr.responseText);
                    }
                });
                //alert("webservice done succesfully");
            }
        }
    });
}

