/* =====================================================
   WEATHERWISE JAVASCRIPT
===================================================== */


/* =========================
   MY LOCATION
========================= */

function getLocation() {

    if (navigator.geolocation) {

        navigator.geolocation.getCurrentPosition(
            showPosition,
            showLocationError
        );

    } else {

        alert(
            "Geolocation is not supported by your browser."
        );

    }

}


function showPosition(position) {

    const lat =
        position.coords.latitude;

    const lon =
        position.coords.longitude;

    window.location =
        "/location?lat=" +
        lat +
        "&lon=" +
        lon;

}


function showLocationError(error) {

    alert(
        "Unable to get your location."
    );

}


/* =========================
   FAVORITES
========================= */

function getFavorites() {

    try {

        return JSON.parse(
            localStorage.getItem("favorites")
        ) || [];

    } catch (error) {

        return [];

    }

}


/* =========================
   UPDATE FAVORITE BUTTON
========================= */

function updateFavoriteButton() {

    const favoriteBtn =
        document.getElementById(
            "favoriteBtn"
        );

    if (!favoriteBtn) {
        return;
    }


    const city =
        favoriteBtn.dataset.city;

    const favorites =
        getFavorites();


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


/* =========================
   FAVORITE BUTTON
========================= */

const favoriteBtn =
    document.getElementById(
        "favoriteBtn"
    );


if (favoriteBtn) {

    favoriteBtn.addEventListener(
        "click",
        function () {

            const city =
                favoriteBtn.dataset.city;

            let favorites =
                getFavorites();


            if (favorites.includes(city)) {

                favorites =
                    favorites.filter(
                        item => item !== city
                    );

            } else {

                favorites.push(city);

            }


            localStorage.setItem(
                "favorites",
                JSON.stringify(favorites)
            );


            updateFavoriteButton();

            loadFavorites();

        }
    );


    updateFavoriteButton();

}


/* =========================
   LOAD FAVORITES
========================= */

function loadFavorites() {

    const container =
        document.getElementById(
            "favoriteCities"
        );

    const card =
        document.getElementById(
            "favoritesCard"
        );


    if (!container || !card) {
        return;
    }


    const favorites =
        getFavorites();


    container.innerHTML = "";


    if (favorites.length === 0) {

        card.style.display = "none";

        return;

    }


    card.style.display = "block";


    favorites.forEach(
        function (city) {

            const wrapper =
                document.createElement(
                    "div"
                );

            wrapper.className =
                "d-inline-block m-1";


            /* Search button */

            const button =
                document.createElement(
                    "button"
                );

            button.className =
                "btn btn-warning btn-sm";

            button.textContent =
                "⭐ " + city;


            button.addEventListener(
                "click",
                function () {

                    const searchInput =
                        document.querySelector(
                            'input[name="city"]'
                        );


                    const searchForm =
                        searchInput
                            ? searchInput.closest(
                                "form"
                            )
                            : null;


                    if (
                        searchInput &&
                        searchForm
                    ) {

                        searchInput.value =
                            city;

                        searchForm.submit();

                    }

                }
            );


            /* Remove button */

            const remove =
                document.createElement(
                    "button"
                );

            remove.className =
                "btn btn-danger btn-sm ms-1";

            remove.textContent =
                "❌";


            remove.addEventListener(
                "click",
                function () {

                    let list =
                        getFavorites();


                    list =
                        list.filter(
                            item => item !== city
                        );


                    localStorage.setItem(
                        "favorites",
                        JSON.stringify(list)
                    );


                    loadFavorites();

                    updateFavoriteButton();

                }
            );


            wrapper.appendChild(button);

            wrapper.appendChild(remove);

            container.appendChild(wrapper);

        }
    );

}


/* Load favorites */

loadFavorites();


/* =========================
   TEMPERATURE UNIT
========================= */

const temperatureElement =
    document.getElementById(
        "temperature"
    );


const unitElement =
    document.getElementById(
        "unit"
    );


const unitToggle =
    document.getElementById(
        "unitToggle"
    );


if (
    temperatureElement &&
    unitElement &&
    unitToggle
) {


    const celsius =
        parseFloat(
            temperatureElement.textContent
        );


    let isCelsius =
        localStorage.getItem(
            "temperatureUnit"
        ) !== "F";


    function updateTemperature() {


        /* Main temperature */

        if (isCelsius) {

            temperatureElement.textContent =
                Math.round(celsius);

            unitElement.textContent =
                "C";

        } else {

            const fahrenheit =
                (celsius * 9 / 5) + 32;

            temperatureElement.textContent =
                Math.round(fahrenheit);

            unitElement.textContent =
                "F";

        }


        /* Forecast maximum */

        document
            .querySelectorAll(
                ".forecast-max"
            )
            .forEach(
                function (element) {

                    const temp =
                        parseFloat(
                            element.dataset.celsius
                        );


                    if (isCelsius) {

                        element.textContent =
                            Math.round(temp);

                    } else {

                        element.textContent =
                            Math.round(
                                (temp * 9 / 5) + 32
                            );

                    }

                }
            );


        /* Forecast minimum */

        document
            .querySelectorAll(
                ".forecast-min"
            )
            .forEach(
                function (element) {

                    const temp =
                        parseFloat(
                            element.dataset.celsius
                        );


                    if (isCelsius) {

                        element.textContent =
                            Math.round(temp);

                    } else {

                        element.textContent =
                            Math.round(
                                (temp * 9 / 5) + 32
                            );

                    }

                }
            );


        /* Forecast units */

        document
            .querySelectorAll(
                ".day-card strong"
            )
            .forEach(
                function (element) {

                    element.innerHTML =
                        element.innerHTML.replace(
                            /°[CF]/g,
                            isCelsius
                                ? "°C"
                                : "°F"
                        );

                }
            );


        document
            .querySelectorAll(
                ".day-card small"
            )
            .forEach(
                function (element) {

                    element.innerHTML =
                        element.innerHTML.replace(
                            /°[CF]/g,
                            isCelsius
                                ? "°C"
                                : "°F"
                        );

                }
            );


        /* Hourly chart */

        if (
            window.hourlyChart &&
            Array.isArray(
                window.hourlyTemperatures
            )
        ) {

            if (isCelsius) {

                window.hourlyChart
                    .data
                    .datasets[0]
                    .data =
                    window.hourlyTemperatures;

                window.hourlyChart
                    .data
                    .datasets[0]
                    .label =
                    "Temperature (°C)";

            } else {

                window.hourlyChart
                    .data
                    .datasets[0]
                    .data =
                    window.hourlyTemperatures.map(
                        function (temp) {

                            return (
                                temp * 9 / 5
                            ) + 32;

                        }
                    );

                window.hourlyChart
                    .data
                    .datasets[0]
                    .label =
                    "Temperature (°F)";

            }


            window.hourlyChart.update();

        }

    }


    /* Toggle button */

    unitToggle.addEventListener(
        "click",
        function () {

            isCelsius =
                !isCelsius;


            localStorage.setItem(
                "temperatureUnit",
                isCelsius
                    ? "C"
                    : "F"
            );


            updateTemperature();

        }
    );


    /* Initial */

    updateTemperature();

}