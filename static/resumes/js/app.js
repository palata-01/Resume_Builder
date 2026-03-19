let currentResumeId = null;
let generatedPdfUrl = null;

function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
}

function addField(containerId, className, placeholder, isInput = false) {
    const container = document.getElementById(containerId);
    const wrapper = document.createElement("div");
    wrapper.className = "dynamic-item";

    if (isInput) {
        wrapper.innerHTML = `
            <input type="text" class="${className}" placeholder="${placeholder}">
            <button type="button" class="remove-btn">Remove</button>
        `;
    } else {
        wrapper.innerHTML = `
            <textarea class="${className}" rows="3" placeholder="${placeholder}"></textarea>
            <button type="button" class="remove-btn">Remove</button>
        `;
    }

    container.appendChild(wrapper);
    bindInputs();
    updatePreview();
}

document.addEventListener("click", function (e) {
    if (e.target.classList.contains("remove-btn")) {
        e.target.parentElement.remove();
        updatePreview();
    }
});

function getValues(className) {
    return [...document.querySelectorAll(`.${className}`)]
        .map(el => el.value.trim())
        .filter(Boolean);
}

function toTitleCase(text) {
    return text.replace(/\w\S*/g, function (txt) {
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
}

function detectDuplicateSkills(skills) {
    const seen = new Set();
    const duplicates = new Set();

    skills.forEach(skill => {
        const normalized = skill.toLowerCase().trim();
        if (seen.has(normalized)) {
            duplicates.add(skill);
        } else {
            seen.add(normalized);
        }
    });

    return [...duplicates];
}

function updatePreview() {
    const fullName = document.getElementById("full_name").value.trim();
    const email = document.getElementById("email").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const title = document.getElementById("title").value.trim();
    const summary = document.getElementById("summary").value.trim();

    const skills = getValues("skill-input");
    const education = getValues("education-input");
    const experience = getValues("experience-input");
    const projects = getValues("project-input");
    const certifications = getValues("certification-input");

    const preview = document.getElementById("resumePreview");

    preview.innerHTML = `
        <h1>${fullName || "Your Name"}</h1>
        <p>${email || "Email"} ${phone ? " | " + phone : ""}</p>
        <h3>${title || "Professional Title"}</h3>
        <hr>

        <h2>Summary</h2>
        <p>${summary || "Your summary will appear here..."}</p>

        <h2>Skills</h2>
        <ul>${skills.map(skill => `<li>${skill}</li>`).join("")}</ul>

        <h2>Education</h2>
        <ul>${education.map(item => `<li>${item}</li>`).join("")}</ul>

        <h2>Experience</h2>
        <ul>${experience.map(item => `<li>${item}</li>`).join("")}</ul>

        <h2>Projects</h2>
        <ul>${projects.map(item => `<li>${item}</li>`).join("")}</ul>

        <h2>Certifications</h2>
        <ul>${certifications.map(item => `<li>${item}</li>`).join("")}</ul>
    `;

    const allText = [
        fullName,
        email,
        phone,
        title,
        summary,
        ...skills,
        ...education,
        ...experience,
        ...projects,
        ...certifications
    ].join(" ").trim();

    const words = allText ? allText.split(/\s+/).length : 0;
    const characters = allText.length;
    const paragraphs = summary ? summary.split("\n").filter(p => p.trim()).length : 0;
    const readingTime = Math.max(1, Math.ceil(words / 200));

    document.getElementById("wordCount").innerText = words;
    document.getElementById("characterCount").innerText = characters;
    document.getElementById("letterCount").innerText = characters;
    document.getElementById("paragraphCount").innerText = paragraphs;
    document.getElementById("readingTime").innerText = readingTime;

    document.getElementById("lengthWarning").innerText =
        words > 700 ? "Warning: The recommended resume length is under 700 words." : "";

    const duplicateSkills = detectDuplicateSkills(skills);
    document.getElementById("duplicateWarning").innerText =
        duplicateSkills.length ? `Duplicate skill detected: ${duplicateSkills.join(", ")}` : "";

    document.getElementById("capitalizationSuggestion").innerText =
        title ? `Suggestion: ${toTitleCase(title)}` : "";

    document.getElementById("lastEdited").innerText =
        "Last Edited: " + new Date().toLocaleString();
}

function bindInputs() {
    document.querySelectorAll("input, textarea").forEach(el => {
        el.removeEventListener("input", updatePreview);
        el.addEventListener("input", updatePreview);
    });
}

async function parseJsonResponse(response) {
    const contentType = response.headers.get("content-type") || "";

    if (!contentType.includes("application/json")) {
        const text = await response.text();
        console.log("Non-JSON response:", text);
        throw new Error("Backend JSON nahi bhej raha. Check terminal / URL routing.");
    }

    return await response.json();
}

bindInputs();
updatePreview();

document.getElementById("resumeForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const payload = {
        full_name: document.getElementById("full_name").value.trim(),
        email: document.getElementById("email").value.trim(),
        phone: document.getElementById("phone").value.trim(),
        dob: document.getElementById("dob").value,
        title: document.getElementById("title").value.trim(),
        summary: document.getElementById("summary").value.trim(),
        skills: getValues("skill-input"),
        education: getValues("education-input"),
        experience: getValues("experience-input"),
        projects: getValues("project-input"),
        certifications: getValues("certification-input"),
    };

    try {
        const response = await fetch("/api/resumes/", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify(payload)
        });

        const data = await parseJsonResponse(response);

        if (!response.ok) {
            alert("Save failed: " + JSON.stringify(data));
            return;
        }

        currentResumeId = data.id;
        alert(`Resume saved successfully.\nResume ID: ${data.resume_id}`);
    } catch (error) {
        console.error("Save error:", error);
        alert("Error saving resume: " + error.message);
    }
});

