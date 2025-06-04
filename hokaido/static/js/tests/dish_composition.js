document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('answer-form');
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    const submitBtn = document.getElementById('submit-btn');
    const feedback = document.getElementById('feedback');

    if (!form || !checkboxes.length || !submitBtn || !feedback) return;

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            submitBtn.disabled = !Array.from(checkboxes).some(cb => cb.checked);
        });
    });

    submitBtn.addEventListener('click', function() {
        checkboxes.forEach(cb => cb.disabled = true);
        submitBtn.disabled = true;

        form.submit();
    });
});