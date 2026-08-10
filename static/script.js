// ===========================
// My Location
// ===========================

function getLocation() {

    if (navigator.geolocation) {

        navigator.geolocation.getCurrentPosition(showPosition);

    } else {

        alert("Geolocation is not supported.");

    }

}


function showPosition(position) {

    const lat = position.coords.latitude;
    const lon = position.coords.longitude;

    window.location =
        "/location?lat=" + lat + "&lon=" + lon;
}


// ===========================
// Favorite Cities
// ===========================

const favoriteBtn =
    document.getElementById("favoriteBtn");


function loadFavorites() {

    const favorites =
        JSON.parse(localStorage.getItem("favorites")) || [];

    const container =
        document.getElementById("favoriteCities");

    const card =
        document.getElementById("favoritesCard");

    if (!container || !card) {
        return;
    }

    container.innerHTML = "";

    if (favorites.length === 0) {

        card.style.display = "none";
        return;

    }

    card.style.display = "block";


    favorites.forEach(function(city) {

        const wrapper =
            document.createElement("div");

        wrapper.className =
            "d-inline-block m-1";


        const button =
            document.createElement("button");

        button.className =
            "btn btn-warning btn-sm";

        button.innerHTML =
            "⭐ " + city;


        button.onclick = function() {

            const input =
                document.querySelector(
                    'input[name="city"]'
                );

            if (input) {

                input.value = city;

                input.closest("form").submit();

            }

        };


        const remove =
            document.createElement("button");

        remove.className =
            "btn btn-danger btn-sm ms-1";

        remove.innerHTML =
            "❌";


        remove.onclick = function() {

            let list =
                JSON.parse(
                    localStorage.getItem("favorites")
                ) || [];


            list = list.filter(function(item) {

                return item !== city;

            });


            localStorage.setItem(
                "favorites",
                JSON.stringify(list)
            );


            loadFavorites();
            updateFavoriteButton();

        };


        wrapper.appendChild(button);
        wrapper.appendChild(remove);

        container.appendChild(wrapper);

    });

}


// ===========================
// Favorite Button
// ===========================

function updateFavoriteButton() {

    if (!favoriteBtn) {
        return;
    }

    const city =
        favoriteBtn.dataset.city;

    const favorites =
        JSON.parse(
            localStorage.getItem("favorites")
        ) || [];


    if (favorites.includes(city)) {

        favoriteBtn.innerHTML =
            "⭐ Remove from Favorites";

        favoriteBtn.classList.remove(
            "btn-warning"
        );

        favoriteBtn.classList.add(
            "btn-success"
        );

    } else {

        favoriteBtn.innerHTML =
            "⭐ Add to Favorites";

        favoriteBtn.classList.remove(
            "btn-success"
        );

        favoriteBtn.classList.add(
            "btn-warning"
        );

    }

}


if (favoriteBtn) {

    favoriteBtn.addEventListener(
        "click",
        function() {

            const city =
                favoriteBtn.dataset.city;

            let favorites =
                JSON.parse(
                    localStorage.getItem("favorites")
                ) || [];


            if (favorites.includes(city)) {

                favorites =
                    favorites.filter(
                        function(item) {
                            return item !== city;
                        }
                    );

            } else {

                favorites.push(city);

            }


            localStorage.setItem(
                "favorites",
                JSON.stringify(favorites)
            );


            loadFavorites();
            updateFavoriteButton();

        }
    );

}


loadFavorites();
updateFavoriteButton();
// ===========================
// Temperature Unit Toggle
// ===========================

const temperatureElement =
    document.getElementById("temperature");

const unitElement =
    document.getElementById("unit");

const unitToggle =
    document.getElementById("unitToggle");


if (temperatureElement && unitElement && unitToggle) {

    const celsius =
        parseFloat(temperatureElement.textContent);

    let isCelsius =
        localStorage.getItem("temperatureUnit") !== "F";


    function updateTemperature() {

        if (isCelsius) {

            temperatureElement.textContent =
                Math.round(celsius);

            unitElement.textContent = "C";

        } else {

            const fahrenheit =
                (celsius * 9 / 5) + 32;

            temperatureElement.textContent =
                Math.round(fahrenheit);

            unitElement.textContent = "F";
        }

    }


    unitToggle.addEventListener(
        "click",
        function () {

            isCelsius = !isCelsius;

            localStorage.setItem(
                "temperatureUnit",
                isCelsius ? "C" : "F"
            );

            updateTemperature();
            updateHourlyChart();

        }
    );


    updateTemperature();

}
// ===========================
// Hourly Chart Temperature Unit
// ===========================

function updateHourlyChart() {

    if (!window.hourlyChart || !window.hourlyTemperatures) {
        return;
    }

    const isCelsius =
        localStorage.getItem("temperatureUnit") !== "F";

    if (isCelsius) {

        window.hourlyChart.data.datasets[0].data =
            window.hourlyTemperatures;

        window.hourlyChart.data.datasets[0].label =
            "Temperature (°C)";

    } else {

        window.hourlyChart.data.datasets[0].data =
            window.hourlyTemperatures.map(function(temp) {

                return (temp * 9 / 5) + 32;

            });

        window.hourlyChart.data.datasets[0].label =
            "Temperature (°F)";
    }

    window.hourlyChart.update();
}