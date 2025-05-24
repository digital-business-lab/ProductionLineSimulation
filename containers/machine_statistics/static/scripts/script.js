const sections = ["machine_cnc", "machine_assembly_robot", "machine_packaging"];
const metrics = {
    "machine_cnc" : ["Tool Temperature", "Spindle Speed"],
    "machine_assembly_robot" : ["Speed of Movement", "Load Weight"],
    "machine_packaging" : ["Package Weight", "Packaging Material"]
}
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
                        label: `${metrics[section][0]}`,
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
                            title: {
                                display: true,
                                text: 'Timestamp'
                            },
                            ticks: {
                                display: false  // Hides individual timestamps
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
                        label: `${metrics[section][1]}`,
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
                            title: {
                                display: true,
                                text: 'Timestamp'
                            },
                            ticks: {
                                display: false
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
        setInterval(() => fetchAndRender(section), 5000);
    });
}

document.addEventListener("DOMContentLoaded", startUpdating);
