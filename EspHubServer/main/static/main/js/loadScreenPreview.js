function loadScreenPreview(url) {
    console.log(url);

    $('#loader').show();

    $.get(url, function (result) {
        console.log("Image loading done.");
        _drawToCanvas(result);
    }).fail(function () {
        console.log("Loading screen preview fail.")
    })
}

function _drawToCanvas(imgBytes) {
    var canvas = document.getElementById("screen-preview");
    var ctx = canvas.getContext('2d');

    var image = new Image();
    image.src = "data:image/png;base64," + imgBytes;
    image.onload = function () {
        ctx.drawImage(image, 0, 0);
    };

    $('#loader').hide();
    $('#canvas-container').show();
}