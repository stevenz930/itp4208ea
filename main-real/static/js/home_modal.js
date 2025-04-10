document.addEventListener('DOMContentLoaded', function() {
    let myModal = document.getElementById('exampleModal');
    if(myModal){
        let modal = new bootstrap.Modal(myModal);
        modal.show();
    }
});