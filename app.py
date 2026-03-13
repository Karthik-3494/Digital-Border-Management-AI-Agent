import streamlit as st
import os
from graph import app as agent_app
from tools import rag_system

st.set_page_config(page_title="Border Control AI", layout="wide")
st.title("Digital Border Control System")

if "processed" not in st.session_state:
    st.session_state.processed = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "final_state" not in st.session_state:
    st.session_state.final_state = {}

if not st.session_state.processed:
    st.subheader("1. Traveler Document & Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        action = st.selectbox("Action", ["enter", "exit", "retrieve"])
        uploaded_file = st.file_uploader("Upload Passport Scan", type=["png", "jpg", "jpeg"])
        
    with col2:
        st.markdown("**Additional Security Checks**")
        validity = st.number_input("Passport Validity Remaining (Months)", min_value=0, value=6)
        visa = st.selectbox("Current Visa Status", ["Valid", "Expired", "Not Required", "Pending"])
        sevis = st.selectbox("Student SEVIS Status", ["N/A", "Active", "Inactive"])
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            i94 = st.checkbox("I-94 Completed?")
        with col_b:
            customs = st.checkbox("Customs Cleared?")
        with col_c:
            bio = st.checkbox("Biometrics Captured?")

    if uploaded_file and st.button("Run AI Verification"):
        folder = "passport_images"
        os.makedirs(folder, exist_ok=True)
        save_path = os.path.join(folder, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.spinner("Agent is analyzing the document..."):
            initial_state = {
                "person_id": uploaded_file.name, 
                "action": action,
                "manual_inputs": {
                    "passport_validity_time": validity,
                    "visa_status": visa,
                    "student_sevis_data": sevis,
                    "i94_form_completed": i94,
                    "customs_declaration_completed": customs,
                    "biometrics_captured": bio
                }
            }
            final_state = agent_app.invoke(initial_state)

            st.session_state.final_state = final_state
            st.session_state.processed = True
            
            rag_resp = final_state.get("rag_response", "")
            content = rag_resp.content if hasattr(rag_resp, "content") else rag_resp
            st.session_state.messages.append({"role": "assistant", "content": content})
            st.rerun() 

if st.session_state.processed:
    st.success("Verification Complete!")
    
    if st.button("Scan New Traveler"):
        st.session_state.processed = False
        st.session_state.messages = []
        st.session_state.final_state = {}
        st.rerun()

    st.divider()
    col_res1, col_res2 = st.columns([1, 1.5])
    
    with col_res1:
        st.subheader("Extracted Data")
        st.json(st.session_state.final_state.get("scanned_data", st.session_state.final_state.get("db_data", {})))
        
    with col_res2:
        st.subheader("AI Analysis & Chat")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask the AI follow-up questions..."):
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                with st.spinner("Checking rules..."):
                    raw_response = rag_system.invoke({"info": prompt})
                    response_text = raw_response.content if hasattr(raw_response, "content") else raw_response
                    st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})