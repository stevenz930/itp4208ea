document.addEventListener('DOMContentLoaded', function() {
    let scrollTable = document.getElementById('scrollTable');
    let scrollLeft = document.getElementById('scrollLeft');
    let scrollRight = document.getElementById('scrollRight');

    let myTab = document.getElementById('myTab');
    let scrollLeftInTab = document.getElementById('scrollLeftInTab');
    let scrollRightInTab = document.getElementById('scrollRightInTab');

    scrollTableHorizontal(scrollTable, scrollLeft, scrollRight);
    scrollTableHorizontal(myTab, scrollLeftInTab, scrollRightInTab);
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
