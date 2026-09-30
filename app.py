import streamlit as st
import pdfplumber
import requests
import json
import os
import random
import time

st.set_page_config(page_title="Zailrs", page_icon="D", layout="centered")

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
    opacity: 0.4;
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
[data-testid="stDecoration"] {
    display: none;
}
[data-testid="stStatusWidget"] {
    display: none;
}
a[href*="github.com"] {
    display: none !important;
}
footer {
    visibility: hidden;
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

def get_error_code(data):
    if "error" in data and isinstance(data["error"], dict):
        return data["error"].get("code", 0)
    return 0

def call_ai(prompt, api_key):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=" + api_key
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    data = {"error": {"code": 0}}
    for attempt in range(4):
        try:
            res = requests.post(url, json=payload, timeout=60)
            data = res.json()
        except Exception:
            data = {"error": {"code": 0}}
        if "candidates" in data:
            return data
        code = get_error_code(data)
        if code in (0, 500, 503):
            time.sleep(3 * (attempt + 1))
        else:
            return data
    return data

def get_answer(data):
    if "candidates" in data:
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"], None
        except Exception:
            return None, "The AI could not produce an answer this time. Please try again."
    code = get_error_code(data)
    if code == 429:
        message = "Daily limit reached for now. Please try again later."
    elif code == 503:
        message = "The AI service is busy right now. Please try again in a minute."
    else:
        message = "Something went wrong. Please try again in a moment."
    return None, message

def get_api_key():
    for name in ["AI_API_KEY", "GEMINI_API_KEY"]:
        if name in st.secrets:
            return st.secrets[name]
    return None

def input_border():
    st.markdown("""
<style>
div[data-baseweb="input"] {
    border: 2px solid #5C1520 !important;
    border-radius: 8px !important;
    background-color: white !important;
}
div[data-baseweb="input"]:focus-within {
    border-color: #3D0E15 !important;
    box-shadow: 0 0 0 3px rgba(92, 21, 32, 0.25) !important;
}
div[data-baseweb="input"] input {
    background-color: white !important;
}
</style>
""", unsafe_allow_html=True)

def falling_icons_background():
    icons_svg = [
        '<svg width="30" height="30" viewBox="0 0 24 24"><rect x="4" y="2" width="16" height="20" fill="#4A90D9"/><rect x="7" y="5" width="3" height="3" fill="white"/><rect x="14" y="5" width="3" height="3" fill="white"/><rect x="7" y="10" width="3" height="3" fill="white"/><rect x="14" y="10" width="3" height="3" fill="white"/><rect x="7" y="15" width="3" height="3" fill="white"/><rect x="14" y="15" width="3" height="3" fill="white"/></svg>',
        '<svg width="30" height="30" viewBox="0 0 24 24"><rect x="3" y="8" width="18" height="12" rx="2" fill="#B8860B"/><rect x="8" y="5" width="8" height="4" rx="1" fill="#8B6508"/><rect x="3" y="12" width="18" height="2" fill="#8B6508"/></svg>',
        '<svg width="28" height="28" viewBox="0 0 24 24"><rect x="4" y="2" width="16" height="20" fill="white" stroke="#5C1520" stroke-width="1"/><rect x="7" y="6" width="10" height="1.5" fill="#5C1520"/><rect x="7" y="10" width="10" height="1.5" fill="#5C1520"/><rect x="7" y="14" width="6" height="1.5" fill="#5C1520"/></svg>',
        '<svg width="30" height="30" viewBox="0 0 24 24"><rect x="3" y="10" width="18" height="10" fill="#2E8B57"/><polygon points="12,2 22,10 2,10" fill="#3CB371"/><rect x="6" y="13" width="2" height="6" fill="white"/><rect x="11" y="13" width="2" height="6" fill="white"/><rect x="16" y="13" width="2" height="6" fill="white"/></svg>',
        '<svg width="30" height="30" viewBox="0 0 24 24"><rect x="4" y="14" width="3" height="7" fill="#E07A2F"/><rect x="9" y="9" width="3" height="12" fill="#4A90D9"/><rect x="14" y="4" width="3" height="17" fill="#5C1520"/></svg>',
    ]
    html = ""
    for i in range(18):
        icon = random.choice(icons_svg)
        left = random.randint(0, 96)
        duration = random.randint(8, 18)
        delay = random.randint(0, 15)
        html += '<div class="falling-icon" style="left:' + str(left) + 'vw; animation-duration:' + str(duration) + 's; animation-delay:-' + str(delay) + 's;">' + icon + '</div>'
    st.markdown(html, unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "login"

def login_page():
    input_border()
    falling_icons_background()
    st.title("Zailrs")
    st.markdown("<p class=\"tagline\">Get instant AI feedback on your resume</p>", unsafe_allow_html=True)
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

    st.write("Need an account? Use the button below to sign up.")
    if st.button("Go to Sign Up"):
        st.session_state.page = "signup"
        st.rerun()

def signup_page():
    input_border()
    falling_icons_background()
    st.title("Zailrs")
    st.markdown("<p class=\"tagline\">Create your free account</p>", unsafe_allow_html=True)
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

    st.write("Already have an account? Use the button below to log in.")
    if st.button("Go to Login"):
        st.session_state.page = "login"
        st.rerun()

def main_app():
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("Zailrs")
        st.markdown("<p class=\"tagline\">AI Resume Checker</p>", unsafe_allow_html=True)
    with col2:
        st.write("")
        st.write("User: " + st.session_state.username)
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    st.divider()

    if st.session_state.username == "admin":
        with st.expander("Admin: View all registered users"):
            st.json(load_users())
        st.divider()

    api_key = get_api_key()
    if api_key is None:
        st.error("The AI service is not available right now. Please try again later.")
        return

    st.markdown("#### Step 1: Upload your resume")
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"], label_visibility="collapsed")

    resume_text = ""
    if uploaded_file is not None:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                resume_text += page.extract_text() or ""

    if uploaded_file is not None:
        tab1, tab2 = st.tabs(["Score Against a Job", "Find Matching Companies"])

        with tab1:
            st.markdown("##### Paste the job description")
            job_description = st.text_area("Paste the job description here", label_visibility="collapsed", height=150)

            if job_description:
                if st.button("Check My Resume"):
                    with st.spinner("Analyzing your resume. This can take up to a minute..."):
                        prompt = "You are an expert recruiter. Rate this resume out of 10 "
                        prompt += "based on how well it matches the job description, "
                        prompt += "as a hiring company would evaluate it. "
                        prompt += "Start your response with Rating: X/10 on its own line, "
                        prompt += "then explain the rating and list 3-5 specific improvements.\n\n"
                        prompt += "RESUME:\n" + resume_text + "\n\n"
                        prompt += "JOB DESCRIPTION:\n" + job_description

                        answer, error = get_answer(call_ai(prompt, api_key))

                        if error:
                            st.error(error)
                        else:
                            st.markdown("<div class=\"result-box\">" + answer + "</div>", unsafe_allow_html=True)

        with tab2:
            st.write("Based on your resume's skills and experience, find companies that are a good fit.")
            if st.button("Find Top 50 Companies"):
                with st.spinner("Finding matching companies. This can take up to a minute..."):
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

                    answer, error = get_answer(call_ai(prompt, api_key))

                    if error:
                        st.error(error)
                    else:
                        st.markdown(answer)

if st.session_state.logged_in:
    main_app()
else:
    if st.session_state.page == "signup":
        signup_page()
    else:
        login_page()