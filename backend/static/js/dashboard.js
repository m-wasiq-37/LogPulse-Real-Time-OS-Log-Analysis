let socket;
let logPieChart, logFreqChart;

function initDashboard() {
    socket = io();

    socket.on('connected', function(data) {
        console.log(data.msg);
    });

    socket.on('new_log', function(log) {
        addLogToFeed(log);
        updateAnalytics();
    });

    fetchLogs();
    updateAnalytics();

    document.getElementById('filter-form').onsubmit = function(e) {
        e.preventDefault();
        filterLogs();
    };
}

function addLogToFeed(log) {
    const feed = document.getElementById('logs-feed');
    const el = document.createElement('div');
    el.innerHTML = `<span class="log-level-${log.level}">[${log.level}]</span>
        <span>${new Date(log.timestamp).toLocaleString()}</span>
        <span>(${log.source})</span>
        <span>${log.message}</span>`;
    feed.prepend(el);
    if (feed.children.length > 200) feed.removeChild(feed.lastChild);
}

function fetchLogs() {
    fetch('/api/logs')
    .then(res => res.json())
    .then(logs => {
        const feed = document.getElementById('logs-feed');
        feed.innerHTML = '';
        logs.reverse().forEach(addLogToFeed);
    });
}

function filterLogs() {
    const form = document.getElementById('filter-form');
    const data = {
        level: form.level.value,
        source: form.source.value,
        start: form.start.value ? Date.parse(form.start.value) : null,
        end: form.end.value ? Date.parse(form.end.value) + 86400000 : null
    };
    fetch('/api/logs/filter', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(logs => {
        const feed = document.getElementById('logs-feed');
        feed.innerHTML = '';
        logs.reverse().forEach(addLogToFeed);
    });
}

function updateAnalytics() {
    fetch('/api/analytics/counts')
    .then(res => res.json())
    .then(data => {
        if (!logPieChart) {
            let ctx = document.getElementById('log-pie').getContext('2d');
            logPieChart = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: Object.keys(data),
                    datasets: [{
                        label: 'Log Types',
                        data: Object.values(data),
                        backgroundColor: [
                            '#58a6ff', '#f85149', '#238636'
                        ]
                    }]
                }
            });
        } else {
            logPieChart.data.labels = Object.keys(data);
            logPieChart.data.datasets[0].data = Object.values(data);
            logPieChart.update();
        }
    });

    fetch('/api/analytics/frequency')
    .then(res => res.json())
    .then(data => {
        let labels = Object.keys(data);
        let values = Object.values(data);
        if (!logFreqChart) {
            let ctx = document.getElementById('log-freq').getContext('2d');
            logFreqChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Logs per Minute',
                        data: values,
                        borderColor: '#58a6ff',
                        fill: false,
                        tension: 0.3
                    }]
                }
            });
        } else {
            logFreqChart.data.labels = labels;
            logFreqChart.data.datasets[0].data = values;
            logFreqChart.update();
        }
    });

    fetch('/api/analytics/top')
    .then(res => res.json())
    .then(data => {
        const ul = document.getElementById('top-events');
        ul.innerHTML = '';
        Object.entries(data).forEach(([msg, count]) => {
            const li = document.createElement('li');
            li.textContent = `${msg} (${count})`;
            ul.appendChild(li);
        });
    });
}