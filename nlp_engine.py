import json
import re
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# NLTK Downloads & Initialization
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Initialize NLTK corpora safely without downloading over network at runtime
try:
    STOP_WORDS = set(stopwords.words('english'))
except Exception:
    STOP_WORDS = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'you', 'i', 'my', 'your', 'it', 'with', 'by', 'as'}

try:
    lemmatizer = WordNetLemmatizer()
except Exception:
    lemmatizer = None

SMALL_TALK_INTENTS = {
    "greetings": {
        "patterns": [r"\b(hi|hello|hey|greetings|good morning|good afternoon|good evening|namaste|sup|howdy)\b"],
        "responses": [
            "Namaste! 🙏 I'm NovaBot, your AI Support Assistant for NovaTech India. How can I assist you today? Ask me about UPI payments, Cash on Delivery (COD), shipping across India, warranty, or returns!",
            "Hello! 👋 Welcome to NovaTech India Support. How can I help you today with your order, shipping, or technical query?"
        ]
    },
    "thanks": {
        "patterns": [r"\b(thanks|thank you|thx|appreciated|great help|awesome|thankyou|dhanyawad)\b"],
        "responses": [
            "You're very welcome! 😊 Let me know if you need anything else.",
            "Glad I could help! Feel free to ask if you have more questions."
        ]
    },
    "farewell": {
        "patterns": [r"\b(bye|goodbye|see ya|have a good day|cya|take care)\b"],
        "responses": [
            "Goodbye! Have a wonderful day ahead! 👋",
            "Bye! Feel free to reach out whenever you have questions."
        ]
    },
    "identity": {
        "patterns": [r"\b(who are you|what is your name|what can you do|who made you|who created you|who created|who made|are you a bot|what are you)\b"],
        "responses": [
            "I am NovaBot India, an intelligent FAQ assistant powered by Natural Language Processing (NLP) & Cosine Similarity! I can help you with orders, UPI/COD payments, shipping across India, warranty, and customer support."
        ]
    }
}

