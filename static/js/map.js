var objLat = 5.35995728923316;
var objLng = -4.008238011482126;
var objMarkerIcon = JSON.parse('{{ objMarkerIcon|escapejs }}');

var map = L.map('map', {
    center: [objLat, objLng],
    zoom: 12
});

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18
}).addTo(map);

var objMarker = L.marker([objLat, objLng], {icon: L.icon(objMarkerIcon)}).addTo(map);

var routingControl = L.Routing.control({
    waypoints: [
        L.latLng(objLat, objLng)
    ],
    routeWhileDragging: true,
    geocoder: L.Control.Geocoder.nominatim(),
    router: new L.Routing.osrmv1({
        serviceUrl: 'https://router.project-osrm.org/route/v1'
    })
}).addTo(map);

var userMarker = L.marker(map.getCenter(), {
    icon: L.divIcon({
        className: 'user-marker',
        html: '<i class="fas fa-map-marker-alt"></i>'
    })
}).addTo(map);

function onLocationSuccess(position) {
    var userLatLng = L.latLng(position.coords.latitude, position.coords.longitude);
    userMarker.setLatLng(userLatLng);
    routingControl.setWaypoints([
        userLatLng,
        objMarker.getLatLng()
    ]);
    map.panTo(userLatLng);
    document.getElementById('distance').textContent = userLatLng.distanceTo(objMarker.getLatLng()).toFixed(2) + ' m';
}

function onLocationError(error) {
    console.log(error);    
} 
      
navigator.geolocation.watchPosition(onLocationSuccess, onLocationError, {
    enableHighAccuracy: true,
    maximumAge: 1000,
    timeout: 3000
});