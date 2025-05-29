document.addEventListener('DOMContentLoaded', function() {
    const gameContainer = document.querySelector('.quiz-container');
    if (!gameContainer) return;

    const correctAnswer = gameContainer.dataset.correctAnswer;
    const buttons = document.querySelectorAll('.option-btn');
    const feedback = document.getElementById('feedback');
    const nextBtn = document.getElementById('next-btn');
    const form = document.getElementById('answer-form');
    const answerInput = document.createElement('input');
    answerInput.type = 'hidden';
    answerInput.name = 'answer';
    form.appendChild(answerInput);

    if (!buttons.length || !feedback || !nextBtn || !form) return;

    let selectedAnswer = null;

    buttons.forEach(button => {
        button.addEventListener('click', function() {
            // Сброс предыдущего выбора
            buttons.forEach(btn => {
                btn.classList.remove('selected', 'correct', 'incorrect');
            });

            // Установка нового выбора
            selectedAnswer = this.dataset.answer;
            answerInput.value = selectedAnswer;
            this.classList.add('selected');
            nextBtn.disabled = false;

            // Подсветка правильного ответа
            buttons.forEach(btn => {
                if (btn.dataset.answer === correctAnswer) {
                    btn.classList.add('correct-answer');
                }
            });

            // Показ результата
            if (selectedAnswer === correctAnswer) {
                feedback.textContent = 'Правильно! Нажмите "Далее"';
                feedback.className = 'quiz-feedback correct';
            } else {
                feedback.textContent = 'Неверно! Нажмите "Далее"';
                feedback.className = 'quiz-feedback incorrect';
            }
        });
    });

    nextBtn.addEventListener('click', function() {
        if (!selectedAnswer) return;
        
        // Блокировка интерфейса
        buttons.forEach(btn => btn.disabled = true);
        nextBtn.disabled = true;
        
        // Задержка перед отправкой
        setTimeout(() => {
            form.submit();
        }, 500);
    });
});