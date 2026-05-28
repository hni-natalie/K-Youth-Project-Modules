let files = [];

window.addEventListener("DOMContentLoaded", () => {

    const fileContainer = document.getElementById("fileContainer");
    const input = document.getElementById("messageInput");
    const fileInput = document.getElementById("fileInput");

    input.value = "";
    input.style.height = "45px";

    /* ===================== AUTO RESIZE ===================== */

    input.addEventListener("input", function () {
        this.style.height = "auto";
        this.style.height = this.scrollHeight + "px";
    });

    /* ===================== ENTER = SEND ===================== */

    input.addEventListener("keydown", function (event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });

    /* ===================== FILE UPLOAD ===================== */

    fileInput.addEventListener("change", function (event) {
        const selectedFiles = Array.from(event.target.files);

        console.log("📥 FILE INPUT SELECTED:", selectedFiles);

        files.push(...selectedFiles);

        console.log("📦 FILES STORED IN MEMORY:", files);

        renderFiles();

        fileInput.value = "";
    });

    window.sendMessage = sendMessage;

    window.addEventListener("load", () => input.focus());

    /* ===================== FILE UI ===================== */

    function renderFiles() {
        if (files.length === 0) {
            fileContainer.classList.add("d-none");
            fileContainer.innerHTML = "";
            return;
        }

        fileContainer.classList.remove("d-none");

        fileContainer.innerHTML = files.map((f, i) => `
            <div class="bg-secondary text-white p-2 mb-1 rounded d-flex justify-content-between align-items-center">
                <span>📎 ${f.name}</span>
                <button class="btn btn-sm btn-light" onclick="removeFile(${i})">
                    ✕
                </button>
            </div>
        `).join("");
    }

    window.removeFile = function (index) {
        files.splice(index, 1);
        renderFiles();
    };

    function clearFiles() {
        files = [];
        renderFiles();
        fileInput.value = "";
    }

    /* ===================== CHAT UI ===================== */

    function addLoadingMessage() {
        const chatBox = document.getElementById("chatBox");

        const wrapper = document.createElement("div");
        wrapper.id = "loading-message";
        wrapper.className = "text-start mb-2";

        wrapper.innerHTML = `
            <div class="d-inline-flex align-items-center gap-2 p-2 rounded bg-dark-subtle text-dark">
                <span class="spinner-border spinner-border-sm"></span>
                <span>Thinking...</span>
            </div>
        `;

        chatBox.appendChild(wrapper);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function removeLoadingMessage() {
        const loading = document.getElementById("loading-message");
        if (loading) loading.remove();
    }

    function addMessage(text, sender) {
        const chatBox = document.getElementById("chatBox");

        const wrapper = document.createElement("div");

        wrapper.className =
            sender === "user"
                ? "text-end mb-2"
                : "text-start mb-2";

        const bubble = document.createElement("div");

        bubble.className =
            sender === "user"
                ? "d-inline-block p-2 rounded bg-secondary text-white"
                : "d-inline-block p-2 rounded bg-dark-subtle text-dark";

        bubble.innerText = text;

        wrapper.appendChild(bubble);
        chatBox.appendChild(wrapper);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function addFileBubbles(fileList) {
        const chatBox = document.getElementById("chatBox");

        fileList.forEach(f => {
            const wrapper = document.createElement("div");
            wrapper.className = "text-end mb-1";

            wrapper.innerHTML = `
                <div class="d-inline-flex align-items-center gap-2 p-2 px-3 rounded bg-light text-dark border">
                    📄 ${f.name}
                </div>
            `;

            chatBox.appendChild(wrapper);
        });
    }

    /* ===================== PDF EXTRACTION ===================== */

    async function extractPDFText(file) {
        try {
            console.log("📄 Extracting:", file.name);

            const arrayBuffer = await file.arrayBuffer();

            const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;

            console.log("📄 Pages:", pdf.numPages);

            let text = "";

            for (let i = 1; i <= pdf.numPages; i++) {

                const page = await pdf.getPage(i);

                const content = await page.getTextContent();

                const pageText = content.items
                    .map(item => item.str)
                    .join(" ");

                console.log(`PAGE ${i}:`, pageText);

                text += pageText + "\n";
            }

            console.log("✅ FINAL TEXT:", text);

            return text.trim();

        } catch (err) {
            console.error("❌ PDF extract failed:", err);
            return "";
        }
    }

    /* ===================== MAIN SEND ===================== */

    async function sendMessage() {

        const text = input.value.trim();

        if (!text && files.length === 0) return;

        const currentFiles = [...files];

        console.log("🚀 SENDING MESSAGE");
        console.log("📝 TEXT:", text);
        console.log("📎 FILES COUNT:", currentFiles.length);
        console.log("📎 FILES:", currentFiles);

        if (currentFiles.length > 0) { addFileBubbles(currentFiles); }

        if (text) { addMessage(text, "user"); }

        addLoadingMessage();

        input.value = "";
        input.style.height = "45px";

        const formData = new FormData();

        formData.append("message", text);

        let extractedText = "";

        console.log( "=== BEFORE APPENDING FILES ===" );

        for (const f of currentFiles) {

            console.log( "➡️ adding file:", f.name, f);

            // Keep file upload
            formData.append("files", f);

            // Extract PDF text
            if (
                f.type === "application/pdf" ||
                f.name.toLowerCase().endsWith(".pdf")
            ) {

                const pdfText =
                    await extractPDFText(f);

                extractedText += `
===== FILE: ${f.name} =====

${pdfText}

`;
            }
        }

        // Send extracted text
        formData.append( "pdf_text", extractedText );

        console.log( "📑 EXTRACTED PDF TEXT:" );

        console.log(extractedText);

        /* ===================== DEBUG ===================== */

        console.log( "=== DEBUG FORM DATA ===" );

        for (let pair of formData.entries()) {
            console.log( pair[0], pair[1] );
        }

        try {

            const res = await fetch(
                `${BACKEND_URL}/chat`,
                {
                    method: "POST",
                    body: formData
                }
            );

            const data = await res.json();

            removeLoadingMessage();
            clearFiles();

            console.log( "📩 RESPONSE:", data );

            if (data.success === false) {
                addMessage(
                    data.message ||
                    "Something went wrong",
                    "bot"
                );
            } else {
                addMessage( data.response, "bot" );
            }

        } catch (err) {

            removeLoadingMessage();

            addMessage( "❌ Backend error", "bot" );

            console.error( "FETCH ERROR:", err );
        }

        input.focus();
    }

});