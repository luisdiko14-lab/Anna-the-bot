async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        document.getElementById('cpu-val').textContent = data.cpu;
        document.getElementById('ram-val').textContent = data.ram;
        document.getElementById('platform-val').textContent = data.platform;
        document.getElementById('status-badge').textContent = data.status;
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

setInterval(updateStats, 2000);
updateStats();
