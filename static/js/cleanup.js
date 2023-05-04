function hasGetUserMedia() {
    return !!(navigator.getUserMedia || navigator.webkitGetUserMedia ||
        navigator.mozGetUserMedia || navigator.msGetUserMedia);
}

if (hasGetUserMedia()) {
    // Good to go!
    document.addEventListener('DOMContentLoaded', () => {

        let v = document.getElementById("myVideo");
        photo = document.getElementById('photo');
        let fileSrc;

        // Create a canvas to grab an image for upload
        let imageCanvas = document.createElement('canvas');
        let imageCtx = imageCanvas.getContext("2d");

        // Add file blob to a form and post using xmlhttprequest
        function postFile(file) {

            let formdata = new FormData();
            formdata.append("image", file);
            let xhr = new XMLHttpRequest();
            xhr.open('POST', "/image", true);
            xhr.onload = function () {
                if (this.status === 200) {
                    console.log(this.response);
                    fileSrc = this.response;
                }
                else {
                    console.error(xhr);
                }
            };
            xhr.send(formdata);
        };

        // Get the image from the canvas
        function sendImagefromCanvas() {

            // Make sure the canvas is set to the current video size
            imageCanvas.width = v.videoWidth;
            imageCanvas.height = v.videoHeight;

            imageCtx.drawImage(v, 0, 0, v.videoWidth, v.videoHeight);

            //let us store the image before posting it
            const data = imageCanvas.toDataURL('image/png');
            // Convert the canvas to blob and post the file
            imageCanvas.toBlob(postFile, 'image/png');

            // stop the stream, hide the div element and show the picture we just took
            stopVideo(v);
            hideVideo();
            // show the picture just taken
            photo.setAttribute('src', data);


        };

        // Take a picture on click on video
        v.onclick = function () {
            $('audio')[0].play();
            sendImagefromCanvas();
        };

        // Take a picture on click on video
        photo.onclick = function () {
            // hide the photo
            hideVideo();
            startVideoStream();
        };


        // Start the video stream with autoplay onload
        window.onload = startVideoStream();

        function startVideoStream() {


            // Get current window size
            var sw = document.body.clientWidth;
            var sh = document.body.clientHeight;

            // Get camera video stream
            navigator.mediaDevices.getUserMedia({
                video: {
                    // constraints for video recording
                    width: { ideal: sw },
                    height: { ideal: sh },
                    facingMode: "environment"
                },
                audio: false
            })
                .then(stream => {
                    v.srcObject = stream;
                })
                .catch(err => {
                    console.log('navigator.getUserMedia error: ', err)
                });
        };

        function hideVideo() {
            var x = document.getElementById("videoDiv");
            var y = document.getElementById("photoDiv");
            if (x.style.display === "none") {
                x.style.display = "block";
                y.style.display = "none";
            } else {
                x.style.display = "none";
                y.style.display = "block";
            }
        };

        // stop only camera as audio is off
        function stopVideo(videoElem) {
            const stream = videoElem.srcObject;
            const tracks = stream.getTracks();

            tracks.forEach((track) => {
                track.stop();
            });

            videoElem.srcObject = null;
        };

    });

} else {
    alert('Video is not supported in your browser at the moment :(');
};

function submit_cleanup_report_btn() {
    document.getElementById("cleanup").submit();
};
