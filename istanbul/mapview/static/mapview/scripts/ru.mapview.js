var django = {
  "jQuery": jQuery.noConflict(true)
};
var jQuery = django.jQuery;
var $ = jQuery;

String.prototype.format = function () {
  var formatted = this;
  for (var arg in arguments) {
    formatted = formatted.replace("{" + arg + "}", arguments[arg]);
  }
  return formatted;
};


var ru = (function ($, ru) {
  "use strict";

  ru.mapview = (function ($, config) {
    // Local variables for ru.mapview
    const tileUrl_1 = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
        tileUrl = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        attribution_1 = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' +
                      ' contributors &copy; <a href="https://carto.com/attribution">CARTO</a>',
        attribution = '&copy; <a href="https://www.openstreetmap.org/copyright" title="Open Street Map">OSM</a>',
        tiles = L.tileLayer(tileUrl, { attribution }),
        mapview_tiles = L.tileLayer(tileUrl, { attribution }),
        // Trial: for fontawesome *4*
        fontAwesomeIcon = L.divIcon({
          html: '<i class="fa fa-map-marker fa-alt" style="color: darkred;"></i>',
          iconSize: [20, 20],
          className: 'myDivIcon'
        });
    var main_map_object = null,   // Leaflet map object
        loc_sWaiting = " <span class=\"glyphicon glyphicon-refresh glyphicon-refresh-animate\"></span>",
        loc_oms = null,
        loc_divErr = "diadict_err",
        loc_layerDict = {},
        loc_layerList = [],
        loc_overlayMarkers = {},
        loc_colorDict = {},
        loc_trefwoord = [],
        loc_colors = '#0fba62,#5aa5c4,black,#345beb,#e04eed,#ed4c72,#1e662a,#c92f04,#e39817'.split(',');
    
    // Private methods specifiction
    var private_methods = {
      errMsg: function(sMsg, ex) {
        var sHtml = "";
        if (ex === undefined) {
          sHtml = "Error: " + sMsg;
        } else {
          sHtml = "Error in [" + sMsg + "]<br>" + ex.message;
        }
        sHtml = "<code>" + sHtml + "</code>";
        $("#" + loc_divErr).html(sHtml);
      },

      errClear: function() {
        $("#" + loc_divErr).html("");
      },

      /**
       * create_instance
       * 
       * Create a new instance of an object
       */
      create_instance: function (elStart) {
        var targeturl = "",
            data = null,
            frm = null;
        try {
          // Get the form
          frm = $(elStart).find("form").first();
          // Get the targeturl
          targeturl = $(frm).attr("targeturl");
          // Get the data
          data = frm.serializeArray();
          // Submit a POST to create the new instance
          $(frm).attr("action", targeturl);
          $(frm).attr("method", "post");
          $(frm).submit();
          //$.post(targeturl, data);

        } catch (ex) {
          errMsg("create_instance", ex);
        }
      },

      /**
       * make_icon
       * 
       * @param {str}   name, representing category
       * @returns {bool}
       */
      make_icon: function(name) {
        var oBack = {};

        try {
          oBack = {
            className: name,
            // Note: for fontawesome *4*
            // html: '<i class="fa fa-map-marker fa-alt" style="font-size: 24px; color: '+loc_colorDict[name]+';"></i>',
            // Note: for fontawesome *5*
            html: '<i class="fas fa-map-marker-alt" style="color: ' + loc_colorDict[name] + ';"></i>',
            iconAncor: [3, 15]
          };
          return L.divIcon(oBack);
        } catch (ex) {
          errMsg("make_icon", ex);
        }
      },

      /**
       * make_geo
       * 
       * @param {entry}   entry object
       * @returns {bool}
       */
      make_geo: function (entry) {
        var point,    // Latitude, longitude array
          trefwoord = "",
          popup = "",
          idx = -1,
          marker;

        try {
          // Validate
          if (entry.point === null || entry.point === "") { return false; }
          // Get the trefwoord
          trefwoord = entry.trefwoord;
          if (loc_trefwoord.indexOf(trefwoord) < 0) {
            // Add it
            loc_trefwoord.push(trefwoord);
            // Set the color table
            idx = loc_trefwoord.indexOf(trefwoord);
            loc_colorDict[trefwoord] = loc_colors[idx % 10];
          }
          // Get to the point
          point = entry.point.split(",").map(Number);

          // Set the geometrical entry
          marker = L.geoJSON(entry.geojson) //.addTo(main_map_object);

          // Create marker for this point
          //marker = L.marker(point, { icon: private_methods.make_icon(trefwoord) });

          // Add a popup to the marker
          //popup = entry.woord + "\n (" + entry.kloeke + ": " + entry.stad + ")";
          popup = entry.pop_up;
          marker.bindPopup(popup, { maxWidth: 200, closeButton: false });

          // Add to OMS
          if (loc_oms !== null) { loc_oms.addMarker(marker); }
          // Add marker to the trefwoord collectionlayer
          if (loc_layerDict[trefwoord] === undefined) {
            loc_layerDict[trefwoord] = [];
          }
          loc_layerDict[trefwoord].push(marker);
        } catch (ex) {
          private_methods.errMsg("make_geo", ex);
        }
      },
 
      /**
       * make_marker
       * 
       * @param {entry}   entry object
       * @returns {bool}
       */
      make_marker: function (entry) {
        var point,    // Latitude, longitude array
            trefwoord = "",
            popup = "",
            idx = -1,
            marker;

        try {
          // Validate
          if (entry.point === null || entry.point === "") { return false; }
          // Get the trefwoord
          trefwoord = entry.trefwoord;
          if (loc_trefwoord.indexOf(trefwoord) < 0) {
            // Add it
            loc_trefwoord.push(trefwoord);
            // Set the color table
            idx = loc_trefwoord.indexOf(trefwoord);
            loc_colorDict[trefwoord] = loc_colors[idx % 10];
          }
          // Get to the point
          point = entry.point.split(",").map(Number);

          // Create marker for this point
          marker = L.marker(point, { icon: private_methods.make_icon(trefwoord) });

          // Add a popup to the marker
          //popup = entry.woord + "\n (" + entry.kloeke + ": " + entry.stad + ")";
          popup = entry.pop_up;
          marker.bindPopup(popup, { maxWidth: 200, closeButton: false });

          // Add to OMS
          if (loc_oms !== null) { loc_oms.addMarker(marker); }
          // Add marker to the trefwoord collectionlayer
          if (loc_layerDict[trefwoord] === undefined) {
            loc_layerDict[trefwoord] = [];
          }
          loc_layerDict[trefwoord].push(marker);
        } catch (ex) {
          private_methods.errMsg("make_marker", ex);
        }
      },

      leaflet_editable: function (this_map) {
        try {
          // Editable shapes
          L.EditControl = L.Control.extend({
            options: {
              position: 'topleft',
              callback: null,
              kind: '',
              html: ''
            },

            onAdd: function (map) {
              var container = L.DomUtil.create('div', 'leaflet-control leaflet-bar'),
                link = L.DomUtil.create('a', '', container);

              link.href = '#';
              link.title = 'Create a new ' + this.options.kind;
              link.innerHTML = this.options.html;
              L.DomEvent.on(link, 'click', L.DomEvent.stop)
                .on(link, 'click', function () {
                  window.LAYER = this.options.callback.call(map.editTools);
                }, this);

              return container;
            }
          });
          L.NewMarkerControl = L.EditControl.extend({
            options: {
              position: 'topleft',
              callback: this_map.editTools.startMarker,
              kind: 'marker',
              html: '🖈'
            }
          });
          L.NewLineControl = L.EditControl.extend({
            options: {
              position: 'topleft',
              callback: this_map.editTools.startPolyline,
              kind: 'line',
              html: '\\/\\'
            }
          });
          L.NewPolygonControl = L.EditControl.extend({
            options: {
              position: 'topleft',
              callback: this_map.editTools.startPolygon,
              kind: 'polygon',
              html: '▰'
            }
          });

          this_map.addControl(new L.NewMarkerControl());
          this_map.addControl(new L.NewLineControl());
          this_map.addControl(new L.NewPolygonControl());
          // Add delete capabilities
          var clickShape = function (e) {
            var x = 1, arPoints = null, sGeoJson;
            // Is editing enabled?
            if (this.editEnabled()) {
              // Is this a ctrl or a shift?
              if (e.originalEvent.ctrlKey || e.originalEvent.metaKey) {
                // Ctrl + click: delete
                this.editor.deleteShapeAt(e.latlng);
              } else if (e.originalEvent.shiftKey) {
                // Shift + click: add location based on this shape
                //arPoints = e.target.getLatLngs().map(function (point) { return [point.lat, point.lng]; });
                sGeoJson = JSON.stringify(e.target.toGeoJSON());
                $("#image_polygon").val(sGeoJson);
                private_methods.create_instance("#create_image");
              }
            }
          };
          var clickMarker = function (e) {
            var x = 1, sGeoJson = ""; // coords = null;

            // Is editing enabled?
            if (this.editEnabled()) {
              // Is this a ctrl or a shift?
              if (e.originalEvent.ctrlKey || e.originalEvent.metaKey) {
                // Ctrl + click: delete
                e.target.remove();
              } else if (e.originalEvent.shiftKey) {
                // Shift + click: add location based on this marker
                // coords = e.target.getLatLng();
                sGeoJson = JSON.stringify(e.target.toGeoJSON());
                $("#marker_loc").val(sGeoJson);
                private_methods.create_instance("#create_location");
              }

            }
          };
          this_map.on('layeradd', function (e) {
            // Ctrl + click is deleting the selected shape
            if (e.layer instanceof L.Path) {
              e.layer.on('click', L.DomEvent.stop).on('click', clickShape, e.layer);
            } else if (e.layer instanceof L.Marker) {
              e.layer.on('click', L.DomEvent.stop).on('click', clickMarker, e.layer);
            }
            // Double click is toggling the edit mode of the particular shape
            if (e.layer instanceof L.Path) {
              e.layer.on('dblclick', L.DomEvent.stop).on('dblclick', e.layer.toggleEdit);
            } else if (e.layer instanceof L.Marker) {
              e.layer.on('dblclick', function (ev2) {
                var x = ev2;
            });
            }
          });

          // Add event listener to the map
          this_map.addEventListener('mousedown', function (event) {
            var lat = Math.round(event.latlng.lat * 100000) / 100000,
                lng = Math.round(event.latlng.lng * 100000) / 100000,
                ctrl = event.originalEvent.ctrlKey,
                shift = event.originalEvent.shiftKey;

            this_map.position = lat + "," + lng;
            console.log("Position = " + this_map.position);
          });

        } catch (ex) {
          private_methods.errMsg("leaflet_editable", ex);
        }
      },

      leaflet_scrollbars: function () {
        var layers_list = "section.leaflet-control-layers-list",
            layers_scrollbar = "leaflet-control-layers-scrollbar",
            height = 300;

        try {
          //if ($(layers_list)[0].scrollHeight > height) {
          //  $(layers_list).addClass(layers_scrollbar);
          //  $(layers_list)[0].style.height = height + 'px';
          //}
          height = $(layers_list)[0].clientHeight;
          if ($(layers_list)[0].scrollHeight > height) {
            $(layers_list).addClass(layers_scrollbar);
            $(layers_list)[0].style.height = height + 'px';
          }
        } catch (ex) {
          private_methods.errMsg("leaflet_scrollbars", ex);
        }
      }

    }

    // Public methods
    return {
      /**
       * legend_click 
       *    Toggle 'minus' and 'plus' glyphicon, indicating whether the legend includes or excludes all items
       * 
       * @param {dom}   where this request starts from
       * @returns {void}
       */
      legend_click: function(el) {
        var el_sign = null,
            mod_cont = null,
            lfl_sect = null;

        try {
          mod_cont = $(el).closest(".modal-content");
          lfl_sect = $(mod_cont).find("section.leaflet-control-layers-list");
          // Get the minus/plus sign
          el_sign = $(el).find("span.glyphicon").first();
          // Action depends on what the current status is
          if ($(el_sign).hasClass("glyphicon-minus")) {
            // Change from minus to plus
            $(el_sign).removeClass("glyphicon-minus");
            $(el_sign).addClass("glyphicon-plus");
            // Uncheck all checkbox values ...
            $(lfl_sect).find(".leaflet-control-layers-selector").each(function () {
              var $this = $(this);
              $this[0].checked = true;
              $this.click();
            });
          } else {
            // Change from plus to minus
            $(el_sign).removeClass("glyphicon-plus");
            $(el_sign).addClass("glyphicon-minus");
            // Check all checkbox values ...
            $(lfl_sect).find(".leaflet-control-layers-selector").each(function () {
              var $this = $(this);
              $this[0].checked = false;
              $this.click();
            });
          }

        } catch (ex) {
          private_methods.errMsg("lemma_map", ex);

        }
      },

      /**
       * lemma_map 
       *    Show all dialect words for the particular Lemma
       *    The dialect words are grouped per 'trefwoord'
       * 
       * @param {dom}   where this request starts from
       * @returns {void}
       */
      lemma_map: function (el) {
        var frm = "#lemmasearch",
            map_title = "#map_view_title",
            map_id = "map_lemma",
            map_view = "#map_view",
            data = null,
            entries = null,
            lemma = "",
            label = "",
            point = null,
            points = [],
            keywords = [],
            polyline = null,
            oOverlay = null,
            i = 0,
            idx = 0,
            targeturl = "",
            targetid = "";

        try {
          // Get the form data
          //frm = $("form").first();
          data = $(frm).serializeArray();
          targeturl = $(el).attr("targeturl");
          targetid = $(el).attr("targetid");

          // Show the modal
          $(map_view).modal("toggle");

          // Possibly remove what is still there
          if (main_map_object !== null) {
            // Remove tile layer from active map
            tiles.remove()
            // Remove the actual map
            try {
              main_map_object.remove();
            } catch (ex) {
              i = 0;
            }
            main_map_object = null;
            // Reset the 
          }
          // Indicate we are waiting
          $("#" + map_id).html(loc_sWaiting);
          if (points.length > 0) points.clear();
          // Other initializations
          loc_layerDict = {};
          loc_layerList = [];
          loc_trefwoord = [];
          loc_colorDict = {};
          loc_overlayMarkers = {};

          // Post the data to the server
          $.post(targeturl, data, function (response) {
            var key, layername, kvalue;

            // Sanity check
            if (response !== undefined) {
              if (response.status == "ok") {
                if ('entries' in response) {
                  entries = response['entries'];
                  label = response['label'];
                  // Make sure the label shows
                  $(map_title).html("Begrip: [" + label + "]");

                  if (main_map_object == null) {
                    // now get the first point
                    for (i = 0; i < entries.length; i++) {
                      if (entries[i].point !== null && entries[i].point !== "") {
                        // Add point to the array of points to find out the bounds
                        points.push(entries[i].point.split(",").map(Number));
                        // Create a marker for this point
                        private_methods.make_marker(entries[i]);
                      }
                    }
                    if (points.length > 0) {
                      // Get the first point
                      point = points[0];
                      // CLear the map section from the waiting symbol
                      $("#" + map_id).html();
                      // Set the starting map
                      main_map_object = L.map(map_id).setView([point[0], point[1]], 12);
                      // Add it to my tiles
                      tiles.addTo(main_map_object);
                      // https://github.com/jawj/OverlappingMarkerSpiderfier-Leaflet to handle overlapping markers
                      loc_oms = new OverlappingMarkerSpiderfier(main_map_object, { keepSpiderfied: true });

                      // Convert layerdict into layerlist
                      for (key in loc_layerDict) {
                        loc_layerList.push({ key: key, value: loc_layerDict[key], freq: loc_layerDict[key].length });
                      }
                      // sort the layerlist
                      loc_layerList.sort(function (a, b) {
                        return b.freq - a.freq;
                      });

                      // Make a layer of markers from the layerLIST
                      for (idx in loc_layerList) {
                        key = loc_layerList[idx].key;
                        layername = '<span style="color: ' + loc_colorDict[key] + ';">' + key + '</span>' + ' (' + loc_layerList[idx].freq + ')';
                        kvalue = loc_layerList[idx].value;
                        if (kvalue.length > 0) {
                          try {
                            loc_overlayMarkers[layername] = L.layerGroup(kvalue).addTo(main_map_object);
                          } catch (ex) {
                            i = 100;
                          }
                        }
                      }
                      L.control
                        .layers({}, loc_overlayMarkers, { collapsed: false })
                        .addTo(main_map_object)

                      // Set map to fit the markers
                      polyline = L.polyline(points);
                      if (points.length > 1) {
                        main_map_object.fitBounds(polyline.getBounds());
                      } else {
                        main_map_object.setView(points[0], 12);
                      }

                      private_methods.leaflet_scrollbars();

                    }
                  }

                  // Make sure it is redrawn
                  // main_map_object.invalidateSize();
                  setTimeout(function () {
                    main_map_object.invalidateSize();
                    if (points.length > 1) {
                      main_map_object.fitBounds(polyline.getBounds());
                    } else {
                      main_map_object.setView(points[0], 12);
                    }

                    private_methods.leaflet_scrollbars();

                  }, 200);
                  // Debug  break point
                  i = 100;
                } else {
                  errMsg("Response is okay, but [html] is missing");
                }
                // Knoppen weer inschakelen

              } else {
                if ("msg" in response) {
                  errMsg(response.msg);
                } else {
                  errMsg("Could not interpret response " + response.status);
                }
              }
            }
          });
        } catch (ex) {
          private_methods.errMsg("lemma_map", ex);
        }
      },

      /**
       * dialect_map 
       *    Show all dialect dialect locations available
       *    The dialect words are grouped around the *first kloeke letter*
       * 
       * @param {dom}   where this request starts from
       * @returns {void}
       */
      dialect_map: function (el) {
        var frm = "#dialectsearch",         // On dialect_list.html
            map_title = "#map_view_title",  // Part of map_view.html
            map_id = "map_lemma",           // Part of map_view.html
            map_view = "#map_view",         // Part of map_view.html
            data = null,
            entries = null,
            lemma = "",
            label = "",
            point = null,
            points = [],
            keywords = [],
            polyline = null,
            oOverlay = null,
            i = 0,
            idx = 0,
            targeturl = "",
            targetid = "";

        try {
          // Get the form data
          //frm = $("form").first();
          data = $(frm).serializeArray();
          targeturl = $(el).attr("targeturl");
          targetid = $(el).attr("targetid");

          // Show the modal
          $(map_view).modal("toggle");

          // Possibly remove what is still there
          if (main_map_object !== null) {
            // Remove tile layer from active map
            tiles.remove()
            // Remove the actual map
            try {
              main_map_object.remove();
            } catch (ex) {
              i = 0;
            }
            main_map_object = null;
            // Reset the 
          }
          // Indicate we are waiting
          $("#" + map_id).html(loc_sWaiting);
          if (points.length > 0) points.clear();
          // Other initializations
          loc_layerDict = {};
          loc_layerList = [];
          loc_trefwoord = [];           // THis now contains the first letter of the Kloeke Codes
          loc_colorDict = {};
          loc_overlayMarkers = {};

          // Post the data to the server
          $.post(targeturl, data, function (response) {
            var key, layername, kvalue;

            // Sanity check
            if (response !== undefined) {
              if (response.status == "ok") {
                if ('entries' in response) {
                  entries = response['entries'];
                  label = response['label'];
                  // Make sure the label shows
                  $(map_title).html("Begrip: [" + label + "]");

                  if (main_map_object == null) {
                    // now get the first point
                    for (i = 0; i < entries.length; i++) {
                      if (entries[i].point !== null && entries[i].point !== "") {
                        // Add point to the array of points to find out the bounds
                        points.push(entries[i].point.split(",").map(Number));
                        // Create a marker for this point
                        private_methods.make_marker(entries[i]);
                      }
                    }
                    if (points.length > 0) {
                      // Get the first point
                      point = points[0];
                      // CLear the map section from the waiting symbol
                      $("#" + map_id).html();
                      // Set the starting map
                      main_map_object = L.map(map_id).setView([point[0], point[1]], 12);
                      // Add it to my tiles
                      tiles.addTo(main_map_object);
                      // https://github.com/jawj/OverlappingMarkerSpiderfier-Leaflet to handle overlapping markers
                      loc_oms = new OverlappingMarkerSpiderfier(main_map_object, { keepSpiderfied: true });

                      // Convert layerdict into layerlist
                      for (key in loc_layerDict) {
                        loc_layerList.push({ key: key, value: loc_layerDict[key], freq: loc_layerDict[key].length });
                      }
                      // sort the layerlist
                      loc_layerList.sort(function (a, b) {
                        return b.freq - a.freq;
                      });

                      // Make a layer of markers from the layerLIST
                      for (idx in loc_layerList) {
                        key = loc_layerList[idx].key;
                        layername = '<span style="color: ' + loc_colorDict[key] + ';">' + key + '</span>' + ' (' + loc_layerList[idx].freq + ')';
                        kvalue = loc_layerList[idx].value;
                        if (kvalue.length > 0) {
                          try {
                            loc_overlayMarkers[layername] = L.layerGroup(kvalue).addTo(main_map_object);
                          } catch (ex) {
                            i = 100;
                          }
                        }
                      }
                      L.control
                        .layers({}, loc_overlayMarkers, { collapsed: false })
                        .addTo(main_map_object)

                      // Set map to fit the markers
                      polyline = L.polyline(points);
                      if (points.length > 1) {
                        main_map_object.fitBounds(polyline.getBounds());
                      } else {
                        main_map_object.setView(points[0], 12);
                      }

                      private_methods.leaflet_scrollbars();

                    }
                  }

                  // Make sure it is redrawn
                  // main_map_object.invalidateSize();
                  setTimeout(function () {
                    main_map_object.invalidateSize();
                    if (points.length > 1) {
                      main_map_object.fitBounds(polyline.getBounds());
                    } else {
                      main_map_object.setView(points[0], 12);
                    }

                    private_methods.leaflet_scrollbars();

                  }, 200);
                  // Debug  break point
                  i = 100;
                } else {
                  errMsg("Response is okay, but [html] is missing");
                }
                // Knoppen weer inschakelen

              } else {
                if ("msg" in response) {
                  errMsg(response.msg);
                } else {
                  errMsg("Could not interpret response " + response.status);
                }
              }
            }
          });
        } catch (ex) {
          private_methods.errMsg("dialect_map", ex);
        }
      },

      /**
       * language_map 
       *    Show all points selected by the language listview - provided these points have coordinates
       *    The dialect words are grouped around their type (?)
       * 
       * @param {dom}   where this request starts from
       * @returns {void}
       */
      language_map: function (el) {
        var frm = "#famtree_main",    // On family_languages.html
          frm2 = null,
          id_filter = "#basiclist_filter",
          map_id = "werkstuk_map",    // Part of map_view_full.html
          data = null,
          entries = null,
          lemma = "",
          label = "",
          point = null,
          points = [],
          keywords = [],
          polyline = null,
          oOverlay = null,
          i = 0,
          idx = 0,
          targeturl = "",
          targetid = "";

        try {
          // Figure out which form to take
          frm2 = $(el).closest("form");
          if ($(frm2).length > 0) {
            frm = $(frm2).first();
          } else if ($(id_filter).length > 0) {
            frm = $(id_filter).first();
          }
          // Get the form data
          data = $(frm).serializeArray();
          targeturl = $(el).attr("targeturl");
          targetid = $(el).attr("targetid");

          // Possibly remove what is still there
          if (main_map_object !== null) {
            // Remove tile layer from active map
            tiles.remove()
            // Remove the actual map
            try {
              main_map_object.remove();
            } catch (ex) {
              i = 0;
            }
            main_map_object = null;
            // Reset the 
          }
          // Indicate we are waiting
          $("#" + map_id).html(loc_sWaiting);
          if (points.length > 0) points.clear();
          // Other initializations
          loc_layerDict = {};
          loc_layerList = [];
          loc_trefwoord = [];           // THis now contains the first letter of the Kloeke Codes
          loc_colorDict = {};
          loc_overlayMarkers = {};

          // Post the data to the server
          $.post(targeturl, data, function (response) {
            var key, layername, kvalue;

            // Sanity check
            if (response !== undefined) {
              if (response.status == "ok") {
                if ('entries' in response) {
                  entries = response['entries'];
                  label = response['label'];

                  if (main_map_object == null) {
                    // now get the first point
                    for (i = 0; i < entries.length; i++) {
                      if (entries[i].point !== null && entries[i].point !== "") {
                        // Add point to the array of points to find out the bounds
                        points.push(entries[i].point.split(",").map(Number));
                        // Create a marker for this point
                        private_methods.make_marker(entries[i]);
                      }
                    }
                    if (points.length > 0) {
                      // Get the first point
                      point = points[0];
                      // CLear the map section from the waiting symbol
                      $("#" + map_id).html();
                      // Set the starting map
                      main_map_object = L.map(map_id).setView([point[0], point[1]], 12);
                      // Add it to my tiles
                      tiles.addTo(main_map_object);
                      // https://github.com/jawj/OverlappingMarkerSpiderfier-Leaflet to handle overlapping markers
                      loc_oms = new OverlappingMarkerSpiderfier(main_map_object, { keepSpiderfied: true });

                      // Convert layerdict into layerlist
                      for (key in loc_layerDict) {
                        loc_layerList.push({ key: key, value: loc_layerDict[key], freq: loc_layerDict[key].length });
                      }
                      // sort the layerlist
                      loc_layerList.sort(function (a, b) {
                        return b.freq - a.freq;
                      });

                      // Make a layer of markers from the layerLIST
                      for (idx in loc_layerList) {
                        key = loc_layerList[idx].key;
                        layername = '<span style="color: ' + loc_colorDict[key] + ';">' + key + '</span>' + ' (' + loc_layerList[idx].freq + ')';
                        kvalue = loc_layerList[idx].value;
                        if (kvalue.length > 0) {
                          try {
                            loc_overlayMarkers[layername] = L.layerGroup(kvalue).addTo(main_map_object);
                          } catch (ex) {
                            i = 100;
                          }
                        }
                      }
                      L.control
                        .layers({}, loc_overlayMarkers, { collapsed: false })
                        .addTo(main_map_object)

                      // Set map to fit the markers
                      polyline = L.polyline(points);
                      if (points.length > 1) {
                        main_map_object.fitBounds(polyline.getBounds());
                      } else {
                        main_map_object.setView(points[0], 12);
                      }

                      private_methods.leaflet_scrollbars();

                    }
                  }

                  // Make sure it is redrawn
                  setTimeout(function () {
                    // Double check
                    if (main_map_object === null) {
                      // Don't do anything here
                    } else {
                      main_map_object.invalidateSize();
                      if (points.length > 1) {
                        main_map_object.fitBounds(polyline.getBounds());
                      } else {
                        main_map_object.setView(points[0], 12);
                      }

                      private_methods.leaflet_scrollbars();
                    }

                  }, 400);
                  // Debug  break point
                  i = 100;
                } else {
                  errMsg("Response is okay, but [html] is missing");
                }
                // Knoppen weer inschakelen

              } else {
                if ("msg" in response) {
                  errMsg(response.msg);
                } else {
                  errMsg("Could not interpret response " + response.status);
                }
              }
            }
          });
        } catch (ex) {
          private_methods.errMsg("language_map", ex);
        }
      },

      /**
       * list_to_map 
       *    Show all points selected by a user-defined listview - provided these points have coordinates
       *    The points are grouped around their type (?)
       * 
       *    Expectations:
       *    - the 'el' div should have attributes:
       *      'targeturl' - The URL to call
       * 
       * @param {el}        DOM element where this request starts from
       * @param {options}   dictionary with 'filter', 'map' and 'title' identifiers (set to default values)
       * @returns {void}
       */
      list_to_map: function (el, options = { filter: "basiclist_filter", map: "werkstuk_map", title: "map_view_title" }) {
        var frm = null,       // Used in the Radboud 'basic' app
          frm2 = null,
          data = null,
          entries = null,
          point = null,
          points = [],
          geometries = [],    // Geojson geometries
          id_filter = null,
          map_id = null,
          polyline = null,
          map_title = null,
          has_edit_permission = false,
          trefwoord = "",
          i = 0,
          j = 0,
          idx = 0,
          label = "",           // This is, so far, only used for a modal-form
          targeturl = ""; //,
        //oOverlay = null,    // Possibly this and the remaining ones are NOT USED?
        //keywords = [],
        //lemma = "",
        //targetid = "";

        try {
          // Get the map_id and the id_filter
          id_filter = options.filter;
          map_id = options.map;
          map_title = options.title;
          // Make sure the identifiers are correct
          //  - map_id must *NOT start with #
          if (map_id.startsWith("#")) { map_id = map_id.substring(1); }
          //  - id_filter and map_title *MUST* start with #
          if (!id_filter.startsWith("#")) { id_filter = "#" + id_filter; }
          if (!map_title.startsWith("#")) { map_title = "#" + map_title; }

          // Figure out which form to take
          frm2 = $(el).closest("form");
          if ($(frm2).length > 0) {
            frm = $(frm2).first();
          } else if ($(id_filter).length > 0) {
            frm = $(id_filter).first();
          }

          // Get the form data
          data = $(frm).serializeArray();
          targeturl = $(el).attr("targeturl");

          // Possibly remove what is still there
          if (main_map_object !== null) {
            // Remove tile layer from active map
            mapview_tiles.remove()
            // Remove the actual map
            try {
              main_map_object.remove();
            } catch (ex) {
              i = 0;
            }
            main_map_object = null;
            // Reset the 
          }
          // Indicate we are waiting
          $("#" + map_id).html(loc_sWaiting);
          if (points.length > 0) points.clear();
          // Other initializations
          loc_layerDict = {};
          loc_layerList = [];
          loc_trefwoord = [];           // THis now contains the first letter of the Kloeke Codes
          loc_colorDict = {};
          loc_overlayMarkers = {};

          // Post the data to the server
          $.post(targeturl, data, function (response) {
            var key, layername, kvalue, oGeo;

            // Sanity check
            if (response !== undefined) {
              if (response.status == "ok") {
                if ('entries' in response) {
                  // Get the edit permission
                  if (response.is_app_editor !== undefined) {
                    has_edit_permission = response.is_app_editor;
                  }
                  // Get the entries
                  entries = response['entries'];

                  // The title LABEL is for a Modal Dialog view
                  label = response['label'];
                  if ($(map_title).length > 0) {
                    $(map_title).html(label);
                  }

                  if (main_map_object == null) {
                    // now get the first point
                    for (i = 0; i < entries.length; i++) {
                      if (entries[i].point !== null && entries[i].point !== "") {
                        // Add point to the array of points to find out the bounds
                        points.push(entries[i].point.split(",").map(Number));
                        // Is this geojson or not?
                        if (entries[i].geojson !== undefined && entries[i].geojson !== null) {
                          // Probably  geojson
                          // geometries.push(entries[i].geojson);
                          private_methods.make_geo(entries[i]);
                        } else {
                          // Create a marker for this point
                          private_methods.make_marker(entries[i]);
                        }
                      }
                    }
                    if (points.length > 0) {
                      // Get the first point
                      point = points[0];
                      // CLear the map section from the waiting symbol
                      $("#" + map_id).html();
                      // Set the starting map
                      // EK: Added "editable" to it
                      main_map_object = L.map(map_id, { editable: true }).setView([point[0], point[1]], 12);
                      // Add it to my mapview_tiles
                      mapview_tiles.addTo(main_map_object);
                      // https://github.com/jawj/OverlappingMarkerSpiderfier-Leaflet to handle overlapping markers
                      loc_oms = new OverlappingMarkerSpiderfier(main_map_object, { keepSpiderfied: true });

                      // Convert layerdict into layerlist
                      for (key in loc_layerDict) {
                        loc_layerList.push({ key: key, value: loc_layerDict[key], freq: loc_layerDict[key].length });
                      }
                      // sort the layerlist
                      loc_layerList.sort(function (a, b) {
                        return b.freq - a.freq;
                      });

                      // Make a layer of markers from the layerLIST
                      for (idx in loc_layerList) {
                        key = loc_layerList[idx].key;
                        layername = '<span style="color: ' + loc_colorDict[key] + ';">' + key + '</span>' + ' (' + loc_layerList[idx].freq + ')';
                        kvalue = loc_layerList[idx].value;
                        if (kvalue.length > 0) {
                          try {
                            loc_overlayMarkers[layername] = L.layerGroup(kvalue).addTo(main_map_object);
                          } catch (ex) {
                            i = 100;
                          }
                        }
                      }
                      L.control
                        .layers({}, loc_overlayMarkers, { collapsed: false })
                        .addTo(main_map_object)

                      // Set map to fit the markers
                      polyline = L.polyline(points);
                      if (points.length > 1) {
                        main_map_object.fitBounds(polyline.getBounds());
                      } else {
                        main_map_object.setView(points[0], 12);
                      }

                      private_methods.leaflet_scrollbars();

                      // If there is permission, switch on editable
                      if (has_edit_permission) {
                        private_methods.leaflet_editable(main_map_object);
                      }

                    }

                  }

                  // Make sure it is redrawn
                  setTimeout(function () {
                    // Double check
                    if (main_map_object === null) {
                      // Don't do anything here
                    } else {
                      main_map_object.invalidateSize();
                      if (points.length > 1) {
                        main_map_object.fitBounds(polyline.getBounds());
                      } else {
                        main_map_object.setView(points[0], 12);
                      }

                      private_methods.leaflet_scrollbars();
                    }

                  }, 400);
                  // Debug  break point
                  i = 100;
                } else {
                  errMsg("Response is okay, but [html] is missing");
                }
                // Knoppen weer inschakelen

              } else {
                if ("msg" in response) {
                  errMsg(response.msg);
                } else {
                  errMsg("Could not interpret response " + response.status);
                }
              }
            }
          });
        } catch (ex) {
          private_methods.errMsg("list_to_map", ex);
        }
      }


    };

  }($, ru.config));

  return ru;
}(jQuery, window.ru || {})); // window.ru: see http://stackoverflow.com/questions/21507964/jslint-out-of-scope

// ============================= MAP ======================================================



