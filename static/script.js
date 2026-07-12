const hourSlider = document.getElementById('hour');
const hourValue = document.getElementById('hour-value');

function formatHour(h) {
  h = parseInt(h);
  const period = h < 12 ? 'AM' : 'PM';
  let displayHour = h % 12;
  if (displayHour === 0) displayHour = 12;
  return `${displayHour}:00 ${period}`;
}

hourSlider.addEventListener('input', () => {
  hourValue.textContent = formatHour(hourSlider.value);
});
hourValue.textContent = formatHour(hourSlider.value);

const predictBtn = document.getElementById('predict-btn');
const resetBtn = document.getElementById('reset-btn');
const formCard = document.getElementById('form-card');
const resultCard = document.getElementById('result-card');
const step1 = document.getElementById('step-indicator-1');
const step2 = document.getElementById('step-indicator-2');

predictBtn.addEventListener('click', async () => {
  predictBtn.disabled = true;
  predictBtn.querySelector('span').textContent = 'Checking...';

  const payload = {
    month: document.getElementById('month').value,
    day_of_week: document.getElementById('day_of_week').value,
    hour: document.getElementById('hour').value,
    distance: document.getElementById('distance').value,
    carrier: document.getElementById('carrier').value,
    origin: document.getElementById('origin').value,
    dest: document.getElementById('dest').value,
  };

  try {
    const res = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    showResult(data);
  } catch (err) {
    alert('Something went wrong. Please try again.');
    console.error(err);
  } finally {
    predictBtn.disabled = false;
    predictBtn.querySelector('span').textContent = 'Check my flight';
  }
});

function showResult(data) {
  formCard.classList.add('hidden');
  resultCard.classList.remove('hidden');
  step1.classList.remove('active');
  step2.classList.add('active');

  const statusEl = document.getElementById('result-status');
  const iconEl = document.getElementById('result-icon');
  const barEl = document.getElementById('result-prob-bar');
  const textEl = document.getElementById('result-prob-text');

  statusEl.textContent = data.status;
  textEl.textContent = data.probability + '% delay probability';

  if (data.is_delayed) {
    statusEl.className = 'result-status delayed';
    barEl.className = 'result-prob-bar delayed';
    iconEl.textContent = '🌧️';
  } else {
    statusEl.className = 'result-status ontime';
    barEl.className = 'result-prob-bar ontime';
    iconEl.textContent = '☀️';
  }

  setTimeout(() => {
    barEl.style.width = data.probability + '%';
  }, 50);
}

resetBtn.addEventListener('click', () => {
  resultCard.classList.add('hidden');
  formCard.classList.remove('hidden');
  step1.classList.add('active');
  step2.classList.remove('active');
  document.getElementById('result-prob-bar').style.width = '0%';
});
