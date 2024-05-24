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
    
    fetch('/translate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: text })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            const videoUrls = data.video_urls;
            playVideosInSequence(videoUrls, signBox);
        }
    });
});

document.getElementById('startCameraBtn').addEventListener('click', () => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
            camera.srcObject = stream;
            streamReference = stream; // Keep a reference to the stream
        }).catch(err => {
            console.error('Error accessing camera: ', err);
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
    
    const canvas = document.createElement('canvas');
    canvas.width = camera.videoWidth;
    canvas.height = camera.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(camera, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL('image/png');
    
    fetch('/signToText', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: imageData })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            signTextOutput.innerText = data.translated_text;
        }
    });
});

translationSelect.dispatchEvent(new Event('change'));

function playVideosInSequence(videoUrls, container) {
    container.innerHTML = '';
    let currentIndex = 0;

    function playNextVideo() {
        if (currentIndex >= videoUrls.length) {
            return;
        }

        const video = document.createElement('video');
        video.src = videoUrls[currentIndex];
        video.width = '100%';
        video.height = '100%';
        video.controls = false;
        video.autoplay = true;
        video.onended = playNextVideo;

        container.innerHTML = '';
        container.appendChild(video);

        currentIndex++;
    }

    playNextVideo();
}
