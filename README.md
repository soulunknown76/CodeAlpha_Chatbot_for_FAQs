# 🤖 NovaBot AI — Intelligent FAQ Chatbot

A high-performance, NLP-powered FAQ Chatbot system built using **NLTK**, **Scikit-Learn (TF-IDF & Cosine Similarity)**, a **Flask REST Backend**, and a **Modern Glassmorphic Web UI** featuring voice input, text-to-speech, interactive FAQ management, live theme switching, and analytics tracking.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1-black?style=for-the-badge&logo=flask)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-TF--IDF-orange?style=for-the-badge&logo=scikit-learn)
![NLTK](https://img.shields.io/badge/NLTK-NLP-green?style=for-the-badge)
![UI](https://img.shields.io/badge/UI-Glassmorphism-purple?style=for-the-badge)
![Localization](https://img.shields.io/badge/India-INR%20%E2%82%B9-red?style=for-the-badge)

---

## ✨ Features

- 🧠 **NLP Preprocessing Pipeline**: Lowercasing, contraction expansion, punctuation cleaning, tokenization, stop-word removal, and WordNet lemmatization.
- 📐 **Vectorization & Cosine Similarity**: Scikit-Learn `TfidfVectorizer` (unigrams + bigrams) paired with `cosine_similarity` for accurate question matching.
- 💬 **Intent Classification & Small-Talk**: Recognizes greetings (*"Namaste"*, *"Hello"*), fare-wells, thanks, and bot identity queries.
- 🛡️ **Confidence Thresholds & Fallback Handling**:
  - **High Match (≥50%)**: Direct FAQ answer with category badge.
  - **Medium Match (25%-49%)**: Matched answer with top 3 suggested related questions.
  - **Low Match (<25%)**: Friendly fallback response with recommended close questions.
- 🎨 **Modern Glassmorphism Web UI**:
  - **4 Live Color Themes**: 🌌 Aurora Violet, 🌿 Emerald Cyber, 🔥 Sunset Coral, 💎 Sapphire Ocean (persisted via `localStorage`).
  - **Voice Dictation & Text-to-Speech**: Integrated Web Speech API for voice input and read-aloud playback.
  - **Interactive Action Buttons**: Copy answers, rate helpfulness (Thumbs Up/Down).
  - **Knowledge Base Explorer**: Searchable FAQ modal grouped by categories.
  - **Dynamic FAQ Manager**: Add new FAQs live without restarting the server!
  - **Analytics Drawer**: Real-time stats tracking query count, match confidence, and user satisfaction rate.
- 🇮🇳 **India & Rupee (₹) Customization**: Full support for UPI payments (Google Pay, PhonePe, Paytm), RuPay, Cash on Delivery (COD), and pan-India shipping details.
- 💻 **CLI Terminal Interface**: Command-line mode for direct terminal interaction.

---

## 📁 Project Structure

```text
CodeAlpha chat bot/
├── data/
│   └── faqs.json          # FAQ Dataset (Categorized questions, answers, keywords, tags)
├── static/
│   ├── index.html         # Main Web UI layout & modals
│   ├── style.css          # Glassmorphism design system & theme variables
│   └── app.js             # Frontend API integration & Web Speech logic
├── app.py                 # Flask REST API server with port fallback
├── nlp_engine.py          # Core NLP, TF-IDF & Cosine Similarity Engine
├── cli.py                 # Interactive Terminal CLI interface
├── test_nlp.py            # Automated NLP test suite
├── requirements.txt       # Python dependencies list
└── README.md              # Documentation
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.10** or higher installed on your system.

### 1. Installation

Clone or open the repository, then set up the virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Web Application (Flask Server)

```bash
python app.py
```

Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`** (or `http://127.0.0.1:5001` if port 5000 is occupied)

### 3. Run the CLI Terminal Chatbot

```bash
python cli.py
```

### 4. Run Automated NLP Tests

```bash
python test_nlp.py
```

---

## 🔌 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/chat` | Submit a query string (`{"query": "..."}`) to receive matched FAQ answer, confidence score, category, and suggested questions. |
| `GET` | `/api/faqs` | Retrieve all indexed FAQs. Supports `?category=...` query parameter filtering. |
| `POST` | `/api/faqs` | Add a new FAQ entry live (`{"category": "...", "question": "...", "answer": "...", "keywords": "...", "tags": "..."}`). |
| `POST` | `/api/feedback` | Record user rating (`{"faq_id": 1, "rating": "positive"}`). |
| `GET` | `/api/stats` | Retrieve total queries, average match confidence, and rating ratios. |

---

## 🎨 Theme Switcher

The Web UI features 4 custom CSS themes that can be selected live from the header dropdown:
1. **Aurora Violet** (`aurora`): Default deep midnight indigo with violet-pink glows.
2. **Emerald Cyber** (`emerald`): Deep emerald matrix with mint & cyan accents.
3. **Sunset Coral** (`sunset`): Obsidian plum background with warm amber & red gradients.
4. **Sapphire Ocean** (`sapphire`): Deep abyss blue with electric azure & indigo glows.

---

## 📝 License

Distributed under the MIT License. Built for CodeAlpha Artificial Intelligence Internship.
