var count = 0;

if (count > 0) {
    console.log("no action");
}
else {
    console.log("fire modal");
    modalload();
}

function modalload() {
    var myModal = new bootstrap.Modal(document.getElementById('Modal'), {})
    myModal.toggle()
    count ++;
}

