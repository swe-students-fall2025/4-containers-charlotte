const params = new URLSearchParams(window.location.search);
const id = params.get("id");

async function loadResult() {
    const res = await fetch(`/api/get_result/${id}`);
    const data = await res.json();

    const div = document.getElementById("result");
    div.innerHTML = `
        <p><strong>File:</strong> ${data.filename}</p>
        <p><strong>Language:</strong> ${data.target_language}</p>
        <p><strong>Result:</strong></p>
        <pre>${data.result_text}</pre>
        <p><strong>Timestamp:</strong> ${new Date(data.timestamp)}</p>
    `;
}

loadResult();
