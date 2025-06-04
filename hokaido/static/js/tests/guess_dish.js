function handleGuessDishGame() {
    const gameContainer = document.querySelector('.quiz-container');
    if (!gameContainer) return;

    const correctAnswer = gameContainer.dataset.correctAnswer;
    const buttons = document.querySelectorAll('.option-btn');
    const feedback = document.getElementById('feedback');
    const nextBtn = document.getElementById('next-btn');
    const form = document.getElementById('answer-form');
    const userAnswerInput = document.createElement('input');
    userAnswerInput.type = 'hidden';
    userAnswerInput.name = 'answer';
    form.appendChild(userAnswerInput);

    const confirmedInput = document.createElement('input');
    confirmedInput.type = 'hidden';
    confirmedInput.name = 'confirmed';
    confirmedInput.value = 'false';
    form.appendChild(confirmedInput);

    if (!buttons.length || !feedback || !nextBtn || !form) return;

    let selectedAnswer = null;

    buttons.forEach(button => {
        button.addEventListener('click', function() {
            buttons.forEach(btn => btn.classList.remove('selected'));
            this.classList.add('selected');
            selectedAnswer = this.dataset.answer;
            userAnswerInput.value = selectedAnswer;
            nextBtn.disabled = false;
            
            buttons.forEach(btn => {
                btn.classList.toggle('show-correct', btn.dataset.answer === correctAnswer);
            });

            feedback.textContent = selectedAnswer === correctAnswer 
                ? 'Правильно! Нажмите "Далее"' 
                : 'Неверно! Нажмите "Далее"';
            feedback.className = `quiz-feedback ${selectedAnswer === correctAnswer ? 'correct' : 'incorrect'}`;
        });
    });

    nextBtn.addEventListener('click', function() {
        if (!selectedAnswer) return;
        
        confirmedInput.value = 'true';
        buttons.forEach(btn => btn.disabled = true);
        nextBtn.disabled = true;
        
        setTimeout(() => {
            form.submit();
        }, 500);
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', handleGuessDishGame);
} else {
    handleGuessDishGame();
}