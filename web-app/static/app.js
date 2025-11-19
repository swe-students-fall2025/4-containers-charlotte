// upload page
if (window.location.pathname === "/" || window.location.pathname === "/upload") {
    const form = document.getElementById("uploadForm");
    const fileInput = document.getElementById("fileInput");
    const statusEl = document.getElementById("uploadStatus");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        statusEl.textContent = "Uploading and processing...";

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);
        formData.append("target_language", document.getElementById("targetLanguage").value);

        const resp = await fetch("/api/upload", {
            method: "POST",
            body: formData
        });

        const data = await resp.json();

        if (!resp.ok) {
            statusEl.textContent = "Error: " + (data.error || "Upload failed");
            return;
        }

        // Store result in localStorage so result.html can read it
        localStorage.setItem("resultData", JSON.stringify(data));

        window.location.href = "/result";
    });
}



// result page
if (window.location.pathname === "/result") {
    const data = JSON.parse(localStorage.getItem("resultData") || "{}");

    document.getElementById("transcriptText").textContent = data.transcript || "(none)";
    document.getElementById("translationText").textContent = data.translation || "(none)";

    if (data.audio_url) {
        document.getElementById("outputAudio").src = data.audio_url;
    }
}


//  history page
if (window.location.pathname === "/history") {
    const tbody = document.querySelector("#historyTable tbody");

    fetch("/api/history")
        .then(r => r.json())
        .then(rows => {
            rows.forEach(row => {
                const tr = document.createElement("tr");

                tr.innerHTML = `
                    <td>${row.created_at || ""}</td>
                    <td>${row.original_filename || ""}</td>
                    <td>${row.transcript || ""}</td>
                    <td>${row.translation || ""}</td>
                    <td>${row.audio_url ? `<audio controls src="${row.audio_url}"></audio>` : ""}</td>
                `;

                tbody.appendChild(tr);
            });
        });
}
