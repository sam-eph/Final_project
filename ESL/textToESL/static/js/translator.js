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
            const unfoundWords = data.unfound_words;

            if (unfoundWords.length > 0) {
                alert("The following words were not found in the dictionary: " + unfoundWords.join(', '));
            }

            if (videoUrls.length > 0) {
                playVideosInSequence(videoUrls, signBox);
            } else {
                signBox.innerHTML = 'No valid videos found for the input text.';
            }
        }
    });
});

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
