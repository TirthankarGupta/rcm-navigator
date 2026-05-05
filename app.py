import streamlit as st
# ---- LOGIN SYSTEM ----
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == st.secrets["username"] and password == st.secrets["password"]:
            st.session_state.authenticated = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()   # ⛔ VERY IMPORTANT
    
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
payer = insurance.lower()

payer_type = "generic"

if "medicare" in payer:
    payer_type = "medicare"
elif "medicaid" in payer or "better health" in payer:
    payer_type = "medicaid"
if "show_result" not in st.session_state:
    st.session_state.show_result = False

# ---- LOAD DATA ----
with open("DATA.txt", "r") as file:
    data = file.read()

# ---- HCPCS IMAGE MAP ----
hcpcs_data = {
    "E0114": {"body": "Mobility / Crutches"},
    "E0143": {"body": "Lower Extremity / Walker"},
    "E0149": {"body": "Mobility / Heavy Duty Walker"},
    "L0172": {"body": "Neck (Cervical Spine)"},
    "L0174": {"body": "Neck (Cervical Spine)"},
    "L0621": {"body": "Lower Back (Lumbar Spine)"},
    "L1620": {"body": "Hip"},
    "L1820": {"body": "Knee"},
    "L1830": {"body": "Knee"},
    "L1833": {"body": "Knee"},
    "L1902": {"body": "Ankle"},
    "L3260": {"body": "Foot"},
    "L3670": {"body": "Shoulder / Arm"},
    "L3809": {"body": "Wrist / Hand / Finger"},
    "L3908": {"body": "Wrist / Hand"},
    "L4361": {"body": "Foot / Ankle"},
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
    st.session_state.show_result = True

if st.session_state.show_result:
    section = get_section(insurance, data)
    col1, col2 = st.columns([2, 1])

    if section:
        with col1:

            # ---- CHECKBOXES ----
            st.markdown("### ✅ Pre-Submission Checks")

            hcpcs_match = st.checkbox("HCPCS matches Delivery Receipt")
            dx_match = st.checkbox("Dx code matches")
            eligibility_ok = st.checkbox("Eligibility verified")
            signature_present = st.checkbox("Signature present on Delivery Receipt")
            physician_info = st.checkbox("Referring physician info present")
            charges_valid = st.checkbox("Charges and Allowable not zero")


            # ---- DECISION LOGIC ----
            failures = []

            if payer_type == "medicare" and not eligibility_ok:
                failures.append("Medicare eligibility critical check failed")

            if not hcpcs_match:
                failures.append("HCPCS mismatch")

            if not dx_match:
                failures.append("Dx code mismatch")

            if not eligibility_ok:
                failures.append("Eligibility not verified")

            if not signature_present:
                failures.append("Missing signature")

            if not physician_info:
                failures.append("Missing referring physician info")

            if not charges_valid:
                failures.append("Invalid charges/allowable")


            # ---- DECISION OUTPUT ----
            st.markdown("---")
            total_checks = 6
            failed_checks = len(failures)
            risk_score = int((failed_checks / total_checks) * 100)

            st.markdown(f"### 📊 Risk Score: {risk_score}/100")
            st.markdown("### 🧠 Decision")

            if len(failures) == 0:
                st.success("✔ SAFE TO SUBMIT")
            elif len(failures) <= 2:
                st.warning("⚠ NEEDS REVIEW")
            else:
                st.error("❌ HIGH RISK")

            # ---- FINAL RECOMMENDATION ----
            if len(failures) == 0:
                st.success("🚀 READY FOR SUBMISSION")
            elif len(failures) <= 2:
                st.warning("🛠 FIX ISSUES BEFORE SUBMISSION")
            else:
                st.error("⛔ DO NOT SUBMIT – HIGH RISK")
    
            # ---- DENIAL RISK INSIGHT ----
            if failures:
                st.markdown("### ⚠️ Likely Denial Reason")

                if "Missing signature" in failures and "Eligibility not verified" in failures:
                    st.warning("High denial risk due to missing signature and eligibility not verified")
            
                elif "Missing signature" in failures:
                    st.warning("Claim may be denied due to missing patient/representative signature")
            
                elif "Eligibility not verified" in failures:
                    st.warning("Claim may be denied due to eligibility not verified")
            
                elif "HCPCS mismatch" in failures:
                    st.warning("Incorrect HCPCS may lead to denial or rework")
            
                elif "Invalid charges/allowable" in failures:
                    st.warning("Incorrect charge/allowable may result in rejection or underpayment")
            
            # ---- SHOW REASONS ----
            if failures:
                st.markdown("**Issues found:**")
                for f in failures:
                    st.write(f"- {f}")
                                
                st.markdown("### 🔧 Recommended Actions")

                if "HCPCS mismatch" in failures:
                    st.write("- Verify HCPCS against Delivery Receipt and Charge Entry")

                if "Dx code mismatch" in failures:
                    st.write("- Cross-check Dx codes for accuracy and laterality")
            
                if "Eligibility not verified" in failures:
                    st.write("- Run eligibility check before submission")
            
                if "Missing signature" in failures:
                    st.write("- Obtain valid patient/representative signature")
            
                if "Missing referring physician info" in failures:
                    st.write("- Update referring physician details before billing")
            
                if "Invalid charges/allowable" in failures:
                    st.write("- Validate charge and allowable amounts")

            # ---- CHECKLIST ----
            st.markdown("---")
            st.markdown("### 📋 Checklist")

            for line in section.split("\n"):
                if line.strip() and "aetna" not in line.lower() and "-----" not in line:
                    st.markdown(
                        f"<div class='checklist'>✅ {line.strip()}</div>",
                        unsafe_allow_html=True
                    )

        # ---- DEVICE IMAGE ----
        if hcpcs:
            code = hcpcs.strip().upper()
            image_path = f"images/{code}.jpg"
            
            import os
            if os.path.exists(image_path):
                with col2:
                    if code in hcpcs_data:
                        st.success(f"🦴 Affected Area: {hcpcs_data[code]['body']}")
                        
                    st.markdown(f"### 🩺 Device ({code})")
                    st.image(image_path, use_column_width=True)

                    st.markdown("### 🦴 Human Skeleton")
                    st.image("images/skeleton.jpg", use_column_width=True)

    else:
        st.error("Insurance not found")
