document.getElementById("uploadForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById("fileInput");
    const targetLang = document.getElementById("targetLang").value;

    const formData = new FormData();
    formData.append("audio", fileInput.files[0]);
    formData.append("target_language", targetLang);

    const status = document.getElementById("status");
    status.innerHTML = "Processing...";

    const res = await fetch("/api/upload_audio", {
        method: "POST",
        body: formData
    });

    const data = await res.json();

    if (data.id) {
        window.location.href = `/result?id=${data.id}`;
    } else {
        status.innerHTML = "Error processing audio.";
    }
});
