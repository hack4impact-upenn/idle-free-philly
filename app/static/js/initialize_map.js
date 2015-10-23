geocoder = new google.maps.Geocoder();
address = document.getElementById("address");
INITIAL_CENTER_LAT = 39.952;
INITIAL_CENTER_LONG = -75.195;
ZOOM = 17;
initial_coords = new google.maps.LatLng(INITIAL_CENTER_LAT, INITIAL_CENTER_LONG);
function initialize() {
    var mapProp = {
        center: initial_coords,
        zoom:ZOOM,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    map=new google.maps.Map(document.getElementById("googleMap"),mapProp);
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
   /*var center_lat = geoplugin_latitude();
    var center_lng = geoplugin_longitude();
    var pos_center = {
        lat: center_lat,
        lng: center_lng
    };
    map.setCenter(pos_center);*/
}

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

$(document).ready(function() {
    $('#addressForm').on('submit', function (event) {
        update_center();
        return false;
    });
});
$(function() {
    var BOUNDS_MIN = new Date(2015, 0, 1);
    var BOUNDS_MAX = new Date();
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
google.maps.event.addDomListener(window, 'load', initialize)
