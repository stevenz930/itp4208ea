document.addEventListener('DOMContentLoaded', function() {
    let scrollTableCourse = document.getElementById('scrollTable');
    let scrollLeftCourse = document.getElementById('scrollLeft');
    let scrollRightCourse = document.getElementById('scrollRight');

    let myTab = document.getElementById('myTab');
    let scrollLeftInTab = document.getElementById('scrollLeftInTab');
    let scrollRightInTab = document.getElementById('scrollRightInTab');

    scrollTableHorizontal(scrollTableCourse, scrollLeftCourse, scrollRightCourse);
    scrollTableHorizontalTab(myTab, scrollLeftInTab, scrollRightInTab);
})

function scrollTableHorizontal(scrollTable, scrollLeft, scrollRight) {
    //console.log("scrollTable");
    if (!scrollTable){
        return;
    }
    else{
        scrollLeft.addEventListener('click', function() {
            scrollTable.scrollBy({
                left: -(scrollTable.offsetWidth)+260,
                behavior: 'smooth'
            });
        })

        scrollRight.addEventListener('click', function() {
            scrollTable.scrollBy({
                left: scrollTable.offsetWidth-260,
                behavior: 'smooth'
            });
        })
    }
}
function scrollTableHorizontalTab(scrollTable, scrollLeft, scrollRight) {
    //console.log("scrollTableTab");
    if (!scrollTable){
        return;
    }
    else{
        scrollLeft.addEventListener('click', function() {
            scrollTable.scrollBy({
                left: -(scrollTable.offsetWidth)+170,
                behavior: 'smooth'
            });
        })

        scrollRight.addEventListener('click', function() {
            scrollTable.scrollBy({
                left: scrollTable.offsetWidth-170,
                behavior: 'smooth'
            });
        })
    }
}
