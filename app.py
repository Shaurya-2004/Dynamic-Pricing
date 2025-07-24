import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import io
import os
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# LangChain and Groq imports
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Modern Dark Theme CSS with Advanced Animations
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

:root {
    --primary-color: #00d4ff;
    --primary-dark: #0099cc;
    --secondary-color: #1a1a2e;
    --accent-color: #ff6b35;
    --success-color: #00ff88;
    --text-primary: #ffffff;
    --text-secondary: #b0b3b8;
    --bg-primary: #0f0f23;
    --bg-secondary: #16213e;
    --bg-tertiary: #1a1a2e;
    --border-color: #2d3748;
    --glass-bg: rgba(255, 255, 255, 0.05);
    --glass-border: rgba(255, 255, 255, 0.1);
    --shadow-neon: 0 0 20px rgba(0, 212, 255, 0.3);
    --shadow-orange: 0 0 20px rgba(255, 107, 53, 0.3);
    --shadow-green: 0 0 20px rgba(0, 255, 136, 0.3);
}

* {
    font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

/* Main app background */
.main .block-container {
    padding: 2rem 1rem;
    max-width: 1200px;
    background: transparent;
}

/* Animated dark background with floating particles */
body, .stApp {
    background: linear-gradient(135deg, #0f0f23 0%, #16213e 35%, #1a1a2e 100%);
    min-height: 100vh;
    position: relative;
    overflow-x: hidden;
}

/* Floating particles animation */
body::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: 
        radial-gradient(2px 2px at 20px 30px, rgba(0, 212, 255, 0.3), transparent),
        radial-gradient(2px 2px at 40px 70px, rgba(255, 107, 53, 0.3), transparent),
        radial-gradient(1px 1px at 90px 40px, rgba(0, 255, 136, 0.3), transparent),
        radial-gradient(1px 1px at 130px 80px, rgba(0, 212, 255, 0.2), transparent),
        radial-gradient(2px 2px at 160px 30px, rgba(255, 107, 53, 0.2), transparent);
    background-repeat: repeat;
    background-size: 200px 100px;
    animation: particleFloat 20s linear infinite;
    pointer-events: none;
    z-index: -1;
}

@keyframes particleFloat {
    0% { transform: translateY(0px) translateX(0px); }
    33% { transform: translateY(-20px) translateX(10px); }
    66% { transform: translateY(-10px) translateX(-10px); }
    100% { transform: translateY(0px) translateX(0px); }
}

/* Glass morphism navbar */
.navbar {
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 1.5rem 2rem;
    margin-bottom: 2rem;
    border: 1px solid var(--glass-border);
    box-shadow: var(--shadow-neon);
    animation: glassSlideDown 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.navbar::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.1), transparent);
    animation: shimmer 3s infinite;
}

@keyframes shimmer {
    0% { left: -100%; }
    100% { left: 100%; }
}

@keyframes glassSlideDown {
    from {
        transform: translateY(-100px) scale(0.9);
        opacity: 0;
    }
    to {
        transform: translateY(0) scale(1);
        opacity: 1;
    }
}

.navbar button {
    color: var(--text-primary);
    padding: 1rem 1.5rem;
    font-weight: 500;
    border-radius: 15px;
    margin-right: 1rem;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    border: none;
    background: transparent;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.navbar button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, var(--primary-color), transparent);
    transition: all 0.4s ease;
    opacity: 0;
}

.navbar button:hover {
    background: var(--glass-bg);
    color: var(--primary-color);
    transform: translateY(-3px) scale(1.05);
    box-shadow: var(--shadow-neon);
    border: 1px solid var(--primary-color);
}

.navbar button:hover::before {
    left: 100%;
    opacity: 0.3;
}

.navbar button:active {
    transform: translateY(-1px) scale(1.02);
}

/* Enhanced glass morphism cards */
.metric-card {
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 25px;
    padding: 2rem;
    margin: 1.5rem 0;
    border: 1px solid var(--glass-border);
    box-shadow: var(--shadow-neon);
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    animation: cardFloatIn 0.8s ease-out;
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--primary-color), var(--accent-color), var(--success-color));
    animation: gradientShift 3s ease-in-out infinite;
}

