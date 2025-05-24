const sections = ["cnc", "ar", "pack"];
const charts = {};

async function fetchAndRender(section) {
    const res = await fetch(`/data/${section}`);
    const rawData = await res.json();

    const labels = rawData.map(d => new Date(d.timestamp * 1000));
    const data1 = rawData.map(d => d.value1);
    const data2 = rawData.map(d => d.value2);

    if (!charts[section]) {
        charts[section] = [
            new Chart(document.getElementById(`${section}Chart1`).getContext('2d'), {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: `${section.toUpperCase()} Metric 1`,
                        data: data1,
                        borderColor: 'blue',
                        borderWidth: 2,
                        fill: false
                    }]
                },
                options: {
                    animation: false,
                    scales: {
                        x: {
                            ticks: {
                                display: false  // Hide x-axis timestamps
                            }
                        }
                    }
                }
            }),
            new Chart(document.getElementById(`${section}Chart2`).getContext('2d'), {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: `${section.toUpperCase()} Metric 2`,
                        data: data2,
                        borderColor: 'green',
                        borderWidth: 2,
                        fill: false
                    }]
                },
                options: {
                    animation: false,
                    scales: {
                        x: {
                            ticks: {
                                display: false  // Hide x-axis timestamps
                            }
                        }
                    }
                }
            })
        ];
    } else {
        charts[section][0].data.labels = labels;
        charts[section][0].data.datasets[0].data = data1;
        charts[section][0].update();

        charts[section][1].data.labels = labels;
        charts[section][1].data.datasets[0].data = data2;
        charts[section][1].update();
    }
}

function startUpdating() {
    sections.forEach(section => {
        fetchAndRender(section);
        setInterval(() => fetchAndRender(section), 30000);
    });
}

document.addEventListener("DOMContentLoaded", startUpdating);
