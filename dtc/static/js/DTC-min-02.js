$(document).ready(function () {
     
   
    $('.search').find("input").keypress(function(b) {
        if (b.which == 10 || b.which == 13) {
            $('.search').find('a')[0].click();
        }
    });
         
   
    
    //var a = $(".selection-container");
    //$(window).scroll(function () {
    //    if ($(this).scrollTop() > 136) {
    //        a.addClass("f-selection")
    //    } else {
    //        a.removeClass("f-selection")
    //    }
    //});
    /*
      $("#search").focus();
      $("a.boxlink").click(function() {
          if (location.pathname.replace(/^\//, "") == this.pathname.replace(/^\//, "") && location.hostname == this.hostname) {
              smooth_scroll($(this.hash))
          }
      });
    */
    fullscreen = function (b) {
        fulltarget = $(b);
        target = $("#fullscreen-dropback");
        fulltarget.collapse("show");
        fulltarget.parent().addClass("fulltarget");
        target.removeClass("smallreport");
        target.addClass("fullreport");
        $(window).resize()
    };
    smallscreen = function (b) {
        fulltarget = $(b);
        target = $("#fullscreen-dropback");
        fulltarget.parent().removeClass("fulltarget");
        fulltarget.parent().height("auto");
        target.addClass("smallreport");
        target.removeClass("fullreport");
        smooth_scroll(fulltarget);
        $(window).resize()
    };
    share_report_toggle = function (b, c) {
        var c = c || false;
        if (c) {
            $("#" + b + " .toolbar").show();
            share_alert = $("#" + b + "-share").hide()
        } else {
            share_alert = $("#" + b + "-share");
            share_input = $("#" + b + "-share input")[0];
            share_input.value = get_report_tab_link(b);
            share_alert.show();
            $("#" + b + " .toolbar").hide()
        }
    };
    downloads_report = function (b) {
        loc = get_report_tab_link(b);
        window.location.href = "/downloads?report=True&file=" + encodeURIComponent(loc)
    };
    get_report_tab_link = function (b) {
        active_tab = $("#" + b + " .nav-pills li.active a");
        var d = document.location.href.split("#")[0];
        if (active_tab.length > 0) {
            var c = active_tab[0].text.toLowerCase();
            return d + "#" + b + ":" + c + ":full"
        } else {
            return d + "#" + b + ":full"
        }
    };
    smooth_scroll = function (b) {
        b.collapse("show");
        if (this.hash) {
            b = b.length ? b : $("[name=" + this.hash.slice(1) + "]")
        }
        if (b.length) {
            $("html,body").animate({
                scrollTop: b.offset().top - 150
            }, 1000);
            return false
        }
    };
    submit_example = function (c) {
        var b = $("#search")[0];
        b.value = c;
        setTimeout(function () {
            $("#search-form").submit()
        }, 500)
    };
    responsiveSVGs = {};
    resize_elements = function () {
        $("#fullscreen-dropback").css("min-height", $(window).height());
        if ($("#fullscreen-dropback.fullreport").length > 0) {
            $(".panel.fulltarget").height($(window).height() * 0.9)
        }
        for (svg in responsiveSVGs) {
            f = responsiveSVGs[svg]["func"];
            args = responsiveSVGs[svg]["args"];
            f.apply(this, args)
        }
    };
    $(window).resize(function () {
        resize_elements()
    })
});
$(window).load(function () {
    function b(g) {
        return g.charAt(0).toUpperCase() + g.slice(1)
    }
    var d = function (g, h) {
        $(g + " .nav-pills a").filter(function (i) {
            return $(this).text() === h
        }).click()
    };
    if (location.href.indexOf("#") != -1) {
        var a = $(window).scrollTop();
        var e = document.location.hash.split(":");
        var c = "";
        while (e.length > 0) {
            hashbit = e.shift();
            if (c == "") {
                c = hashbit
            } else {
                if (hashbit == "full") {
                    fullscreen(c)
                } else {
                    d(c, b(hashbit))
                }
            }
        }
        smooth_scroll($(c))
    }
    $("#fullscreen-dropback").css("min-height", $(window).height())
});