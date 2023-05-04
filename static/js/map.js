// Initial Map
var map = L.map('map').setView([42.3757148, -71.1146536, 10], 13);
var currentPos;

map.locate({ setView: true, maxZoom: 10 });

// Filter settings for map tiles
let defaultToDarkFilter = [
    'grayscale:100%',
    'invert:100%',
]

L.tileLayer.colorFilter('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    filter: defaultToDarkFilter
}).addTo(map);

function onLocationFound(e) {
    var radius = e.accuracy;

    L.circle(e.latlng, radius).addTo(map);
    map.flyTo(e.latlng, 10);
}

function onLocationError(e) {
    alert(e.message);
}

map.on('locationerror', onLocationError);
map.on('locationfound', onLocationFound);

// Custom Icons
var greenIcon = L.icon({
    iconUrl: "/static/map_icon/trash_green_pin.png",

    iconSize: [50, 60], // size of the icon
    iconAnchor: [25, 60], // point of the icon which will correspond to marker's location
    popupAnchor: [0, -55] // point from which the popup should open relative to the iconAnchor
});

var blueIcon = L.icon({
    iconUrl: "/static/map_icon/trash_blue_pin.png",

    iconSize: [50, 60], // size of the icon
    iconAnchor: [25, 60], // point of the icon which will correspond to marker's location
    popupAnchor: [0, -55] // point from which the popup should open relative to the iconAnchor
});

var redIcon = L.icon({
    iconUrl: "/static/map_icon/trash_red_pin.png",

    iconSize: [50, 60], // size of the icon
    iconAnchor: [25, 60], // point of the icon which will correspond to marker's location
    popupAnchor: [0, -55] // point from which the popup should open relative to the iconAnchor
});

var grayIcon = L.icon({
    iconUrl: "/static/map_icon/trash_gray_pin.png",

    iconSize: [50, 60], // size of the icon
    iconAnchor: [25, 60], // point of the icon which will correspond to marker's location
    popupAnchor: [0, -55] // point from which the popup should open relative to the iconAnchor
});

var orangeIcon = L.icon({
    iconUrl: "/static/map_icon/trash_orange_pin.png",

    iconSize: [50, 60], // size of the icon
    iconAnchor: [25, 60], // point of the icon which will correspond to marker's location
    popupAnchor: [0, -55] // point from which the popup should open relative to the iconAnchor
});

var locationIcon = L.icon({
    iconUrl: "/static/map_icon/location_pin.png",

    iconSize: [50, 60], // size of the icon
    iconAnchor: [25, 60], // point of the icon which will correspond to marker's location
    popupAnchor: [0, -60] // point from which the popup should open relative to the iconAnchor
});

// create an array for markers
var marker = new Array();
var LamMarker;

// pushing items into array one by one and then add markers
function loadMarkers() {

    // load trash pins
    var trashLayerGroup = L.layerGroup().addTo(map);
    for (i = 0; i < trash_pins.length; i++) {

        var trashMarker = new L.marker([trash_pins[i].lat, trash_pins[i].lng], {
            icon: redIcon,
            draggable: false,
            riseOnHover: true,
            title: "Dirty Location",
            alt: "Dirty Location"
        });

        trashMarker.on('click', function(ev) {
            currentPos = map.mouseEventToLatLng(ev.originalEvent);
            window.location.href = ("/trash?lat=" + currentPos.lat + "&lng=" + currentPos.lng);
           });

        marker.push(trashMarker);
        trashLayerGroup.addLayer(trashMarker);
    }

    var overlaytrash = {'markers': trashLayerGroup};

    // load clean pins
    var cleanLayerGroup = L.layerGroup().addTo(map);
    for (i = 0; i < clean_pins.length; i++) {
        var cleanMarker = new L.marker([clean_pins[i].lat, clean_pins[i].lng], {
            icon: greenIcon,
            draggable: false,
            riseOnHover: true,
            title: "Clean Location",
            alt: "Clean Location"
        });

        cleanMarker.on('click', function(ev) {
            currentPos = map.mouseEventToLatLng(ev.originalEvent);
            window.location.href = ("/clean?lat=" + currentPos.lat + "&lng=" + currentPos.lng);
          });

        marker.push(cleanMarker);
        cleanLayerGroup.addLayer(cleanMarker);

        // Update location on changing position
        cleanMarker.on("dragend", function (e) {
            currentPos = e.target.getLatLng();
        });

    }

    var overlayclean = {'markers': cleanLayerGroup};

}

// function to create random unique ids
function rand_ID() {
    let ID4 = () => {
        return Math.floor((1 + Math.random()) * 0x10000)
            .toString(16)
            .substring(1);
    }
}

// Going through all marker-items and delete them
function delMarkers() {
    for (i = 0; i < marker.length; i++) {
        console.log("deleted marker " + [i]);
        map.removeLayer(marker[i]);
    }
}

// Delete the last marker
function delMarker() {
    var tempMarker = this.LamMarker;
    console.log("Marker removed");
    map.removeLayer(tempMarker);
}

function onMapClick(e) {

    // add a new marker
    LamMarker = new L.marker(e.latlng, {
        icon: blueIcon,
        draggable: true,
        riseOnHover: true,
        title: "Selected Location",
        alt: "Selected Location"
    });

    // get the markers position initially
    currentPos = LamMarker.getLatLng();

    marker.push(LamMarker);
    map.addLayer(LamMarker);

    // Update location on changing position
    LamMarker.on("dragend", function (e) {
        currentPos = e.target.getLatLng();
    });

    LamMarker.on('click', function(ev) {
         console.log(currentPos.lat + ', ' + currentPos.lng);
         window.location.href = ("/capture?lat=" + currentPos.lat + "&lng=" + currentPos.lng);
       });

}

function onRightClick(e) {
    delMarker();
}

map.on('contextmenu', onRightClick);
// create action to safe marker so it is available on reload
map.on('click', onMapClick);
// initially load already existing markers
map.whenReady(loadMarkers);


