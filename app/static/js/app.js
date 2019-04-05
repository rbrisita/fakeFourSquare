
const MAP_ZOOM = 16;
const MAP_PROVIDER_URI = 'https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}'
const MAP_ATTRIBUTION = 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>'
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
            <div class="text-center">\
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
const TPL_REVIEW = '\
<div class="row mb-3 border border-dark rounded">\
    <div class="col-12 lead">{BLURB}</div>\
    <div class="col-4 text-left">{RATING}&nbsp<i data-feather="star"></i></div>\
    <div class="col-8 small text-right text-muted">{DATE}</div>\
</div>';
const FORM_REVIEW = '\
<div class="row">\
    <div class="col">\
        <form id="review-form" name="review-form" novalidate>\
            <div class="form-group">\
                <label class="h5" for="blurb">Review</label>\
                <span id="review-blurb--error" class="d-none text-danger small"><strong>Please write a review.</strong></span>\
                <textarea\
                    required\
                    class="form-control"\
                    id="review-blurb"\
                    name="review-blurb"\
                    spellcheck="true"\
                    minlength="3"\
                    maxlength="255"\
                    placeholder="Please enter review here of 3-255 characters."\
                    rows="8"\
                    cols="30"></textarea>\
            </div>\
            <div id="review-rating" class="form-group">\
                <i data-feather="star"></i>\
                <i data-feather="star"></i>\
                <i data-feather="star"></i>\
                <i data-feather="star"></i>\
                <i data-feather="star"></i>\
                <span id="review-rating--error" class="d-none text-danger small"><strong>Please choose a rating.</strong></span>\
            </div>\
            <button type="submit" class="btn btn-primary float-right">Submit</button>\
        </form>\
    </div>\
</div>'

var user_location = {};
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
            accessToken: CONFIG.MAP_ACCESS_TOKEN
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
    let newBounds = center.toBounds(CONFIG.MAP_MAX_AREA);
    map.setMaxBounds(newBounds);
}

function requestPlaces(center) {
    let transitionHandler = function() {
        $('#appModal').off('shown.bs.modal', transitionHandler);
        $.get(
            'api/search/' + center.lng + '/' + center.lat + '/' + Math.floor(CONFIG.MAP_MAX_AREA / 3) + '/',
            function(response) {
                if (!response || !response.data) {
                    showMessage('Error', 'No places found.');
                    return;
                } else  {
                    hideMessage();
                }

                let places = response.data.places;
                setMarkers(places);
                createCards(places);
                cardEventHandler();
                modalEventHandler();
                reviewFormEventHandler();
        }).fail(function(ev) {
            showMessage('Error', 'No places found.');
        });
    };
    $('#appModal').on('shown.bs.modal', transitionHandler);
    showMessage('fake Four Square', 'Requesting or generating places...', true);
}

function showMessage(title, body, hide_close = false) {
    let config = {
        title: title,
        body: body,
        hide_close: hide_close,
        hide_buttons: true
    };
    prepareModal(config);

    let modal = $('#appModal');
    if (modal.css('display') !== 'none') {
        modal.trigger('shown.bs.modal');
    } else {
        modal.modal('show');
    }

}

function hideMessage() {
    $('#appModal').modal('hide');
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
        html += generateCardHTML(item);
    });

    $('div.row.scrollable').html(html);

    feather.replace();
}

function generateCardHTML(item) {
    let html = TPL_CARD.replace(/{TITLE}/g, item.name);
    html = html.replace('{TAGS}', item.tags.join(', '));
    html = html.replace('{ID}', item._id);
    html = html.replace('{RATING}', parseFloat(item.ratings_avg.toFixed(2)));
    return html;
}

