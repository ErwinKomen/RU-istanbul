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
                var imageurl = "";

                try {
                    // Adapt the istanbul background image url
                    if ($(".istanbul-banner").length > 0) {
                        imageurl = $(".istanbul-banner").first().attr("img");
                        $(".istanbul-banner").css("background-image", 'url("' + imageurl + '")');
                    }


                } catch (ex) {
                    private_methods.errMsg("init_typeahead", ex);
                }
            }

            // LAST POINT
        }
    }($, ru.config));

    return ru;
}(jQuery, window.ru || {})); // window.ru: see http://stackoverflow.com/questions/21507964/jslint-out-of-scope

