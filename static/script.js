// Toggle overdraft limit field based on account type selection
function toggleOverdraftField() {
    const accType = document.getElementById("acc_type");
    const overdraftGroup = document.getElementById("overdraftGroup");
    if (!accType || !overdraftGroup) return;
    overdraftGroup.style.display = accType.value === "current" ? "block" : "none";
}

// Live preview of the uploaded KYC photo on the "Open Account" form
function previewPhoto(event) {
    const file = event.target.files && event.target.files[0];
    const wrapper = document.getElementById("photoPreview");
    const img = document.getElementById("photoPreviewImg");
    if (!file || !wrapper || !img) return;

    const reader = new FileReader();
    reader.onload = (e) => {
        img.src = e.target.result;
        wrapper.classList.add("has-image");
    };
    reader.readAsDataURL(file);
}

// Animate a numeric stat from 0 to its target value
function animateCount(el, target, isCurrency, duration = 900) {
    const start = performance.now();
    function tick(now) {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out-cubic
        const value = target * eased;
        el.textContent = isCurrency
            ? "₹" + value.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })
            : Math.round(value).toLocaleString("en-IN");
        if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
}

document.addEventListener("DOMContentLoaded", () => {
    toggleOverdraftField();

    // Auto-uppercase PAN input as the user types (PAN format: ABCDE1234F)
    const panField = document.getElementById("pan");
    if (panField) {
        panField.addEventListener("input", () => {
            panField.value = panField.value.toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, 10);
        });
    }
    document.querySelectorAll('input[name="check_pan"]').forEach((el) => {
        el.addEventListener("input", () => {
            el.value = el.value.toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, 10);
        });
    });

    // Format Aadhaar as the user types: 1234 5678 9012 (digits only, max 12)
    function formatAadhar(el) {
        el.addEventListener("input", () => {
            const digits = el.value.replace(/\D/g, "").slice(0, 12);
            el.value = digits.replace(/(\d{4})(?=\d)/g, "$1 ").trim();
        });
    }
    const aadharField = document.getElementById("aadhar");
    if (aadharField) formatAadhar(aadharField);
    document.querySelectorAll('input[name="check_aadhar"]').forEach(formatAadhar);

    // Auto-hide flash messages after 5 seconds
    document.querySelectorAll(".flash").forEach((el) => {
        setTimeout(() => {
            el.style.transition = "opacity 0.4s ease";
            el.style.opacity = "0";
            setTimeout(() => el.remove(), 400);
        }, 5000);
    });

    // Animate dashboard stat counters (reads target from data-value)
    document.querySelectorAll(".stat-value[data-value]").forEach((el) => {
        const target = parseFloat(el.getAttribute("data-value")) || 0;
        const isCurrency = el.hasAttribute("data-currency");
        animateCount(el, target, isCurrency);
    });
});
