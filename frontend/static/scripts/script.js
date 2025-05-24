// Change color of ampel
function setAmpelState(state, id) {
    const ampel = document.querySelector(`.ampel[data-id="${id}"]`);
    if (!ampel) return;

    const red = ampel.querySelector('[data-color="red"]');
    const yellow = ampel.querySelector('[data-color="yellow"]');
    const green = ampel.querySelector('[data-color="green"]');

    // Reset all to off
    red.style.backgroundColor = 'aliceblue';
    yellow.style.backgroundColor = 'aliceblue';
    green.style.backgroundColor = 'aliceblue';

    // Set based on state
    if (state === 'start') {
        green.style.backgroundColor = '#51cf66'; // green
    } else if (state === 'stop') {
        red.style.backgroundColor = '#ff6b6b'; // red
    }
}

//Function for Table View button that opens grafana in new Tab
function openInNewWindow() {
    const url = "http://localhost:3000/d/postgres-demo/postgres-table-view";
    window.open(url, "_blank");
}

// Function to start machine in backend
async function control(machine, action) {
    const el = document.querySelector(`[data-machine="${machine}"]`);
    const inputs = el.querySelectorAll('input');

    const data = {};
    inputs.forEach((input, i) => {
        data[`param${i + 1}`] = input.value;
    });

    const res = await fetch(`/${action}/${machine}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    const text = await res.text();
    document.getElementById('result').innerText = text;
}

// Function to draw arrows
function drawArrow(fromElem, toElem, svg, mode) {
    const fromRect = fromElem.getBoundingClientRect();
    const toRect = toElem.getBoundingClientRect();
    const svgRect = svg.getBoundingClientRect();

    // Start point: top center of machine
    const startX = fromRect.left + fromRect.width / 2 - svgRect.left;
    const startY = fromRect.top - svgRect.top;

    // End point: bottom center of database
    const endX = toRect.left + toRect.width / 2 - svgRect.left;
    const endY = toRect.bottom - svgRect.top;

    const arrow = document.createElementNS("http://www.w3.org/2000/svg", "line");
    arrow.setAttribute("x1", startX);
    arrow.setAttribute("y1", startY);
    if (mode === true) {
        arrow.setAttribute("x2", startX);
    } else {
        arrow.setAttribute("x2", endX)
    }
    arrow.setAttribute("y2", endY);
    arrow.setAttribute("stroke", "black");
    arrow.setAttribute("stroke-width", "2");
    arrow.setAttribute("class", "animated-line");
    arrow.setAttribute("marker-end", "url(#arrowhead)");

    svg.appendChild(arrow);
}

// Function to draw all specified arrows
function drawAllArrows() {
    const svg = document.getElementById("connection-arrows");

    // Clear any previous content and add arrowhead definition
    svg.innerHTML = `
        <defs>
            <marker
                id="arrowhead"
                markerWidth="6"
                markerHeight="4"
                refX="5"
                refY="2"
                orient="auto">
                <polygon points="0 0, 6 2, 0 4" fill="black" />
            </marker>
        </defs>
    `;
    
    const model_structure = document.querySelector(".Model-Structure")
    const quality_check = document.querySelector(".Quality-Check")
    const database_h1 = document.querySelector(".Database h1");
    const machines = document.querySelectorAll(".Machine");
    
    // Draw arrow from Machine to Database
    machines.forEach(machine => {
        drawArrow(machine, database_h1, svg, true);
    }); 

    // Draw arrow from DB to Model Structure and Quality Check
    drawArrow(database_h1, model_structure, svg, false)
    drawArrow(database_h1, quality_check, svg, false)
}

// Places arrows at location when reloading and resizing window
window.addEventListener('load', drawAllArrows);
window.addEventListener("resize", () => {
    requestAnimationFrame(drawAllArrows)
})