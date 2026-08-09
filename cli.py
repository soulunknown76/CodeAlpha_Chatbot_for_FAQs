import sys
from nlp_engine import FAQChatbotNLP

def main():
    print("=====================================================")
    print("       🤖 NovaBot - FAQ Intelligent Chatbot (CLI)     ")
    print("=====================================================")
    print("Type your questions below. Type 'exit' or 'quit' to end.\n")

    bot = FAQChatbotNLP("data/faqs.json")

    while True:
        try:
            user_input = input("\nYou: ")
            if not user_input.strip():
                continue
            if user_input.strip().lower() in ['exit', 'quit']:
                print("NovaBot: Goodbye! Have a great day! 👋")
                break

            result = bot.match_query(user_input)
            print(f"\nNovaBot [{result['category']} | Confidence: {result['confidence']}%]:")
            print(result['answer'])

            if result.get('suggestions') and len(result['suggestions']) > 0:
                print("\n💡 Related Questions:")
                for idx, s in enumerate(result['suggestions'], 1):
                    print(f"  {idx}. {s['question']} ({s['category']})")

        except (KeyboardInterrupt, EOFError):
            print("\nNovaBot: Goodbye!")
            break

if __name__ == "__main__":
    main()
