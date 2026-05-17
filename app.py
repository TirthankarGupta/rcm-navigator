import streamlit as st
import pandas as pd
import os
import pdfplumber

# ---- LOGIN SYSTEM ----
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:

    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        users = st.secrets["users"]

        if (
            username in users
            and password == users[username]
        ):
            st.session_state.authenticated = True
            st.success("Login successful")
            st.rerun()

        else:
            st.error("Invalid credentials")

    st.stop()

# ---- LOGOUT BUTTON ----

st.sidebar.markdown("---")

if st.sidebar.button("🚪 Logout"):

    st.session_state.authenticated = False

    st.rerun()

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="Insurance Checklist Assistant",
    layout="centered"
)

# ---- SESSION STATE ----
if "show_result" not in st.session_state:
    st.session_state.show_result = False

if "claims" not in st.session_state:
    st.session_state.claims = []

# ---- CUSTOM CSS ----
st.markdown("""
<style>

/* Hide Streamlit UI */
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

/* Input fields */
.stTextInput > div > div > input {
    background-color: white !important;
    color: black !important;
    font-size: 18px !important;
    padding: 12px !important;
    border: 2px solid #4da6ff !important;
    border-radius: 10px !important;
}

/* Checklist */
.checklist {
    font-size: 18px;
    margin-bottom: 10px;
}

/* Checkbox color */

input[type="checkbox"] {
    accent-color: #2E8B57 !important;
}

</style>
""", unsafe_allow_html=True)

# ---- TITLE ----
st.markdown("## 🔎 Enter Insurance Name")

# ---- INPUTS ----
insurance = st.text_input("")
hcpcs = st.text_input("Enter HCPCS Code (Optional)")

payer = insurance.lower()
payer_type = "generic"

if "medicare" in payer:
    payer_type = "medicare"

elif "medicaid" in payer or "better health" in payer:
    payer_type = "medicaid"

# ---- LOAD DATA ----
with open("DATA.txt", "r") as file:
    data = file.read()

# ---- HCPCS BODY MAP ----
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

# ---- HCPCS CATEGORY MAP ----

HCPCS_CATEGORIES = {

    "E0114": "MOBILITY_DEVICE",
    "E0143": "MOBILITY_DEVICE",
    "E0149": "MOBILITY_DEVICE",

    "L0172": "CERVICAL_ORTHOSIS",
    "L0174": "CERVICAL_ORTHOSIS",

    "L0621": "ABDOMINAL_BINDER",

    "L1620": "HIP_ORTHOSIS",

    "L1820": "KNEE_ORTHOSIS",
    "L1830": "KNEE_ORTHOSIS",
    "L1833": "KNEE_ORTHOSIS",

    "L1902": "ANKLE_ORTHOSIS",

    "L3260": "POST_OP_SHOE",

    "L3670": "SHOULDER_ORTHOSIS",

    "L3809": "WRIST_HAND_ORTHOSIS",
    "L3908": "WRIST_HAND_ORTHOSIS",

    "L4361": "WALKER_BOOT",
}

RULES_DB = {

    "medicare": {

        "L0621": {

            "checklist": [
                "Verify lumbar brace documentation",
                "Confirm medical necessity",
                "Check physician signature",
                "Validate HCPCS against delivery receipt"
            ],

            "limitations": [
                "Same or similar device history check required",
                "Frequency limitation may apply"
            ]
        },

        "L1833": {

            "checklist": [
                "Verify knee orthosis documentation",
                "Check referring physician details",
                "Validate Dx supports knee instability",
                "Confirm delivery receipt signature"
            ],

            "limitations": [
                "Prior authorization may apply",
                "Check same/similar history"
            ]
        }
    }
}
# ---- BODY PART ANATOMY IMAGES ----

