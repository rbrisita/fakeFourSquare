
const MAP_ZOOM = 16;
const MAP_ACCESS_TOKEN = 'pk.eyJ1IjoicmJyaXNpdGEiLCJhIjoiY2p0amIyYjUyMGpvZzN5bDloejgwY3NtMSJ9.8z-tpve4BVbiTXZ2nBWSxw'
const MAP_PROVIDER_URI = 'https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}'
const MAP_ATTRIBUTION = 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>'
const MAP_MAX_AREA = 4000;

var coords = {};
var map = L.map('map');
map.on('locationfound', function(ev) {
    coords = [ev.latitude, ev.longitude];
    showMap();
    map.setZoom(MAP_ZOOM);

    let marker = L.marker(coords, {
        title: 'YOU!',
        alt: 'Your location.',
        riseOnHover: true
    }).addTo(map);
    marker.bindPopup("<h4>YOU!</h4>").openPopup();
});
map.on('locationerror', function(ev) {
    showMap();
    setView(getNYCCoords());
});
map.on('load', function(ev) {
    console.log('Map Loaded');
    console.log(ev);
});
map.on('zoomlevelschange', function(ev) {
    let center = map.getBounds().getCenter();
    let newBounds = center.toBounds(MAP_MAX_AREA);
    map.setMaxBounds(newBounds);

    requestPlaces(center);
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

function requestPlaces(center) {
    // Request places
    // api/search/center.latitude/center.longitude/MAP_MAX_AREA
    // api/search/-73.99159/40.728121/2000/
    // populate info cards
    // Allow rating of generated places

    $.get('api/search/' + center.lng + '/' + center.lat + '/' + Math.floor(MAP_MAX_AREA / 3), function(data) {
        console.log('Response');
        console.log(data);
        console.log(arguments);

        setMarkers(data.places);
        // Populate info cards
        // create click relationship
    }).done(function() {
        console.log('Done');
        console.log(arguments);
    }).fail(function() {
        console.log('Fail');
        console.log(arguments);
    }).always(function() {
        console.log('Always');
        console.log(arguments);
    });
}

function setMarkers(places) {
    while(places.length) {
        const p = places.pop();
        console.log(p)
        let marker = L.marker([p.lat, p.lng], {
            title: p.name,
            alt: p.name,
            riseOnHover: true
        }).addTo(map);
        marker.bindPopup("<h5>" + p.name + "</h5>");
    }
}

// GlobalEventHandlers.onload
// map.setMaxBounds
