# ATS Resume Screener using GenAI (Gemini 1.5)

This is an AI-powered Applicant Tracking System (ATS) screener built with **Streamlit**, **Google Gemini API**, and **SQLite**. It analyzes resumes against job descriptions to provide:
- ✅ Resume summaries
- 📊 Percentage match with job descriptions
- 💡 Skill gap and improvement suggestions

## 🔧 Features
- PDF resume to image conversion
- Google Gemini (Vision & Text) for GenAI responses
- Store results in SQLite DB
- Clean, intuitive Streamlit UI
- View past results easily

## 🛠 Tech Stack
- Python, Streamlit
- Google Generative AI (Gemini Pro Vision)
- PDF2Image, PIL
- SQLite, SQLAlchemy
- Dotenv

## 🚀 How to Run
```bash
git clone https://github.com/Pranshigupta7275/ats-resume-screener.git
cd ats-resume-screener
pip install -r requirements.txt
streamlit run app.py