bodypart_images = {

    # ---- KNEE ----

    "L1820": "images/knee.jpg",
    "L1830": "images/knee.jpg",
    "L1833": "images/knee.jpg",

    # ---- LUMBAR SPINE ----

    "L0621": "images/lumbar.jpg",

    # ---- ANKLE / FOOT ----

    "L1902": "images/ankle.jpg",
    "L4361": "images/ankle.jpg",

    # ---- WRIST / HAND ----

    "L3809": "images/wrist.jpg",
    "L3908": "images/wrist.jpg",

    # ---- SHOULDER ----

    "L3670": "images/shoulder.jpg"
}
HCPCS_EXCLUSIONS = {

    # ---- KNEE ORTHOSIS ----

    "L1820": [

        "For Abdominal Binders use 'CG'.",

        "For CO-prefab use ONLY 'KX'.",

        "For Walker/Wheelchair/Crutches/HO-Prefab 'NU & KX'."
    ],

    "L1830": [

        "For Abdominal Binders use 'CG'.",

        "For CO-prefab use ONLY 'KX'.",

        "For Walker/Wheelchair/Crutches/HO-Prefab 'NU & KX'."
    ],

    "L1833": [

        "For Abdominal Binders use 'CG'.",

        "For CO-prefab use ONLY 'KX'.",

        "For Walker/Wheelchair/Crutches/HO-Prefab 'NU & KX'."
    ],

    # ---- ABDOMINAL BINDER ----

    "L0621": [

        "Modifiers only 'LT|RT & KX'.",

        "For CO-prefab use ONLY 'KX'.",

        "For Walker/Wheelchair/Crutches/HO-Prefab 'NU & KX'.",

        "Split as necessary."
    ],

    # ---- MOBILITY DEVICES ----

    "E0114": [

        "Modifiers only 'LT|RT & KX'.",

        "For Abdominal Binders use 'CG'.",

        "For CO-prefab use ONLY 'KX'."
    ],

    "E0143": [

        "Modifiers only 'LT|RT & KX'.",

        "For Abdominal Binders use 'CG'.",

        "For CO-prefab use ONLY 'KX'."
    ],

    "E0149": [

        "Modifiers only 'LT|RT & KX'.",

        "For Abdominal Binders use 'CG'.",

        "For CO-prefab use ONLY 'KX'."
    ],

    # ---- WRIST / HAND ----

    "L3809": [

        "For Abdominal Binders use 'CG'.",

        "For CO-prefab use ONLY 'KX'.",

        "For Walker/Wheelchair/Crutches/HO-Prefab 'NU & KX'."
    ],

    "L3908": [

        "For Abdominal Binders use 'CG'.",

        "For CO-prefab use ONLY 'KX'.",

        "For Walker/Wheelchair/Crutches/HO-Prefab 'NU & KX'."
    ],

    # ---- SHOULDER ----

    "L3670": [

        "For Abdominal Binders use 'CG'.",

        "For CO-prefab use ONLY 'KX'.",

        "For Walker/Wheelchair/Crutches/HO-Prefab 'NU & KX'."
    ],

    # ---- ANKLE ----

    "L1902": [

        "For Abdominal Binders use 'CG'.",

        "For CO-prefab use ONLY 'KX'.",

        "For Walker/Wheelchair/Crutches/HO-Prefab 'NU & KX'."
    ],

    # ---- WALKER BOOT ----

    "L4361": [

        "For Abdominal Binders use 'CG'.",

        "For CO-prefab use ONLY 'KX'.",

        "For Walker/Wheelchair/Crutches/HO-Prefab 'NU & KX'."
    ]
}