class FAQChatbotNLP:
    def __init__(self, faq_file_path="data/faqs.json"):
        self.faq_file_path = faq_file_path
        self.faqs = []
        self.vectorizer = None
        self.tfidf_matrix = None
        self.corpus_processed = []
        self.stats = {
            "total_queries": 0,
            "high_confidence_matches": 0,
            "medium_confidence_matches": 0,
            "low_confidence_matches": 0,
            "avg_confidence": 0.0
        }
        self.feedback_list = []
        self.load_and_train()

    def preprocess_text(self, text: str) -> str:
        """
        Tokenize, clean, remove stopwords, and lemmatize input text.
        """
        if not text:
            return ""
        
        # 1. Lowercase
        text = text.lower()
        
        # 2. Contraction expansion (basic)
        text = re.sub(r"can't", "cannot", text)
        text = re.sub(r"n't", " not", text)
        text = re.sub(r"'s", " is", text)
        text = re.sub(r"'re", " are", text)
        text = re.sub(r"'ve", " have", text)
        text = re.sub(r"'ll", " will", text)
        
        # 3. Clean punctuation
        text = re.sub(r"[^\w\s]", " ", text)
        
        # 4. Tokenize
        try:
            tokens = word_tokenize(text)
        except Exception:
            tokens = text.split()
            
        # 5. Stopwords removal & Lemmatization
        cleaned_tokens = []
        for token in tokens:
            if token not in STOP_WORDS and len(token) > 1 and not token.isdigit():
                try:
                    lemma = lemmatizer.lemmatize(token) if lemmatizer else token
                except Exception:
                    lemma = token
                cleaned_tokens.append(lemma)
                
        return " ".join(cleaned_tokens)

    def load_and_train(self):
        """
        Load FAQ JSON dataset and fit TF-IDF vectorizer over questions and keywords.
        """
        if os.path.exists(self.faq_file_path):
            with open(self.faq_file_path, "r", encoding="utf-8") as f:
                self.faqs = json.load(f)
        else:
            self.faqs = []

        self.corpus_processed = []
        for faq in self.faqs:
            # Combine question, keywords, category, and tags for rich TF-IDF context
            combined_text = f"{faq.get('question', '')} {' '.join(faq.get('keywords', []))} {faq.get('category', '')} {' '.join(faq.get('tags', []))}"
            processed = self.preprocess_text(combined_text)
            self.corpus_processed.append(processed)

        if self.corpus_processed:
            self.vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                sublinear_tf=True,
                token_pattern=r"\w+"
            )
            self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus_processed)

    def reload(self):
        """Reload and retraining when FAQs are added dynamically."""
        self.load_and_train()

    def check_small_talk(self, query: str):
        """Check for small talk / greeting intents using regex patterns."""
        clean_q = query.strip().lower()
        for intent, data in SMALL_TALK_INTENTS.items():
            for pattern in data["patterns"]:
                if re.search(pattern, clean_q):
                    response = data["responses"][0]
                    return {
                        "type": "small_talk",
                        "intent": intent,
                        "answer": response,
                        "confidence": 1.0,
                        "matched_question": query,
                        "category": "Small Talk",
                        "suggestions": []
                    }
        return None

    def match_query(self, user_query: str) -> dict:
        """
        Match a user's query against FAQs using TF-IDF and Cosine Similarity.
        """
        if not user_query or not user_query.strip():
            return {
                "type": "error",
                "answer": "Please type a question so I can assist you!",
                "confidence": 0.0,
                "matched_question": "",
                "category": "None",
                "suggestions": []
            }

        # 1. Check small talk
        small_talk_match = self.check_small_talk(user_query)
        if small_talk_match:
            return small_talk_match

        if not self.vectorizer or self.tfidf_matrix is None or len(self.faqs) == 0:
            return {
                "type": "error",
                "answer": "FAQ Knowledge base is empty right now.",
                "confidence": 0.0,
                "matched_question": "",
                "category": "None",
                "suggestions": []
            }

        # 2. Preprocess user query
        processed_query = self.preprocess_text(user_query)
        
        # Fallback if preprocessing stripped everything (e.g. "is it?")
        if not processed_query:
            processed_query = user_query.lower()

        # 3. Vectorize query & compute cosine similarity
        query_vector = self.vectorizer.transform([processed_query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()

        # 4. Keyword boost calculation
        user_words = set(processed_query.split())
        boosted_similarities = np.copy(similarities)
        
        for idx, faq in enumerate(self.faqs):
            # Check exact keyword or tag matches
            kw_set = set([k.lower() for k in faq.get('keywords', [])] + [t.lower() for t in faq.get('tags', [])])
            q_words = set(self.preprocess_text(faq.get('question', '')).split())
            
            overlap = len(user_words.intersection(kw_set.union(q_words)))
            if overlap > 0:
                boost = min(0.20, 0.05 * overlap)
                boosted_similarities[idx] += boost

        # Cap max similarity at 1.0
        boosted_similarities = np.clip(boosted_similarities, 0.0, 1.0)

        # Rank matches
        top_indices = np.argsort(boosted_similarities)[::-1]
        best_idx = top_indices[0]
        best_score = float(boosted_similarities[best_idx])
        best_faq = self.faqs[best_idx]

        # Get top 3 suggested related questions (excluding top match if score is high)
        suggestions = []
        start_suggestion_idx = 1 if best_score >= 0.40 else 0
        for i in range(start_suggestion_idx, min(len(top_indices), start_suggestion_idx + 3)):
            s_idx = top_indices[i]
            if s_idx < len(self.faqs):
                suggestions.append({
                    "id": self.faqs[s_idx]["id"],
                    "question": self.faqs[s_idx]["question"],
                    "category": self.faqs[s_idx]["category"],
                    "confidence": round(float(boosted_similarities[s_idx]) * 100, 1)
                })

        # Update stats
        self.stats["total_queries"] += 1
        curr_total = self.stats["total_queries"]
        self.stats["avg_confidence"] = round(
            ((self.stats["avg_confidence"] * (curr_total - 1)) + (best_score * 100)) / curr_total, 1
        )

        # Categorize confidence level
        if best_score >= 0.50:
            self.stats["high_confidence_matches"] += 1
            return {
                "type": "faq_match",
                "answer": best_faq["answer"],
                "confidence": round(best_score * 100, 1),
                "matched_question": best_faq["question"],
                "category": best_faq["category"],
                "faq_id": best_faq["id"],
                "suggestions": suggestions
            }
        elif best_score >= 0.25:
            self.stats["medium_confidence_matches"] += 1
            return {
                "type": "faq_match_medium",
                "answer": f"{best_faq['answer']}\n\n*(Note: Matched with '{best_faq['question']}')*",
                "confidence": round(best_score * 100, 1),
                "matched_question": best_faq["question"],
                "category": best_faq["category"],
                "faq_id": best_faq["id"],
                "suggestions": suggestions
            }
        else:
            self.stats["low_confidence_matches"] += 1
            return {
                "type": "fallback",
                "answer": "I'm not completely sure about the answer to that specific query. Here are the closest questions from our knowledge base that might help:",
                "confidence": round(best_score * 100, 1),
                "matched_question": best_faq["question"] if best_score > 0 else "None",
                "category": best_faq["category"] if best_score > 0 else "General",
                "suggestions": suggestions if len(suggestions) > 0 else [
                    {"id": f["id"], "question": f["question"], "category": f["category"]} for f in self.faqs[:3]
                ]
            }

    def add_faq(self, new_faq: dict) -> dict:
        """Add a new FAQ dynamically and persist to json."""
        new_id = max([f.get("id", 0) for f in self.faqs] + [0]) + 1
        faq_entry = {
            "id": new_id,
            "category": new_faq.get("category", "General"),
            "question": new_faq.get("question", "").strip(),
            "answer": new_faq.get("answer", "").strip(),
            "keywords": [k.strip() for k in new_faq.get("keywords", "").split(",") if k.strip()],
            "tags": [t.strip() for t in new_faq.get("tags", "").split(",") if t.strip()]
        }
        self.faqs.append(faq_entry)
        
        # Save to JSON file
        os.makedirs(os.path.dirname(self.faq_file_path), exist_ok=True)
        with open(self.faq_file_path, "w", encoding="utf-8") as f:
            json.dump(self.faqs, f, indent=2)

        # Reload model
        self.reload()
        return faq_entry

    def record_feedback(self, faq_id: int, rating: str, comment: str = ""):
        """Record user feedback (thumbs up / thumbs down)."""
        feedback = {
            "faq_id": faq_id,
            "rating": rating, # 'positive' or 'negative'
            "comment": comment
        }
        self.feedback_list.append(feedback)
        return feedback
