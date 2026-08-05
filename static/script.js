function getLocation(){

    if(navigator.geolocation){

        navigator.geolocation.getCurrentPosition(showPosition);

    }else{

        alert("Geolocation is not supported.");

    }

}

function showPosition(position){

    const lat = position.coords.latitude;
    const lon = position.coords.longitude;

    window.location =
        "/location?lat=" + lat + "&lon=" + lon;

}