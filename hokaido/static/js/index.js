document.addEventListener('DOMContentLoaded', function () {
    const inner = document.querySelector('.carousel-inner');
    const items = document.querySelectorAll('.item');
    const itemsToShow = 3;
    let currentIndex = 0;
    const itemWidth = items[0].offsetWidth + 1;

    document.getElementById('next').addEventListener('click', () => {
        if (currentIndex < items.length - itemsToShow) {
            currentIndex++;
        } else {
            currentIndex = 0;
        }
        updateCarousel();
    });

    document.getElementById('prev').addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
        } else {
            currentIndex = items.length - itemsToShow;
        }
        updateCarousel();
    });

    function updateCarousel() {
        const offset = -currentIndex * itemWidth;
        inner.style.transform = `translateX(${offset}px)`;
    }
});