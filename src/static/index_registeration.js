document.addEventListener("DOMContentLoaded", function() {
    //getting location
    let locLinkBuyer = document.getElementById("locationLinkBuyer")
    let locLinkSeller = document.getElementById("locationLinkSeller")
    let latFieldBuyer = document.getElementById("inputLatitudeBuyer")
    let latFieldSeller = document.getElementById("inputLatitudeSeller")
    let longFieldBuyer = document.getElementById("inputLongitudeBuyer")
    let longFieldSeller = document.getElementById("inputLongitudeSeller")

    locLinkBuyer.onclick = getLocation;
    locLinkSeller.onclick = getLocation;

    function getLocation() {
        if(navigator.geolocation){
            locLinkBuyer.innerHTML = "Please wait....."
            locLinkSeller.innerHTML = "Please wait....."
            navigator.geolocation.getCurrentPosition(fillPosition)
        }
    }

    function fillPosition(position) {
        latFieldBuyer.value = position.coords.latitude + "°N";
        latFieldSeller.value = position.coords.latitude + "°N";
        longFieldBuyer.value = position.coords.longitude + "°E";
        longFieldSeller.value = position.coords.longitude + "°E";
        marker.setLatLng(L.latLng(position.coords.latitude,position.coords.longitude)).update();
        marker2.setLatLng(L.latLng(position.coords.latitude,position.coords.longitude)).update();
        map.flyTo([position.coords.latitude,position.coords.longitude],13)
        mapSeller.flyTo([position.coords.latitude,position.coords.longitude],13)
        locLinkBuyer.innerHTML = "Use my current location"
        locLinkSeller.innerHTML = "Use my current location"
    }

    // Map controls
    // make map

    var lng = parseFloat(longFieldBuyer.value.split("°")[0]);
    var lat = parseFloat(latFieldBuyer.value.split("°")[0]);
    var zoom = 13
    if (isNaN(lat) || isNaN(lng)){
        lat = 28.653050
        lng = 77.206520 
        zoom = 8
    }
    let map = L.map('divMapBuyer').setView([lat,lng],zoom);
    let mapSeller = L.map('divMapSeller').setView([lat,lng],zoom);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(mapSeller);
    // L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    //     attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
    //     maxZoom: 18,
    // }).addTo(map);
    let marker = L.marker([lat, lng]).addTo(map);
    let marker2 = L.marker([lat, lng]).addTo(mapSeller);
    map.on('click', function(e) {
        marker.setLatLng(e.latlng).update();
        marker2.setLatLng(e.latlng).update();
        latFieldBuyer.value = e.latlng.lat + "°N";
        latFieldSeller.value = e.latlng.lat + "°N";
        longFieldBuyer.value = e.latlng.lng + "°E";
        longFieldSeller.value = e.latlng.lng + "°E";
    });
    mapSeller.on('click', function(e) {
        marker.setLatLng(e.latlng).update();
        marker2.setLatLng(e.latlng).update();
        latFieldBuyer.value = e.latlng.lat + "°N";
        latFieldSeller.value = e.latlng.lat + "°N";
        longFieldBuyer.value = e.latlng.lng + "°E";
        longFieldSeller.value = e.latlng.lng + "°E";
    });

    // toggle map
    let mapLinkBuyer = document.getElementById("mapLinkBuyer");
    let mapLinkSeller = document.getElementById("mapLinkSeller");
    let mapBuyerDiv = document.getElementById("divMapBuyer");
    let mapSellerDiv = document.getElementById("divMapSeller");
    let homeBuyerDiv = document.getElementById("divHomeBuyer");
    let homeSellerDiv = document.getElementById("divHomeSeller");
    mapLinkBuyer.onclick = toggleMap;
    mapLinkSeller.onclick = toggleMap;
    toggled= false;
    mapBuyerDiv.style.display = "none";
    homeBuyerDiv.style.display = "block";

    function toggleMap(){
        if(toggled){
            mapBuyerDiv.style.display = "none";
            mapSellerDiv.style.display = "none";
            homeBuyerDiv.style.display = "block";
            homeSellerDiv.style.display = "block";
            map.invalidateSize();
            mapSeller.invalidateSize();
            toggled = false;
        }
        else {
            mapBuyerDiv.style.display = "block";
            mapSellerDiv.style.display = "block";
            homeBuyerDiv.style.display = "none";
            homeSellerDiv.style.display = "none";
            map.invalidateSize();
            mapSeller.invalidateSize();
            toggled = true;
        }
    }

    //dropdows config

    fetch('/static/cities.json')
      .then(response => response.json())
      .then(data => {
        let cities = data;
        let states = [];
        let statesSelect = document.getElementsByClassName('states');
        let citiesSelect = document.getElementsByClassName('cities');

        for (let i = 0; i < cities.length; i++) {
          if (!states.includes(cities[i].state)) {
            states.push(cities[i].state);
          }
        }

        states.sort();

        for (let i = 0; i < statesSelect.length; i++) {
          for (let j = 0; j < states.length; j++) {
            let option = document.createElement('option');
            option.value = states[j];
            option.text = states[j];
            statesSelect[i].appendChild(option);
          }
        }

        for (let i = 0; i < statesSelect.length; i++) {
          statesSelect[i].addEventListener('change', function() {
            let selectedState = this.value;
            let stateCities = [];

            for (let j = 0; j < cities.length; j++) {
              if (cities[j].state === selectedState) {
                stateCities.push(cities[j].name);
              }
            }

            stateCities.sort();

            for (let j = 0; j < citiesSelect.length; j++) {
              citiesSelect[j].innerHTML = '<option value="" disabled selected>Select City</option>';

              for (let k = 0; k < stateCities.length; k++) {
                let option = document.createElement('option');
                option.value = stateCities[k];
                option.text = stateCities[k];
                citiesSelect[j].appendChild(option);
              }
            }

            for (let j = 0; j < statesSelect.length; j++) {
              if (statesSelect[j] !== this) {
                statesSelect[j].value = selectedState;
              }
            }
          });
        }
      });
});
