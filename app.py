import streamlit as st
import pandas as pd
import numpy as np
import datetime
from datetime import date, timedelta
import json
import hashlib
import sqlite3
import os
from PIL import Image
import io
import base64
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import time

# Page configuration
st.set_page_config(
    page_title="Prudential Zenith Travel App",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with RED and GREY color scheme
st.markdown("""
<style>
    /* Main container styling */
    .main-header {
        font-size: 2.5rem;
        color: #D32F2F; /* Red color */
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.8rem;
        color: #616161; /* Grey color */
        margin-top: 1rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    .login-container {
        background-color: #f5f5f5; /* Light grey background */
        border-radius: 15px;
        padding: 30px;
        margin-top: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 2px solid #D32F2F; /* Red border */
    }
    .login-title {
        color: #D32F2F;
        text-align: center;
        font-size: 1.8rem;
        margin-bottom: 25px;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #BDBDBD; /* Grey border */
    }
    .stTextInput>div>div>input:focus {
        border-color: #D32F2F; /* Red focus */
        box-shadow: 0 0 0 2px rgba(211, 47, 47, 0.2);
    }
    .stButton>button {
        background: linear-gradient(to right, #D32F2F, #B71C1C); /* Red gradient */
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 12px 24px;
        border: none;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(to right, #B71C1C, #9A0007); /* Darker red on hover */
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .login-buttons-container {
        display: flex;
        gap: 10px;
        margin-top: 20px;
    }
    .login-buttons-container .stButton {
        flex: 1;
    }
    .card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 5px solid #D32F2F; /* Red accent */
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .approved {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
    }
    .pending {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
    }
    .rejected {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
    }
    .profile-img {
        border-radius: 50%;
        width: 150px;
        height: 150px;
        object-fit: cover;
        border: 3px solid #D32F2F; /* Red border */
    }
    .company-logo {
        text-align: center;
        margin-bottom: 20px;
    }
    .welcome-text {
        text-align: center;
        color: #616161;
        font-size: 1.2rem;
        margin-bottom: 30px;
    }
    .quick-login {
        background-color: #f0f0f0;
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
        border-left: 3px solid #D32F2F;
    }
    .quick-login h4 {
        color: #D32F2F;
        margin-bottom: 10px;
    }
    .footer {
        text-align: center;
        color: #757575;
        font-size: 0.9rem;
        margin-top: 30px;
        padding-top: 15px;
        border-top: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Password hashing - MOVED TO TOP
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'role' not in st.session_state:
    st.session_state.role = ''
if 'department' not in st.session_state:
    st.session_state.department = ''
if 'grade' not in st.session_state:
    st.session_state.grade = ''
if 'full_name' not in st.session_state:
    st.session_state.full_name = ''

# Departments and Grades
DEPARTMENTS = [
    "Administration", "Bancassurance", "Corporate Sales", "Agencies", 
    "Actuary", "Legal and Compliance", "Internal Audit", "Internal Control and Risk", 
    "Finance and Investment", "Commercial and Business Support", "HR", 
    "Claims and Underwriting", "Branding and Corp. Communication", "Customer Service", 
    "IT", "Office of CEO", "Office of Executive Director"
]

GRADES = ["MD", "ED", "GM", "DGM", "AGM", "PM", "SM", "DM", "AM", "SO", "Officer", "EA"]

ROLES = [
    "MD", "ED", "Chief Commercial Officer", "Chief Agency Officer", 
    "Chief Compliance Officer", "Chief Risk Officer", "National Sales Manager", 
    "Head of Department", "Team Lead", "Team Member"
]

# Nigerian states and major cities
NIGERIAN_STATES = {
    "Abia": ["Aba", "Umuahia"],
    "Adamawa": ["Yola", "Mubi", "Jimeta"],
    "Akwa Ibom": ["Uyo", "Eket", "Ikot Ekpene"],
    "Anambra": ["Awka", "Onitsha", "Nnewi"],
    "Bauchi": ["Bauchi"],
    "Bayelsa": ["Yenagoa"],
    "Benue": ["Makurdi", "Gboko"],
    "Borno": ["Maiduguri"],
    "Cross River": ["Calabar"],
    "Delta": ["Asaba", "Warri"],
    "Ebonyi": ["Abakaliki"],
    "Edo": ["Benin City"],
    "Ekiti": ["Ado-Ekiti"],
    "Enugu": ["Enugu"],
    "FCT": ["Abuja"],
    "Gombe": ["Gombe"],
    "Imo": ["Owerri"],
    "Jigawa": ["Dutse"],
    "Kaduna": ["Kaduna"],
    "Kano": ["Kano"],
    "Katsina": ["Katsina"],
    "Kebbi": ["Birnin Kebbi"],
    "Kogi": ["Lokoja"],
    "Kwara": ["Ilorin"],
    "Lagos": ["Lagos", "Ikeja"],
    "Nasarawa": ["Lafia"],
    "Niger": ["Minna"],
    "Ogun": ["Abeokuta"],
    "Ondo": ["Akure"],
    "Osun": ["Osogbo"],
    "Oyo": ["Ibadan"],
    "Plateau": ["Jos"],
    "Rivers": ["Port Harcourt"],
    "Sokoto": ["Sokoto"],
    "Taraba": ["Jalingo"],
    "Yobe": ["Damaturu"],
    "Zamfara": ["Gusau"]
}

# Travel policies
LOCAL_POLICY = {
    "GM & ABOVE": {"hotel": "Receipt required", "feeding": "Receipt required"},
    "AGM-DGM": {"hotel": 100000, "feeding": 20000},
    "SM-PM": {"hotel": 70000, "feeding": 20000},
    "MGR": {"hotel": 50000, "feeding": 10000},
    "AM-DM": {"hotel": 45000, "feeding": 7000},
    "EA-SO": {"hotel": 40000, "feeding": 5000}
}

INTERNATIONAL_POLICY = {
    "GM & ABOVE": {"in_lieu": 700, "out_of_station": 50, "airport_taxi": 100, "total": 850},
    "AGM-DGM": {"in_lieu": 550, "out_of_station": 50, "airport_taxi": 100, "total": 700},
    "SM-PM": {"in_lieu": 475, "out_of_station": 50, "airport_taxi": 100, "total": 625},
    "MGR": {"in_lieu": 375, "out_of_station": 50, "airport_taxi": 100, "total": 525},
    "AM-DM": {"in_lieu": 325, "out_of_station": 50, "airport_taxi": 100, "total": 475},
    "EA-SO": {"in_lieu": 275, "out_of_station": 50, "airport_taxi": 100, "total": 425}
}

# Database initialization - MOVED AFTER make_hashes()
def init_db():
    conn = sqlite3.connect('travel_app.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  full_name TEXT,
                  username TEXT UNIQUE,
                  email TEXT,
                  password TEXT,
                  department TEXT,
                  grade TEXT,
                  role TEXT,
                  profile_pic BLOB,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Travel requests table
    c.execute('''CREATE TABLE IF NOT EXISTS travel_requests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  travel_type TEXT,
                  destination TEXT,
                  city TEXT,
                  purpose TEXT,
                  mode_of_travel TEXT,
                  departure_date DATE,
                  arrival_date DATE,
                  accommodation_needed TEXT,
                  duration_days INTEGER,
                  duration_nights INTEGER,
                  status TEXT DEFAULT 'pending',
                  current_approver TEXT,
                  approval_flow TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (username) REFERENCES users(username))''')
    
    # Travel costs table
    c.execute('''CREATE TABLE IF NOT EXISTS travel_costs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  request_id INTEGER,
                  grade TEXT,
                  per_diem_amount REAL,
                  flight_cost REAL,
                  total_cost REAL,
                  supporting_docs BLOB,
                  admin_notes TEXT,
                  status TEXT DEFAULT 'pending',
                  approval_flow TEXT,
                  current_approver TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (request_id) REFERENCES travel_requests(id))''')
    
    # Approvals table
    c.execute('''CREATE TABLE IF NOT EXISTS approvals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  request_id INTEGER,
                  approver_role TEXT,
                  status TEXT,
                  comments TEXT,
                  approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (request_id) REFERENCES travel_requests(id))''')
    
    # Create default users if they don't exist
    default_users = [
        ("CFO/Executive Director", "cfo_ed", "cfo@prudentialzenith.com", 
         make_hashes("0123456"), "Finance and Investment", "ED", "ED"),
        ("Managing Director", "md", "md@prudentialzenith.com", 
         make_hashes("123456"), "Office of CEO", "MD", "MD"),
    ]
    
    for user in default_users:
        try:
            c.execute('''INSERT OR IGNORE INTO users 
                       (full_name, username, email, password, department, grade, role) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)''', user)
        except:
            pass
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Helper functions
def get_approval_flow(department, grade, role):
    """Determine approval flow based on department and role"""
    if department in ["Finance and Investment", "Administration"]:
        return ["CFO/ED", "MD"]
    elif department in ["Internal Control and Risk", "Internal Audit"]:
        return ["Chief Risk Officer", "MD"]
    elif department == "HR":
        return ["MD"]
    elif department == "Agencies":
        return ["Chief Agencies Officer", "MD"]
    elif department == "Legal and Compliance":
        return ["Chief Compliance Officer", "MD"]
    elif department == "Corporate Sales":
        return ["Chief Commercial Officer", "MD"]
    else:
        return ["Head of Department", "MD"]

def get_grade_category(grade):
    """Map grade to policy category"""
    if grade in ["MD", "ED", "GM"]:
        return "GM & ABOVE"
    elif grade in ["DGM", "AGM"]:
        return "AGM-DGM"
    elif grade in ["PM", "SM"]:
        return "SM-PM"
    elif grade == "MGR":
        return "MGR"
    elif grade in ["AM", "DM"]:
        return "AM-DM"
    else:
        return "EA-SO"

def calculate_travel_costs(grade, travel_type, duration_nights):
    """Calculate travel costs based on policy"""
    grade_category = get_grade_category(grade)
    
    if travel_type == "local":
        policy = LOCAL_POLICY[grade_category]
        if isinstance(policy["hotel"], int):
            hotel_cost = policy["hotel"] * duration_nights
            feeding_cost = policy["feeding"] * 3 * duration_nights  # 3 meals per day
            total = hotel_cost + feeding_cost
        else:
            total = 0  # Receipt required
        return total
    else:
        policy = INTERNATIONAL_POLICY[grade_category]
        return policy["total"] * duration_nights

def login():
    """Login page with red and grey color scheme"""
    # Company header
    st.markdown('<div class="company-logo">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">PRUDENTIAL ZENITH LIFE INSURANCE</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Travel Support Application</h2>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Welcome text
    st.markdown('<p class="welcome-text">Secure access to travel management system for authorized personnel only</p>', unsafe_allow_html=True)
    
    # Login container
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="login-title">🔐 USER LOGIN</h3>', unsafe_allow_html=True)
        
        username = st.text_input("**Username / Employee ID**", placeholder="Enter your username")
        password = st.text_input("**Password**", type="password", placeholder="Enter your password")
        
        # Login buttons
        col_a, col_b = st.columns(2)
        with col_a:
            login_btn = st.button("**LOGIN**", use_container_width=True, type="primary")
        with col_b:
            register_btn = st.button("**CREATE ACCOUNT**", use_container_width=True)
        
        # Quick login info for CFO/ED and MD
        st.markdown('<div class="quick-login">', unsafe_allow_html=True)
        st.markdown('<h4>🔑 Quick Login (Test Credentials)</h4>', unsafe_allow_html=True)
        st.markdown("""
        - **CFO/ED**: Username: `cfo_ed` | Password: `0123456`
        - **MD**: Username: `md` | Password: `123456`
        - **Admin**: Username: `456475` | Password: `prutravel123`
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Authentication logic
        if login_btn:
            if not username or not password:
                st.error("⚠️ Please enter both username and password")
            else:
                # Check for hardcoded admin credentials
                if username == "456475" and password == "prutravel123":
                    st.session_state.logged_in = True
                    st.session_state.username = "admin"
                    st.session_state.role = "admin"
                    st.session_state.department = "Administration"
                    st.session_state.grade = "MD"
                    st.session_state.full_name = "System Administrator"
                    st.success("✅ Admin login successful!")
                    time.sleep(1)
                    st.rerun()
                
                # Check database for user credentials
                else:
                    conn = sqlite3.connect('travel_app.db')
                    c = conn.cursor()
                    c.execute("SELECT * FROM users WHERE username = ?", (username,))
                    user = c.fetchone()
                    conn.close()
                    
                    if user and check_hashes(password, user[4]):
                        st.session_state.logged_in = True
                        st.session_state.username = user[2]
                        st.session_state.role = user[7]
                        st.session_state.department = user[5]
                        st.session_state.grade = user[6]
                        st.session_state.full_name = user[1]
                        st.success(f"✅ Welcome {user[1]}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
        
        if register_btn:
            st.session_state.show_registration = True
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown('Prudential Zenith Life Insurance • Travel Management System v1.0')
    st.markdown('© 2024 All Rights Reserved')
    st.markdown('</div>', unsafe_allow_html=True)

def registration_form():
    """User registration form"""
    st.markdown('<h2 class="sub-header">Create New Account</h2>', unsafe_allow_html=True)
    
    with st.form("registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name*")
            username = st.text_input("Username (Employee ID)*")
            email = st.text_input("Email Address*")
            department = st.selectbox("Department*", DEPARTMENTS)
        
        with col2:
            password = st.text_input("Password*", type="password")
            confirm_password = st.text_input("Confirm Password*", type="password")
            grade = st.selectbox("Grade*", GRADES)
            role = st.selectbox("Role*", ROLES)
        
        profile_pic = st.file_uploader("Profile Picture (Optional)", type=['jpg', 'jpeg', 'png'])
        
        submitted = st.form_submit_button("Create Account")
        
        if submitted:
            if not all([full_name, username, email, password, confirm_password, department, grade, role]):
                st.error("Please fill in all required fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                # Check if user exists
                conn = sqlite3.connect('travel_app.db')
                c = conn.cursor()
                c.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
                existing_user = c.fetchone()
                
                if existing_user:
                    st.error("Username or email already exists")
                else:
                    # Save profile picture
                    pic_data = None
                    if profile_pic:
                        pic_data = profile_pic.read()
                    
                    # Insert user
                    c.execute("""INSERT INTO users 
                                 (full_name, username, email, password, department, grade, role, profile_pic) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                             (full_name, username, email, make_hashes(password), 
                              department, grade, role, pic_data))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success("Account created successfully! Please login.")
                    time.sleep(2)
                    st.session_state.show_registration = False
                    st.rerun()

def dashboard():
    """Main dashboard"""
    # Sidebar navigation with red/grey theme
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 10px;">
            <h3 style="color: #D32F2F; margin-bottom: 5px;">PRUDENTIAL ZENITH</h3>
            <p style="color: #616161; font-size: 0.9rem;">Travel Management</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # User info
        st.markdown(f"**👤 {st.session_state.full_name}**")
        st.markdown(f"**📋 Role:** {st.session_state.role}")
        st.markdown(f"**🏢 Dept:** {st.session_state.department}")
        st.markdown(f"**⭐ Grade:** {st.session_state.grade}")
        
        st.markdown("---")
        
        menu_options = ["Dashboard", "Staff Profile", "Travel Request", "Travel History", "Approvals", "Analytics"]
        
        # Admin specific options
        if st.session_state.role == "admin":
            menu_options.extend(["Admin Panel", "Manage Users"])
        
        selected = option_menu(
            menu_title="Navigation",
            options=menu_options,
            icons=["house", "person", "airplane", "clock-history", "check-circle", "graph-up", 
                   "gear", "people"] if st.session_state.role == "admin" else 
                   ["house", "person", "airplane", "clock-history", "check-circle", "graph-up"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "#D32F2F", "font-size": "18px"}, 
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#D32F2F", "color": "white"},
            }
        )
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            st.session_state.logged_in = False
            st.session_state.username = ''
            st.session_state.role = ''
            st.rerun()
    
    # Main content based on selection
    if selected == "Dashboard":
        show_dashboard()
    elif selected == "Staff Profile":
        show_profile()
    elif selected == "Travel Request":
        travel_request_form()
    elif selected == "Travel History":
        travel_history()
    elif selected == "Approvals":
        approvals_panel()
    elif selected == "Analytics":
        analytics_dashboard()
    elif selected == "Admin Panel":
        admin_panel()
    elif selected == "Manage Users":
        manage_users()

def show_dashboard():
    """Dashboard overview"""
    st.markdown('<h1 class="main-header">Dashboard</h1>', unsafe_allow_html=True)
    
    # Get user data
    conn = sqlite3.connect('travel_app.db')
    
    # Stats cards with red/grey theme
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_travel = pd.read_sql("SELECT COUNT(*) as count FROM travel_requests WHERE username = ?", 
                                  conn, params=(st.session_state.username,)).iloc[0]['count']
        st.metric("Total Travel", total_travel, 
                 delta=None, delta_color="normal",
                 help="Total number of travel requests")
    
    with col2:
        pending = pd.read_sql("""SELECT COUNT(*) as count FROM travel_requests 
                               WHERE username = ? AND status = 'pending'""", 
                             conn, params=(st.session_state.username,)).iloc[0]['count']
        st.metric("Pending", pending, 
                 delta=None, delta_color="inverse",
                 help="Pending travel requests")
    
    with col3:
        approved = pd.read_sql("""SELECT COUNT(*) as count FROM travel_requests 
                                WHERE username = ? AND status = 'approved'""", 
                              conn, params=(st.session_state.username,)).iloc[0]['count']
        st.metric("Approved", approved, 
                 delta=None, delta_color="normal",
                 help="Approved travel requests")
    
    with col4:
        if st.session_state.role == "admin":
            total_users = pd.read_sql("SELECT COUNT(*) as count FROM users", conn).iloc[0]['count']
            st.metric("Total Users", total_users,
                     delta=None, delta_color="normal",
                     help="Total system users")
        else:
            rejected = pd.read_sql("""SELECT COUNT(*) as count FROM travel_requests 
                                    WHERE username = ? AND status = 'rejected'""", 
                                  conn, params=(st.session_state.username,)).iloc[0]['count']
            st.metric("Rejected", rejected,
                     delta=None, delta_color="inverse",
                     help="Rejected travel requests")
    
    st.markdown("---")
    
    # Recent travel requests
    st.markdown("### Recent Travel Requests")
    recent_travel = pd.read_sql("""SELECT * FROM travel_requests 
                                 WHERE username = ? 
                                 ORDER BY created_at DESC LIMIT 5""", 
                               conn, params=(st.session_state.username,))
    
    if not recent_travel.empty:
        for _, row in recent_travel.iterrows():
            status_class = row['status']
            status_color = {
                'approved': '#28a745',
                'pending': '#ffc107',
                'rejected': '#dc3545'
            }.get(status_class, '#616161')
            
            st.markdown(f"""
            <div class="card" style="border-left-color: {status_color};">
                <h4 style="color: #D32F2F;">{row['destination']} ({row['travel_type'].title()})</h4>
                <p><strong>Purpose:</strong> {row['purpose']}</p>
                <p><strong>Dates:</strong> {row['departure_date']} to {row['arrival_date']}</p>
                <p><strong>Status:</strong> <span style="color: {status_color}; font-weight:bold">{row['status'].upper()}</span></p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No travel requests yet")
    
    conn.close()

def show_profile():
    """User profile page"""
    st.markdown('<h1 class="sub-header">Staff Profile</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    user_data = pd.read_sql("SELECT * FROM users WHERE username = ?", 
                           conn, params=(st.session_state.username,)).iloc[0]
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if user_data['profile_pic']:
            st.image(user_data['profile_pic'], width=200)
        else:
            st.image("https://via.placeholder.com/200x200.png?text=No+Image", width=200)
    
    with col2:
        st.markdown(f"### {user_data['full_name']}")
        st.markdown(f"**Employee ID:** {user_data['username']}")
        st.markdown(f"**Email:** {user_data['email']}")
        st.markdown(f"**Department:** {user_data['department']}")
        st.markdown(f"**Grade:** {user_data['grade']}")
        st.markdown(f"**Role:** {user_data['role']}")
    
    conn.close()

def travel_request_form():
    """Travel request form"""
    st.markdown('<h1 class="sub-header">New Travel Request</h1>', unsafe_allow_html=True)
    
    travel_type = st.radio("Travel Type", ["Local", "International"])
    
    with st.form("travel_request"):
        col1, col2 = st.columns(2)
        
        with col1:
            if travel_type == "Local":
                state = st.selectbox("State*", list(NIGERIAN_STATES.keys()))
                city = st.selectbox("City*", NIGERIAN_STATES[state])
                destination = f"{city}, {state}"
            else:
                country = st.text_input("Country*")
                city = st.text_input("City/Region*")
                destination = f"{city}, {country}"
            
            purpose = st.selectbox("Purpose*", 
                                  ["Business Meeting", "Conference", "Training", 
                                   "Project Site Visit", "Other"])
            
            if purpose == "Other":
                purpose = st.text_input("Specify purpose")
        
        with col2:
            mode_of_travel = st.selectbox("Mode of Travel*", 
                                         ["Flight", "Road", "Train", "Water", "Other"])
            
            departure_date = st.date_input("Departure Date*", min_value=date.today())
            arrival_date = st.date_input("Arrival Date*", min_value=departure_date)
            
            accommodation = st.radio("Accommodation Needed?", ["Yes", "No"])
        
        # Auto-calculate duration
        if departure_date and arrival_date:
            duration_days = (arrival_date - departure_date).days + 1
            duration_nights = (arrival_date - departure_date).days
            
            st.markdown(f"**Duration:** {duration_days} days ({duration_nights} nights)")
        else:
            duration_days = 0
            duration_nights = 0
        
        submitted = st.form_submit_button("Submit Request")
        
        if submitted:
            if not all([destination, purpose, mode_of_travel]):
                st.error("Please fill all required fields")
            elif arrival_date <= departure_date:
                st.error("Arrival date must be after departure date")
            else:
                # Get approval flow
                approval_flow = get_approval_flow(
                    st.session_state.department, 
                    st.session_state.grade, 
                    st.session_state.role
                )
                
                # Insert travel request
                conn = sqlite3.connect('travel_app.db')
                c = conn.cursor()
                
                c.execute("""INSERT INTO travel_requests 
                          (username, travel_type, destination, city, purpose, 
                          mode_of_travel, departure_date, arrival_date, 
                          accommodation_needed, duration_days, duration_nights, 
                          current_approver, approval_flow) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         (st.session_state.username, 
                          travel_type.lower(), 
                          destination, 
                          city, 
                          purpose, 
                          mode_of_travel,
                          departure_date.strftime("%Y-%m-%d"),
                          arrival_date.strftime("%Y-%m-%d"),
                          accommodation,
                          duration_days,
                          duration_nights,
                          approval_flow[0],
                          json.dumps(approval_flow)))
                
                request_id = c.lastrowid
                
                # Create initial approval record
                c.execute("""INSERT INTO approvals 
                          (request_id, approver_role, status) 
                          VALUES (?, ?, ?)""",
                         (request_id, approval_flow[0], "pending"))
                
                conn.commit()
                conn.close()
                
                st.success("Travel request submitted successfully!")
                st.info(f"Awaiting approval from: {approval_flow[0]}")
                
                # Calculate estimated costs
                grade_category = get_grade_category(st.session_state.grade)
                
                if travel_type == "Local":
                    policy = LOCAL_POLICY[grade_category]
                    st.markdown("### Estimated Allowances (Local)")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Hotel Allowance", 
                                 f"₦{policy['hotel']:,}" if isinstance(policy['hotel'], int) else policy['hotel'])
                    with col_b:
                        st.metric("Feeding Allowance (per meal)",
                                 f"₦{policy['feeding']:,}" if isinstance(policy['feeding'], int) else policy['feeding'])
                else:
                    policy = INTERNATIONAL_POLICY[grade_category]
                    st.markdown("### Estimated Allowances (International)")
                    col_a, col_b, col_c, col_d = st.columns(4)
                    with col_a:
                        st.metric("In-lieu", f"${policy['in_lieu']}")
                    with col_b:
                        st.metric("Out of Station", f"${policy['out_of_station']}")
                    with col_c:
                        st.metric("Airport Taxi", f"${policy['airport_taxi']}")
                    with col_d:
                        st.metric("Total per day", f"${policy['total']}")
                    st.metric("Total Estimated Cost", f"${policy['total'] * duration_nights:,}")

def travel_history():
    """Travel history page"""
    st.markdown('<h1 class="sub-header">Travel History</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", 
                                    ["All", "pending", "approved", "rejected"])
    with col2:
        type_filter = st.selectbox("Filter by Type", 
                                  ["All", "local", "international"])
    
    # Build query
    query = "SELECT * FROM travel_requests WHERE username = ?"
    params = [st.session_state.username]
    
    if status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)
    
    if type_filter != "All":
        query += " AND travel_type = ?"
        params.append(type_filter)
    
    query += " ORDER BY created_at DESC"
    
    travel_data = pd.read_sql(query, conn, params=params)
    
    if not travel_data.empty:
        for _, row in travel_data.iterrows():
            with st.expander(f"{row['destination']} - {row['status'].upper()} ({row['created_at'][:10]})"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**Purpose:** {row['purpose']}")
                    st.markdown(f"**Mode of Travel:** {row['mode_of_travel']}")
                    st.markdown(f"**Accommodation:** {row['accommodation_needed']}")
                with col_b:
                    st.markdown(f"**Departure:** {row['departure_date']}")
                    st.markdown(f"**Arrival:** {row['arrival_date']}")
                    st.markdown(f"**Duration:** {row['duration_days']} days")
                
                # Show approval flow
                st.markdown("**Approval Flow:**")
                approval_flow = json.loads(row['approval_flow'])
                for i, approver in enumerate(approval_flow):
                    status_icon = "⏳" if i == 0 and row['status'] == 'pending' else "✅"
                    st.markdown(f"{status_icon} {approver}")
    
    else:
        st.info("No travel records found")
    
    conn.close()

def approvals_panel():
    """Approvals panel for managers and approvers"""
    st.markdown('<h1 class="sub-header">Approvals Panel</h1>', unsafe_allow_html=True)
    
    # Determine approver role based on user's position
    approver_role = st.session_state.role
    
    conn = sqlite3.connect('travel_app.db')
    
    # Get pending approvals for this approver
    query = """SELECT tr.*, u.full_name, u.department, u.grade 
               FROM travel_requests tr 
               JOIN users u ON tr.username = u.username 
               WHERE tr.current_approver = ? AND tr.status = 'pending'"""
    
    pending_approvals = pd.read_sql(query, conn, params=(approver_role,))
    
    if not pending_approvals.empty:
        for _, row in pending_approvals.iterrows():
            with st.container():
                st.markdown(f"### Travel Request from {row['full_name']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Destination:** {row['destination']}")
                    st.markdown(f"**Purpose:** {row['purpose']}")
                    st.markdown(f"**Department:** {row['department']}")
                with col2:
                    st.markdown(f"**Travel Type:** {row['travel_type']}")
                    st.markdown(f"**Dates:** {row['departure_date']} to {row['arrival_date']}")
                    st.markdown(f"**Grade:** {row['grade']}")
                
                # Approval buttons
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    if st.button(f"Approve", key=f"approve_{row['id']}"):
                        update_approval_status(row['id'], "approved", approver_role)
                        st.rerun()
                with col_b:
                    if st.button(f"Reject", key=f"reject_{row['id']}"):
                        update_approval_status(row['id'], "rejected", approver_role)
                        st.rerun()
                with col_c:
                    if st.button(f"Request Info", key=f"info_{row['id']}"):
                        st.info("Request more information functionality to be implemented")
                
                st.markdown("---")
    else:
        st.info("No pending approvals")
    
    conn.close()

def update_approval_status(request_id, status, approver_role):
    """Update approval status"""
    conn = sqlite3.connect('travel_app.db')
    c = conn.cursor()
    
    # Update approval record
    c.execute("""UPDATE approvals 
                 SET status = ?, comments = ? 
                 WHERE request_id = ? AND approver_role = ?""",
             (status, "Approved via system", request_id, approver_role))
    
    # Get approval flow
    c.execute("SELECT approval_flow FROM travel_requests WHERE id = ?", (request_id,))
    approval_flow = json.loads(c.fetchone()[0])
    
    # Determine next approver or finalize
    current_index = approval_flow.index(approver_role)
    
    if status == "approved":
        if current_index < len(approval_flow) - 1:
            next_approver = approval_flow[current_index + 1]
            c.execute("""UPDATE travel_requests 
                         SET current_approver = ? 
                         WHERE id = ?""",
                     (next_approver, request_id))
            
            # Create next approval record
            c.execute("""INSERT INTO approvals 
                         (request_id, approver_role, status) 
                         VALUES (?, ?, ?)""",
                     (request_id, next_approver, "pending"))
        else:
            # Final approval - update travel request status
            c.execute("""UPDATE travel_requests 
                         SET status = 'approved', current_approver = NULL 
                         WHERE id = ?""",
                     (request_id,))
            
            # Create travel cost record for admin
            grade = pd.read_sql("SELECT grade FROM users u JOIN travel_requests tr ON u.username = tr.username WHERE tr.id = ?", 
                              conn, params=(request_id,)).iloc[0]['grade']
            
            c.execute("""INSERT INTO travel_costs 
                         (request_id, grade, status) 
                         VALUES (?, ?, ?)""",
                     (request_id, grade, "pending"))
    else:
        # Rejected - update status
        c.execute("""UPDATE travel_requests 
                     SET status = 'rejected', current_approver = NULL 
                     WHERE id = ?""",
                 (request_id,))
    
    conn.commit()
    conn.close()

def analytics_dashboard():
    """Analytics dashboard"""
    st.markdown('<h1 class="sub-header">Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # Get data for charts
    travel_data = pd.read_sql("""
        SELECT tr.*, u.department, u.grade 
        FROM travel_requests tr 
        JOIN users u ON tr.username = u.username
    """, conn)
    
    if not travel_data.empty:
        # Convert dates
        travel_data['departure_date'] = pd.to_datetime(travel_data['departure_date'])
        travel_data['month'] = travel_data['departure_date'].dt.strftime('%Y-%m')
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Travel by department
            dept_counts = travel_data['department'].value_counts()
            fig1 = px.pie(values=dept_counts.values, names=dept_counts.index,
                         title="Travel Requests by Department")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Travel by status
            status_counts = travel_data['status'].value_counts()
            fig2 = px.bar(x=status_counts.index, y=status_counts.values,
                         title="Travel Requests by Status",
                         color=status_counts.index)
            st.plotly_chart(fig2, use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            # Monthly trend
            monthly_counts = travel_data.groupby('month').size().reset_index(name='count')
            fig3 = px.line(monthly_counts, x='month', y='count',
                          title="Monthly Travel Requests Trend")
            st.plotly_chart(fig3, use_container_width=True)
        
        with col4:
            # Travel by type
            type_counts = travel_data['travel_type'].value_counts()
            fig4 = px.bar(x=type_counts.index, y=type_counts.values,
                         title="Local vs International Travel",
                         color=type_counts.index)
            st.plotly_chart(fig4, use_container_width=True)
        
        # Cost analysis (for admin)
        if st.session_state.role == "admin":
            st.markdown("### Cost Analysis")
            
            cost_data = pd.read_sql("""
                SELECT tc.*, tr.destination, tr.travel_type, u.department 
                FROM travel_costs tc 
                JOIN travel_requests tr ON tc.request_id = tr.id 
                JOIN users u ON tr.username = u.username 
                WHERE tc.total_cost IS NOT NULL
            """, conn)
            
            if not cost_data.empty:
                col5, col6 = st.columns(2)
                
                with col5:
                    # Cost by department
                    dept_costs = cost_data.groupby('department')['total_cost'].sum().reset_index()
                    fig5 = px.bar(dept_costs, x='department', y='total_cost',
                                 title="Total Costs by Department")
                    st.plotly_chart(fig5, use_container_width=True)
                
                with col6:
                    # Cost by grade
                    grade_costs = cost_data.groupby('grade')['total_cost'].mean().reset_index()
                    fig6 = px.bar(grade_costs, x='grade', y='total_cost',
                                 title="Average Cost by Grade")
                    st.plotly_chart(fig6, use_container_width=True)
    
    conn.close()

def admin_panel():
    """Admin panel for managing travel costs"""
    if st.session_state.role != "admin":
        st.warning("Access denied")
        return
    
    st.markdown('<h1 class="sub-header">Admin Panel - Travel Cost Management</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # Get approved travel requests needing cost input
    query = """
        SELECT tr.*, u.full_name, u.grade, u.department, tc.id as cost_id 
        FROM travel_requests tr 
        JOIN users u ON tr.username = u.username 
        LEFT JOIN travel_costs tc ON tr.id = tc.request_id 
        WHERE tr.status = 'approved' 
        AND (tc.id IS NULL OR tc.status = 'pending')
    """
    
    approved_requests = pd.read_sql(query, conn)
    
    if not approved_requests.empty:
        for _, row in approved_requests.iterrows():
            with st.expander(f"{row['full_name']} - {row['destination']} ({row['travel_type']})"):
                
                # Calculate estimated costs
                grade_category = get_grade_category(row['grade'])
                
                if row['travel_type'] == 'local':
                    policy = LOCAL_POLICY[grade_category]
                    st.markdown("**Local Travel Policy:**")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Hotel Allowance", 
                                 f"₦{policy['hotel']:,}" if isinstance(policy['hotel'], int) else policy['hotel'])
                    with col_b:
                        st.metric("Feeding Allowance", 
                                 f"₦{policy['feeding']:,}" if isinstance(policy['feeding'], int) else policy['feeding'])
                    
                    estimated_cost = 0
                    if isinstance(policy['hotel'], int):
                        estimated_cost = (policy['hotel'] + (policy['feeding'] * 3)) * row['duration_nights']
                    
                else:
                    policy = INTERNATIONAL_POLICY[grade_category]
                    st.markdown("**International Travel Policy:**")
                    col_a, col_b, col_c, col_d = st.columns(4)
                    with col_a:
                        st.metric("In-lieu", f"${policy['in_lieu']}")
                    with col_b:
                        st.metric("Out of Station", f"${policy['out_of_station']}")
                    with col_c:
                        st.metric("Airport Taxi", f"${policy['airport_taxi']}")
                    with col_d:
                        st.metric("Total per day", f"${policy['total']}")
                    
                    estimated_cost = policy['total'] * row['duration_nights']
                
                st.markdown(f"**Estimated Total Cost:** ${estimated_cost:,.2f}" if row['travel_type'] == 'international' 
                          else f"**Estimated Total Cost:** ₦{estimated_cost:,.2f}")
                
                # Cost input form
                with st.form(f"cost_form_{row['id']}"):
                    flight_cost = st.number_input("Flight Cost", 
                                                 min_value=0.0, 
                                                 value=0.0,
                                                 key=f"flight_{row['id']}")
                    
                    supporting_docs = st.file_uploader("Supporting Documents", 
                                                      type=['pdf', 'jpg', 'png'],
                                                      key=f"docs_{row['id']}")
                    
                    admin_notes = st.text_area("Admin Notes", key=f"notes_{row['id']}")
                    
                    if st.form_submit_button("Submit Costs"):
                        # Update travel costs
                        total_cost = estimated_cost + flight_cost
                        
                        c = conn.cursor()
                        if pd.isna(row['cost_id']):
                            c.execute("""INSERT INTO travel_costs 
                                       (request_id, grade, per_diem_amount, flight_cost, 
                                        total_cost, admin_notes, status) 
                                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                                     (row['id'], row['grade'], estimated_cost, flight_cost,
                                      total_cost, admin_notes, "pending"))
                        else:
                            c.execute("""UPDATE travel_costs 
                                       SET per_diem_amount = ?, flight_cost = ?, 
                                           total_cost = ?, admin_notes = ?, status = 'pending' 
                                       WHERE id = ?""",
                                     (estimated_cost, flight_cost, total_cost, admin_notes, row['cost_id']))
                        
                        conn.commit()
                        st.success("Costs submitted for approval!")
    
    conn.close()

def manage_users():
    """User management for admin"""
    if st.session_state.role != "admin":
        st.warning("Access denied")
        return
    
    st.markdown('<h1 class="sub-header">User Management</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # Get all users
    users = pd.read_sql("SELECT * FROM users", conn)
    
    if not users.empty:
        # Display users table
        st.dataframe(users[['full_name', 'username', 'email', 'department', 'grade', 'role', 'created_at']])
        
        # Add new user form
        st.markdown("### Add New User")
        with st.form("add_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_full_name = st.text_input("Full Name")
                new_username = st.text_input("Username")
                new_email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
            
            with col2:
                new_department = st.selectbox("Department", DEPARTMENTS)
                new_grade = st.selectbox("Grade", GRADES)
                new_role = st.selectbox("Role", ROLES)
            
            if st.form_submit_button("Add User"):
                if all([new_full_name, new_username, new_email, new_password]):
                    c = conn.cursor()
                    try:
                        c.execute("""INSERT INTO users 
                                   (full_name, username, email, password, department, grade, role) 
                                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                                 (new_full_name, new_username, new_email, 
                                  make_hashes(new_password), new_department, new_grade, new_role))
                        conn.commit()
                        st.success("User added successfully!")
                        st.rerun()
                    except:
                        st.error("Username or email already exists")
                else:
                    st.error("Please fill all fields")
    
    conn.close()

# Main app flow
def main():
    if not st.session_state.logged_in:
        if hasattr(st.session_state, 'show_registration') and st.session_state.show_registration:
            registration_form()
        else:
            login()
    else:
        dashboard()

if __name__ == "__main__":
    main()
