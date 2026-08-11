// ===========================
// My Location
// ===========================
function getLocation() {
    if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser.");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        function (position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            window.location.href = `/location?lat=${lat}&lon=${lon}`;
        },
        function () {
            alert("Unable to get your location. Please allow location access.");
        }
    );
}


// ===========================
// Favorite Cities
// ===========================
function loadFavorites() {
    const favorites = JSON.parse(localStorage.getItem("favorites")) || [];
    const container = document.getElementById("favoriteCities");
    const card = document.getElementById("favoritesCard");

    if (!container || !card) return;

    container.innerHTML = "";

    if (favorites.length === 0) {
        card.style.display = "none";
        return;
    }

    card.style.display = "block";

    favorites.forEach(city => {
        const wrapper = document.createElement("div");
        wrapper.className = "d-inline-block m-1";

        const button = document.createElement("button");
        button.className = "btn btn-warning btn-sm";
        button.textContent = "⭐ " + city;
        button.onclick = function () {
            const input = document.querySelector('input[name="city"]');
            const form = input ? input.closest("form") : null;
            if (input && form) {
                input.value = city;
                form.submit();
            }
        };

        const remove = document.createElement("button");
        remove.className = "btn btn-danger btn-sm ms-1";
        remove.textContent = "❌";
        remove.onclick = function () {
            const updated = favorites.filter(item => item !== city);
            localStorage.setItem("favorites", JSON.stringify(updated));
            loadFavorites();
            updateFavoriteButton();
        };

        wrapper.appendChild(button);
        wrapper.appendChild(remove);
        container.appendChild(wrapper);
    });
}

function updateFavoriteButton() {
    const button = document.getElementById("favoriteBtn");
    if (!button) return;

    const city = button.dataset.city;
    const favorites = JSON.parse(localStorage.getItem("favorites")) || [];
    const saved = favorites.includes(city);

    button.textContent = saved ? "⭐ Remove from Favorites" : "⭐ Add to Favorites";
    button.classList.toggle("btn-warning", !saved);
    button.classList.toggle("btn-success", saved);
}


document.addEventListener("DOMContentLoaded", function () {
    const favoriteBtn = document.getElementById("favoriteBtn");

    if (favoriteBtn) {
        favoriteBtn.addEventListener("click", function () {
            const city = favoriteBtn.dataset.city;
            let favorites = JSON.parse(localStorage.getItem("favorites")) || [];

            if (favorites.includes(city)) {
                favorites = favorites.filter(item => item !== city);
            } else {
                favorites.push(city);
            }

            localStorage.setItem("favorites", JSON.stringify(favorites));
            updateFavoriteButton();
            loadFavorites();
        });

        updateFavoriteButton();
    }

    loadFavorites();


    // ===========================
    // Celsius / Fahrenheit
    // ===========================
    const temperatureElement = document.getElementById("temperature");
    const unitElement = document.getElementById("unit");
    const unitToggle = document.getElementById("unitToggle");

    if (temperatureElement && unitElement && unitToggle) {
        const celsius = parseFloat(temperatureElement.textContent);
        let isCelsius = localStorage.getItem("temperatureUnit") !== "F";

        function updateTemperature() {
            if (isCelsius) {
                temperatureElement.textContent = Math.round(celsius);
                unitElement.textContent = "C";
            } else {
                temperatureElement.textContent = Math.round((celsius * 9 / 5) + 32);
                unitElement.textContent = "F";
            }

            document.querySelectorAll(".forecast-max, .forecast-min").forEach(element => {
                const temp = parseFloat(element.dataset.celsius);
                element.textContent = isCelsius
                    ? Math.round(temp)
                    : Math.round((temp * 9 / 5) + 32);
            });

            document.querySelectorAll(".day-card strong, .day-card small").forEach(element => {
                element.innerHTML = element.innerHTML.replace(/°[CF]/g, isCelsius ? "°C" : "°F");
            });

            if (window.hourlyChart && Array.isArray(window.hourlyTemperatures)) {
                const data = isCelsius
                    ? window.hourlyTemperatures
                    : window.hourlyTemperatures.map(temp => (temp * 9 / 5) + 32);

                window.hourlyChart.data.datasets[0].data = data;
                window.hourlyChart.data.datasets[0].label = isCelsius
                    ? "Temperature (°C)"
                    : "Temperature (°F)";
                window.hourlyChart.update();
            }
        }

        unitToggle.addEventListener("click", function () {
            isCelsius = !isCelsius;
            localStorage.setItem("temperatureUnit", isCelsius ? "C" : "F");
            updateTemperature();
        });

        updateTemperature();
    }
});
