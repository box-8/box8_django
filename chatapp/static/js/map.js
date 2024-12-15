const posInit = [45.76316281678944, 4.860897385287324]
var map = {}
var markers = []
var markerGroup = new L.featureGroup()

function map_plot_doc(filetype) {
    analyse_courante.prompt = "map_plot_" + filetype

    $.ajax({
        url: chatapp_talk,
        type: 'POST',
        data: JSON.stringify(analyse_courante),
        contentType: 'application/json',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
            $("#carte-tab").click()
            $.toast({ heading: "Info", text: "Extraction des informations de géolocalisation en cours ...", position: toastPosition, icon: "info", stack: true })
        },
        success: function (response) {
            console.log(response)
            plot_response(response)
        },
        error: function (e) {

        }
    });
}

function plot_response(json_plot) {

    var filename = json_plot.filename
    var summary = json_plot.summary
    console.log(json_plot.infos_geographiques)
    json_plot.infos_geographiques.forEach(function (markerData, index) {
        // console.log(markerData)
        let latlng = [markerData.lat, markerData.lng]
        //let marker = L.marker(latlng).addTo(map);
        let marker = L.marker(latlng)
        let popup = L.popup().setLatLng(latlng).setContent("<b>" + markerData.title + "</b><br>" + markerData.contexte + "<br>page : " + markerData.page) // .openOn(map);
        marker.bindPopup(popup)
        marker.on('dragend', function (event) {
            let position = this.getLatLng();
            this.bindPopup(popup)
            $.toast({ heading: "Info", text: "Marker déplacé à : " + position.lat + ',' + position.lng, position: toastPosition, icon: "info", stack: true })
        });
        // markers.push(marker)
        marker.addTo(markerGroup)
    });
    map.addLayer(markerGroup);
    map.fitBounds(markerGroup.getBounds());
}
function clearMarkers() {
    if (markerGroup) {
        markerGroup.clearLayers();
    }
    $.toast({ heading: "Info", text: "Tous les marqueurs ont été supprimés.", position: "top-right", icon: "info", stack: true });
}

$(document).ready(function () {

    $("#plot-clear").on("click", function () {
        clearMarkers()
    });
    $("#plot-doc").on("click", function () {
        map_plot_doc("pdf")
    });
    $("#plot-sumup").on("click", function () {
        map_plot_doc("txt")
    });

    $("#carte-tab").on("click", function () {
        var btn = $(this)
        if (btn.hasClass("text-info")) {
        } else {
            btn.addClass("text-info")
            setTimeout(function () { initmap() }, 500);
        }
    });

    function initmap() {
        map = L.map('map').setView(posInit, 12);
        const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);
        map.attributionControl.setPrefix('');
    }

    $("#map-mode").on("click", function () {
        if (this.innerHTML == 'mode consultation') {
            this.innerHTML = 'mode édition'
        } else {
            this.innerHTML = 'mode consultation'
        }
        markerGroup.eachLayer(function (marker) {
            if (marker.dragging._enabled) {
                marker.dragging.disable();
            } else {
                marker.dragging.enable();
            }
        })

    });


});
