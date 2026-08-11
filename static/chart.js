/* =====================================================
   HOURLY TEMPERATURE CHART
===================================================== */


if (
    typeof hourlyData !== "undefined" &&
    hourlyData.length > 0
) {


    const labels =
        hourlyData.map(
            item => item.time
        );


    const temperatures =
        hourlyData.map(
            item => item.temp
        );


    /* Make temperatures available to script.js */

    window.hourlyTemperatures =
        temperatures;


    const canvas =
        document.getElementById(
            "hourlyChart"
        );


    if (canvas) {


        window.hourlyChart =
            new Chart(
                canvas,
                {

                    type: "line",

                    data: {

                        labels: labels,

                        datasets: [

                            {

                                label:
                                    "Temperature (°C)",

                                data:
                                    temperatures,

                                borderColor:
                                    "#ffd166",

                                backgroundColor:
                                    "rgba(255, 209, 102, 0.2)",

                                borderWidth: 3,

                                fill: true,

                                tension: 0.4,

                                pointRadius: 5,

                                pointBackgroundColor:
                                    "#ffd166"

                            }

                        ]

                    },


                    options: {

                        responsive: true,

                        maintainAspectRatio:
                            false,


                        plugins: {

                            legend: {

                                labels: {

                                    color:
                                        "white"

                                }

                            }

                        },


                        scales: {

                            x: {

                                ticks: {

                                    color:
                                        "white"

                                },

                                grid: {

                                    color:
                                        "rgba(255,255,255,0.15)"

                                }

                            },


                            y: {

                                ticks: {

                                    color:
                                        "white"

                                },

                                grid: {

                                    color:
                                        "rgba(255,255,255,0.15)"

                                }

                            }

                        }

                    }

                }
            );

    }

}