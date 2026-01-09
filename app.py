import streamlit as st
import google.generativeai as genai
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 1. SETTINGS & AI SETUP ---
st.set_page_config(page_title="COOL FINDS", layout="centered")

# Configure AI 
# Note: It is safer to use st.secrets for keys, but keeping your logic intact:
API_KEY = "AIzaSyDw5eJnSEGvmqdLBFQSGlldGID0B2dJoTs"
genai.configure(api_key="AIzaSyAfWcgLLddabW2NbiXPhEtk2xorDg1DwZs")
model = genai.GenerativeModel('gemini-2.5-flash')

# --- EMAIL HELPER FUNCTION ---
def send_real_email(sender_email, sender_password, receiver_emails, subject, body):
    port = 587  # For starttls
    smtp_server = "smtp.gmail.com"
    
    # Create the email header
    message = MIMEMultipart()
    message["From"] = sender_email
    message["Subject"] = subject
    
    # Add body to email
    message.attach(MIMEText(body, "plain"))
    
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            server.login(sender_email, sender_password)
            
            # Split comma separated emails and send
            recipients = [email.strip() for email in receiver_emails.split(",")]
            for recipient in recipients:
                server.sendmail(sender_email, recipient, message.as_string())
        return True
    except Exception as e:
        st.error(f"Email Error: {e}")
        return False

# --- 2. SESSION STATE INITIALIZATION ---
if 'page' not in st.session_state: st.session_state.page = 1
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'doc_content' not in st.session_state: st.session_state.doc_content = ""
if 'mail_list' not in st.session_state: st.session_state.mail_list = ""

# --- 3. LEGAL TEMPLATES DATA ---
TEMPLATES = {
    "Property": "IN THE COURT OF THE CIVIL JUDGE...\nSuit for Recovery of Possession...\nThe plaintiff is the lawful owner of...",
    "Family": "BEFORE THE HONORABLE FAMILY COURT...\nPetition for Dissolution of Marriage...\nUnder Section 13 of the Hindu Marriage Act...",
    "Labor": "REPRESENTATION BEFORE THE LABOR COMMISSIONER...\nSubject: Unlawful termination of services...",
    "Contract": "LEGAL NOTICE\nRegarding Breach of Agreement dated [Date]...\nDemand for specific performance...",
    "Bail": "IN THE COURT OF SESSIONS...\nApplication for Regular Bail under Section 439 CrPC...\nCrime No: [No]...",
    "Cyber Crime": "TO THE SUPERINTENDENT OF POLICE (CYBER CELL)...\nComplaint regarding unauthorized data access...",
    "Fraud": "COMPLAINT UNDER SECTION 138 OF NI ACT...\nRegarding dishonor of Cheque No: [No]...",
    "Homicide": "MEMORANDUM OF EVIDENCE...\nCase State vs [Name]... Analysis of Section 302 IPC..."
}

# --- 4. GLOBAL STYLING ---
BG_URL = "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?q=80&w=1920"
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('{BG_URL}');
        background-size: cover;
        background-attachment: fixed;
    }}
    .title-text {{
        color: #D4AF37;
        font-family: 'Times New Roman', serif;
        font-size: 55px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0px;
    }}
    .glass-card {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid #D4AF37;
        padding: 25px;
        border-radius: 15px;
        color: white;
    }}
    label {{ color: #D4AF37 !important; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# Sidebar for Email Configuration
with st.sidebar:
    st.header("✉️ Email Settings")
    st.info("Use a Gmail 'App Password' for security.")
    sender_mail = st.text_input("Your Gmail", placeholder="example@gmail.com")
    sender_pass = st.text_input("App Password", type="password")

st.markdown('<p class="title-text">COOL FINDS</p>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:white;'>ADVOCATE MANAGEMENT PORTAL</p><hr>", unsafe_allow_html=True)

# --- PAGE 1: REGISTRATION ---
if st.session_state.page == 1:
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("⚖️ Advocate Registration")
        with st.form("reg_form"):
            name = st.text_input("Advocate Name", placeholder="Enter your full name")
            contact = st.text_input("Contact No")
            enroll = st.text_input("Enrollment ID")
            email = st.text_input("Email ID")
            if st.form_submit_button("Proceed to Dashboard →", use_container_width=True):
                if name and contact and enroll and email:
                    st.session_state.user_name = name
                    st.session_state.page = 2
                    st.rerun()
                else:
                    st.error("⚠️ All fields are mandatory.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- PAGE 2: CASE & DOCUMENT ---
elif st.session_state.page == 2:
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader(f"📂 Case Management: Adv. {st.session_state.get('user_name', '')}")
        
        category = st.radio("Legal Category", ["Civil", "Criminal"], horizontal=True)
        options = ["Property", "Family", "Labor", "Contract"] if category == "Civil" else ["Bail", "Cyber Crime", "Fraud", "Homicide"]
        sub_cat = st.selectbox("Select Case Type", options)

        # Refer Document Button
        if st.button("📑 Refer Document Template"):
            st.session_state.doc_content = TEMPLATES.get(sub_cat, "Template not found.")
            st.info(f"Loaded {sub_cat} template below.")

        doc_text = st.text_area("Document Content", value=st.session_state.doc_content, height=200)
        st.session_state.doc_content = doc_text
        
        mail_input = st.text_area("Recipient Emails (comma separated)", value=st.session_state.mail_list, placeholder="client1@mail.com, client2@mail.com")
        st.session_state.mail_list = mail_input

        col_back, col_submit, col_next = st.columns(3)
        with col_back:
            if st.button("← Back"):
                st.session_state.page = 1
                st.rerun()
        with col_submit:
            if st.button("Submit & Send", type="primary"):
                if not sender_mail or not sender_pass:
                    st.warning("⚠️ Please configure your Email and App Password in the sidebar.")
                elif doc_text and mail_input:
                    with st.spinner("Sending emails..."):
                        success = send_real_email(
                            sender_mail, 
                            sender_pass, 
                            mail_input, 
                            f"Legal Document: {sub_cat}", 
                            doc_text
                        )
                        if success:
                            count = len([m for m in mail_input.split(",") if m.strip()])
                            st.success(f"✅ Document successfully sent to {count} recipient(s)!")
                else:
                    st.warning("Fields missing (Document or Recipient).")
        with col_next:
            if st.button("AI Chatbot →"):
                st.session_state.page = 3
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- PAGE 3: CHATBOT ---
elif st.session_state.page == 3:
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🤖 Legal AI Assistant")
        
        # Display chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if prompt := st.chat_input("Ask a legal question..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            try:
                response = model.generate_content(f"You are a professional Indian lawyer. Answer: {prompt}")
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
            except Exception:
                st.session_state.chat_history.append({"role": "assistant", "content": "AI error. Check API key."})
            st.rerun()
        
        if st.button("← Return to Dashboard", use_container_width=True):
            st.session_state.page = 2
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)