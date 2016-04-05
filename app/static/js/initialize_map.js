geocoder = new google.maps.Geocoder();
address = document.getElementById("address");

// Global array for map markers
var markers = []

// Global Marker Wrappers and Map
var globalMarkerWrappers = null;
var globalMap = null;

// Initial map center coordinates
INITIAL_CENTER_LAT = 39.952;
INITIAL_CENTER_LONG = -75.195;
initial_coords = new google.maps.LatLng(INITIAL_CENTER_LAT, INITIAL_CENTER_LONG);

// Initial map zoom value
ZOOM = 17;

// Bounds for the Date Slider. End date is current date.
var BOUNDS_MIN = new Date(2015, 0, 1);
var BOUNDS_MAX = new Date();

function MarkerWrapper(actualMarker, incidentDate, contentString) {
    this.actualMarker = actualMarker;
    this.incidentDate = incidentDate;
    this.contentString = contentString;
}

function storeMarkerState(markerWrappers, map, minDate) {
    globalMarkerWrappers = markerWrappers;
    globalMap = map;
    console.log(markerWrappers[0].actualMarker);
    for (mw = 0; mw < globalMarkerWrappers.length; mw++)
    {
        (globalMarkerWrappers[mw].actualMarker).setMap(globalMap);
    }
    BOUNDS_MIN = minDate;
}



//Use Google geocoder to update geolocation given an address through
//the address search box
// Use Google geocoder to update geolocation given an address through
// the address search box
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
                globalMap.setCenter(results[0].geometry.location);
            }
        });
    }
}

// Get address submit event
$(document).ready(function() {
    $('#addressForm').on('submit', function (event) {
        update_center();
        return false;
    });
});

function initializeDateSlider() {
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
    $("#slider").bind("valuesChanged", function(e, data) {
    	console.log("Values just changed. min: " + String(data.values.min).substring(4, 15) + " max: " + String(data.values.max).substring(4, 15));
        var beginYear = parseInt(String(data.values.min).substring(11, 15), 10);
        var beginDay = parseInt(String(data.values.min).substring(8, 10), 10);
        var endYear = parseInt(String(data.values.max).substring(11, 15), 10);
        var endDay = parseInt(String(data.values.min).substring(8, 10), 10);
        var beginMonth = 0;
        var endMonth = 0;
        monthObj = {
            "Jan": 0,
            "Feb": 1,
            "Mar": 2,
            "Apr": 3,
            "May": 4,
            "Jun": 5,
            "Jul": 6,
            "Aug": 7,
            "Sep": 8,
            "Oct": 9,
            "Nov": 10,
            "Dec": 11
        };
        beginMonth = monthObj[String(data.values.min).substring(4, 7)];
        endMonth = monthObj[String(data.values.max).substring(4, 7)];
        beginDate = new Date(beginYear, beginMonth, beginDay);
        endDate = new Date(endYear, endMonth, endDay);
        for (mw = 0; mw < globalMarkerWrappers.length; mw++) {
            if ((globalMarkerWrappers[mw].incidentDate.getTime() < beginDate.getTime()) ||
                (globalMarkerWrappers[mw].incidentDate.getTime() > endDate.getTime())) {
                globalMarkerWrappers[mw].actualMarker.setMap(null);
            }
            else
            {
                globalMarkerWrappers[mw].actualMarker.setMap(globalMap);
            }
        }
    });
}