@keyframes gradientShift {
    0%, 100% { transform: translateX(-100%); }
    50% { transform: translateX(100%); }
}

@keyframes cardFloatIn {
    from {
        transform: translateY(50px) rotateX(10deg);
        opacity: 0;
    }
    to {
        transform: translateY(0) rotateX(0deg);
        opacity: 1;
    }
}

.metric-card:hover {
    transform: translateY(-10px) scale(1.02);
    box-shadow: var(--shadow-neon), 0 25px 50px rgba(0, 0, 0, 0.3);
    border-color: var(--primary-color);
}

/* Neon buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
    color: var(--bg-primary);
    border: none;
    padding: 1rem 2.5rem;
    border-radius: 15px;
    font-weight: 600;
    font-size: 0.9rem;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: var(--shadow-neon);
    position: relative;
    overflow: hidden;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.stButton > button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    transition: all 0.4s ease;
}

.stButton > button:hover {
    transform: translateY(-3px) scale(1.05);
    box-shadow: var(--shadow-neon), 0 15px 30px rgba(0, 212, 255, 0.4);
    background: linear-gradient(135deg, var(--accent-color), var(--primary-color));
}

.stButton > button:hover::before {
    left: 100%;
}

.stButton > button:active {
    transform: translateY(-1px) scale(1.02);
}

/* Cyberpunk loading spinner */
.loading-spinner {
    border: 3px solid rgba(0, 212, 255, 0.2);
    border-top: 3px solid var(--primary-color);
    border-radius: 50%;
    width: 30px;
    height: 30px;
    animation: cyberpunkSpin 1s linear infinite;
    margin: 0 auto;
    box-shadow: var(--shadow-neon);
}

@keyframes cyberpunkSpin {
    0% { 
        transform: rotate(0deg);
        box-shadow: var(--shadow-neon);
    }
    50% { 
        box-shadow: var(--shadow-orange);
    }
    100% { 
        transform: rotate(360deg);
        box-shadow: var(--shadow-neon);
    }
}

/* Enhanced form inputs */
.stTextInput > div > div > input,
.stSelectbox > div > div > select {
    border-radius: 15px;
    border: 2px solid var(--border-color);
    padding: 1rem 1.5rem;
    transition: all 0.4s ease;
    background: var(--glass-bg);
    color: var(--text-primary);
    backdrop-filter: blur(10px);
    font-size: 1rem;
}

.stTextInput > div > div > input::placeholder {
    color: var(--text-secondary);
}

.stTextInput > div > div > input:focus,
.stSelectbox > div > div > select:focus {
    border-color: var(--primary-color);
    box-shadow: var(--shadow-neon);
    transform: translateY(-2px) scale(1.02);
    background: rgba(0, 212, 255, 0.05);
}

/* Glowing text animations */
h1, h2, h3 {
    color: var(--text-primary);
    font-weight: 700;
    animation: textGlow 0.8s ease-out;
    text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
}

@keyframes textGlow {
    from {
        transform: translateY(-20px);
        opacity: 0;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.8);
    }
    to {
        transform: translateY(0);
        opacity: 1;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
    }
}

/* Status messages with neon effects */
.stSuccess, .stError, .stInfo {
    border-radius: 15px;
    animation: neonSlideIn 0.6s ease-out;
    backdrop-filter: blur(10px);
}

.stSuccess {
    box-shadow: var(--shadow-green);
    border-left: 4px solid var(--success-color);
}

.stError {
    box-shadow: var(--shadow-orange);
    border-left: 4px solid var(--accent-color);
}

@keyframes neonSlideIn {
    from {
        transform: translateX(100px) scale(0.8);
        opacity: 0;
    }
    to {
        transform: translateX(0) scale(1);
        opacity: 1;
    }
}

