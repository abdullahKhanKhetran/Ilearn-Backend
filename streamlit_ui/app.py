import streamlit as st
import requests
import json

# API Configuration
API_URL = "http://127.0.0.1:8000"  # Changed from localhost to 127.0.0.1

st.set_page_config(
    page_title="Zeeshan's Bot - Student Performance",
    page_icon="🎓",
    layout="wide"
)

# Initialize session state for conversation
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "current_student_id" not in st.session_state:
    st.session_state.current_student_id = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🎓 Zeeshan's Bot")
st.markdown("**Your AI Assistant for Student Performance Analysis** 📊")

# Sidebar
with st.sidebar:
    st.header("📊 Student Selection")
    
    # Fetch available students
    try:
        response = requests.get(f"{API_URL}/students")
        if response.status_code == 200:
            students = response.json()["students"]
            student_options = {f"{s['student_id']} - {s['name']}": s['student_id'] for s in students}
            
            selected = st.selectbox(
                "Choose a student:",
                options=list(student_options.keys()),
                index=0
            )
            selected_student_id = student_options[selected]
            
            # If student changed, reset conversation
            if selected_student_id != st.session_state.current_student_id:
                st.session_state.current_student_id = selected_student_id
                st.session_state.conversation_history = []
                st.session_state.messages = []
                st.rerun()
    except:
        st.error("⚠️ Cannot connect to API. Please start the backend server.")
        st.code("cd api && uvicorn main:app --reload")
    
    st.markdown("---")
    
    if st.button("🔄 New Conversation", use_container_width=True):
        st.session_state.conversation_history = []
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 💡 Quick Start")
    st.info("""
    **Try saying:**
    - Hi / Hello
    - How is this student doing?
    - What subjects need work?
    - Show attendance details
    - Thanks!
    """)

# Chat interface (ChatGPT style)
st.markdown("---")

# Display chat messages
message_count = 0
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show performance badge if present
        if message["role"] == "assistant" and "performance_category" in message:
            category = message["performance_category"]
            if category == "Fantastic":
                st.success(f"🌟 **{category}** Performance")
            elif category == "Average":
                st.info(f"📈 **{category}** Performance")
            elif category == "Below Average":
                st.warning(f"📉 **{category}** Performance")
        
        # Show suggestions
        if message["role"] == "assistant" and "suggestions" in message and message["suggestions"]:
            st.markdown("**💭 Suggested questions:**")
            cols = st.columns(min(len(message["suggestions"]), 2))
            for idx, suggestion in enumerate(message["suggestions"][:4]):
                with cols[idx % 2]:
                    # Unique key using message_count and timestamp
                    unique_key = f"sug_msg{message_count}_idx{idx}"
                    if st.button(suggestion, key=unique_key, use_container_width=True):
                        # Trigger suggestion as new message
                        st.session_state.pending_message = suggestion
                        st.rerun()
    
    message_count += 1

# Check if there's a pending message from suggestion click
if "pending_message" in st.session_state:
    user_message = st.session_state.pending_message
    del st.session_state.pending_message
else:
    # Chat input
    user_message = st.chat_input("Ask about the student's performance...")

# Process user message
if user_message:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    with st.chat_message("user"):
        st.markdown(user_message)
    
    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "student_id": st.session_state.current_student_id,
                        "message": user_message,
                        "conversation_history": st.session_state.conversation_history
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    bot_response = data["response"]
                    
                    # Display response
                    st.markdown(bot_response)
                    
                    # Show performance category
                    if data.get("performance_category"):
                        category = data["performance_category"]
                        if category == "Fantastic":
                            st.success(f"🌟 **{category}** Performance")
                        elif category == "Average":
                            st.info(f"📈 **{category}** Performance")
                        elif category == "Below Average":
                            st.warning(f"📉 **{category}** Performance")
                    
                    # Show suggestions
                    if data.get("suggestions"):
                        st.markdown("**💭 Suggested questions:**")
                        cols = st.columns(min(len(data["suggestions"]), 2))
                        for idx, suggestion in enumerate(data["suggestions"][:4]):
                            with cols[idx % 2]:
                                # Unique key for new suggestions
                                unique_key = f"sug_new_{len(st.session_state.messages)}_{idx}"
                                if st.button(suggestion, key=unique_key, use_container_width=True):
                                    st.session_state.pending_message = suggestion
                                    st.rerun()
                    
                    # Update conversation history
                    st.session_state.conversation_history = [
                        {"role": msg["role"], "content": msg["content"]}
                        for msg in data["conversation_history"]
                    ]
                    
                    # Add to messages
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": bot_response,
                        "performance_category": data.get("performance_category"),
                        "suggestions": data.get("suggestions", [])
                    })
                    
                    st.rerun()
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Start server: `cd api && uvicorn main:app --reload`")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.caption("💬 Zeeshan's Bot ")