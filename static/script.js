// Add edit events to all rectangle elements
document.querySelectorAll('.rectangle').forEach(box => {
    addEditEvent(box);
});

// Function to add click and blur events for editing content
function addEditEvent(element) {
    // Store the original and pre-written text in data attributes
    element.dataset.originalText = element.innerText;
    element.dataset.preWrittenText = element.innerText.split('\n')[0]; // First line is assumed as pre-written text

    element.addEventListener('click', function() {
        let lines = this.innerText.split('\n');
        if (lines.length > 1) {
            // If additional lines exist, prompt to edit the content after the first line
            const newText = prompt("Edit or add new text:", lines.slice(1).join('\n'));
            if (newText !== null) {
                // Update the content after pre-written text
                this.innerText = lines[0] + "\n" + newText.trim();
                moveCursorToNextLine(this);
            }
        } else {
            // If no additional lines, prompt to add text after the pre-written content
            const newText = prompt("Add new text below the existing content:");
            if (newText !== null) {
                this.innerText = lines[0] + "\n" + newText.trim();
                moveCursorToNextLine(this);
            }
        }
    });

    // Handle blur event to save content once editing is finished
    element.addEventListener('blur', function() {
        if (this.isContentEditable) {
            this.dataset.originalText = this.innerText;
            this.contentEditable = false;
            this.classList.remove('editing');
        }
    }, true);
}

// Function to move cursor to the last line after editing
function moveCursorToNextLine(element) {
    const lines = element.innerText.split('\n');
    if (lines.length > 1) {
        const range = document.createRange();
        const sel = window.getSelection();
        range.setStart(element.firstChild, element.innerText.length);
        range.collapse(true);
        sel.removeAllRanges();
        sel.addRange(range);
        element.focus();
    }
}

// Function to update the flowchart with the new form input data
function updateFlowchart() {
    document.getElementById("submit-button").style.display = "inline";

    // Retrieve input values and update corresponding elements
    const inputData = [
        { id: "total-subject", value: document.getElementById("input-total-subject").value },
        { id: "screening-eligibility", value: document.getElementById("input-screening-eligibility").value },
        { id: "eligible-enrollment", value: document.getElementById("input-eligible-enrollment").value },
        { id: "consent-enrolled", value: document.getElementById("input-consent-enrolled").value },
        { id: "images", value: document.getElementById("input-images").value },
        { id: "forehead", value: document.getElementById("input-forehead").value },
        { id: "sternum", value: document.getElementById("input-sternum").value },
        { id: "abdomen", value: document.getElementById("input-abdomen").value },
        { id: "hips-thighs", value: document.getElementById("input-hips-thighs").value },
        { id: "legs", value: document.getElementById("input-legs").value },
        { id: "palm", value: document.getElementById("input-palm").value },
        { id: "soles", value: document.getElementById("input-soles").value },
        { id: "clips-videos", value: document.getElementById("input-clips-videos").value },
        { id: "clip-forehead", value: document.getElementById("input-clip-forehead").value },
        { id: "clip-sternum", value: document.getElementById("input-clip-sternum").value },
        { id: "clip-abdomen", value: document.getElementById("input-clip-abdomen").value },
        { id: "clip-hips-thighs", value: document.getElementById("input-clip-hips-thighs").value },
        { id: "clip-legs", value: document.getElementById("input-clip-legs").value },
        { id: "clip-palm", value: document.getElementById("input-clip-palm").value },
        { id: "clip-soles", value: document.getElementById("input-clip-soles").value },
        { id: "consent-refused", value: document.getElementById("input-consent-refused").value },
        { id: "total-consent-refused", value: document.getElementById("input-total-consent-refused").value },
        { id: "reason-1", value: document.getElementById("input-reason-1").value },
        { id: "reason-2", value: document.getElementById("input-reason-2").value }
    ];

    inputData.forEach(item => updateElementContent(item.id, item.value));
}

// Helper function to update or replace content in elements
function updateElementContent(elementId, newValue) {
    if (newValue) {
        const element = document.getElementById(elementId);
        const originalContent = element.getAttribute('data-original-content') || element.innerHTML.split("<br>")[0];
        element.setAttribute('data-original-content', originalContent); // Store original content
        element.innerHTML = originalContent + "<br>" + newValue; // Replace content with original + new content
    }
}

// Function to submit the form data via AJAX
function submitForm() {
    // Get all form data
    const formData = new FormData(document.getElementById('flowchart-form'));
    
    // Convert form data to a JSON object
    const formObject = {};
    formData.forEach((value, key) => formObject[key] = value);

    // Make an AJAX request to send the form data to the server
    fetch('/save_entry', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formObject),
    })
    .then(response => response.json())
    .then(data => {
        alert("Entry saved successfully!");
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}
