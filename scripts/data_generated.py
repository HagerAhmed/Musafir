import time
import random
import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from db import save_conversation, save_feedback

# Timezone
tz = ZoneInfo("Africa/Cairo")

# --- Travel Assistant context ---
CITIES = ["Cairo", "London", "Rome", "Seoul"]

QUESTIONS = [
    "What should I eat in {}?",
    "What are the best places to visit in {}?",
    "Is {} safe for tourists?",
    "What is the best time to visit {}?",
    "What local customs should I know before visiting {}?",
    "How can I get around in {}?",
    "Where can I find halal food in {}?",
    "What souvenirs can I buy from {}?",
]

ANSWERS = [
    "You should try local dishes and street food, especially near the city center.",
    "There are many historical landmarks and cultural sites worth exploring.",
    "It's generally safe, but always stay alert in crowded areas.",
    "The best time to visit is during spring and autumn when the weather is pleasant.",
    "Respect local traditions and dress modestly in religious places.",
    "Public transportation is reliable, but taxis and ride-sharing are convenient too.",
    "Halal food is widely available in many areas — just check restaurant labels.",
    "Local markets and artisan shops offer beautiful handmade souvenirs.",
]

MODELS = ["mistral-medium-2508", "ministral-8b-latest", "mistral-small-latest"]
RELEVANCE = ["RELEVANT", "PARTLY_RELEVANT", "NON_RELEVANT"]


def generate_synthetic_data(start_time, end_time):
    """Generate historical conversations for testing."""
    current_time = start_time
    conversation_count = 0
    print(f"🌍 Generating historical travel data from {start_time} to {end_time}...")

    while current_time < end_time:
        conversation_id = str(uuid.uuid4())
        city = random.choice(CITIES)
        question = random.choice(QUESTIONS).format(city)
        answer = random.choice(ANSWERS)
        model = random.choice(MODELS)
        relevance = random.choice(RELEVANCE)

        answer_data = {
            "answer": answer,
            "response_time": random.uniform(0.5, 5.0),
            "relevance": relevance,
            "relevance_explanation": f"This answer is {relevance.lower()} for the user query.",
            "model_used": model,
            "prompt_tokens": random.randint(50, 200),
            "completion_tokens": random.randint(50, 300),
            "total_tokens": random.randint(100, 500),
            "eval_prompt_tokens": random.randint(50, 150),
            "eval_completion_tokens": random.randint(20, 100),
            "eval_total_tokens": random.randint(70, 250),
        }

        save_conversation(conversation_id, question, answer_data, city, current_time)
        print(f"💾 Saved conversation ({city}, {model}, {relevance}) at {current_time}")

        # 70% of conversations get feedback
        if random.random() < 0.7:
            feedback = 1 if random.random() < 0.8 else -1
            save_feedback(conversation_id, feedback, current_time)
            print(f"📝 Feedback recorded ({'👍' if feedback > 0 else '👎'})")

        current_time += timedelta(minutes=random.randint(3, 15))
        conversation_count += 1

        if conversation_count % 10 == 0:
            print(f"Generated {conversation_count} conversations...")

    print(f"✅ Historical data generation complete. Total: {conversation_count} records.")


def generate_live_data():
    """Continuously generate synthetic live conversations."""
    conversation_count = 0
    print("🚀 Starting live data generation (Ctrl+C to stop)...")

    while True:
        current_time = datetime.now(tz)
        conversation_id = str(uuid.uuid4())
        city = random.choice(CITIES)
        question = random.choice(QUESTIONS).format(city)
        answer = random.choice(ANSWERS)
        model = random.choice(MODELS)
        relevance = random.choice(RELEVANCE)

        answer_data = {
            "answer": answer,
            "response_time": random.uniform(0.5, 4.0),
            "relevance": relevance,
            "relevance_explanation": f"This answer is {relevance.lower()} to the query.",
            "model_used": model,
            "prompt_tokens": random.randint(60, 180),
            "completion_tokens": random.randint(40, 200),
            "total_tokens": random.randint(100, 350),
            "eval_prompt_tokens": random.randint(30, 100),
            "eval_completion_tokens": random.randint(10, 80),
            "eval_total_tokens": random.randint(40, 180),
        }

        save_conversation(conversation_id, question, answer_data, city, current_time)
        print(f"💬 Live conversation ({city}, {model}, {relevance}) at {current_time}")

        if random.random() < 0.7:
            feedback = 1 if random.random() < 0.8 else -1
            save_feedback(conversation_id, feedback, current_time)
            print(f"📝 Live feedback ({'👍' if feedback > 0 else '👎'})")

        conversation_count += 1
        if conversation_count % 10 == 0:
            print(f"Generated {conversation_count} live entries...")

        time.sleep(1)


if __name__ == "__main__":
    print(f"Script started at {datetime.now(tz)}")
    end_time = datetime.now(tz)
    start_time = end_time - timedelta(hours=6)

    print(f"📅 Generating data from {start_time} to {end_time}")
    generate_synthetic_data(start_time, end_time)

    print("🌐 Switching to live mode...")
    try:
        generate_live_data()
    except KeyboardInterrupt:
        print(f"⏹️ Live data generation stopped at {datetime.now(tz)}.")
    finally:
        print(f"✅ Script finished at {datetime.now(tz)}.")
