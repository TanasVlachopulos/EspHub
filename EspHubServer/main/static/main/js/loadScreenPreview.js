function loadScreenPreview(url) {
    console.log(url);

    _drawSpinner();

    $.get(url, function (result) {
        console.log("data:image/png;base64," + result);
        _drawToCanvas(result);
    }).fail(function () {
        console.log("Loading screen preview fail.")
    })
}

function _drawSpinner() {
    var canvas = document.getElementById("screen-preview");
    var ctx = canvas.getContext('2d');

    var image = new Image();
    image.src = "/static/main/images/spinner.svg";
    image.onload = function () {
        ctx.drawImage(image, 0, 0);
    }
}

function _drawToCanvas(imgBytes) {
    var canvas = document.getElementById("screen-preview");
    var ctx = canvas.getContext('2d');

    var image = new Image();
    image.src = "data:image/png;base64," + imgBytes;
    image.onload = function () {
        ctx.drawImage(image, 0, 0);
    }
}