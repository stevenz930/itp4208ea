document.addEventListener('DOMContentLoaded', function() {
    let scrollInstructor = document.getElementById('scrollInstructor');
    let scrollLeftInstructor = document.getElementById('scrollLeftInstructor');
    let scrollRightInstructor = document.getElementById('scrollRightInstructor');
    //console.log(scrollInstructor);
    //console.log(scrollLeftInstructor);
    //console.log(scrollRightInstructor);

    scrollTableHorizontal(scrollInstructor, scrollLeftInstructor, scrollRightInstructor);
})

function scrollTableHorizontal(scrollTable, scrollLeft, scrollRight) {
    if (!scrollTable){
        return;
    }
    else{
        scrollLeft.addEventListener('click', function() {
            scrollTable.scrollBy({
                left: -(scrollTable.offsetWidth),
                behavior: 'smooth'
            })
        })

        scrollRight.addEventListener('click', function() {
            scrollTable.scrollBy({
                left: scrollTable.offsetWidth,
                behavior: 'smooth'
            })
        })
    }
}