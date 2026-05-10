import streamlit as st
import pandas as pd
import os

# ---- LOGIN SYSTEM ----
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:

    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if (
            username == st.secrets["username"]
            and password == st.secrets["password"]
        ):
            st.session_state.authenticated = True
            st.success("Login successful")
            st.rerun()

        else:
            st.error("Invalid credentials")

    st.stop()

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

</style>
""", unsafe_allow_html=True)

# ---- TITLE ----
st.markdown("## 🔎 Enter Insurance Name")

# ---- INPUTS ----
insurance = st.text_input("")
hcpcs = st.text_input("Enter HCPCS Code (Optional)")
claim_id = st.text_input("Enter Claim Number (Optional)")

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

HCPCS_EXCLUSIONS = {

    "L1833": [

        "For Abdominal Binders use 'CG'.",

        "For CO-prefab use ONLY 'KX'.",

        "For Walker/Wheelchair/Crutches/HO-Prefab 'NU & KX'."
    ],
    
    "L0621": [
    "For CO-prefab use ONLY 'KX'.",
    "For Walker/Wheelchair/Crutches/HO-Prefab 'NU & KX'."
    ]
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

            # ---- RISK SCORE ----
            st.markdown("---")

            total_checks = 6
            failed_checks = len(failures)

            risk_score = int(
                (failed_checks / total_checks) * 100
            )

            st.markdown(
                f"### 📊 Risk Score: {risk_score}/100"
            )

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

            # ---- SUBMIT BUTTON ----
            if st.button("📌 Mark as Submitted"):

                if claim_id:

                    st.session_state.claims.append({
                        "claim_id": claim_id,
                        "insurance": insurance,
                        "hcpcs": hcpcs,
                        "risk": risk_score,
                        "status": "Submitted"
                    })

                    st.success(
                        "Claim recorded successfully"
                    )

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

                    st.markdown(
                        "🦴 Human Skeleton"
                    )

                    st.image(
                        "images/skeleton.jpg",
                        use_column_width=True
                    )

    else:

        st.error("Insurance not found")
    
# ---- CLAIM SUMMARY ----
if st.session_state.claims:

    df_claims = pd.DataFrame(
        st.session_state.claims
    )

    st.sidebar.markdown("---")

    st.sidebar.markdown(
        "## 🧾 Claims Operations Panel"
    )

    st.sidebar.write(
        f"Total Claims Submitted: {len(st.session_state.claims)}"
    )

    avg_risk = df_claims["risk"].mean()

    st.sidebar.write(
        f"Average Risk Score: {avg_risk:.1f}/100"
    )

    for c in st.session_state.claims:

        if c["risk"] <= 15:
            icon = "🟢"

        elif c["risk"] <= 40:
            icon = "🟡"

        else:
            icon = "🔴"

        st.sidebar.write(
            f"{icon} Claim #{c['claim_id']} | Risk: {c['risk']}/100"
        )

    csv = df_claims.to_csv(
        index=False
    ).encode("utf-8")

    st.sidebar.download_button(
        label="📥 Export Claims to CSV",
        data=csv,
        file_name="submitted_claims.csv",
        mime="text/csv"
    )