LIMITATIONS_RULES = {

    ("AETNA MEDICARE", "L1833"): {
        "limitation": "1 device per 3–5 years",
        "exclusion": "Not covered for mild OA without instability",
        "documentation": "Physician notes of instability, SWO, face-to-face"
    },

    ("CGS MEDICARE", "L1833"): {
        "limitation": "Ambulatory patients only; replacement if lost/stolen/damaged",
        "exclusion": "Excluded if billed incorrectly (OTS vs custom)",
        "documentation": "Face-to-face encounter, SWO, instability documentation"
    },

    ("AETNA (14079)", "L1833"): {
        "limitation": "1 per 3 years",
        "exclusion": "Not covered for preventive/postural use",
        "documentation": "Chart notes of ligament laxity or instability"
    },

    ("AETNA BETTER HEALTH", "L1833"): {
        "limitation": "Limited to medically necessary cases",
        "exclusion": "Excluded if used for mild pain only",
        "documentation": "Requires physician documentation of instability"
    },

    ("BCBS", "L1833"): {
        "limitation": "1 device per 5 years",
        "exclusion": "Excluded for preventive use",
        "documentation": "Medical necessity documentation, instability proof"
    },

    ("AETNA MEDICARE", "L0621"): {
    "limitation": "1 device per 5 years",
    "exclusion": "Excluded if elastic/fabric only",
    "documentation": "SWO, proof of delivery, spinal weakness documentation"
},

("CGS MEDICARE", "L0621"): {
    "limitation": "Ambulatory patients only",
    "exclusion": "Excluded if not rigid/semi-rigid",
    "documentation": "Face-to-face encounter, SWO, spinal weakness"
},

("AETNA MEDICARE", "L3908"): {
    "limitation": "1 brace per affected side within useful lifetime",
    "exclusion": "Excluded for comfort/support use only",
    "documentation": "Wrist injury documentation, SWO, physician notes"
},

("AETNA MEDICARE", "L4361"): {
    "limitation": "Coverage limited to ambulatory necessity",
    "exclusion": "Excluded for mild sprain without instability",
    "documentation": "Ankle injury documentation, SWO, proof of ambulation difficulty"
},

("AETNA MEDICARE", "L1902"): {
    "limitation": "1 brace per affected extremity",
    "exclusion": "Excluded for preventive athletic use",
    "documentation": "Ankle instability findings, SWO, physician documentation"
},

("AETNA MEDICARE", "L3670"): {
    "limitation": "Coverage limited to injury/post-operative use",
    "exclusion": "Excluded for temporary discomfort only",
    "documentation": "Shoulder injury documentation, treatment plan, SWO"
}

}
# ---- FUNCTION ----
def get_section(insurance_name, raw_data):

    insurance_name = insurance_name.strip().upper()

    sections = raw_data.split("---")

    for section in sections:

        lines = section.strip().split("\n")

        if not lines:
            continue

        header = lines[0].strip()

        if header.startswith("[") and header.endswith("]"):

            section_name = header[1:-1].strip().upper()

            if section_name == insurance_name:
                return "\n".join(lines[1:])

    return None

# ---- BUTTON ----
if st.button("📌 Generate Checklist"):
    st.session_state.show_result = True

