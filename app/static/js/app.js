
const MAP_ZOOM = 16;
const MAP_ACCESS_TOKEN = 'pk.eyJ1IjoicmJyaXNpdGEiLCJhIjoiY2p0amIyYjUyMGpvZzN5bDloejgwY3NtMSJ9.8z-tpve4BVbiTXZ2nBWSxw'
const MAP_PROVIDER_URI = 'https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}'
const MAP_ATTRIBUTION = 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>'
const MAP_MAX_AREA = 4000;
const TPL_CARD = '\
<div data-card id="{ID}" class="card border-dark col" style="width: 18rem;">\
    <h5 class="card-header d-md-block d-none text-truncate">{TITLE}</h5>\
    <h6 class="card-header d-md-none font-weight-bold text-truncate">{TITLE}</h6>\
    <div class="card-body">\
        <p class="card-text"><i data-feather="tag"></i>&nbsp<span class="font-weight-bold">{TAGS}</span></p>\
        <div class="card-text row">\
            <div class="col icon-star text-left">\
                <a href="#appModal" class="card-link" data-icon-type=1 data-toggle="modal" data-target="#appModal">\
                    <span class="font-weight-bold">{RATING}</span>&nbsp<i data-feather="star"></i>\
                </a>\
            </div>\
            <div class="col text-center">\
                <a href="#appModal" class="card-link" data-icon-type=2 data-toggle="modal" data-target="#appModal">\
                    <i data-feather="message-square"></i>\
                </a>\
            </div>\
            <div class="col text-right">\
                <a href="#appModal" class="card-link" data-icon-type=3 data-toggle="modal" data-target="#appModal">\
                    <i data-feather="compass"></i>\
                </a>\
            </div>\
        </div>\
    </div>\
</div>';

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
            createCards(places);
            listenCards();
            listenModal();
    });

    // Test fail condition
    // Modal pop up
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

function createCards(places) {
    let html = '';

    places.forEach(function(item) {
        html += TPL_CARD.replace(/{TITLE}/g, item.name);
        html = html.replace('{TAGS}', item.tags.join(', '));
        html = html.replace('{ID}', item._id);
        html = html.replace('{RATING}', item.ratings_avg);
    });

    $('div.row.scrollable').html(html);

    feather.replace();
}

function listenCards() {
    $('[data-card]').on('click', function(ev) {
        // Don't act on internal card links or it's contents.
        let parents = $(ev.target).parents('.card-link');
        if (parents.length || $(ev.target).hasClass('card-link')) {
            return;
        }

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

function listenModal() {
    $('#appModal').on('show.bs.modal', (ev) => {
        let icon = $(ev.relatedTarget);
        let type = icon.data('icon-type');
        let card = icon.closest('[data-card]');
        let id = card.attr('id');
        let name = card.find('.card-header').first().text();

        // TODO test icon type for specfic config
        let config = {
            title: name + ' Reviews',
            body: 'Requesting reviews...',
            hideClose: true,
            hideButtons: true
        };

        prepareModal(config);

        // Request reviews for id
        // TODO: Needs better API api/places/id/reviews is better
        $.get('api/places/' + id, (data) => {
            resetModal();

            reviews = data.reviews;

            let html = '';
            reviews.forEach(function(item) {
                html += '<h5>' + item.blurb + '</h5>';
                html += '<b class="float-left">' + item.rating + ' stars</b>';
                html += '<b class="float-right">' + item.date + '</b>';
            });

            $('.modal-title').html(name + ' Reviews');
            $('.modal-body').html(html);
        });

        // TODO Test failure case

    });

    $('#appModal').on('hidden.bs.modal', (ev) => {
        console.log(this);
        console.log(ev);
    });
}

function prepareModal(config) {
    $('.modal-title').html(config.title);
    $('.modal-body').html(config.body);

    if (config.hideClose) {
        $('.close').hide();
    } else {
        $('.close').show();
    }

    if (config.hideButtons) {
        $('.modal-footer').hide();
    } else {
        $('.modal-footer').show();
    }

}

function resetModal() {
    let config = {
        title: '',
        body: '',
        hideClose: false,
        hideButtons: false
    }

    prepareModal(config);
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
