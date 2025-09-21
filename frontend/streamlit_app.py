import streamlit as st
import requests
import json
from PIL import Image
import io
import numpy as np

# Simple import - Backend is now in the same directory
from Backend.db.database import SessionLocal

# Dynamic backend URL - different for local vs Streamlit Cloud
IS_STREAMLIT_CLOUD = os.environ.get('STREAMLIT_SERVER_IS_RUNNING_ON_STREAMLIT_CLOUD', False)

if IS_STREAMLIT_CLOUD:
    # Production: Backend runs on port 8000 in same container
    BACKEND_URL = "http://localhost:8000"
else:
    # Local development: Backend runs on port 8003
    BACKEND_URL = "http://localhost:8003"

st.set_page_config(page_title="OMR Evaluation System", page_icon="📝", layout="wide")
st.title("📝 Automated OMR Evaluation System")
st.markdown("Upload OMR answer sheets for automatic evaluation and scoring")

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = []

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    exam_code = st.text_input("Exam Code", placeholder="e.g., MATH_2024_FINAL")
    student_id = st.text_input("Student ID", placeholder="e.g., S12345")
    
    # Fetch available exams from backend
    try:
        response = requests.get(f"{BACKEND_URL}/exams")
        if response.status_code == 200:
            exams = response.json()
            exam_options = [exam['exam_code'] for exam in exams]
            selected_exam = st.selectbox("Select Exam", options=exam_options)
        else:
            st.warning("Could not fetch exams from backend")
            selected_exam = None
    except:
        selected_exam = None
        st.warning("Backend not reachable")

# File upload section
st.header("📤 Upload OMR Sheet")
uploaded_file = st.file_uploader("Choose an OMR sheet image", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # Display uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded OMR Sheet", use_column_width=True)
    
    # Process button
    if st.button("🚀 Evaluate OMR Sheet", type="primary"):
        with st.spinner("Processing OMR sheet..."):
            try:
                # Prepare the file for upload
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                data = {
                    "exam_code": exam_code or selected_exam,
                    "student_id": student_id
                }
                
                # Send to backend
                response = requests.post(
                    f"{BACKEND_URL}/process-omr",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.results.append(result)
                    st.success("✅ Evaluation completed successfully!")
                    
                    # Display results
                    st.header("📊 Results")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Total Score", result.get('total_score', 0))
                        st.metric("Student ID", result.get('student_id', 'N/A'))
                        st.metric("Exam Code", result.get('exam_code', 'N/A'))
                    
                    with col2:
                        if result.get('section_scores'):
                            st.write("**Section Scores:**")
                            for section, score in result['section_scores'].items():
                                st.write(f"{section}: {score}")
                        
                        if result.get('raw_answers'):
                            st.write("**Answers:**")
                            st.json(result['raw_answers'])
                
                else:
                    st.error(f"❌ Error: {response.text}")
                    
            except Exception as e:
                st.error(f"❌ Processing failed: {str(e)}")

# Display previous results
if st.session_state.results:
    st.header("📋 Evaluation History")
    for i, result in enumerate(st.session_state.results):
        with st.expander(f"Result {i+1} - {result.get('student_id', 'Unknown')} - Score: {result.get('total_score', 0)}"):
            st.json(result)

# Health check
try:
    health_response = requests.get(f"{BACKEND_URL}/health")
    if health_response.status_code == 200:
        st.sidebar.success("✅ Backend connected")
    else:
        st.sidebar.error("❌ Backend not healthy")
except:
    st.sidebar.error("❌ Backend not reachable")

# Footer
st.markdown("---")
st.markdown("**Automated OMR Evaluation System** | Built with Streamlit & FastAPI")