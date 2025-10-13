var django = {
    "jQuery": jQuery.noConflict(true)
};
var jQuery = django.jQuery;
var $ = jQuery;

(function ($) {
    $(function () {
        $(document).ready(function () {
            // Initialize event listeners
            ru.istanbul.init_events();

        });
    });
})(django.jQuery);


// based on the type, action will be loaded

// var $ = django.jQuery.noConflict();

var ru = (function ($, ru) {
    "use strict";

    ru.istanbul = (function ($, config) {
        // Define variables for ru.basic here
        var loc_divErr = "basic_err",
            loc_urlStore = "",      // Keep track of URL to be shown
            dummy = 1;

        // Private methods specification
        var private_methods = {
            /**
             * aaaaaaNotVisibleFromOutside - example of a private method
             * @returns {String}
             */
            aaaaaaNotVisibleFromOutside: function () {
                return "something";
            },
            /** 
             *  errClear - clear the error <div>
             */
            errClear: function () {
                $("#" + loc_divErr).html("");
            },

            /** 
             *  errMsg - show error message in <div> loc_divErr
             */
            errMsg: function (sMsg, ex) {
                var sHtml = "Error in [" + sMsg + "]<br>";
                if (ex !== undefined && ex !== null) {
                    sHtml = sHtml + ex.message;
                }
                $("#" + loc_divErr).html(sHtml);
            }
        }
        // Public methods
        return {
          init_events: function () {
            var imageurl = "",
                elMapOpen = null;

            try {
              // Adapt the istanbul background image url
              if ($(".istanbul-banner").length > 0) {
                imageurl = $(".istanbul-banner").first().attr("img");
                $(".istanbul-banner").css("background-image", 'url("' + imageurl + '")');
              }

              // Check if we need to call goto_view
              elMapOpen = $("#do_open_map");
              if ($(elMapOpen).length > 0) {
                // We need to open the map
                $("#maplistcarto").click();
              }

              // Check for .rel-image
              $(".rel-image").unbind("click").on("click", function (event) {
                var elThis = $(this);

                // Prevent clicking through
                // event.preventDefault;
                ru.istanbul.show_picture(elThis);
              });

            } catch (ex) {
              private_methods.errMsg("init_events", ex);
            }
          },

          /**
           * goto_view
           *   Open the mapview or the listview
           *
           */
          goto_view: function (elStart, sView, sMapType) {
            var height = 0,
              footer_pos = 0,
              width = 0,
              top = 25,
              options = {},
              id_mapview = "#basicmap",
              id_listview = "#basiclist_top";
            try {
              switch (sView) {
                case "map":   // Open the map-view
                  $(id_listview).addClass("hidden");
                  $(id_mapview).removeClass("hidden");
                  $(".map-tree-switch").addClass("map-active");
                  $(".map-list-switch").addClass("map-active");

                  if ($(".werkstuk-map").length > 0) {
                    // Calculate and set the height
                    if ($("footer").length === 0) {
                      footer_pos = $("div[class=col-1]").last().position().top;
                    } else {
                      footer_pos = $("footer").position().top;
                    }
                    height = footer_pos - $(".werkstuk-map").position().top - 85;
                    width = $(id_mapview).width();
                    top = $("nav").height() - 15;
                    $(".werkstuk-map").css("height", height + "px");
                    $(".werkstuk-map").css("width", width + "px");
                  }

                  // Initiate showing a map
                  if (sMapType === undefined || sMapType === "") { sMapType = "osm"; }
                  options['filter'] = "basiclist_filter";
                  options['map'] = "werkstuk_map";
                  options['title'] = "map_view_title";
                  options['maptype'] = sMapType;
                  ru.mapview.list_to_map(elStart, options);
                  break;
                case "tree":  // Open the treeview
                  $(id_mapview).addClass("hidden");
                  $(id_listview).removeClass("hidden");
                  $(".map-tree-switch").removeClass("map-active");
                  break;
                case "list":  // Open the listview
                  $(id_mapview).addClass("hidden");
                  $(id_listview).removeClass("hidden");
                  $(".map-list-switch").removeClass("map-active");
                  break;
              }

            } catch (ex) {
              private_methods.errMsg("goto_view", ex);
            }
          },

          /**
           * show_picture
           *   Make sure that the modal shows the correct picture and additional information
           *
           */
          show_picture: function (elStart) {
            var elImage = null,
              sImgText = "",
              elInfo = null;

            try {
              // Determine the locations
              elImage = $(".modal-image").first();
              elInfo = $(".modal-info").first();

              // copy the image
              $(elImage).html($(elStart).find("img").first().parent().html());
              // Make sure the col-md-12 class is removed here
              $(elImage).find(".col-md-12").removeClass("col-md-12");

              // Copy the information
              $(elInfo).html($(elStart).attr("info"));
            } catch (ex) {
              private_methods.errMsg("show_picture", ex);
            }
          }


            // LAST POINT
        }
    }($, ru.config));

    return ru;
}(jQuery, window.ru || {})); // window.ru: see http://stackoverflow.com/questions/21507964/jslint-out-of-scope