# ---- MAIN LOGIC ----
if st.session_state.show_result:

    section = get_section(insurance, data)

    col1, col2 = st.columns([2, 1])

    if section:

        with col1:

            # ---- CHECKBOXES ----
            st.markdown("### ✅ Pre-Submission Checks")

            hcpcs_match = st.checkbox(
                "HCPCS matches Delivery Receipt"
            )

            dx_match = st.checkbox(
                "Dx code matches"
            )

            eligibility_ok = st.checkbox(
                "Eligibility verified"
            )

            signature_present = st.checkbox(
                "Signature present on Delivery Receipt"
            )

            physician_info = st.checkbox(
                "Referring physician info present"
            )

            charges_valid = st.checkbox(
                "Charges and Allowable not zero"
            )

            # ---- FAILURE LOGIC ----
            failures = []

            if payer_type == "medicare" and not eligibility_ok:
                failures.append(
                    "Medicare eligibility critical check failed"
                )

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

           
            # ---- DENIAL INSIGHT ----
            if failures:

                st.markdown(
                    "### ⚠️ Likely Denial Reason"
                )

                if (
                    "Missing signature" in failures
                    and
                    "Eligibility not verified" in failures
                ):
                    st.warning(
                        "High denial risk due to missing signature and eligibility not verified"
                    )

                elif "Missing signature" in failures:
                    st.warning(
                        "Claim may be denied due to missing patient/representative signature"
                    )

                elif "Eligibility not verified" in failures:
                    st.warning(
                        "Claim may be denied due to eligibility not verified"
                    )

                elif "HCPCS mismatch" in failures:
                    st.warning(
                        "Incorrect HCPCS may lead to denial or rework"
                    )

                elif "Invalid charges/allowable" in failures:
                    st.warning(
                        "Incorrect charge/allowable may result in rejection or underpayment"
                    )

            # ---- ISSUES ----
            if failures:

                st.markdown("**Issues found:**")

                for f in failures:
                    st.write(f"- {f}")

                st.markdown(
                    "### 🔧 Recommended Actions"
                )

                if "HCPCS mismatch" in failures:
                    st.write(
                        "- Verify HCPCS against Delivery Receipt and Charge Entry"
                    )

                if "Dx code mismatch" in failures:
                    st.write(
                        "- Cross-check Dx codes for accuracy and laterality"
                    )

                if "Eligibility not verified" in failures:
                    st.write(
                        "- Run eligibility check before submission"
                    )

                if "Missing signature" in failures:
                    st.write(
                        "- Obtain valid patient/representative signature"
                    )

                if "Missing referring physician info" in failures:
                    st.write(
                        "- Update referring physician details before billing"
                    )

                if "Invalid charges/allowable" in failures:
                    st.write(
                        "- Validate charge and allowable amounts"
                    )

                                              # ---- CHECKLIST ----

            st.markdown("---")
            st.markdown("### 📋 Checklist")

            hcpcs_key = hcpcs.strip().upper()

            exclude_terms = HCPCS_EXCLUSIONS.get(
                hcpcs_key,
                []
            )

            checklist_lines = []

            for line in section.split("\n"):

                clean_line = line.strip()

                if not clean_line:
                    continue

                if "aetna" in clean_line.lower():
                    continue

                if "-----" in clean_line:
                    continue

                if clean_line in exclude_terms:
                    continue

                checklist_lines.append(clean_line)

            for item in checklist_lines:

                st.markdown(
                    f"<div class='checklist'>✅ {item}</div>",
                    unsafe_allow_html=True
                )
        # ---- DEVICE IMAGE ----

        if hcpcs:

            code = hcpcs.strip().upper()

            image_path = f"images/{code}.jpg"

            if os.path.exists(image_path):

                with col2:

                    if code in hcpcs_data:

                        st.markdown(
                            f"🦴 Affected Area: {hcpcs_data[code]['body']}"
                        )

                    st.markdown(
                        f"🩺 Device ({code})"
                    )

                    st.image(
                        image_path,
                        use_column_width=True
                    )

                    if code in bodypart_images:
                        st.markdown(
                            "🦴 Anatomy Reference"
                        )
                      
                    st.image(
                        bodypart_images[code],
                        use_column_width=True
                        )

    else:

        st.error("Insurance not found")
    
# ---- COVERAGE INTELLIGENCE PANEL ----

if hcpcs and insurance:

    insurance_key = insurance.strip().upper()
    hcpcs_key = hcpcs.strip().upper()

    rule_data = LIMITATIONS_RULES.get(
        (insurance_key, hcpcs_key)
    )

    if rule_data:

        st.sidebar.markdown("---")

        st.sidebar.markdown("## 🧠 Payer Rules & Coverage Intelligence")

        st.sidebar.warning(
            f"Limitation:\n\n{rule_data['limitation']}"
        )

        st.sidebar.error(
            f"Exclusion:\n\n{rule_data['exclusion']}"
        )

        st.sidebar.info(
            f"Documentation:\n\n{rule_data['documentation']}"
        )
