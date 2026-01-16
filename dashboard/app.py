# dashboard/app.py
import streamlit as st, requests

st.title("🎙️ AI Meeting Assistant")

uploaded_file = st.file_uploader("Upload meeting audio", type=["mp3", "wav", "m4a"])
tool = st.selectbox("Send follow-ups via", ["Gmail", "Notion", "Trello"])

if st.button("Process Meeting") and uploaded_file:
    files = {"file": uploaded_file.getvalue()}
    response = requests.post(f"http://localhost:8000/process?tool={tool}", files=files)
    result = response.json()

    st.subheader("📝 Summary")
    st.write(result["summary"]["summary"])

    st.subheader("✅ Action Items")
    for item in result["action_items"]:
        st.write(f"- {item['task']} (Owner: {item['owner']}, Due: {item.get('due')})")

    st.success(f"Follow-up messages sent via {tool}!")