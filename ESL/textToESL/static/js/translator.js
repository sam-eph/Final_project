
const translationSelect = document.getElementById('translationSelect');
const textToSign = document.getElementById('textToSign');
const signToText = document.getElementById('signToText');
const signOutput = document.getElementById('signOutput');
const signTextOutput = document.getElementById('signTextOutput');
const camera = document.getElementById('camera');
let streamReference; // Reference to the media stream

translationSelect.addEventListener('change', () => {
    if (translationSelect.value === 'textToSign') {
    textToSign.style.display = 'flex';
    signToText.style.display = 'none';
    signOutput.style.display = 'flex';
    signTextOutput.style.display = 'none';
    } else {
    textToSign.style.display = 'none';
    signToText.style.display = 'flex';
    signOutput.style.display = 'none';
    signTextOutput.style.display = 'flex';
    }
});

document.getElementById('translateToSignBtn').addEventListener('click', () => {
    const text = document.getElementById('textInput').value;
    if (text.trim() === '') return;
    const signBox = document.querySelector('.sign-box');
    signBox.innerHTML = 'Translating...';
    setTimeout(() => {
    signBox.innerHTML = 'Sign for "' + text + '"';
    }, 2000);
});

document.getElementById('startCameraBtn').addEventListener('click', () => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
        camera.srcObject = stream;
        streamReference = stream; // Keep a reference to the stream
    });
    }
});

document.getElementById('stopCameraBtn').addEventListener('click', () => {
    if (streamReference) {
    streamReference.getTracks().forEach(track => track.stop());
    camera.srcObject = null;
    }
});

document.getElementById('captureBtn').addEventListener('click', () => {
    signTextOutput.innerText = 'Translating sign to text...';
    setTimeout(() => {
    signTextOutput.innerText = 'This is a placeholder translation.';
    }, 2000);
});

translationSelect.dispatchEvent(new Event('change'));