function cardEventHandler() {
    $('[data-card]').on('click', function(ev) {
        // Don't act on internal card links or it's contents.
        let parents = $(ev.target).parents('.card-link');
        if (parents.length || $(ev.target).hasClass('card-link')) {
            return;
        }

        // Stop any prior animation
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

/**
 * Modal is shown through Bootstrap data attributes.
 *
 * The related target that issued the modal's show command is used to request further action.
 */
function modalEventHandler() {
    $('#appModal').on('show.bs.modal', (ev) => {
        let icon = $(ev.relatedTarget);
        let type = icon.data('icon-type');
        let card = icon.closest('[data-card]');
        let place_id = card.attr('id');
        let name = card.find('.card-header').first().text();

        window.place_name = name;
        window.place_id = place_id;

        if (type === 1) {
            showReviews(place_id, name);
        } else if (type === 2) {
            $('#request-review-form').trigger('click');
        } else if (type === 3) {
            showDirections(place_id, name);
        }
    });
}

function showReviews(place_id, name) {
    let config = {
        title: name + ' Reviews',
        body: 'Requesting reviews...',
        hide_close: true,
        hide_buttons: true
    };
    prepareModal(config);

    requestReviews(place_id, name);
}

function requestReviews(place_id, name) {
    let html = '';
    $.get('api/places/' + place_id + '/reviews/', (response) => {
        reviews = response.data.reviews;
        if (!reviews.length) {
            html = '<h5>No reviews found.</h5>';
        } else {
            reviews.forEach(function(item) {
                html += generateReviewHTML(item);
            });
        }
    }).fail(function() {
        html = '<h5>No reviews found.</h5>';
    }).always(function() {
        resetModal();
        $('.modal-title').html(name + ' Reviews');
        $('.modal-body .container-fluid').html(html);
        feather.replace();
    });
}

function showDirections(place_id, name) {
    let config = {
        title: name + ' Directions',
        body: 'Directions opended in new view.',
        hide_close: false,
        hide_buttons: true
    };
    prepareModal(config);

    let marker = markers[place_id];
    let latLng = marker.getLatLng();

    let url = 'https://www.google.com/maps/dir/?api=1&origin={SLAT},{SLNG}&destination={DLAT},{DLNG}&travelmode=walking';

    url = url.replace('{SLAT}', user_location.lat);
    url = url.replace('{SLNG}', user_location.lng);
    url = url.replace('{DLAT}', latLng.lat);
    url = url.replace('{DLNG}', latLng.lng);

    window.open(url);
}

function generateReviewHTML(item) {
    let html = TPL_REVIEW.replace('{BLURB}', item.blurb);
    html = html.replace('{RATING}', item.rating);
    html = html.replace('{DATE}', item.date);
    return html;
}

function reviewFormEventHandler() {
    $('#request-review-form').on('click', function(ev) {
        let config = {
            title: 'Add ' + window.place_name + ' Review',
            body: FORM_REVIEW.replace('{ID}', window.place_id),
            hide_close: false,
            hide_buttons: true
        };
        prepareModal(config);
        feather.replace();

        reviewFormRatingHandler();
        reviewFormBlurbHandler();
        reviewFormSubmitHandler();
    });
}

function reviewFormRatingHandler() {
    $('#review-rating').on('click', function(ev) {
        let selected = (ev.target.nodeName.toUpperCase() == 'SVG') ? ev.target : ev.target.parentNode;
        if (selected.nodeName.toUpperCase() != 'SVG') {
            return;
        }

        $('#review-rating--error').addClass('d-none');

        let svgs = $('#review-rating svg');
        svgs.removeClass('selected');
        svgs.each(function() {
            $(this).addClass('selected');
            if (this === selected) {
                return false;
            }
        });
    });
}

function reviewFormBlurbHandler() {
    $('#review-blurb').trigger('focus');
    $('#review-blurb').on('focus', function(ev) {
        $('#review-blurb--error').addClass('d-none');
    });
}

function reviewFormSubmitHandler() {
    $('#review-form').on('submit', function(ev) {
        ev.preventDefault();
        ev.stopPropagation();

        let blurb = $('#review-blurb').val().trim().replace(/\s+/,' ');
        let rating = $('#review-rating svg.selected').length;

        if (!reviewFormValid(blurb, rating)) {
            return;
        }

        // Post review to place id
        $.post(
            'api/places/' + window.place_id + '/reviews/',
            {
                blurb: blurb,
                rating: rating
            },
            function(response) {
                let link = $('#' + window.place_id + ' .icon-star .card-link');
                let modalHiddenHandler = (ev) => {
                    $('#appModal').off('hidden.bs.modal', modalHiddenHandler);
                    link.trigger('click');
                };
                $('#appModal').on('hidden.bs.modal', modalHiddenHandler);
                hideMessage();

                $.get(
                    'api/places/' + window.place_id + '/',
                    function(response) {
                        let ratings_avg = response.data.place.ratings_avg;
                        link.find('span').text(parseFloat(ratings_avg.toFixed(2)));
                    }
                );
            },
            'json'
        ).fail(function() {
            showMessage('Review Submission Failed', 'Please try again later.');
        });
    });
}

function reviewFormValid(blurb, rating) {
    let blurb_error = (blurb.length < 3);
    let rating_error = (!rating);

    if (blurb_error) {
        $('#review-blurb--error').removeClass('d-none');
    } else {
        $('#review-blurb--error').addClass('d-none');
    }

    if (rating_error) {
        $('#review-rating--error').removeClass('d-none');
    } else {
        $('#review-rating--error').addClass('d-none');
    }

    return !(rating_error || blurb_error)
}

function prepareModal(config) {
    $('.modal-title').html(config.title);
    $('.modal-body .container-fluid').html(config.body);

    if (config.hide_close) {
        $('#icon-close').hide();
    } else {
        $('#icon-close').show();
    }

    if (config.hide_buttons) {
        $('.modal-footer').hide();
    } else {
        $('.modal-footer').show();
    }
}

function resetModal() {
    let config = {
        title: '',
        body: '',
        hide_close: false,
        hide_buttons: false
    }

    prepareModal(config);
}

function getNYCLatLng() {
    return  L.latLng(
        CONFIG.LOCATION_LAT,
        CONFIG.LOCATION_LNG
    );
}

/*
 * Entry point to locate user.
 */
$(function() {
    showMessage('fake Four Square', 'Finding location...', true);

    let locationFoundHandler = function(ev) {
        map.off('locationfound', locationFoundHandler);
        map.off('locationerror', locationErrorHandler);

        user_location = ev.latlng;
        showLocation(user_location);
    };

    let locationErrorHandler = function(ev) {
        map.off('locationfound', locationFoundHandler);
        map.off('locationerror', locationErrorHandler);

        user_location = getNYCLatLng();
        showLocation(user_location);
    };

    map.on('locationfound', locationFoundHandler);
    map.on('locationerror', locationErrorHandler);

    map.locate();
});
