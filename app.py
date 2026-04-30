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
/* FORCE input field visibility */
.stTextInput > div > div > input {
    background-color: white !important;
    color: black !important;
    font-size: 18px !important;
    padding: 12px !important;
    border: 2px solid #4da6ff !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
}
.stTextInput > div > div > input:focus {
    border: 2px solid #ff4d4d !important;
    box-shadow: 0 0 8px rgba(255, 77, 77, 0.6) !important;
}
</style>
""", unsafe_allow_html=True)

# ---- TITLE ----
st.markdown("## 🔎 Enter Insurance Name")

# ---- INPUT ----
insurance = st.text_input("")
hcpcs = st.text_input("Enter HCPCS Code (Optional)")

# ---- LOAD DATA ----
with open("DATA.txt", "r") as file:
    data = file.read()

# ---- HCPCS IMAGE MAP ----
hcpcs_images = {
    "L0174": "https://cdn.shopify.com/s/files/1/0080/8372/products/neckbrace.jpg",
    "L0999": "https://cdn.shopify.com/s/files/1/0080/8372/products/neckbrace.jpg",
    "E0143": "https://cdn.shopify.com/s/files/1/0080/8372/products/walker.jpg"
}

# ---- LOGIC ----
def get_section(insurance, data):
    insurance = insurance.strip().upper()

    sections = data.split("---")

    for section in sections:
        lines = section.strip().split("\n")

        if not lines:
            continue

        header = lines[0].strip()

        # Extract name inside [ ]
        if header.startswith("[") and header.endswith("]"):
            section_name = header[1:-1].strip().upper()

            if section_name == insurance:
                return "\n".join(lines[1:])  # return only that section

    return None

# ---- BUTTON ----
if st.button("📌 Generate Checklist"):
    section = get_section(insurance, data)

    col1, col2 = st.columns([2, 1])

    if section:
        with col1:
            st.markdown("### 📄 Checklist")

            for line in section.split("\n"):
                if line.strip() and "aetna" not in line.lower() and "-----" not in line:
                    st.markdown(f"<div class='checklist'>✅ {line.strip()}</div>", unsafe_allow_html=True)
            
        if hcpcs:
            code = hcpcs.strip().upper()

            image_path = f"images/{code}.jpg"

            import os
            if os.path.exists(image_path):
                with col2:
                    st.markdown(f"### 🩺 Device ({code})")
                    st.image(image_path, use_column_width=True)            
    else:
        st.error("Insurance not found")
