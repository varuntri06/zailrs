import streamlit as st
import pdfplumber
import requests
import json
import os
import random

st.set_page_config(page_title="Zailrs", page_icon="📄", layout="centered")

st.markdown("""
<style>
.stApp {
    background-color: #FDF6F0;
}
h1, h2, h3 {
    color: #5C1520;
}
.stButton>button {
    background-color: #5C1520;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 8px 20px;
    font-weight: 600;
    transition: transform 0.2s ease;
}
.stButton>button:hover {
    background-color: #3D0E15;
    color: white;
    transform: scale(1.05);
}
.result-box {
    background-color: white;
    padding: 25px;
    border-radius: 12px;
    border-left: 6px solid #5C1520;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    margin-top: 15px;
}
.tagline {
    color: #7A5C5C;
    font-size: 16px;
    margin-top: -10px;
}
.falling-icon {
    position: fixed;
    top: -60px;
    font-size: 28px;
    opacity: 0.35;
    z-index: 0;
    animation-name: fall;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
    pointer-events: none;
}
@keyframes fall {
    0% { transform: translateY(0); }
    100% { transform: translateY(110vh); }
}
</style>
""", unsafe_allow_html=True)

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def call_gemini(prompt, api_key):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key=" + api_key
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    res = requests.post(url, json=payload)
    return res.json()

def falling_icons_background():
    icons = ["🏢", "💼", "📄", "🏦", "🏬", "🖥️", "📊"]
    html = ""
    for i in range(18):
        icon = random.choice(icons)
        left = random.randint(0, 98)
        duration = random.randint(8, 18)
        delay = random.randint(0, 15)
        html += '<div class="falling-icon" style="left:' + str(left) + 'vw; animation-duration:' + str(duration) + 's; animation-delay:-' + str(delay) + 's;">' + icon + '</div>'
    st.markdown(html, unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "login"

def login_page():
    falling_icons_background()
    st.title("📄 Zailrs")
    st.markdown('<p class="tagline">Get instant AI feedback on your resume</p>', unsafe_allow_html=True)
    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_users()
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Wrong username or password")

    st.write("Don't have an account?")
    if st.button("Go to Sign Up"):
        st.session_state.page = "signup"
        st.rerun()

def signup_page():
    falling_icons_background()
    st.title("📄 Zailrs")
    st.markdown('<p class="tagline">Create your free account</p>', unsafe_allow_html=True)
    st.subheader("Sign Up")

    new_username = st.text_input("Choose a username")
    new_password = st.text_input("Choose a password", type="password")

    if st.button("Create Account"):
        users = load_users()
        if new_username in users:
            st.error("Username already exists. Try another one.")
        elif new_username == "" or new_password == "":
            st.error("Please fill in both fields.")
        else:
            users[new_username] = new_password
            save_users(users)
            st.success("Account created! You can now log in.")

    st.write("Already have an account?")
    if st.button("Go to Login"):
        st.session_state.page = "login"
        st.rerun()

def main_app():
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("📄 Zailrs")
        st.markdown('<p class="tagline">AI Resume Checker</p>', unsafe_allow_html=True)
    with col2:
        st.write("")
        st.write(f"👤 {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    st.divider()

    if "GEMINI_API_KEY" not in st.secrets:
        st.error("API key not found. Please add GEMINI_API_KEY to .streamlit/secrets.toml")
        return

    api_key = st.secrets["GEMINI_API_KEY"]

    st.markdown("#### 1️⃣ Upload your resume")
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"], label_visibility="collapsed")

    resume_text = ""
    if uploaded_file is not None:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                resume_text += page.extract_text() or ""

    if uploaded_file is not None:
        tab1, tab2 = st.tabs(["📊 Score Against a Job", "🏢 Find Matching Companies"])

        with tab1:
            st.markdown("##### Paste the job description")
            job_description = st.text_area("Paste the job description here", label_visibility="collapsed", height=150)

            if job_description:
                if st.button("🔍 Check My Resume"):
                    with st.spinner("Analyzing your resume..."):
                        prompt = "You are an expert recruiter. Rate this resume out of 10 "
                        prompt += "based on how well it matches the job description, "
                        prompt += "as a hiring company would evaluate it. "
                        prompt += "Start your response with 'Rating: X/10' on its own line, "
                        prompt += "then explain the rating and list 3-5 specific improvements.\n\n"
                        prompt += "RESUME:\n" + resume_text + "\n\n"
                        prompt += "JOB DESCRIPTION:\n" + job_description

                        data = call_gemini(prompt, api_key)

                        if "candidates" in data:
                            result_text = data["candidates"][0]["content"]["parts"][0]["text"]
                            st.markdown(f'<div class="result-box">{result_text}</div>', unsafe_allow_html=True)
                        else:
                            st.error("Something went wrong:")
                            st.text(str(data))

        with tab2:
            st.write("Based on your resume's skills and experience, find companies that are a good fit.")
            if st.button("🏢 Find Top 50 Companies"):
                with st.spinner("Finding matching companies..."):
                    prompt = "Based on the skills, experience, and field shown in this resume, "
                    prompt += "list the top 50 companies (a mix of large, well-known companies and "
                    prompt += "relevant startups, prioritizing companies that hire in India where possible) "
                    prompt += "that would likely be a good fit for this candidate. "
                    prompt += "Format the answer as a numbered markdown list from 1 to 50, one company per line, "
                    prompt += "with the company name in bold using double asterisks, followed by a dash and "
                    prompt += "a 3-5 word reason. Example format:\n"
                    prompt += "1. **Google** - strong fit for backend roles\n"
                    prompt += "2. **Infosys** - good for entry-level developers\n\n"
                    prompt += "RESUME:\n" + resume_text

                    data = call_gemini(prompt, api_key)

                    if "candidates" in data:
                        result_text = data["candidates"][0]["content"]["parts"][0]["text"]
                        st.markdown(result_text)
                    else:
                        st.error("Something went wrong:")
                        st.text(str(data))

if st.session_state.logged_in:
    main_app()
else:
    if st.session_state.page == "signup":
        signup_page()
    else:
        login_page()