document.addEventListener("DOMContentLoaded", function () {
    if (typeof hourlyData === "undefined" || hourlyData.length === 0) {
        return;
    }

    const canvas = document.getElementById("hourlyChart");
    if (!canvas || typeof Chart === "undefined") {
        return;
    }

    const labels = hourlyData.map(item => item.time);
    const temperatures = hourlyData.map(item => Number(item.temp));

    window.hourlyTemperatures = temperatures;
    window.hourlyLabels = labels;

    window.hourlyChart = new Chart(canvas, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Temperature (°C)",
                data: temperatures,
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: "white" }
                }
            },
            scales: {
                x: {
                    ticks: { color: "white" },
                    grid: { color: "rgba(255,255,255,0.15)" }
                },
                y: {
                    ticks: {
                        color: "white",
                        callback: value => value + "°"
                    },
                    grid: { color: "rgba(255,255,255,0.15)" }
                }
            }
        }
    });
});