document.getElementById("generatePdfBtn").addEventListener("click", async function () {
    if (!currentResumeId) {
        alert("Please save the resume first.");
        return;
    }

    try {
        const response = await fetch(`/api/resumes/${currentResumeId}/generate-pdf/`, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "X-CSRFToken": getCSRFToken()
            }
        });

        const data = await parseJsonResponse(response);
        console.log("PDF response:", data);

        if (!response.ok) {
            alert(data.error || "PDF generation failed.");
            return;
        }

        generatedPdfUrl = data.pdf_url || null;

        if (!generatedPdfUrl) {
            alert("PDF generated response aaya, but file URL missing hai. Backend save check karo.");
            return;
        }

        alert(`PDF generated successfully.\nPassword: ${data.password || "No password"}\nPDF URL: ${generatedPdfUrl}`);
    } catch (error) {
        console.error("PDF error:", error);
        alert("Error generating PDF: " + error.message);
    }
});

document.getElementById("downloadBtn").addEventListener("click", async function () {
    if (!currentResumeId) {
        alert("Please save and generate PDF first.");
        return;
    }

    try {
        const response = await fetch(`/api/resumes/${currentResumeId}/download/`, {
            method: "GET",
            credentials: "same-origin"
        });

        const data = await parseJsonResponse(response);

        if (!response.ok) {
            alert(data.error || "Download failed.");
            return;
        }

        if (!data.pdf_url) {
            alert("PDF URL not found.");
            return;
        }

        window.open(data.pdf_url, "_blank");
    } catch (error) {
        console.error("Download error:", error);
        alert("Error downloading PDF: " + error.message);
    }
});
document.getElementById("printBtn").addEventListener("click", function () {
    const previewElement = document.getElementById("resumePreview");
    const previewContent = previewElement ? previewElement.innerHTML.trim() : "";

    if (!previewContent) {
        alert("Preview content not found.");
        return;
    }

    const printWindow = window.open("", "_blank", "width=900,height=700");

    if (!printWindow) {
        alert("Popup blocked. Please allow popups for printing.");
        return;
    }

    printWindow.document.open();
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Print Resume</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    padding: 30px;
                    color: #222;
                    background: #fff;
                }
                h1 {
                    font-size: 28px;
                    margin-bottom: 8px;
                    color: #1d3557;
                }
                h2 {
                    font-size: 20px;
                    margin-top: 18px;
                    margin-bottom: 8px;
                    color: #1d3557;
                }
                h3 {
                    font-size: 16px;
                    margin: 8px 0;
                    color: #444;
                }
                p {
                    margin-bottom: 8px;
                    line-height: 1.5;
                }
                ul {
                    padding-left: 20px;
                    margin-bottom: 10px;
                }
                li {
                    margin-bottom: 6px;
                }
                hr {
                    margin: 12px 0;
                    border: 0;
                    border-top: 1px solid #ccc;
                }
            </style>
        </head>
        <body>
            ${previewContent}
        </body>
        </html>
    `);
    printWindow.document.close();

    printWindow.onload = function () {
        printWindow.focus();
        printWindow.print();
    };
});
document.getElementById("shareEmailBtn").addEventListener("click", async function () {
    if (!currentResumeId) {
        alert("Please save and generate PDF first.");
        return;
    }

    const email = prompt("Enter recipient email:");
    if (!email) return;
    if (!email.includes("@")) {
    alert("Please enter a valid email address.");
    return;
}

    try {
        const response = await fetch(`/api/sharing/${currentResumeId}/email/`, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({ email: email })
        });

        const data = await parseJsonResponse(response);

        if (!response.ok) {
            alert(data.error || "Email sharing failed.");
            return;
        }

        alert(data.message || "Email shared successfully.");
    } catch (error) {
        console.error("Email error:", error);
        alert("Error sharing via email: " + error.message);
    }
});

document.getElementById("shareWhatsappBtn").addEventListener("click", async function () {
    if (!currentResumeId) {
        alert("Please save and generate PDF first.");
        return;
    }

    const phone = prompt("Enter WhatsApp number with country code, e.g. 919876543210:");
    if (!phone) return;

    const cleanedPhone = phone.replace(/\D/g, "");

    if (!cleanedPhone) {
        alert("Please enter a valid WhatsApp number.");
        return;
    }

    try {
        const response = await fetch(`/api/sharing/${currentResumeId}/whatsapp/`, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({ phone: cleanedPhone })
        });

        const data = await parseJsonResponse(response);

        if (!response.ok) {
            alert(data.error || "WhatsApp sharing failed.");
            return;
        }

        const whatsappUrl = `https://wa.me/${data.phone}?text=${encodeURIComponent(data.whatsapp_text)}`;
        window.open(whatsappUrl, "_blank");
    } catch (error) {
        console.error("WhatsApp error:", error);
        alert("Error sharing via WhatsApp: " + error.message);
    }
});