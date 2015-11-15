geocoder = new google.maps.Geocoder();
address = document.getElementById("address");
//Initial map center coordinates
INITIAL_CENTER_LAT = 39.952;
INITIAL_CENTER_LONG = -75.195;
initial_coords = new google.maps.LatLng(INITIAL_CENTER_LAT, INITIAL_CENTER_LONG);
//Initial map zoom value
ZOOM = 17;
//An integer for the offset between the actual window size and the
//JavaScript-determined Window size in order to size the map
WINDOW_OFFSET = 70

//Bounds for the Date Slider. End date is current date.
var BOUNDS_MIN = new Date(2015, 0, 1);
var BOUNDS_MAX = new Date();

//Get Incident Report information through HTML and Jinja2 and add markers
//to the map.
function addMarkers(map) {
    var vehicle_ids_str = $("#vehicle_ids").data();
    var license_plates_str = $("#license_plates").data();
    var latitudes = $("#latitudes").data();
    var longitudes = $("#longitudes").data();
    var dates_str = $("#dates").data();
    var durations_str = $("#durations").data();
    var agencies_str = $("#agencies").data();
    var pictures_str = $("#pictures").data();
    var descriptions_str = $("#descriptions").data();
    //Tokenize the strings representing arrays that are given through HTML
    //by Jinja2
    var vehicle_ids = (vehicle_ids_str.name).split('\'');
    var license_plates = (license_plates_str.name).split('\'');
    var dates = (dates_str.name).split('\'');
    var durations = (durations_str.name).split('\'');
    var agencies = (agencies_str.name).split('\'');
    var pictures = (pictures_str.name).split('\'');
    var descriptions = (descriptions_str.name).split('\'');
    for (i = 0; i < (latitudes.name).length; i = i + 1) {
        //In order that the same marker isn't modified every time,
        //we create a new function here to create and design each marker
        $(function() {
            var marker = new google.maps.Marker({
                //Use latitude and longitude values from incident report
                //to set position of marker
                position:{lat: latitudes.name[i], lng: longitudes.name[i]}
            });

            //Tie marker to map passed as an argument
            
            marker.setMap(map);
            
            //Information presented when marker is clicked
            var contentString = '<div id="content">' +
                '<div id="siteNotice">' +
                '</div>' +
                '<h1 id="firstHeading" class="firstHeading">Vehicle ID: ' + vehicle_ids[2*i+1] +'</h1>' +
                '<div id="bodyContent">' +
                '<p>License Plate: ' + license_plates[2*i+1] + '</p>' +
                '<p>Date: ' + dates[2*i+1] + '</p>' +
                '<p>Duration: ' + durations[2*i+1] + '</p>' +
                '<p>Agency: ' + agencies[2*i+1] + '</p>' +
                '<p>Link to Picture: ' + pictures[2*i+1] + '</p>' +
                '<p>Description: ' + descriptions[2*i+1] + '</p>' +
                '</div>' +
                '</div>';
            var infoWindow = new google.maps.InfoWindow({
                content: contentString
            });

            //Add click listener to marker for displaying infoWindow
            marker.addListener('click', function() {
                infoWindow.open(map, marker);
            });
        });
    }
}

//Initialize map and add markers
function initialize() {
    var mapProp = {
        center: initial_coords,
        zoom:ZOOM,

        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    map=new google.maps.Map(document.getElementById("googleMap"),mapProp);
    google.maps.event.addListener(map, 'click', function(event) {
            $('#latitude').val(event.latLng.lat());
            $('#longitude').val(event.latLng.lng());
            getReverseGeocodingData(event.latLng.lat(), event.latLng.lng())
      });
    //Use HTML geolocation to center map if possible
    if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                var pos_center = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };

                map.setCenter(pos_center);
            });
    }
    else {
        console.log("Browser is not supporting geolocation.");
    }
    addMarkers(map);
}

function getReverseGeocodingData(lat, lng) {
    var latlng = new google.maps.LatLng(lat, lng);
    // This is making the Geocode request
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({ 'latLng': latlng }, function (results, status) {
        if (status !== google.maps.GeocoderStatus.OK) {
            alert(status);
        }
        // This is checking to see if the Geoeode Status is OK before proceeding
        if (status == google.maps.GeocoderStatus.OK) {
            console.log(results);
             $('#location').val(results[0].formatted_address);
        }
    });
}

function geoFindMe() {

  if (!navigator.geolocation){
      return;
    }

  function success(position) {
    var geocoder = new google.maps.Geocoder;

    $('#latitude').val(position.coords.latitude);
    $('#longitude').val(position.coords.longitude);
    getReverseGeocodingData(position.coords.latitude, position.coords.longitude)
  };

  function error() {
  };
  navigator.geolocation.getCurrentPosition(success, error);
}

//Use Google geocoder to update geolocation given an address through
//the address search box
function update_center() {
    geocoder = new google.maps.Geocoder();
    address = $("#address").val();
    if (geocoder) {
        console.log(address);
        geocoder.geocode( { 'address': address},
        function(results, status) {
            if (status != google.maps.GeocoderStatus.OK) {
                alert("Geocode not successful - " + status);
            }
            else if (status == google.maps.GeocoderStatus.ZERO_RESULTS) {
                alert("Address not found!");
            }
            else {
                map.setCenter(results[0].geometry.location);
            }
        });
    }
}

//Get address submit event
$(document).ready(function() {
    $('#addressForm').on('submit', function (event) {
        update_center();
        return false;
    });
});

//Date Slider - TODO
$(function() {
    $("#slider").dateRangeSlider({
        bounds: {
            min: BOUNDS_MIN,
            max: BOUNDS_MAX,
        },
        arrows: false,
        defaultValues: {
            min: BOUNDS_MIN,
            max: BOUNDS_MAX,
        },
    });
});

//Add the map to the window
google.maps.event.addDomListener(window, 'load', initialize)

//Set the map's height to be (hopefully) full window height
$(function() {
    $("#googleMap").css("height", $(window).height()-WINDOW_OFFSET);
});
