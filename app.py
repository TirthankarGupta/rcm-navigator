import streamlit as st
# ---- LOGIN SYSTEM ----
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login():
    st.markdown("## 🔐 Login Required")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "Admin@2026":
            st.session_state.authenticated = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

if not st.session_state.authenticated:
    login()
    st.stop()
# ---- PAGE CONFIG ----
st.set_page_config(page_title="Insurance Checklist Assistant", layout="centered")

# ---- CUSTOM CSS ----
st.markdown("""
<style>

/* Hide Streamlit header */
header {visibility: hidden;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Background */
.stApp {
    background: linear-gradient(to right, #e6f0ff, #f2f7ff);
}

/* Button */
div.stButton > button {
    background: linear-gradient(to bottom, #ff4d4d, #cc0000);
    color: white;
    font-size: 18px;
    border-radius: 10px;
    box-shadow: 0 5px #990000;
}

div.stButton > button:active {
    transform: translateY(2px);
    box-shadow: 0 2px #660000;
}

/* Checklist */
.checklist {
    font-size: 20px;
    margin-bottom: 10px;
}
/* Improve input field visibility */
div[data-baseweb="input"] {
    background-color: white !important;
    border-radius: 10px !important;
    border: 2px solid #4da6ff !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15) !important;
}

div[data-baseweb="input"] input {
    background-color: white !important;
    color: black !important;
    font-size: 18px !important;
    padding: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ---- TITLE ----
st.markdown("## 🔎 Enter Insurance Name")

# ---- INPUT ----
insurance = st.text_input("")

# ---- LOAD DATA ----
with open("DATA.txt", "r") as file:
    data = file.read()

# ---- LOGIC ----
def get_section(insurance_name, text):
    insurance_name = insurance_name.lower()

    if "aetna better health" in insurance_name:
        start = text.lower().find("aetna better health of il")
        end = text.lower().find("aetna medicare")
        return text[start:end]

    elif "aetna medicare" in insurance_name:
        start = text.lower().find("aetna medicare")
        return text[start:]

    else:
        return None

# ---- BUTTON ----
if st.button("📌 Generate Checklist"):
    section = get_section(insurance, data)

    if section:
        st.markdown("### 📄 Checklist")

        for line in section.split("\n"):
            if line.strip() and "aetna" not in line.lower() and "-----" not in line:
                st.markdown(f"<div class='checklist'>✅ {line.strip()}</div>", unsafe_allow_html=True)
    else:
        st.error("Insurance not found")
