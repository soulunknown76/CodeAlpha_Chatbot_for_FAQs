import sys
import io

# Force UTF-8 stdout for Windows console emoji support
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from nlp_engine import FAQChatbotNLP

def run_tests():
    print("--- Initializing FAQ Chatbot NLP Engine ---")
    bot = FAQChatbotNLP(faq_file_path="data/faqs.json")
    print(f"Loaded {len(bot.faqs)} FAQs successfully.")

    test_queries = [
        "Hi, good morning!",
        "How can I track my package?",
        "What cards do you accept for payment?",
        "Can I return an item if I don't like it?",
        "How long does refund take?",
        "My device is not turning on what should I do?",
        "Is there international shipping available to London?",
        "What is the airspeed velocity of an unladen swallow?", # Out of scope query
        "Who created NovaBot?"
    ]

    print("\n--- Running Test Queries ---")
    for q in test_queries:
        res = bot.match_query(q)
        print(f"\nUser Query: '{q}'")
        print(f"Match Type: {res['type']}")
        print(f"Category: {res['category']}")
        print(f"Matched Question: {res.get('matched_question', 'N/A')}")
        print(f"Confidence: {res['confidence']}%")
        print(f"Answer snippet: {res['answer'][:100]}...")
        if res.get('suggestions'):
            print("Suggestions:")
            for s in res['suggestions']:
                print(f" - [{s['category']}] {s['question']} ({s.get('confidence', 'N/A')}%)")

if __name__ == "__main__":
    run_tests()
