
const MAP_ZOOM = 16;
const MAP_ACCESS_TOKEN = 'pk.eyJ1IjoicmJyaXNpdGEiLCJhIjoiY2p0amIyYjUyMGpvZzN5bDloejgwY3NtMSJ9.8z-tpve4BVbiTXZ2nBWSxw'
const MAP_PROVIDER_URI = 'https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}'
const MAP_ATTRIBUTION = 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>'
const MAP_MAX_AREA = 4000;
const TPL_INFO_CARD = '<div id="{ID}" class="col col-md-12 align-self-center scrollable-content">{HTML}</div>';

var markers = [];
var map = L.map('map');

function showLocation(latLng) {
    map.setView(latLng, MAP_ZOOM);

    map.on('zoomlevelschange', zoomLevelsChangeHandler);

    let tileLayer = L.tileLayer(
        MAP_PROVIDER_URI, {
            attribution: MAP_ATTRIBUTION,
            maxZoom: 18,
            minZoom: 14,
            id: 'mapbox.streets',
            accessToken: MAP_ACCESS_TOKEN
    }).addTo(map);

    spinnerToggle(tileLayer);
}

function spinnerToggle(tileLayer) {
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

function zoomLevelsChangeHandler(ev) {
    map.off('zoomlevelschange', zoomLevelsChangeHandler);

    let center = map.getBounds().getCenter();
    setLocationMarker(center);
    restrictMapMovement(center);

    requestPlaces(center);
}

function setLocationMarker(center) {
    let person = L.icon({
        iconUrl: 'https://raw.githubusercontent.com/iconic/open-iconic/master/png/person-4x.png',
        iconSize: [32, 32],
        popupAnchor: [0, -16]
    });

    let marker = L.marker(
        center,
        {
            icon: person,
            title: 'YOU!',
            alt: 'Your location.',
            riseOnHover: true
    }).addTo(map);
    marker.bindPopup('<h4>YOU!</h4>').openPopup();
}

function restrictMapMovement(center) {
    let newBounds = center.toBounds(MAP_MAX_AREA);
    map.setMaxBounds(newBounds);
}

function requestPlaces(center) {
    $.get(
        'api/search/' + center.lng + '/' + center.lat + '/' + Math.floor(MAP_MAX_AREA / 3),
        function(data) {
            let places = data.places;
            setMarkers(places);
            createInfoCards(places);
            listenInfoCards();
    });

    // Test fail condition
}

function setMarkers(places) {
    places.forEach(function(item) {
        let marker = L.marker(
            L.latLng(
                parseFloat(item.lat),
                parseFloat(item.lng)
            ),{
                title: item.name,
                alt: item.name,
                riseOnHover: true
        }).addTo(map);
        markers[item._id] = marker.bindPopup('<h5>' + item.name + '</h5>');
    });
}

function createInfoCards(places) {
    let html = '';
    let info = '';

    places.forEach(function(item) {
        info = '<h4>' + item.name + '</h4><p>' + item.tags.join() + '<p>';
        html += TPL_INFO_CARD.replace('{HTML}', info);
        html = html.replace('{ID}', item._id);
    });

    $('div.row.scrollable-row').html(html);
}

function listenInfoCards() {
    $('.scrollable-content').on('click', function() {
        map.stop();

        let id = $(this).attr('id');
        let marker = markers[id];
        let moveEndHandler = () => {
            map.off('moveend', moveEndHandler);
            marker.openPopup();
        };

        map.on('moveend', moveEndHandler);
        map.flyTo(marker.getLatLng());
    });
}

function getNYCLatLng() {
    return  L.latLng(
        40.729243,
        -73.984423
    );
}

/*
 * Entry point to locate user.
 */
$(function() {
    let locationFoundHandler = function(ev) {
        map.off('locationfound', locationFoundHandler);
        map.off('locationerror', locationErrorHandler);

        showLocation(ev.latlng);
    };

    let locationErrorHandler = function(ev) {
        map.off('locationfound', locationFoundHandler);
        map.off('locationerror', locationErrorHandler);

        showLocation(getNYCLatLng());
    };

    map.on('locationfound', locationFoundHandler);
    map.on('locationerror', locationErrorHandler);

    map.locate();
});
