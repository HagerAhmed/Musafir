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

    # --- Sidebar ---
    st.sidebar.header("⚙️ Settings")

    city = st.sidebar.selectbox("🌆 Choose a City:", ["Cairo", "London", "Rome", "Seoul"])
    model_choice = st.sidebar.selectbox("🤖 Choose Model:", ["mistral-medium-2508", "ministral-8b-latest", "mistral-small-latest"])
    search_type = st.sidebar.radio("🔍 Search Type:", ["Qdrant", "Elasticsearch_Text", "Elasticsearch_Vector", "MinSearch"])

    st.sidebar.markdown("---")
    st.sidebar.info("💡 Tip: You can switch models or search type anytime!")

    # --- Session Initialization ---
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # --- Chat Interface ---
    st.subheader("💬 Ask Musafir")
    user_input = st.chat_input("Type your travel question...")

    if user_input:
        with st.spinner("Thinking... ✈️"):
            start_time = time.time()
            answer_data = get_answer(user_input, city, model_choice, search_type)
            end_time = time.time()

            # Save conversation
            save_conversation(st.session_state.conversation_id, user_input, answer_data, city)

            # Store chat messages
            st.session_state.messages.append({
                "role": "user", "content": user_input
            })
            st.session_state.messages.append({
                "role": "assistant", "content": answer_data["answer"], "meta": answer_data
            })

    # --- Display Chat Messages ---
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant" and "meta" in msg:
                meta = msg["meta"]
                st.caption(f"🕓 {meta['response_time']:.2f}s | 🤖 {meta['model_used']} | 🔎 {meta['search_type']} | 📈 Relevance: {meta['relevance']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("👍", key=f"up_{uuid.uuid4()}"):
                        save_feedback(st.session_state.conversation_id, 1)
                        st.success("Thanks for the positive feedback! 😊")
                with col2:
                    if st.button("👎", key=f"down_{uuid.uuid4()}"):
                        save_feedback(st.session_state.conversation_id, -1)
                        st.warning("We'll use this to improve. 🙏")

    # --- Analytics and Recent Activity ---
    with st.expander("📊 Insights & Recent Conversations"):
        st.markdown("### Recent Conversations")
        relevance_filter = st.selectbox("Filter by relevance:", ["All", "RELEVANT", "PARTLY_RELEVANT", "NON_RELEVANT"])
        recent_conversations = get_recent_conversations(limit=5, relevance=relevance_filter if relevance_filter != "All" else None)

        for conv in recent_conversations:
            with st.container():
                st.write(f"**Q:** {conv['question']}")
                st.write(f"**A:** {conv['answer']}")
                st.caption(f"Relevance: {conv['relevance']} | Model: {conv['model_used']} | Search: {conv['search_type']}")
                st.divider()

        st.markdown("### Feedback Summary")
        feedback_stats = get_feedback_stats()
        st.metric("👍 Positive", feedback_stats['thumbs_up'])
        st.metric("👎 Negative", feedback_stats['thumbs_down'])


if __name__ == "__main__":
    main()
