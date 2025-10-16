import streamlit as st
import time
import uuid
from assistant import get_answer
from db import save_conversation, save_feedback, get_recent_conversations, get_feedback_stats

# ---------------------------
# Utility
# ---------------------------
def print_log(message):
    print(message, flush=True)

# ---------------------------
# Main Streamlit App
# ---------------------------
def main():
    st.set_page_config(page_title="Musafir - Travel Assistant", page_icon="🌍", layout="wide")

    # --- Title and Description ---
    st.title("🛫 Musafir: Your AI Travel Companion")
    st.markdown("""
        <div style="color:#555; font-size:16px; margin-bottom:20px;">
        Musafir helps you plan your next adventure! 🌏  
        Ask anything about destinations, attractions, or travel tips — powered by intelligent retrieval and AI models.
        </div>
    """, unsafe_allow_html=True)

    # --- Sidebar (LEFT) ---
    st.sidebar.header("⚙️ Settings")

    model_choice = st.sidebar.selectbox("🤖 Choose Model:", ["mistral-medium-2508", "ministral-8b-latest", "mistral-small-latest"])
    print_log(f"User selected model: {model_choice}")
    
    search_type = st.sidebar.radio("🔍 Search Type:", ["Qdrant", "Elasticsearch_Text", "Elasticsearch_Vector", "MinSearch"])
    print_log(f"User selected search type: {search_type}")

    st.sidebar.markdown("---")
    st.sidebar.info("💡 Tip: You can switch models or search type anytime!")

    # --- Session Initialization ---
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())
        print_log(f"New conversation started with ID: {st.session_state.conversation_id}")
    if "count" not in st.session_state:
        st.session_state.count = 0
        print_log("Feedback count initialized to 0")

    # --- Two-column layout (LEFT: main chat / RIGHT: recent conv + stats) ---
    left_col, right_col = st.columns([2.5, 1])

    # =====================
    # LEFT COLUMN
    # =====================
    with left_col:
        city = st.selectbox("Select a City:", ["Cairo", "London", "Rome", "Seoul"])
        print_log(f"User selected city: {city}")

        user_input = st.text_input("Enter your question:")

        if st.button("Ask"):
            print_log(f"User asked: '{user_input}'")
            with st.spinner("Thinking... ✈️"):
                print_log(f"Getting answer from assistant using {model_choice} model and {search_type} search")
                start_time = time.time()
                answer_data = get_answer(user_input, city, model_choice, search_type)
                end_time = time.time()
                print_log(f"Answer received in {end_time - start_time:.2f} seconds")
                st.success("Completed!")
                st.write(answer_data["answer"])

                # Display monitoring info
                st.write(f"Response time: {answer_data['response_time']:.2f} seconds")
                st.write(f"Relevance: {answer_data['relevance']}")
                st.write(f"Model used: {answer_data['model_used']}")
                st.write(f"Total tokens: {answer_data['total_tokens']}")
                st.write(f"Search Method: {answer_data['search_type']}")

                # Save conversation
                print_log("Saving conversation to database")
                save_conversation(st.session_state.conversation_id, user_input, answer_data, city)
                print_log("Conversation saved successfully")

        # Feedback buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍"):
                st.session_state.count += 1
                print_log(f"Positive feedback received. New count: {st.session_state.count}")
                save_feedback(st.session_state.conversation_id, 1)
                print_log("Positive feedback saved to database")
                st.success("Thanks for your feedback! 😊")
                st.session_state.conversation_id = str(uuid.uuid4())

        with col2:
            if st.button("👎"):
                st.session_state.count -= 1
                print_log(f"Negative feedback received. New count: {st.session_state.count}")
                save_feedback(st.session_state.conversation_id, -1)
                print_log("Negative feedback saved to database")
                st.warning("Thanks for your feedback! We'll use it to improve. 🙏")
                st.session_state.conversation_id = str(uuid.uuid4())

        st.write(f"Current count: {st.session_state.count}")

    # =====================
    # RIGHT COLUMN
    # =====================
    with right_col:
        # Feedback stats
        feedback_stats = get_feedback_stats()
        st.subheader("📊 Feedback Stats")
        st.metric("👍 Thumbs Up", feedback_stats['thumbs_up'])
        st.metric("👎 Thumbs Down", feedback_stats['thumbs_down'])

        st.subheader("🕓 Recent Conversations")
        relevance_filter = st.selectbox(
            "Filter by relevance:",
            ["All", "RELEVANT", "PARTLY_RELEVANT", "NON_RELEVANT"],
            key="relevance_filter",
        )

        recent_conversations = get_recent_conversations(
            limit=5,
            relevance=relevance_filter if relevance_filter != "All" else None,
        )

        for conv in recent_conversations:
            st.write(f"**Q:** {conv['question']}")
            st.write(f"**A:** {conv['answer']}")
            st.caption(f"Relevance: {conv['relevance']} | Model: {conv['model_used']} | Search: {conv['search_type']}")
            st.write("---")

print_log("Streamlit app loop completed")

if __name__ == "__main__":
    print_log("Travel Assistant application started")
    main()
