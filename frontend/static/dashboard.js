// ===== CLOCK SETUP =====
const clockNumbers = [
    { outer: 12, inner: "00", angle: 0 },
    { outer: 1, inner: 13, angle: 30 },
    { outer: 2, inner: 14, angle: 60 },
    { outer: 3, inner: 15, angle: 90 },
    { outer: 4, inner: 16, angle: 120 },
    { outer: 5, inner: 17, angle: 150 },
    { outer: 6, inner: 18, angle: 180 },
    { outer: 7, inner: 19, angle: 210 },
    { outer: 8, inner: 20, angle: 240 },
    { outer: 9, inner: 21, angle: 270 },
    { outer: 10, inner: 22, angle: 300 },
    { outer: 11, inner: 23, angle: 330 },
];

function initClock() {
    const tickGroup = document.getElementById("tick-marks");
    const numberGroup = document.getElementById("clock-numbers");
    const cx = 200, cy = 200;

    // Add SVG gradient for bezel
    const svg = document.getElementById("clock-svg");
    const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
    
    const grad = document.createElementNS("http://www.w3.org/2000/svg", "linearGradient");
    grad.setAttribute("id", "bezelGrad");
    grad.setAttribute("x1", "0%");
    grad.setAttribute("y1", "0%");
    grad.setAttribute("x2", "100%");
    grad.setAttribute("y2", "100%");
    
    const stops = [
        { offset: "0%", color: "#c0c0c0" },
        { offset: "25%", color: "#707070" },
        { offset: "50%", color: "#a0a0a0" },
        { offset: "75%", color: "#808080" },
        { offset: "100%", color: "#c0c0c0" }
    ];
    
    stops.forEach(s => {
        const stop = document.createElementNS("http://www.w3.org/2000/svg", "stop");
        stop.setAttribute("offset", s.offset);
        stop.setAttribute("stop-color", s.color);
        grad.appendChild(stop);
    });
    
    defs.appendChild(grad);
    svg.insertBefore(defs, svg.firstChild);

    // Generate tick marks
    for (let i = 0; i < 60; i++) {
        const angle = (i * 6 - 90) * (Math.PI / 180);
        const isMajor = i % 5 === 0;
        const outerR = 182;
        const innerR = isMajor ? 166 : 174;

        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", cx + outerR * Math.cos(angle));
        line.setAttribute("y1", cy + outerR * Math.sin(angle));
        line.setAttribute("x2", cx + innerR * Math.cos(angle));
        line.setAttribute("y2", cy + innerR * Math.sin(angle));
        line.setAttribute("class", isMajor ? "tick-major" : "tick-minor");
        tickGroup.appendChild(line);
    }

    // Generate numbers
    clockNumbers.forEach(({ outer, inner, angle }) => {
        const rad = (angle - 90) * (Math.PI / 180);
        const outerR = 148;
        const innerR = 115;

        const outerText = document.createElementNS("http://www.w3.org/2000/svg", "text");
        outerText.setAttribute("x", cx + outerR * Math.cos(rad));
        outerText.setAttribute("y", cy + outerR * Math.sin(rad));
        outerText.setAttribute("class", "outer-number");
        outerText.textContent = outer;
        numberGroup.appendChild(outerText);

        const innerText = document.createElementNS("http://www.w3.org/2000/svg", "text");
        innerText.setAttribute("x", cx + innerR * Math.cos(rad));
        innerText.setAttribute("y", cy + innerR * Math.sin(rad));
        innerText.setAttribute("class", "inner-number");
        innerText.textContent = inner;
        numberGroup.appendChild(innerText);
    });
}

function updateClock() {
    const now = new Date();
    const hours = now.getHours();
    const minutes = now.getMinutes();
    const seconds = now.getSeconds();

    const hourDeg = (hours % 12) * 30 + minutes * 0.5;
    const minuteDeg = minutes * 6 + seconds * 0.1;
    const secondDeg = seconds * 6;

    document.getElementById("hour-hand").setAttribute("transform", `rotate(${hourDeg}, 200, 200)`);
    document.getElementById("minute-hand").setAttribute("transform", `rotate(${minuteDeg}, 200, 200)`);
    document.getElementById("second-hand").setAttribute("transform", `rotate(${secondDeg}, 200, 200)`);

    // Digital time
    const h24 = String(hours).padStart(2, "0");
    const m = String(minutes).padStart(2, "0");
    const s = String(seconds).padStart(2, "0");
    document.getElementById("digital-time").textContent = `${h24}:${m}:${s}`;

    // Date
    const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    const dayName = days[now.getDay()];
    const month = now.getMonth() + 1;
    const day = now.getDate();
    const year = now.getFullYear();
    document.getElementById("date-display").textContent = `${dayName} ${month}/${day}/${year}`;
}

// ===== SYSTEM STATS (placeholder - will connect to API) =====
function updateSystemGauges(cpu, hailo, ram, storage) {
    const maxDash = 163.4;

    function setGauge(ringId, valId, value) {
        const ring = document.getElementById(ringId);
        const val = document.getElementById(valId);
        if (ring) ring.style.strokeDasharray = `${(value / 100) * maxDash} ${maxDash}`;
        if (val) val.textContent = `${value}%`;
    }

    setGauge("cpu-ring", "cpu-val", cpu);
    setGauge("hailo-ring", "hailo-val", hailo);
    setGauge("ram-ring", "ram-val", ram);
    setGauge("storage-ring", "storage-val", storage);
}

// ===== INIT =====
document.addEventListener("DOMContentLoaded", () => {
    initClock();
    updateClock();
    setInterval(updateClock, 1000);

// Fetch live system stats every 3 seconds
    async function fetchSystemStats() {
        try {
            const res = await fetch("/api/system");
            const data = await res.json();
            updateSystemGauges(
                Math.round(data.cpu),
                Math.round(data.hailo),
                Math.round(data.ram),
                Math.round(data.storage)
            );
        } catch (e) {
            console.error("Failed to fetch system stats:", e);
        }
    }
    fetchSystemStats();
    setInterval(fetchSystemStats, 3000);
});
