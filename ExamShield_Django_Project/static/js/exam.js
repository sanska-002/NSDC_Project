(() => {
  const root = document.getElementById('exam-root');
  if (!root) return;
  const submitUrl = root.dataset.submitUrl;
  const form = document.getElementById('exam-form');
  const submitButton = document.getElementById('submit-button');
  const timerEl = document.getElementById('timer');
  let seconds = Number(root.dataset.remaining || 0);
  let submitting = false;
  let hiddenTriggered = false;

  function collectAnswers() {
    const answers = {};
    form.querySelectorAll('input[type="radio"]:checked').forEach(input => {
      answers[input.name.replace(/^q_/, '')] = input.value;
    });
    return answers;
  }

  async function submitExam(reason) {
    if (submitting) return;
    submitting = true;
    submitButton.disabled = true;
    submitButton.textContent = 'Submitting…';
    try {
      const response = await fetch(submitUrl, {
        method: 'POST',
        headers: {'Content-Type':'application/json','X-CSRFToken':getCookie('csrftoken')},
        credentials: 'same-origin',
        keepalive: true,
        body: JSON.stringify({answers: collectAnswers(), reason})
      });
      const data = await response.json();
      if (data.redirect) window.location.href = data.redirect;
      else throw new Error('Submission failed');
    } catch (error) {
      // A keepalive request may complete even while the page is being hidden.
      // If still visible, let the student retry instead of falsely claiming success.
      submitting = false;
      submitButton.disabled = false;
      submitButton.textContent = 'Retry submission';
      alert('We could not confirm submission. Please keep this page open and retry.');
    }
  }

  function getCookie(name) {
    const match = document.cookie.split('; ').find(row => row.startsWith(name + '='));
    return match ? decodeURIComponent(match.split('=').slice(1).join('=')) : '';
  }

  function renderTimer() {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    timerEl.textContent = `${String(mins).padStart(2,'0')}:${String(secs).padStart(2,'0')}`;
  }
  renderTimer();
  const interval = setInterval(() => {
    seconds -= 1;
    renderTimer();
    if (seconds <= 0) {
      clearInterval(interval);
      submitExam('timeout');
    }
  }, 1000);

  submitButton.addEventListener('click', () => {
    if (confirm('Submit your exam now? You cannot change answers afterward.')) submitExam('submitted');
  });

  // Detect the page becoming hidden (tab switch, minimize, or navigating away).
  // This is best-effort browser detection, not a tamper-proof anti-cheat mechanism.
  document.addEventListener('visibilitychange', () => {
    if (document.hidden && !hiddenTriggered && !submitting) {
      hiddenTriggered = true;
      submitExam('tab_switch'); //************************/
    }
  });

  // Warn on attempted refresh/close. Browsers control the wording and may ignore this.
  window.addEventListener('beforeunload', (event) => {
    if (!submitting) {
      event.preventDefault();
      event.returnValue = '';
    }
  });
})();