/* Chat messages with holographic effect */
.chat-message {
    background: var(--glass-bg);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    padding: 1.5rem 2rem;
    margin: 1rem 0;
    animation: hologramAppear 0.6s ease-out;
    border-left: 4px solid var(--primary-color);
    box-shadow: var(--shadow-neon);
    position: relative;
    overflow: hidden;
}

.chat-message::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.1), transparent);
    animation: holographicSweep 2s infinite;
}

@keyframes holographicSweep {
    0% { left: -100%; }
    100% { left: 100%; }
}

@keyframes hologramAppear {
    from {
        transform: scale(0.8) rotateY(10deg);
        opacity: 0;
    }
    to {
        transform: scale(1) rotateY(0deg);
        opacity: 1;
    }
}

/* Data tables with cyber styling */
.dataframe {
    border-radius: 15px;
    overflow: hidden;
    box-shadow: var(--shadow-neon);
    animation: dataMatrixLoad 0.8s ease-out;
    background: var(--glass-bg);
    backdrop-filter: blur(10px);
}

@keyframes dataMatrixLoad {
    from { 
        opacity: 0;
        transform: scale(0.9);
    }
    to { 
        opacity: 1;
        transform: scale(1);
    }
}

/* Futuristic auth container */
.auth-container {
    max-width: 450px;
    margin: 2rem auto;
    background: var(--glass-bg);
    backdrop-filter: blur(25px);
    border-radius: 30px;
    padding: 3rem;
    box-shadow: var(--shadow-neon), 0 25px 50px rgba(0, 0, 0, 0.3);
    border: 1px solid var(--glass-border);
    animation: authPortalOpen 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.auth-container::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: conic-gradient(from 0deg, transparent, var(--primary-color), transparent, var(--accent-color), transparent);
    animation: portalRotate 4s linear infinite;
    opacity: 0.1;
}

