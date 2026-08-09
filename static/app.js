document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const chatForm = document.getElementById('chatForm');
  const userInput = document.getElementById('userInput');
  const chatHistory = document.getElementById('chatHistory');
  const micBtn = document.getElementById('micBtn');
  const quickChips = document.getElementById('quickChips');
  const clearChatBtn = document.getElementById('clearChatBtn');

  // Modals & Buttons
  const faqModalBtn = document.getElementById('faqModalBtn');
  const faqModal = document.getElementById('faqModal');
  const closeFaqModal = document.getElementById('closeFaqModal');
  const faqSearchInput = document.getElementById('faqSearchInput');
  const categoryTabs = document.getElementById('categoryTabs');
  const faqList = document.getElementById('faqList');

  const addFaqBtn = document.getElementById('addFaqBtn');
  const addFaqModal = document.getElementById('addFaqModal');
  const closeAddFaqModal = document.getElementById('closeAddFaqModal');
  const addFaqForm = document.getElementById('addFaqForm');

  const analyticsBtn = document.getElementById('analyticsBtn');
  const analyticsModal = document.getElementById('analyticsModal');
  const closeAnalyticsModal = document.getElementById('closeAnalyticsModal');

  // Speech Recognition Setup
  let recognition = null;
  let isRecording = false;

  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      userInput.value = transcript;
      micBtn.classList.remove('recording');
      isRecording = false;
    };

    recognition.onerror = () => {
      micBtn.classList.remove('recording');
      isRecording = false;
    };

    recognition.onend = () => {
      micBtn.classList.remove('recording');
      isRecording = false;
    };
  } else {
    micBtn.style.display = 'none';
  }

  micBtn?.addEventListener('click', () => {
    if (!recognition) return;
    if (isRecording) {
      recognition.stop();
      micBtn.classList.remove('recording');
      isRecording = false;
    } else {
      recognition.start();
      micBtn.classList.add('recording');
      isRecording = true;
    }
  });

  // Handle Chat Submission
  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const query = userInput.value.strip ? userInput.value.trim() : userInput.value;
    if (!query) return;
    
    sendUserQuery(query);
    userInput.value = '';
  });

  // Quick Chips Click Event
  quickChips.addEventListener('click', (e) => {
    if (e.target.classList.contains('chip')) {
      const query = e.target.getAttribute('data-query');
      sendUserQuery(query);
    }
  });

  // Clear Chat History
  clearChatBtn.addEventListener('click', () => {
    chatHistory.innerHTML = `
      <div class="welcome-card">
        <div class="welcome-icon">
          <i class="fa-solid fa-comments"></i>
        </div>
        <h2>Welcome to NovaBot FAQ Assistant!</h2>
        <p>Chat cleared! Feel free to ask another question.</p>
      </div>
    `;
  });

  async function sendUserQuery(query) {
    // 1. Render User Message
    appendUserMessage(query);

    // 2. Render Typing Indicator
    const typingId = showTypingIndicator();

    try {
      // 3. Call Backend API
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query })
      });

      const data = await response.json();
      removeTypingIndicator(typingId);

      if (data.success && data.result) {
        appendBotResponse(data.result);
      } else {
        appendBotResponse({
          type: 'error',
          answer: 'Sorry, I encountered an error processing your query. Please try again.',
          confidence: 0,
          category: 'Error'
        });
      }
    } catch (err) {
      console.error(err);
      removeTypingIndicator(typingId);
      appendBotResponse({
        type: 'error',
        answer: 'Network error. Make sure the Python Flask server is running!',
        confidence: 0,
        category: 'Network Error'
      });
    }
  }

  function appendUserMessage(text) {
    // Remove welcome card if present
    const welcomeCard = chatHistory.querySelector('.welcome-card');
    if (welcomeCard) welcomeCard.remove();

    const row = document.createElement('div');
    row.className = 'message-row user-row';
    row.innerHTML = `
      <div class="msg-avatar"><i class="fa-solid fa-user"></i></div>
      <div class="msg-bubble">
        <div class="msg-text">${escapeHtml(text)}</div>
      </div>
    `;
    chatHistory.appendChild(row);
    scrollToBottom();
  }

  function showTypingIndicator() {
    const id = 'typing-' + Date.now();
    const row = document.createElement('div');
    row.className = 'message-row bot-row';
    row.id = id;
    row.innerHTML = `
      <div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>
      <div class="msg-bubble">
        <div class="typing-indicator">
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>
      </div>
    `;
    chatHistory.appendChild(row);
    scrollToBottom();
    return id;
  }

  function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  function appendBotResponse(res) {
    const row = document.createElement('div');
    row.className = 'message-row bot-row';

    // Confidence badge styling
    let confClass = 'confidence-low';
    if (res.confidence >= 50) confClass = 'confidence-high';
    else if (res.confidence >= 25) confClass = 'confidence-medium';

    const categoryBadge = `<span class="category-badge">${escapeHtml(res.category || 'General')}</span>`;
    const confBadge = `<span class="confidence-badge ${confClass}"><i class="fa-solid fa-bullseye"></i> ${res.confidence}% match</span>`;

    // Format Answer text with basic markdown formatting
    let formattedAnswer = escapeHtml(res.answer)
      .replace(/\n/g, '<br>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Suggestions HTML
    let suggestionsHtml = '';
    if (res.suggestions && res.suggestions.length > 0) {
      const items = res.suggestions.map(s => `
        <button class="suggestion-item" data-query="${escapeHtml(s.question)}">
          ❓ ${escapeHtml(s.question)} <small style="color:var(--text-muted)">(${s.category})</small>
        </button>
      `).join('');

      suggestionsHtml = `
        <div class="suggestions-box">
          <div class="suggestions-title"><i class="fa-solid fa-lightbulb"></i> Related Questions:</div>
          ${items}
        </div>
      `;
    }

    const faqId = res.faq_id || 0;

    row.innerHTML = `
      <div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>
      <div class="msg-bubble">
        <div class="msg-header-meta">
          ${categoryBadge}
          ${confBadge}
        </div>
        <div class="msg-text">${formattedAnswer}</div>
        ${suggestionsHtml}
        <div class="msg-actions">
          <button class="action-btn tts-btn" title="Read Aloud"><i class="fa-solid fa-volume-high"></i> Read</button>
          <button class="action-btn copy-btn" title="Copy Answer"><i class="fa-solid fa-copy"></i> Copy</button>
          <button class="action-btn rate-btn rate-up" data-id="${faqId}" data-rating="positive" title="Helpful"><i class="fa-regular fa-thumbs-up"></i></button>
          <button class="action-btn rate-btn rate-down" data-id="${faqId}" data-rating="negative" title="Not Helpful"><i class="fa-regular fa-thumbs-down"></i></button>
        </div>
      </div>
    `;

    chatHistory.appendChild(row);
    scrollToBottom();

    // Attach Event Listeners to Message Actions
    const ttsBtn = row.querySelector('.tts-btn');
    ttsBtn?.addEventListener('click', () => speakText(res.answer));

    const copyBtn = row.querySelector('.copy-btn');
    copyBtn?.addEventListener('click', () => {
      navigator.clipboard.writeText(res.answer);
      copyBtn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
      setTimeout(() => copyBtn.innerHTML = '<i class="fa-solid fa-copy"></i> Copy', 2000);
    });

    const rateBtns = row.querySelectorAll('.rate-btn');
    rateBtns.forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const id = btn.getAttribute('data-id');
        const rating = btn.getAttribute('data-rating');
        
        await fetch('/api/feedback', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ faq_id: id, rating: rating })
        });

        rateBtns.forEach(b => b.classList.remove('active-rating'));
        btn.classList.add('active-rating');
      });
    });

    // Attach listener for suggestion items inside bot message
    const sugItems = row.querySelectorAll('.suggestion-item');
    sugItems.forEach(item => {
      item.addEventListener('click', () => {
        const q = item.getAttribute('data-query');
        sendUserQuery(q);
      });
    });
  }

  function speakText(text) {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text.replace(/<[^>]*>?/gm, ''));
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  }

  function scrollToBottom() {
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }

  function escapeHtml(text) {
    if (!text) return '';
    return text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // --- FAQ Explorer Modal Logic ---
  let allFaqs = [];
  let currentCategory = 'All';

  faqModalBtn.addEventListener('click', () => {
    faqModal.classList.add('active');
    loadFaqs();
  });

  closeFaqModal.addEventListener('click', () => faqModal.classList.remove('active'));

  async function loadFaqs() {
    faqList.innerHTML = '<div class="loading-spinner"><i class="fa-solid fa-circle-notch fa-spin"></i> Loading FAQs...</div>';
    try {
      const res = await fetch('/api/faqs');
      const data = await res.json();
      if (data.success) {
        allFaqs = data.faqs;
        renderCategoryTabs(data.categories);
        renderFaqList();
      }
    } catch (err) {
      faqList.innerHTML = '<div class="error-msg">Failed to load FAQs.</div>';
    }
  }

  function renderCategoryTabs(categories) {
    categoryTabs.innerHTML = `<button class="tab-btn ${currentCategory === 'All' ? 'active' : ''}" data-category="All">All</button>`;
    categories.forEach(cat => {
      const btn = document.createElement('button');
      btn.className = `tab-btn ${currentCategory === cat ? 'active' : ''}`;
      btn.setAttribute('data-category', cat);
      btn.textContent = cat;
      categoryTabs.appendChild(btn);
    });

    categoryTabs.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        categoryTabs.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentCategory = btn.getAttribute('data-category');
        renderFaqList();
      });
    });
  }

  faqSearchInput.addEventListener('input', () => renderFaqList());

  function renderFaqList() {
    const searchTerm = faqSearchInput.value.toLowerCase();
    const filtered = allFaqs.filter(faq => {
      const matchCat = (currentCategory === 'All' || faq.category === currentCategory);
      const matchSearch = (
        faq.question.toLowerCase().includes(searchTerm) ||
        faq.answer.toLowerCase().includes(searchTerm) ||
        (faq.keywords && faq.keywords.some(k => k.toLowerCase().includes(searchTerm)))
      );
      return matchCat && matchSearch;
    });

    if (filtered.length === 0) {
      faqList.innerHTML = '<div class="no-results" style="text-align:center; padding:20px; color:var(--text-muted);">No FAQs found matching your criteria.</div>';
      return;
    }

    faqList.innerHTML = filtered.map(faq => `
      <div class="faq-card">
        <div class="faq-card-header">
          <div class="faq-card-question">${escapeHtml(faq.question)}</div>
          <button class="btn btn-glass ask-faq-btn" data-query="${escapeHtml(faq.question)}" title="Ask bot this question">
            <i class="fa-solid fa-paper-plane"></i> Ask
          </button>
        </div>
        <div class="faq-card-answer">${escapeHtml(faq.answer)}</div>
        <div class="faq-card-footer">
          <span><i class="fa-solid fa-folder"></i> ${escapeHtml(faq.category)}</span>
          <span><i class="fa-solid fa-tags"></i> ${(faq.tags || []).join(', ')}</span>
        </div>
      </div>
    `).join('');

    faqList.querySelectorAll('.ask-faq-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const query = btn.getAttribute('data-query');
        faqModal.classList.remove('active');
        sendUserQuery(query);
      });
    });
  }

  // --- Add FAQ Modal Logic ---
  addFaqBtn.addEventListener('click', () => addFaqModal.classList.add('active'));
  closeAddFaqModal.addEventListener('click', () => addFaqModal.classList.remove('active'));

  addFaqForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const newFaq = {
      category: document.getElementById('faqCategory').value,
      question: document.getElementById('faqQuestion').value,
      answer: document.getElementById('faqAnswer').value,
      keywords: document.getElementById('faqKeywords').value,
      tags: document.getElementById('faqTags').value
    };

    try {
      const res = await fetch('/api/faqs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newFaq)
      });
      const data = await res.json();
      if (data.success) {
        alert('✅ New FAQ added successfully and Bot re-trained!');
        addFaqForm.reset();
        addFaqModal.classList.remove('active');
      }
    } catch (err) {
      alert('Failed to add FAQ.');
    }
  });

  // --- Analytics Modal Logic ---
  analyticsBtn.addEventListener('click', async () => {
    analyticsModal.classList.add('active');
    try {
      const res = await fetch('/api/stats');
      const data = await res.json();
      if (data.success) {
        const s = data.stats;
        document.getElementById('statTotalFaqs').textContent = s.total_faqs;
        document.getElementById('statTotalQueries').textContent = s.total_queries;
        document.getElementById('statAvgConfidence').textContent = `${s.avg_confidence}%`;
        document.getElementById('statPositiveRate').textContent = `${s.positive_feedback_rate}%`;

        document.getElementById('statHighMatches').textContent = s.high_confidence_matches;
        document.getElementById('statMediumMatches').textContent = s.medium_confidence_matches;
        document.getElementById('statLowMatches').textContent = s.low_confidence_matches;

        const totalQ = s.total_queries || 1;
        document.getElementById('barHigh').style.width = `${(s.high_confidence_matches / totalQ) * 100}%`;
        document.getElementById('barMedium').style.width = `${(s.medium_confidence_matches / totalQ) * 100}%`;
        document.getElementById('barLow').style.width = `${(s.low_confidence_matches / totalQ) * 100}%`;
      }
    } catch (err) {
      console.error(err);
    }
  });

  closeAnalyticsModal.addEventListener('click', () => analyticsModal.classList.remove('active'));

  // Theme Switching Logic
  const themeSelector = document.getElementById('themeSelector');
  const savedTheme = localStorage.getItem('novabot_theme') || 'aurora';
  if (themeSelector) {
    themeSelector.value = savedTheme;
    document.documentElement.setAttribute('data-theme', savedTheme);

    themeSelector.addEventListener('change', (e) => {
      const selected = e.target.value;
      document.documentElement.setAttribute('data-theme', selected);
      localStorage.setItem('novabot_theme', selected);
    });
  }

  // Close modals on clicking overlay backdrop
  [faqModal, addFaqModal, analyticsModal].forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.remove('active');
    });
  });
});
