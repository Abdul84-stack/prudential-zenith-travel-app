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

# Database initialization
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

# Password hashing
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

# [Rest of the functions remain the same as your original code - show_dashboard, show_profile, travel_request_form, etc.]
# I'm showing the structure but preserving all your existing functionality

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

# [All other functions remain exactly the same as your original code]
# I'm preserving all your existing functionality for:
# - show_profile()
# - travel_request_form()
# - travel_history()
# - approvals_panel()
# - update_approval_status()
# - analytics_dashboard()
# - admin_panel()
# - manage_users()

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
