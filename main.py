import streamlit as st
import pdfplumber
import io
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="AI Resume Analyser", page_icon="📄", layout="centered")
st.title("📄 AI Resume Analyser")
st.markdown("Upload your resume and get AI-powered feedback!")


def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text


def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")


uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "txt"])
job_role = st.text_input("Enter Job Role (e.g. Software Engineer, Data Analyst)")
analyze = st.button("Analyse Resume")


if analyze and uploaded_file:
    if not GROQ_API_KEY:
        st.error("Groq API key not found! Add GROQ_API_KEY to your .env file.")
        st.stop()

    try:
        with st.spinner("Analysing your resume..."):
            file_content = extract_text_from_file(uploaded_file)

            if not file_content.strip():
                st.error("Could not extract text from the file. Please try another file.")
                st.stop()

            prompt = f"""You are an expert resume reviewer and career coach with 10+ years of experience.
Please analyse the following resume and provide detailed feedback.
Focus on specific improvements for: {job_role if job_role else 'general job applications'}

Your feedback should include:
1. Overall impression
2. Strengths of the resume
3. Areas of improvement
4. Missing keywords or skills for the role
5. Formatting suggestions
6. Final score out of 10

Resume Content:
{file_content}

Please provide clear, actionable feedback."""

            client = Groq(api_key=GROQ_API_KEY)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert resume reviewer and career coach with 10+ years of experience."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            st.markdown("### 📊 Analysis Result")
            st.markdown(response.choices[0].message.content)

    except Exception as e:
        st.error(f"Something went wrong: {e}")

elif analyze and not uploaded_file:
    st.warning("Please upload a resume file first!")