
const MAP_ZOOM = 16;
const MAP_ACCESS_TOKEN = 'pk.eyJ1IjoicmJyaXNpdGEiLCJhIjoiY2p0amIyYjUyMGpvZzN5bDloejgwY3NtMSJ9.8z-tpve4BVbiTXZ2nBWSxw'
const MAP_PROVIDER_URI = 'https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}'
const MAP_ATTRIBUTION = 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>'
const MAP_MAX_AREA = 2000;

var coords = {};
var map = L.map('map');
map.on('locationfound', function(ev) {
    console.log('Map locationfound');
    console.log(ev);
    coords = [ev.latitude, ev.longitude];
    showMap();
    map.setZoom(MAP_ZOOM);
});
map.on('locationerror', function(ev) {
    console.log('Map locationerror');
    console.log(ev);
    showMap();
    coords = getNYCCoords();
    setView(coords);
});
map.on('load', function(ev) {
    console.log('Map Loaded');
    console.log(ev);
});
map.on('zoomlevelschange', function(ev) {
    console.log('Map zoomlevelschange');
    console.log(ev);

    let marker = L.marker(coords, {
        title: 'YOU!',
        alt: 'Your location.',
        riseOnHover: true
    }).addTo(map);
    marker.bindPopup("<h4>YOU!</h4>").openPopup();

    let bounds = map.getBounds()
    let center = bounds.getCenter();
    let newBounds = center.toBounds(MAP_MAX_AREA);
    map.setMaxBounds(newBounds);

    // Request places
    // api/search/center.latitude/center.longitude/MAX_MAP_AREA
    // api/search/-73.99159/40.728121/2000/
    // populate info cards
    // Allow rating of generated places
});

$(function() {
    console.log("Handler for .ready() called.")
    map.locate({
        setView: true,
    });
});

$(window).on( "load", function() {
    console.log("Handler for window load called.")
});


function getNYCCoords() {
    return [40.729243, -73.984423];
}

function setView(viewCoords) {
    map.setView(viewCoords, MAP_ZOOM);
}

function showMap() {
    let tileLayer = L.tileLayer(MAP_PROVIDER_URI, {
        attribution: MAP_ATTRIBUTION,
        maxZoom: 18,
        minZoom: 14,
        zoom: MAP_ZOOM,
        id: 'mapbox.streets',
        accessToken: MAP_ACCESS_TOKEN
    }).addTo(map);

    tileLayer.on('tileloadstart', function() {
        $('.spinner').removeClass('d-none');
    });
    tileLayer.on('tileerror', function() {
        $('.spinner').addClass('d-none');
    });
    tileLayer.on('load', function() {
        $('.spinner').addClass('d-none');
    });
}

// GlobalEventHandlers.onload
// map.setMaxBounds
