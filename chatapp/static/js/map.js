// Script Gestion de la Carte interractive

const posNaldeo = [45.76316281678944, 4.860897385287324]
var map = {}
var markers = []
var markerGroup = new L.featureGroup()
$(document).ready(function () {
    $('#viewer-plotmap').click(function (event) {
        map_plot_doc()
    });
})

function map_plot_doc() {
    analyse_courante.prompt = "map_plot_doc"
    $.ajax({
        url: urlMapPlot,
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
    console.log(json_plot)
    json_plot.infos_geographiques.forEach(function (markerData, index) {
        // console.log(markerData)
        let latlng = [markerData.lat, markerData.lng]
        //let marker = L.marker(latlng).addTo(map);
        let marker = L.marker(latlng)
        let popup = L.popup().setLatLng(latlng).setContent("<b>" + filename + "</b><br>" + markerData.title + " : " + markerData.contexte + "<br>page : " + markerData.page) // .openOn(map);
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

$(document).ready(function () {

    $("#plot-doc").on("click", function () {
        map_plot_doc()
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
        map = L.map('map').setView(posNaldeo, 12);
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