@keyframes portalRotate {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes authPortalOpen {
    from {
        transform: scale(0.5) rotateY(90deg);
        opacity: 0;
    }
    to {
        transform: scale(1) rotateY(0deg);
        opacity: 1;
    }
}

/* Enhanced stat boxes */
.stat-box {
    background: var(--glass-bg);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    padding: 2rem 1.5rem;
    text-align: center;
    margin: 0.75rem;
    min-height: 140px;
    min-width: 200px;
    box-shadow: var(--shadow-neon);
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    animation: statPulseIn 0.8s ease-out;
    border: 1px solid var(--glass-border);
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.stat-box::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
    animation: energyFlow 2s ease-in-out infinite;
}

@keyframes energyFlow {
    0%, 100% { transform: scaleX(0); }
    50% { transform: scaleX(1); }
}

@keyframes statPulseIn {
    0% {
        transform: scale(0.3) rotateZ(-10deg);
        opacity: 0;
    }
    50% {
        transform: scale(1.1) rotateZ(5deg);
    }
    100% {
        transform: scale(1) rotateZ(0deg);
        opacity: 1;
    }
}

.stat-box:hover {
    transform: translateY(-8px) scale(1.05);
    box-shadow: var(--shadow-neon), 0 20px 40px rgba(0, 212, 255, 0.2);
    border-color: var(--primary-color);
}

/* Quantum pulse animation for important elements */
.pulse {
    animation: quantumPulse 3s infinite;
}

@keyframes quantumPulse {
    0%, 100% {
        transform: scale(1);
        box-shadow: var(--shadow-neon);
    }
    25% {
        transform: scale(1.02);
        box-shadow: var(--shadow-orange);
    }
    50% {
        transform: scale(1.05);
        box-shadow: var(--shadow-green);
    }
    75% {
        transform: scale(1.02);
        box-shadow: var(--shadow-orange);
    }
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
    background: var(--primary-color);
    border-radius: 4px;
    box-shadow: 0 0 5px rgba(0, 212, 255, 0.5);
}

::-webkit-scrollbar-thumb:hover {
    background: var(--accent-color);
    box-shadow: 0 0 10px rgba(255, 107, 53, 0.5);
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {visibility: hidden;}

/* Override Streamlit's default dark theme */
.stApp > header {
    background-color: transparent;
}

.stApp {
    color: var(--text-primary);
}

/* Custom cyberpunk glow for titles */
.cyber-title {
    background: linear-gradient(45deg, var(--primary-color), var(--accent-color), var(--success-color));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: titleGlow 2s ease-in-out infinite alternate;
}

@keyframes titleGlow {
    from {
        filter: drop-shadow(0 0 5px rgba(0, 212, 255, 0.5));
    }
    to {
        filter: drop-shadow(0 0 15px rgba(255, 107, 53, 0.8));
    }
}
</style>
""", unsafe_allow_html=True)

# DB setup
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
''')
c.execute('''
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT,
    response TEXT
)
''')
conn.commit()

# LangChain/Groq Setup
if "groq_chat_model" not in st.session_state:
    try:
        st.session_state.groq_chat_model = ChatGroq(temperature=0, groq_api_key=GROQ_API_KEY, model_name="llama3-8b-8192")
    except Exception as e:
        st.error(f"Failed to initialize Groq model. Make sure GROQ_API_KEY is set correctly. Error: {e}")
        st.session_state.groq_chat_model = None

if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = ConversationBufferMemory(return_messages=True)

# Prompt template for the chatbot
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an AI Assistant for a dynamic pricing dashboard.
            You can answer questions about product prices, quantities, sales, revenue, and profit margins.
            Provide concise and helpful answers based on typical business data.
            If the question is outside these topics, politely redirect the user to ask about business metrics."""
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

# Utils
def create_user(username, password):
    password_hash = generate_password_hash(password)
    try:
        c.execute('INSERT INTO users (username, password_hash) VALUES (?,?)', (username, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def check_user(username, password):
    c.execute('SELECT id, password_hash FROM users WHERE username=?', (username,))
    user = c.fetchone()
    if user and check_password_hash(user[1], password):
        return user[0]
    return None

def save_chat(user_id, msg, response):
    c.execute('INSERT INTO chat_history (user_id, message, response) VALUES (?,?,?)', (user_id, msg, response))
    conn.commit()

def get_history(user_id):
    c.execute('SELECT message, response FROM chat_history WHERE user_id=?', (user_id,))
    return c.fetchall()

# Session state initialization
if 'page' not in st.session_state:
    st.session_state.page = 'login'

if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# Update session state page based on query params only on initial load
if 'init_page_set' not in st.session_state:
    query_page = st.query_params.get('page')
    if query_page in ['overview', 'chatbot', 'history', 'logout', 'login', 'signup']:
        st.session_state.page = query_page
    st.session_state.init_page_set = True

# Enhanced sidebar navigation with better positioning
def show_navbar():
    # Sidebar navigation instead of top navbar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 class="cyber-title" style="font-size: 1.5rem;">🎯 NEURAL NAV</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation buttons in sidebar
        if st.button("📊 Dashboard Overview", key="nav_overview", use_container_width=True):
            st.session_state.page = 'overview'
            st.rerun()
            
        if st.button("🤖 AI Assistant", key="nav_chatbot", use_container_width=True):
            st.session_state.page = 'chatbot'
            st.rerun()
            
        if st.button("📜 Conversation Logs", key="nav_history", use_container_width=True):
            st.session_state.page = 'history'
            st.rerun()
            
        st.markdown("---")
        
        # View selector in sidebar
        if 'view_mode' not in st.session_state:
            st.session_state.view_mode = "Complete Overview"
            
        st.session_state.view_mode = st.radio(
            "🔍 Choose Display Mode:",
            ["Complete Overview", "Analytics Focus", "Data Management", "AI Analysis"],
            key="view_selector"
        )
        
        # Chart display options
        st.markdown("### 📊 Chart Controls")
        show_price_chart = st.checkbox("Price Distribution", value=True, key="show_price")
        show_quantity_chart = st.checkbox("Quantity Analysis", value=True, key="show_quantity")
        show_margin_chart = st.checkbox("Margin Insights", value=False, key="show_margin")
        
        st.markdown("---")
        
        # Logout at bottom of sidebar
        if st.button("🚪 Secure Logout", key="nav_logout", use_container_width=True):
            st.session_state.page = 'logout'
            st.rerun()

# Enhanced login page
def login_page():
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem; position: relative; z-index: 1;">
        <h1 class="cyber-title" style="font-size: 3rem; margin-bottom: 0.5rem;">🔐</h1>
        <h2 class="cyber-title" style="margin-bottom: 0.5rem;">NEURAL ACCESS</h2>
        <p style="color: var(--text-secondary);">Initialize secure connection</p>
    </div>
    """, unsafe_allow_html=True)

    username = st.text_input("Username", placeholder="Enter neural ID", key="login_username")
    password = st.text_input("Password", type="password", placeholder="Enter access key", key="login_password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 CONNECT", use_container_width=True, key="login_button_main"):
            if username and password:
                user_id = check_user(username, password)
                if user_id:
                    st.session_state.user_id = user_id
                    st.session_state.page = 'overview'
                    st.success("Neural link established! 🎉")
                    st.rerun() # Force rerun to navigate to dashboard
                else:
                    st.error("Access denied ❌")
            else:
                st.warning("Please complete neural authentication")

    with col2:
        if st.button("📝 REGISTER", use_container_width=True, key="signup_button_redirect"):
            st.session_state.page = 'signup'
            st.rerun() # Force rerun to navigate to signup

    st.markdown('</div>', unsafe_allow_html=True)

# Enhanced signup page
def signup_page():
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem; position: relative; z-index: 1;">
        <h1 class="cyber-title" style="font-size: 3rem; margin-bottom: 0.5rem;">📝</h1>
        <h2 class="cyber-title" style="margin-bottom: 0.5rem;">NEURAL REGISTRATION</h2>
        <p style="color: var(--text-secondary);">Create new digital identity</p>
    </div>
    """, unsafe_allow_html=True)

    username = st.text_input("Neural ID", placeholder="Choose unique identifier", key="signup_username")
    password = st.text_input("Access Key", type="password", placeholder="Create secure passphrase", key="signup_password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎯 INITIALIZE", use_container_width=True, key="create_account_button"):
            if username and password:
                if len(password) >= 6:
                    if create_user(username, password):
                        st.success("Neural profile created! 🎉")
                        st.session_state.page = 'login'
                        st.balloons()
                        st.rerun() # Force rerun to navigate to login
                    else:
                        st.error("Neural ID already exists ❌")
                else:
                    st.warning("Access key must be at least 6 characters")
            else:
                st.warning("Please complete all neural parameters")

    with col2:
        if st.button("🔙 RETURN", use_container_width=True, key="back_to_login_button"):
            st.session_state.page = 'login'
            st.rerun() # Force rerun to navigate to login

    st.markdown('</div>', unsafe_allow_html=True)

# Enhanced overview page with completely restructured layout
def overview_page():
    show_navbar()

    # Hero section - more compact
    st.markdown("""
    <div class="metric-card pulse" style="text-align: center; margin-bottom: 1.5rem; padding: 1.5rem;">
        <h1 class="cyber-title" style="font-size: 2.8rem; margin-bottom: 0.3rem;">🧪 QUANTUM PRICING NEXUS</h1>
        <p style="font-size: 1rem; color: var(--text-secondary);">Advanced Neural Network Pricing Analytics</p>
    </div>
    """, unsafe_allow_html=True)

    # Sample data (since we don't have the actual file)
    @st.cache_data
    def load_data():
        # Generate sample data for demonstration
        np.random.seed(42)
        n_products = 100

        skus = [f"SKU-{1000+i}" for i in range(n_products)]
        quantities = np.random.randint(10, 1000, n_products)
        prices = np.random.uniform(100, 2000, n_products)
        sales = quantities * prices
        costs = prices * np.random.uniform(0.5, 0.8, n_products)

        return pd.DataFrame({
            'sku': skus,
            'total_quantity': quantities,
            'suggested_price': prices,
            'total_sales': sales,
            'cost': costs
        })

    df = load_data()
    df['margin'] = ((df['suggested_price'] - df['cost']) / df['suggested_price'])

    # Column-based layout - Core Layout Change #1
    main_col1, main_col2 = st.columns([2, 1], gap="large")
    
    with main_col1:
        # Left side: Stats and Analytics
        
        # View-based content display - Interactivity Change
        if st.session_state.view_mode == "Complete Overview":
            # Stats in 2x2 grid
            stat_row1_col1, stat_row1_col2 = st.columns(2, gap="medium")
            with stat_row1_col1:
                st.markdown(f"""
                <div class="stat-box">
                    <h3 style="color: var(--primary-color); margin: 0 0 0.5rem 0; font-size: 1.8rem;">📦 {len(df):,}</h3>
                    <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">Neural Products</p>
                </div>
                """, unsafe_allow_html=True)

            with stat_row1_col2:
                total_revenue = df['total_sales'].sum()
                st.markdown(f"""
                <div class="stat-box">
                    <h3 style="color: var(--success-color); margin: 0 0 0.5rem 0; font-size: 1.4rem;">💰 ₹{total_revenue:,.0f}</h3>
                    <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">Quantum Revenue</p>
                </div>
                """, unsafe_allow_html=True)

            stat_row2_col1, stat_row2_col2 = st.columns(2, gap="medium")
            with stat_row2_col1:
                avg_price = df['suggested_price'].mean()
                st.markdown(f"""
                <div class="stat-box">
                    <h3 style="color: var(--accent-color); margin: 0 0 0.5rem 0; font-size: 1.6rem;">📈 ₹{avg_price:.0f}</h3>
                    <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">Neural Price</p>
                </div>
                """, unsafe_allow_html=True)

            with stat_row2_col2:
                avg_margin = df['margin'].mean()
                st.markdown(f"""
                <div class="stat-box">
                    <h3 style="color: var(--primary-color); margin: 0 0 0.5rem 0; font-size: 1.7rem;">📊 {avg_margin:.1%}</h3>
                    <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">Profit Matrix</p>
                </div>
                """, unsafe_allow_html=True)

        elif st.session_state.view_mode == "Analytics Focus":
            # Focus on key metrics only
            analytics_col1, analytics_col2 = st.columns(2, gap="large")
            with analytics_col1:
                total_revenue = df['total_sales'].sum()
                st.metric("💰 Total Revenue", f"₹{total_revenue:,.0f}", delta="12.5%")
            with analytics_col2:
                avg_margin = df['margin'].mean()
                st.metric("📊 Avg Margin", f"{avg_margin:.1%}", delta="2.3%")

        # Charts section with column layout - Layout Change #2
        if st.session_state.view_mode in ["Complete Overview", "Analytics Focus"]:
            st.markdown("### 📊 Performance Analytics")
            
            chart_col1, chart_col2 = st.columns(2, gap="medium")
            
            with chart_col1:
                if st.session_state.get('show_price', True):
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.subheader("💵 Price Distribution")
                    st.bar_chart(df.set_index('sku')['suggested_price'].head(15))
                    st.markdown('</div>', unsafe_allow_html=True)
            
            with chart_col2:
                if st.session_state.get('show_quantity', True):
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.subheader("📦 Quantity Analysis")
                    top10 = df.sort_values('total_quantity', ascending=False).head(15)
                    st.bar_chart(top10.set_index('sku')['total_quantity'])
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Optional third chart
            if st.session_state.get('show_margin', False):
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.subheader("📈 Margin Insights")
                st.bar_chart(df.set_index('sku')['margin'].head(15))
                st.markdown('</div>', unsafe_allow_html=True)

    with main_col2:
        # Right side: Controls and Data Management
        
        # File upload in expander - Structural Change #3
        with st.expander("📂 Upload Neural Dataset", expanded=False):
            uploaded_file = st.file_uploader(
                "Choose CSV file", 
                type=['csv'], 
                help="Upload quantum sales data",
                key="data_uploader"
            )
            if uploaded_file:
                st.success(f"✅ File loaded: {uploaded_file.name}")
                
            if st.button("🔄 Process Data", key="process_data", use_container_width=True):
                with st.spinner("Processing quantum algorithms..."):
                    import time
                    time.sleep(2)
                st.success("Neural network updated! ✨")

        # AI Analysis moved to prominent position - Layout Change #4
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("🤖 AI Quick Analysis")
        
        if st.button("🎯 Generate AI Insights", key="ai_insights", use_container_width=True):
            with st.spinner("Consulting neural networks..."):
                import time
                time.sleep(1.5)
            st.info("💡 **AI Insight**: Top 20% of products drive 67% of revenue. Consider premium pricing strategy.")
            
        if st.button("📊 Predict Trends", key="predict_trends", use_container_width=True):
            with st.spinner("Analyzing market patterns..."):
                import time
                time.sleep(1.5)
            st.success("📈 **Prediction**: 15% revenue increase expected with dynamic pricing implementation.")
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Filters in compact form
        with st.expander("🔍 Advanced Filters", expanded=True):
            sku_filter = st.text_input("SKU Filter:", placeholder="Search SKU...", key="sku_filter")
            margin_range = st.slider("Margin Range", 0.0, 1.0, (0.2, 0.6), key="margin_range")
            
            if sku_filter:
                df = df[df['sku'].str.contains(sku_filter, case=False, na=False)]
            df = df[(df['margin'] >= margin_range[0]) & (df['margin'] <= margin_range[1])]

        # Export options
        st.markdown("### ⬇ Export Options")
        export_col1, export_col2 = st.columns(2, gap="small")
        
        with export_col1:
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📄 CSV",
                csv_data,
                "neural_data.csv",
                "text/csv",
                use_container_width=True,
                key="export_csv"
            )
        
        with export_col2:
            # Simplified Excel export button
            st.button("📊 Excel", use_container_width=True, key="export_excel_placeholder")

    # Bottom section with tabs - Structural Change #5
    if st.session_state.view_mode in ["Complete Overview", "Data Management"]:
        st.markdown("---")
        
        tab1, tab2, tab3 = st.tabs(["🏆 Top Products", "📈 Performance Metrics", "🔮 Predictions"])
        
        with tab1:
            col1, col2 = st.columns([2, 1])
            with col1:
                top10 = df.sort_values('total_quantity', ascending=False).head(6)
                for i, (_, product) in enumerate(top10.iterrows()):
                    st.markdown(f"""
                    <div style="background: var(--glass-bg); border-radius: 10px; padding: 1rem; margin: 0.5rem 0; border-left: 3px solid var(--primary-color);">
                        <strong>{product['sku']}</strong> - Qty: {product['total_quantity']:,} | Price: ₹{product['suggested_price']:.0f}
                    </div>
                    """, unsafe_allow_html=True)
            with col2:
                st.metric("Best Performer", top10.iloc[0]['sku'])
                st.metric("Top Quantity", f"{top10.iloc[0]['total_quantity']:,}")
        
        with tab2:
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            with metric_col1:
                st.metric("Avg Revenue", f"₹{df['total_sales'].mean():,.0f}")
            with metric_col2:
                st.metric("Median Price", f"₹{df['suggested_price'].median():.0f}")
            with metric_col3:
                st.metric("Price Range", f"₹{df['suggested_price'].max() - df['suggested_price'].min():.0f}")
        
        with tab3:
            st.info("🔮 **Neural Prediction**: Implementing dynamic pricing could increase overall margins by 8-12%")
            st.warning("⚠️ **Risk Analysis**: 23% of products show price sensitivity above market average")

    # Compact footer
    st.markdown("""
    <div style="text-align: center; margin-top: 1rem; padding: 0.8rem; font-size: 0.8rem;
                background: var(--glass-bg); border-radius: 10px; color: var(--text-secondary);">
        Neural Analytics • Quantum Processing • AI-Powered Insights
    </div>
    """, unsafe_allow_html=True)

# Enhanced chatbot page
def chatbot_page():
    show_navbar()

    st.markdown("""
    <div class="metric-card" style="text-align: center;">
        <h1 class="cyber-title">🤖 NEURAL AI ASSISTANT</h1>
        <p style="color: var(--text-secondary);">Query the quantum business intelligence matrix</p>
    </div>
    """, unsafe_allow_html=True)

    # Display chat history from session state
    for msg in st.session_state.chat_memory.buffer:
        if isinstance(msg, HumanMessage):
            st.markdown(f"""
            <div class="chat-message">
                <strong style="color: var(--primary-color);">NEURAL USER:</strong> {msg.content}
            </div>
            """, unsafe_allow_html=True)
        elif isinstance(msg, AIMessage):
            st.markdown(f"""
            <div class="chat-message" style="border-left-color: var(--success-color);">
                <strong style="color: var(--success-color);">QUANTUM AI:</strong> {msg.content}
            </div>
            """, unsafe_allow_html=True)

    # Chat input
    user_input = st.chat_input("💬 Enter neural query:", key="chat_input")

    if user_input:
        if st.session_state.groq_chat_model:
            with st.spinner("Processing neural pathways..."):
                # Append user message to memory
                st.session_state.chat_memory.chat_memory.add_user_message(user_input)

                # Create the chain
                chain = prompt | st.session_state.groq_chat_model

                # Invoke the model
                response = chain.invoke({
                    "input": user_input,
                    "history": st.session_state.chat_memory.buffer
                }).content

                # Append AI response to memory
                st.session_state.chat_memory.chat_memory.add_ai_message(response)

                # Save to database
                save_chat(st.session_state.user_id, user_input, response)

                # Rerun to display updated chat history
                st.rerun()
        else:
            st.error("Neural AI not initialized. Please verify quantum API connection.")

# Enhanced history page
def history_page():
    show_navbar()

    st.markdown("""
    <div class="metric-card" style="text-align: center;">
        <h1 class="cyber-title">📜 NEURAL CONVERSATION LOGS</h1>
        <p style="color: var(--text-secondary);">Access your quantum interaction archive</p>
    </div>
    """, unsafe_allow_html=True)

    history = get_history(st.session_state.user_id)

    if history:
        for i, (message, response) in enumerate(reversed(history)):
            st.markdown(f"""
            <div class="chat-message" style="animation-delay: {i * 0.1}s;">
                <strong style="color: var(--primary-color);">NEURAL USER:</strong> {message}
            </div>
            <div class="chat-message" style="border-left-color: var(--success-color); animation-delay: {i * 0.1 + 0.05}s;">
                <strong style="color: var(--success-color);">QUANTUM AI:</strong> {response}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="metric-card" style="text-align: center;">
            <h3>📭 Neural logs empty</h3>
            <p style="color: var(--text-secondary);">Initialize quantum conversation to populate neural archives!</p>
        </div>
        """, unsafe_allow_html=True)
        # Add a Streamlit button to navigate to chat, as HTML onclick is not ideal
        if st.button("🤖 ACTIVATE NEURAL CHAT →", key="go_to_chat_from_history"):
            st.session_state.page = 'chatbot'
            st.rerun()


def logout_page():
    st.session_state.user_id = None
    st.session_state.page = 'login'
    st.session_state.chat_memory.clear()  # Clear chat memory on logout
    st.rerun()

# Enhanced router with page transitions
current_page = st.session_state.page

if st.session_state.user_id:
    if current_page == 'overview':
        overview_page()
    elif current_page == 'chatbot':
        chatbot_page()
    elif current_page == 'history':
        history_page()
    elif current_page == 'logout':
        logout_page() # This function already handles st.rerun()
    else:
        # Default authenticated page if current_page is not recognized
        st.session_state.page = 'overview'
        overview_page()
else:
    if current_page == 'login':
        login_page()
    elif current_page == 'signup':
        signup_page()
    else:
        # Default unauthenticated page if current_page is not recognized
        st.session_state.page = 'login'
        login_page()

        