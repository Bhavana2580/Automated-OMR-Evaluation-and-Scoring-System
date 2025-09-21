# 📄 Automated OMR Evaluation & Scoring System

## 🚀 Overview
This project is an *Automated OMR (Optical Mark Recognition) Evaluation System* designed for *Innomatics Research Labs* placement readiness assessments.  
It automates the entire evaluation process of OMR sheets captured via mobile phone, providing *subject-wise scores* and *overall marks* instantly.  

Traditional manual evaluation is:
- ⏳ Time-consuming
- ❌ Error-prone
- 👥 Resource-intensive  

This system reduces turnaround time from *days to minutes*, ensuring quick feedback for students.

---

## 🎯 Features
- 📸 Capture OMR sheets using *mobile phone camera*
- 🖼 *Image preprocessing*: skew correction, rotation, perspective adjustment
- 🔍 *Bubble detection*: Detects filled vs. unfilled bubbles using OpenCV
- 🤖 *Ambiguity handling*: ML-based classification for unclear marks
- 📝 *Answer key support* for multiple sets (e.g., Set A & Set B)
- 📊 *Per-subject scoring* (Python, EDA, SQL, Power BI, Statistics) & total marks
- 🌐 *Web application* with:
  - Upload interface
  - Dashboard for scores
  - Result export (CSV/XLSX)
  - Audit trail with stored evaluated sheets
- ⚡ Error tolerance < 0.5%

---

## 🛠 Tech Stack

### Core OMR Processing
- *Python*
- *OpenCV* → image preprocessing & bubble extraction
- *NumPy / SciPy* → array & thresholding ops
- *pdf2image / Pillow* → handling images & PDFs
- *scikit-learn / TensorFlow Lite* (optional) → ML classification for uncertain cases

### Backend
- *Flask / FastAPI* → REST APIs for evaluation
- *PostgreSQL / SQLite* → results storage & metadata
- *Pandas / OpenPyXL* → export results as CSV/XLSX

### Frontend
- *Streamlit* (MVP) → evaluator dashboard
- *Static Assets* → style.css, logo.png

---

## 📂 Folder Structure
Automated-OMR-Evaluation-System/
│
├── backend/
│   ├── omr/                
│   │   ├── processor.py
│   │   ├── utils.py
│   │   └── classifier.py
│   ├── db/                 
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── crud.py
│   │   └── schemas.py
│   ├── sample_data/
│   │   ├── images/
│   │   │   ├── A/   # OMR images (Set A)
│   │   │   ├── B/   # OMR images (Set B)
│   │   └── answer_keys/
│   │       └── Key(Set A and B).xlsx
│   ├── student_responses.xlsx   # Generated student responses
│   ├── scores.xlsx              # Computed scores
│   ├── run_omr_pipeline_multi.py
│   └── Dockerfile
│
├── frontend/
│   ├── streamlit_app.py
│   ├── package.json
│   ├── static/
│   │   ├── logo.png
│   │   └── style.css
│
└── README.md


👨‍💻 Contributors
G.Bhavana – Developer
Innomatics Research Labs – Project Challenge


📜 License
This project is licensed under the MIT License – free to use and modify.
