const chat = document.getElementById('chat');
const composer = document.getElementById('composer');
const questionInput = document.getElementById('questionInput');
const askButton = document.getElementById('askButton');

const playerBar = document.getElementById('playerBar');
const player = document.getElementById('player');
const playerLabel = document.getElementById('playerLabel');
const closePlayer = document.getElementById('closePlayer');

let introRemoved = false;

function removeIntro() {
  if (introRemoved) return;
  const intro = document.querySelector('.intro');
  if (intro) intro.remove();
  introRemoved = true;
}

function addMessage(role, html) {
  const wrap = document.createElement('div');
  wrap.className = `message ${role}`;
  wrap.innerHTML = `<div class="bubble">${html}</div>`;
  chat.appendChild(wrap);
  chat.scrollTop = chat.scrollHeight;
  return wrap;
}

function addTyping() {
  const wrap = document.createElement('div');
  wrap.className = 'message assistant';
  wrap.id = 'typingIndicator';
  wrap.innerHTML = `<div class="bubble typing"><span></span><span></span><span></span></div>`;
  chat.appendChild(wrap);
  chat.scrollTop = chat.scrollHeight;
}

function removeTyping() {
  const el = document.getElementById('typingIndicator');
  if (el) el.remove();
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function playAt(videoNumber, startSeconds, title) {
  playerBar.hidden = false;
  player.src = `/media/${videoNumber}`;
  player.currentTime = 0;
  playerLabel.textContent = `Video ${videoNumber} · ${title || ''}`;
  player.onloadedmetadata = () => {
    player.currentTime = startSeconds;
    player.play();
  };
  playerBar.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

closePlayer.addEventListener('click', () => {
  player.pause();
  player.src = '';
  playerBar.hidden = true;
});

async function askQuestion(question) {
  removeIntro();
  addMessage('user', escapeHtml(question));
  addTyping();
  askButton.disabled = true;

  try {
    const res = await fetch('/api/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    const data = await res.json();
    removeTyping();

    if (!res.ok) {
      addMessage('assistant', escapeHtml(data.error || 'Something went wrong.'));
      return;
    }

    let html = `<p>${escapeHtml(data.answer)}</p>`;

    if (data.sources && data.sources.length) {
      html += '<div class="cue-row">';
      data.sources.forEach(src => {
        html += `
          <button class="cue-chip"
            data-video="${src.video_number}"
            data-start="${src.start}"
            data-title="${escapeHtml(src.text.slice(0, 40))}">
            <span class="video-tag">Video ${src.video_number}</span> ${src.timestamp}
          </button>`;
      });
      html += '</div>';
    }

    const msgEl = addMessage('assistant', html);
    msgEl.querySelectorAll('.cue-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        playAt(chip.dataset.video, parseFloat(chip.dataset.start), chip.dataset.title);
      });
    });

  } catch (err) {
    removeTyping();
    addMessage('assistant', 'Could not reach the server. Is app.py still running?');
  } finally {
    askButton.disabled = false;
  }
}

composer.addEventListener('submit', (e) => {
  e.preventDefault();
  const question = questionInput.value.trim();
  if (!question) return;
  questionInput.value = '';
  askQuestion(question);
});

document.querySelectorAll('.suggestion-chip').forEach(chip => {
  chip.addEventListener('click', () => askQuestion(chip.dataset.q));
});

document.querySelectorAll('.video-item').forEach(item => {
  item.addEventListener('click', () => {
    playAt(item.dataset.video, 0, item.querySelector('.video-title').textContent);
  });
});
