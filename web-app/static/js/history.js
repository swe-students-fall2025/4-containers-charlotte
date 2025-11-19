async function loadHistory() {
    const res = await fetch("/api/get_history");
    const items = await res.json();

    const div = document.getElementById("history");

    div.innerHTML = items.map(i => `
        <div class="card mb-3 p-3">
            <p><strong>File:</strong> ${i.filename}</p>
            <p><strong>Language:</strong> ${i.target_language}</p>
            <p><strong>Date:</strong> ${new Date(i.timestamp)}</p>
            <a href="/result?id=${i._id}" class="btn btn-primary btn-sm">View Result</a>
        </div>
    `).join("");
}

loadHistory();
