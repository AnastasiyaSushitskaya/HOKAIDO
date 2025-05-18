document.addEventListener('DOMContentLoaded', function() {
    const categories = document.querySelectorAll('.test-category');
    
    // Открываем первую категорию
    if (categories.length > 0) {
        categories[0].classList.add('active');
    }
    
    // Обработчик кликов
    document.querySelectorAll('.test-category-header').forEach(header => {
        header.addEventListener('click', function() {
            const category = this.parentElement;
            const wasActive = category.classList.contains('active');
            
            // Закрываем все категории
            categories.forEach(c => c.classList.remove('active'));
            
            // Открываем текущую, если она была закрыта
            if (!wasActive) {
                category.classList.add('active');
            }
        });
    });
});