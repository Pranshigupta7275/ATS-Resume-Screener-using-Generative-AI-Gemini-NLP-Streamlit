import os
import logging
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
import fitz
import google.generativeai as genai
import io
import base64
from db import ATSResult, session

# ------------------- Streamlit UI Config -------------------

st.set_page_config(
    page_title="ATS Resume Screener",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ------------------- Sidebar (Branding & Links) -------------------

import streamlit as st

# Sidebar content
with st.sidebar:
    st.image("Pranshi.png")
    st.markdown("### 💼 *ATS Resume Screener*")
    st.markdown("---")

    st.markdown("#### 👤 **Pranshi Gupta**")
    st.markdown("📍 *Noida, India*")
    st.markdown("✉️ Reach out for collaboration or feedback!")

    st.markdown("---")
    st.markdown("### 🔗 **Connect With Me**")
    st.markdown("[🔗 LinkedIn](https://www.linkedin.com/in/pranshi-gupta-211520290/)")
    st.markdown("[💻 GitHub](https://github.com/Pranshigupta7275)")
    st.markdown("---")
    st.caption("Made with ❤️ using Streamlit")


# ------------------- Main App Header -------------------

st.markdown("""
    <style>
    .main-title {
        font-size: 28px;
        font-weight: bold;
        color: #2c3e50;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">📄 ATS Resume Screener</p>', unsafe_allow_html=True)

# ------------------- Setup -------------------

os.environ["STREAMLIT_SUPPRESS_CONFIG_WARNINGS"] = "1"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ------------------- PDF → Image Conversion -------------------
@st.cache_data
def input_pdf_setup(uploaded_file):
    """
    Extracts raw text from each page of an uploaded PDF and
    returns it as a list of parts the Gemini model can consume.
    """
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        pdf_parts = []

        for page in doc:
            page_text = page.get_text("text")
            pdf_parts.append({"text": page_text})

        return pdf_parts

    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise

# ------------------- Gemini API Response -------------------

def get_genai_response(input_text, pdf_content, prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        parts = []
        if input_text:
            parts.append({"text": input_text})

        # NEW – append each page’s text
        for page_part in pdf_content:
            parts.append(page_part)           

        if prompt:
            parts.append({"text": prompt})

        response = model.generate_content(parts)
        return response.text if hasattr(response, "text") else str(response)

    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
        return f"⚠️ Error: {e}"

# ------------------- Prompts -------------------

input_prompt1 = """
You are an expert HR professional skilled in analyzing resumes across software development, data science, web development, and analytics domains.

Carefully review the uploaded resume and provide a concise, well-structured analysis with the following details:

1. 🔍 Candidate Summary: Highlight their education, experience, and focus area.
2. 🛠️ Key Technical Skills: List technologies, languages, and tools mentioned.
3. 💪 Strengths: Mention any strong points, achievements, or standout skills.
4. ✏️ Resume Improvements: Suggest formatting or content improvements.
5. 🧭 Recommended Roles: Suggest 2–3 job titles or domains that best fit their profile.

Use bullet points where helpful. Keep your response clear and ATS-friendly.
"""

input_prompt2 = """
You are a professional ATS (Applicant Tracking System) engine.

Compare the uploaded resume with the following job description and return a structured analysis:

1. ✅ **Percentage Match**: Estimate how well the resume aligns with the job description (in %).
2. 🔑 **Matching Skills/Keywords**: List skills or keywords found in both resume and job description.
3. ❌ **Missing Keywords**: List key skills or terms from the job description that are missing in the resume.
4. 📈 **Suggestions to Improve Match**: Suggest specific changes to improve alignment (e.g., add missing keywords, rephrase existing content).

Start your response with the percentage match.
Be precise, structured, and useful for real-world screening.
"""
 
input_prompt3 = """
You are an expert career mentor and AI assistant.

Your task is to analyze the resume and suggest skill improvements based on current industry trends and the provided job description.

Please provide:

1. 📌 **Gaps in Skills or Experience**: Mention any missing or weak areas that reduce job fitness.
2. 🛠️ **Technologies or Tools to Learn**: List 3–5 high-demand tools, frameworks, or practices the candidate should add.
3. 🧾 **Certifications or Courses to Pursue**: Recommend any specific online certifications (from Coursera, Udemy, etc.).
4. 📂 **Portfolio Suggestions**: Suggest 1–2 practical projects the candidate can build to stand out.

Tailor your response based on the job description and role expectations.
Keep it concise, positive, and action-oriented.
"""


# ------------------- Streamlit UI -------------------

input_text = st.text_area("📝 Paste Job Description:")
uploaded_file = st.file_uploader("📄 Upload Resume PDF", type=["pdf"])

if uploaded_file:
    st.success("✅ Resume Uploaded")

# ------------------- Buttons -------------------

col1, col2, col3 = st.columns(3)

with col1:
    submit1 = st.button("🔍 Tell Me About Resume")
with col2:
    submit2 = st.button("💡 Improve My Skills")
with col3:
    submit3 = st.button("📈 ATS Match Score")

if not uploaded_file and (submit1 or submit2 or submit3):
    st.warning("⚠️ Please upload a resume PDF.")

if (submit2 or submit3) and not input_text.strip():
    st.warning("⚠️ Please provide a job description.")

# ------------------- Main Logic -------------------

if uploaded_file:
    try:
        pdf_content = input_pdf_setup(uploaded_file)

        if submit1:
            with st.spinner("Analyzing resume summary..."):
                response = get_genai_response("", pdf_content, input_prompt1)
            with st.expander("📄 Resume Summary"):
                st.write(response)
            session.add(ATSResult(
                job_description="",
                resume_filename=uploaded_file.name,
                analysis_type="Resume Summary",
                result=response))
            session.commit()

        elif submit2 and input_text.strip():
            with st.spinner("Analyzing skill gaps..."):
                response = get_genai_response(input_text, pdf_content, input_prompt3)
            with st.expander("💡 Skill Gap Analysis"):
                st.write(response)
            session.add(ATSResult(
                job_description=input_text,
                resume_filename=uploaded_file.name,
                analysis_type="Skill Improvement",
                result=response))
            session.commit()

        elif submit3 and input_text.strip():
            with st.spinner("Matching resume with job description..."):
                response = get_genai_response(input_text, pdf_content, input_prompt2)
            with st.expander("📈 ATS Match Score"):
                st.write(response)
            session.add(ATSResult(
                job_description=input_text,
                resume_filename=uploaded_file.name,
                analysis_type="ATS Match",
                result=response))
            session.commit()

    except Exception as e:
        st.error(f"Something went wrong: {e}")

# ------------------- View Past Results -------------------

if st.button("📁 View Saved Results"):
    results = session.query(ATSResult).all()
    for r in results:
        st.subheader(f"{r.analysis_type} – {r.resume_filename}")
        st.markdown(f"**Job Description:** {r.job_description[:300]}")
        st.text_area("🧠 AI Result", r.result, height=200)

# ------------------- Delete Past Results -------------------
if st.button("🗑️ Delete All Results"):
    from db import delete_all_results
    delete_all_results()
    st.success("✅ All results deleted successfully!")

    

    

