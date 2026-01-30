# dashboard/app.py
import streamlit as st, requests

st.title("🎙️ AI Meeting Assistant")

uploaded_file = st.file_uploader("Upload meeting audio", type=["mp3", "wav", "m4a"])
tool = st.selectbox("Send follow-ups via", ["Gmail", "Notion", "Trello"])

if st.button("Process Meeting") and uploaded_file:
    with st.spinner("Processing meeting..."):
        try:
            files = {"file": uploaded_file.getvalue()}
            response = requests.post(f"http://localhost:8000/process?tool={tool}", files=files, timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                
                if "summary" in result and isinstance(result["summary"], dict):
                    st.subheader("📝 Summary")
                    st.write(result["summary"].get("summary", "No summary available."))
                    
                    st.subheader("✅ Action Items")
                    action_items = result.get("action_items", [])
                    if action_items:
                        for item in action_items:
                            st.write(f"- {item.get('task', 'N/A')} (Owner: {item.get('owner', 'N/A')}, Due: {item.get('due', 'N/A')})")
                    else:
                        st.info("No action items extracted.")
                        
                    st.success(f"Follow-up messages sent via {tool}!")
                else:
                    st.error("Unexpected response format from the server.")
                    st.json(result)
            else:
                st.error(f"Error from server: {response.status_code}")
                st.write(response.text)
                
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the backend server. Is it running?")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")