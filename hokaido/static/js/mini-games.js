document.addEventListener('DOMContentLoaded', function() {
    const categories = document.querySelectorAll('.test-category');
    
    if (categories.length > 0) {
        categories[0].classList.add('active');
    }
    
    document.querySelectorAll('.test-category-header').forEach(header => {
        header.addEventListener('click', function() {
            const category = this.parentElement;
            const wasActive = category.classList.contains('active');
            
            categories.forEach(c => c.classList.remove('active'));
            
            if (!wasActive) {
                category.classList.add('active');
            }
        });
    });
});