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
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Prudential Zenith Travel App",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with modern UI
st.markdown("""
<style>
    /* Main container styling */
    .main-header {
        font-size: 2.5rem;
        color: #D32F2F;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        background: linear-gradient(90deg, #D32F2F, #B71C1C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #424242;
        margin-top: 1rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .card {
        background: white;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 25px;
        border-left: 6px solid #D32F2F;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transition: transform 0.3s ease;
    }
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
    }
    .stButton>button {
        background: linear-gradient(90deg, #D32F2F, #B71C1C);
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 12px 28px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #B71C1C, #9A0007);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(211, 47, 47, 0.3);
    }
    .profile-img {
        border-radius: 50%;
        width: 150px;
        height: 150px;
        object-fit: cover;
        border: 4px solid #D32F2F;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .status-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 2px;
    }
    .status-pending {
        background-color: #FFF3CD;
        color: #856404;
        border: 1px solid #FFEAA7;
    }
    .status-approved {
        background-color: #D4EDDA;
        color: #155724;
        border: 1px solid #C3E6CB;
    }
    .status-rejected {
        background-color: #F8D7DA;
        color: #721C24;
        border: 1px solid #F5C6CB;
    }
    .status-paid {
        background-color: #CCE5FF;
        color: #004085;
        border: 1px solid #B8DAFF;
    }
    .form-container {
        background: white;
        border-radius: 12px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border-top: 4px solid #D32F2F;
    }
    .approval-flow {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 20px 0;
        padding: 15px;
        background: #F8F9FA;
        border-radius: 8px;
    }
    .approval-step {
        text-align: center;
        padding: 10px;
        flex: 1;
    }
    .step-active {
        color: #D32F2F;
        font-weight: 600;
    }
    .step-completed {
        color: #28A745;
        font-weight: 600;
    }
    .budget-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }
    .dashboard-widget {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
        border: 1px solid #E9ECEF;
    }
</style>
""", unsafe_allow_html=True)

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
    "MD", "ED", "CFO/ED", "Chief Commercial Officer", "Chief Agency Officer", 
    "Chief Compliance Officer", "Chief Risk Officer", "National Sales Manager", 
    "Head of Administration", "Head of Department", "Team Lead", "Team Member",
    "Payables Officer", "Budget Officer"
]

# Updated Nigerian states with all major cities
NIGERIAN_STATES = {
    "Abia": ["Aba", "Umuahia"],
    "Adamawa": ["Yola", "Mubi", "Jimeta"],
    "Akwa Ibom": ["Uyo", "Eket", "Ikot Ekpene"],
    "Anambra": ["Awka", "Onitsha", "Nnewi"],
    "Bauchi": ["Bauchi", "Azare", "Misau"],
    "Bayelsa": ["Yenagoa", "Brass", "Sagbama"],
    "Benue": ["Makurdi", "Gboko", "Otukpo"],
    "Borno": ["Maiduguri", "Bama", "Dikwa"],
    "Cross River": ["Calabar", "Ogoja", "Ikom"],
    "Delta": ["Asaba", "Warri", "Sapele"],
    "Ebonyi": ["Abakaliki", "Afikpo", "Onueke"],
    "Edo": ["Benin City", "Auchi", "Ekpoma"],
    "Ekiti": ["Ado-Ekiti", "Ikere-Ekiti", "Ise-Ekiti"],
    "Enugu": ["Enugu", "Nsukka", "Agbani"],
    "FCT": ["Abuja", "Gwagwalada", "Kuje"],
    "Gombe": ["Gombe", "Bajoga", "Kaltungo"],
    "Imo": ["Owerri", "Orlu", "Okigwe"],
    "Jigawa": ["Dutse", "Hadejia", "Gumel"],
    "Kaduna": ["Kaduna", "Zaria", "Kafanchan"],
    "Kano": ["Kano", "Wudil", "Rano"],
    "Katsina": ["Katsina", "Funtua", "Daura"],
    "Kebbi": ["Birnin Kebbi", "Argungu", "Yauri"],
    "Kogi": ["Lokoja", "Okene", "Idah"],
    "Kwara": ["Ilorin", "Offa", "Omu-Aran"],
    "Lagos": ["Lagos", "Ikeja", "Badagry"],
    "Nasarawa": ["Lafia", "Keffi", "Akwanga"],
    "Niger": ["Minna", "Bida", "Suleja"],
    "Ogun": ["Abeokuta", "Sagamu", "Ijebu-Ode"],
    "Ondo": ["Akure", "Ondo", "Owo"],
    "Osun": ["Osogbo", "Ife", "Ilesa"],
    "Oyo": ["Ibadan", "Ogbomoso", "Oyo"],
    "Plateau": ["Jos", "Bukuru", "Shendam"],
    "Rivers": ["Port Harcourt", "Bonny", "Okrika"],
    "Sokoto": ["Sokoto", "Tambuwal", "Gwadabawa"],
    "Taraba": ["Jalingo", "Wukari", "Bali"],
    "Yobe": ["Damaturu", "Potiskum", "Gashua"],
    "Zamfara": ["Gusau", "Kaura Namoda", "Anka"]
}

# Database initialization with enhanced tables
def init_db():
    conn = sqlite3.connect('travel_app.db')
    c = conn.cursor()
    
    # Enhanced Users table with account details
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  full_name TEXT,
                  username TEXT UNIQUE,
                  email TEXT,
                  password TEXT,
                  department TEXT,
                  grade TEXT,
                  role TEXT,
                  employee_id TEXT,
                  phone TEXT,
                  bank_name TEXT,
                  account_number TEXT,
                  account_name TEXT,
                  profile_pic BLOB,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
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
                  payment_status TEXT DEFAULT 'pending',
                  current_approver TEXT,
                  approval_flow TEXT,
                  total_cost REAL DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (username) REFERENCES users(username))''')
    
    # Enhanced Travel costs table with budget tracking
    c.execute('''CREATE TABLE IF NOT EXISTS travel_costs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  request_id INTEGER,
                  grade TEXT,
                  per_diem_amount REAL,
                  flight_cost REAL,
                  accommodation_cost REAL,
                  transportation_cost REAL,
                  other_costs REAL,
                  total_cost REAL,
                  budgeted_cost REAL,
                  budget_balance REAL,
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
    
    # Budget table
    c.execute('''CREATE TABLE IF NOT EXISTS budget
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  department TEXT,
                  budget_year INTEGER,
                  budget_month INTEGER,
                  planned_budget REAL,
                  ytd_budget REAL,
                  ytd_actual REAL,
                  variance REAL,
                  variance_percentage REAL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Payment transactions table
    c.execute('''CREATE TABLE IF NOT EXISTS payments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  request_id INTEGER,
                  amount REAL,
                  payment_date DATE,
                  payment_method TEXT,
                  reference_number TEXT,
                  status TEXT DEFAULT 'pending',
                  processed_by TEXT,
                  processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (request_id) REFERENCES travel_requests(id))''')
    
    # Create default users
    default_users = [
        ("Head of Administration", "head_admin", "admin@prudentialzenith.com", 
         make_hashes("123456"), "Administration", "GM", "Head of Administration", "EMP001"),
        ("Chief Compliance Officer", "chief_compliance", "compliance@prudentialzenith.com", 
         make_hashes("123456"), "Legal and Compliance", "DGM", "Chief Compliance Officer", "EMP002"),
        ("Chief Risk Officer", "chief_risk", "risk@prudentialzenith.com", 
         make_hashes("123456"), "Internal Control and Risk", "DGM", "Chief Risk Officer", "EMP003"),
        ("Payables Officer", "payables", "payables@prudentialzenith.com", 
         make_hashes("123456"), "Finance and Investment", "PM", "Payables Officer", "EMP004"),
        ("Budget Officer", "budget", "budget@prudentialzenith.com", 
         make_hashes("123456"), "Finance and Investment", "PM", "Budget Officer", "EMP005"),
        ("CFO/Executive Director", "cfo_ed", "cfo@prudentialzenith.com", 
         make_hashes("0123456"), "Finance and Investment", "ED", "CFO/ED", "EMP006"),
        ("Managing Director", "md", "md@prudentialzenith.com", 
         make_hashes("123456"), "Office of CEO", "MD", "MD", "EMP007"),
    ]
    
    for user in default_users:
        try:
            c.execute('''INSERT OR IGNORE INTO users 
                       (full_name, username, email, password, department, grade, role, employee_id) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', user)
        except:
            pass
    
    # Initialize budget data
    current_year = datetime.datetime.now().year
    for dept in DEPARTMENTS:
        c.execute('''INSERT OR IGNORE INTO budget 
                   (department, budget_year, planned_budget, ytd_budget, ytd_actual) 
                   VALUES (?, ?, ?, ?, ?)''',
                 (dept, current_year, 10000000, 0, 0))
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Helper functions
def get_payment_approval_flow(total_cost):
    """Determine approval flow based on total cost"""
    if total_cost > 5000000:  # Above 5 million Naira
        return ["Head of Administration", "Chief Compliance Officer", "Chief Risk Officer", "MD"]
    else:  # 5 million Naira or less
        return ["Head of Administration", "Chief Compliance Officer", "Chief Risk Officer", "ED"]

def calculate_travel_costs(grade, travel_type, duration_nights, destination_type="domestic"):
    """Calculate travel costs based on policy and destination"""
    grade_category = get_grade_category(grade)
    
    if travel_type == "local":
        # Local travel policies
        local_rates = {
            "GM & ABOVE": {"hotel": 150000, "feeding": 25000},
            "AGM-DGM": {"hotel": 100000, "feeding": 20000},
            "SM-PM": {"hotel": 70000, "feeding": 15000},
            "MGR": {"hotel": 50000, "feeding": 10000},
            "AM-DM": {"hotel": 40000, "feeding": 8000},
            "EA-SO": {"hotel": 30000, "feeding": 5000}
        }
        policy = local_rates[grade_category]
        hotel_cost = policy["hotel"] * duration_nights
        feeding_cost = policy["feeding"] * 3 * duration_nights
        return hotel_cost + feeding_cost
    else:
        # International travel policies
        international_rates = {
            "GM & ABOVE": {"in_lieu": 700, "out_of_station": 50, "airport_taxi": 100},
            "AGM-DGM": {"in_lieu": 550, "out_of_station": 50, "airport_taxi": 100},
            "SM-PM": {"in_lieu": 475, "out_of_station": 50, "airport_taxi": 100},
            "MGR": {"in_lieu": 375, "out_of_station": 50, "airport_taxi": 100},
            "AM-DM": {"in_lieu": 325, "out_of_station": 50, "airport_taxi": 100},
            "EA-SO": {"in_lieu": 275, "out_of_station": 50, "airport_taxi": 100}
        }
        policy = international_rates[grade_category]
        total_per_day = sum(policy.values())
        return total_per_day * duration_nights

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

def update_budget(department, amount, transaction_type="expense"):
    """Update budget balance"""
    conn = sqlite3.connect('travel_app.db')
    c = conn.cursor()
    
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    
    c.execute('''SELECT * FROM budget 
                 WHERE department = ? AND budget_year = ?''', 
              (department, current_year))
    
    budget_data = c.fetchone()
    
    if budget_data:
        budget_id, dept, year, month, planned, ytd_budget, ytd_actual, variance, var_percent, created = budget_data
        
        if transaction_type == "expense":
            new_ytd_actual = ytd_actual + amount
        else:
            new_ytd_actual = ytd_actual - amount  # For budget increases
        
        new_variance = planned - new_ytd_actual
        new_variance_percent = (new_variance / planned * 100) if planned > 0 else 0
        
        c.execute('''UPDATE budget 
                     SET ytd_actual = ?, variance = ?, variance_percentage = ? 
                     WHERE id = ?''',
                  (new_ytd_actual, new_variance, new_variance_percent, budget_id))
    
    conn.commit()
    conn.close()

def generate_pdf_report(request_id):
    """Generate PDF report for travel request"""
    conn = sqlite3.connect('travel_app.db')
    
    # Get travel request details
    request_data = pd.read_sql('''SELECT tr.*, u.full_name, u.employee_id, u.department, u.grade, 
                                        u.bank_name, u.account_number, u.account_name,
                                        tc.total_cost as approved_cost
                                 FROM travel_requests tr 
                                 JOIN users u ON tr.username = u.username 
                                 LEFT JOIN travel_costs tc ON tr.id = tc.request_id 
                                 WHERE tr.id = ?''', 
                              conn, params=(request_id,)).iloc[0]
    
    # Get approval history
    approval_history = pd.read_sql('''SELECT approver_role, status, comments, approved_at 
                                     FROM approvals 
                                     WHERE request_id = ? 
                                     ORDER BY approved_at''', 
                                  conn, params=(request_id,))
    
    conn.close()
    
    # Create PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "PRUDENTIAL ZENITH LIFE INSURANCE")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 70, "Travel Request Report")
    c.line(50, height - 80, width - 50, height - 80)
    
    # Request Details
    y_position = height - 100
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, "Travel Request Details")
    y_position -= 20
    
    details = [
        ("Request ID:", str(request_data['id'])),
        ("Employee:", request_data['full_name']),
        ("Employee ID:", request_data['employee_id']),
        ("Department:", request_data['department']),
        ("Grade:", request_data['grade']),
        ("Destination:", request_data['destination']),
        ("Purpose:", request_data['purpose']),
        ("Travel Type:", request_data['travel_type']),
        ("Dates:", f"{request_data['departure_date']} to {request_data['arrival_date']}"),
        ("Duration:", f"{request_data['duration_days']} days"),
        ("Status:", request_data['status']),
        ("Payment Status:", request_data.get('payment_status', 'pending')),
        ("Approved Cost:", f"₦{request_data.get('approved_cost', 0):,.2f}"),
    ]
    
    c.setFont("Helvetica", 10)
    for label, value in details:
        c.drawString(50, y_position, f"{label}")
        c.drawString(150, y_position, f"{value}")
        y_position -= 15
    
    # Bank Details
    y_position -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, "Bank Details for Payment")
    y_position -= 20
    
    bank_details = [
        ("Bank Name:", request_data.get('bank_name', 'Not provided')),
        ("Account Number:", request_data.get('account_number', 'Not provided')),
        ("Account Name:", request_data.get('account_name', 'Not provided')),
    ]
    
    c.setFont("Helvetica", 10)
    for label, value in bank_details:
        c.drawString(50, y_position, f"{label}")
        c.drawString(150, y_position, f"{value}")
        y_position -= 15
    
    # Approval History
    if not approval_history.empty:
        y_position -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "Approval History")
        y_position -= 20
        
        for _, row in approval_history.iterrows():
            c.drawString(50, y_position, f"{row['approver_role']}: {row['status']}")
            y_position -= 15
            if pd.notna(row['comments']):
                c.drawString(70, y_position, f"Comment: {row['comments'][:50]}...")
                y_position -= 15
            c.drawString(70, y_position, f"Date: {row['approved_at']}")
            y_position -= 20
    
    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, 30, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(width - 150, 30, "Prudential Zenith Travel System")
    
    c.save()
    buffer.seek(0)
    return buffer

def login():
    """Login page"""
    st.markdown('<h1 class="main-header">PRUDENTIAL ZENITH LIFE INSURANCE</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header" style="text-align: center;">Travel & Expense Management System</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<h3 style="text-align: center; color: #D32F2F;">🔐 USER LOGIN</h3>', unsafe_allow_html=True)
        
        username = st.text_input("**Username**", placeholder="Enter your username")
        password = st.text_input("**Password**", type="password", placeholder="Enter your password")
        
        col_a, col_b = st.columns(2)
        with col_a:
            login_btn = st.button("**LOGIN**", use_container_width=True, type="primary")
        with col_b:
            register_btn = st.button("**REGISTER**", use_container_width=True)
        
        # Quick login info
        with st.expander("Quick Login Credentials"):
            st.markdown("""
            **Test Accounts:**
            - Head of Administration: `head_admin` / `123456`
            - Chief Compliance Officer: `chief_compliance` / `123456`
            - Chief Risk Officer: `chief_risk` / `123456`
            - Payables Officer: `payables` / `123456`
            - Budget Officer: `budget` / `123456`
            - CFO/ED: `cfo_ed` / `0123456`
            - MD: `md` / `123456`
            """)
        
        if login_btn:
            if not username or not password:
                st.error("Please enter both username and password")
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
                    st.success(f"Welcome {user[1]}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        if register_btn:
            st.session_state.show_registration = True
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def registration_form():
    """User registration form"""
    st.markdown('<h1 class="sub-header">Create New Account</h1>', unsafe_allow_html=True)
    
    with st.form("registration_form"):
        st.markdown("### Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name*")
            username = st.text_input("Username*")
            employee_id = st.text_input("Employee ID*")
            email = st.text_input("Email Address*")
            phone = st.text_input("Phone Number")
        
        with col2:
            password = st.text_input("Password*", type="password")
            confirm_password = st.text_input("Confirm Password*", type="password")
            department = st.selectbox("Department*", DEPARTMENTS)
            grade = st.selectbox("Grade*", GRADES)
            role = st.selectbox("Role*", ROLES)
        
        st.markdown("### Bank Details")
        col3, col4 = st.columns(2)
        with col3:
            bank_name = st.text_input("Bank Name")
            account_number = st.text_input("Account Number")
        with col4:
            account_name = st.text_input("Account Name")
            profile_pic = st.file_uploader("Profile Picture", type=['jpg', 'jpeg', 'png'])
        
        submitted = st.form_submit_button("Create Account")
        
        if submitted:
            if not all([full_name, username, employee_id, email, password, confirm_password, department, grade, role]):
                st.error("Please fill in all required fields (*)")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                conn = sqlite3.connect('travel_app.db')
                c = conn.cursor()
                c.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
                existing_user = c.fetchone()
                
                if existing_user:
                    st.error("Username or email already exists")
                else:
                    pic_data = None
                    if profile_pic:
                        pic_data = profile_pic.read()
                    
                    c.execute("""INSERT INTO users 
                                 (full_name, username, email, password, department, grade, role,
                                  employee_id, phone, bank_name, account_number, account_name, profile_pic) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                             (full_name, username, email, make_hashes(password), department, grade, role,
                              employee_id, phone, bank_name, account_number, account_name, pic_data))
                    
                    conn.commit()
                    conn.close()
                    st.success("Account created successfully! Please login.")
                    time.sleep(2)
                    st.session_state.show_registration = False
                    st.rerun()

def dashboard():
    """Main dashboard"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 10px;">
            <h3 style="color: #D32F2F; margin-bottom: 5px;">PRUDENTIAL ZENITH</h3>
            <p style="color: #424242; font-size: 0.9rem; font-weight: 600;">Travel System</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown(f"**👤 {st.session_state.full_name}**")
        st.markdown(f"**📋 {st.session_state.role}**")
        st.markdown(f"**🏢 {st.session_state.department}**")
        st.markdown("---")
        
        menu_options = ["Dashboard", "My Profile", "Travel Request", "Travel History", 
                       "Approvals", "Budget Analytics", "Reports"]
        
        # Role-specific options
        if st.session_state.role in ["Head of Administration", "admin"]:
            menu_options.extend(["Payment Processing", "Budget Management"])
        if st.session_state.role == "Payables Officer":
            menu_options.append("Payment Processing")
        if st.session_state.role in ["MD", "ED", "CFO/ED"]:
            menu_options.extend(["Executive Dashboard"])
        
        selected = option_menu(
            menu_title="Navigation",
            options=menu_options,
            icons=["house", "person", "airplane", "clock-history", "check-circle", 
                  "graph-up-arrow", "file-earmark-text", "cash-coin", "calculator"] 
                  if "Payment Processing" in menu_options else 
                  ["house", "person", "airplane", "clock-history", "check-circle", 
                   "graph-up-arrow", "file-earmark-text"],
            menu_icon="compass",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "#D32F2F", "font-size": "18px"}, 
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px"},
                "nav-link-selected": {"background-color": "#D32F2F", "color": "white"},
            }
        )
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            st.session_state.logged_in = False
            st.session_state.username = ''
            st.session_state.role = ''
            st.rerun()
    
    # Route to selected page
    if selected == "Dashboard":
        show_dashboard()
    elif selected == "My Profile":
        show_profile()
    elif selected == "Travel Request":
        travel_request_form()
    elif selected == "Travel History":
        travel_history()
    elif selected == "Approvals":
        approvals_panel()
    elif selected == "Budget Analytics":
        budget_analytics()
    elif selected == "Reports":
        reports_dashboard()
    elif selected == "Payment Processing":
        payment_processing()
    elif selected == "Budget Management":
        budget_management()
    elif selected == "Executive Dashboard":
        executive_dashboard()

def show_dashboard():
    """Dashboard overview"""
    st.markdown('<h1 class="main-header">Dashboard</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_requests = pd.read_sql("SELECT COUNT(*) as count FROM travel_requests WHERE username = ?", 
                                    conn, params=(st.session_state.username,)).iloc[0]['count']
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Requests", total_requests)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        pending = pd.read_sql("""SELECT COUNT(*) as count FROM travel_requests 
                               WHERE username = ? AND status = 'pending'""", 
                             conn, params=(st.session_state.username,)).iloc[0]['count']
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Pending", pending)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        approved = pd.read_sql("""SELECT COUNT(*) as count FROM travel_requests 
                                WHERE username = ? AND status = 'approved'""", 
                              conn, params=(st.session_state.username,)).iloc[0]['count']
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Approved", approved)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        paid = pd.read_sql("""SELECT COUNT(*) as count FROM travel_requests 
                            WHERE username = ? AND payment_status = 'paid'""", 
                          conn, params=(st.session_state.username,)).iloc[0]['count']
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Paid", paid)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent activities
    col5, col6 = st.columns([2, 1])
    
    with col5:
        st.markdown("### Recent Travel Requests")
        recent_travel = pd.read_sql("""SELECT * FROM travel_requests 
                                     WHERE username = ? 
                                     ORDER BY created_at DESC LIMIT 5""", 
                                   conn, params=(st.session_state.username,))
        
        if not recent_travel.empty:
            for _, row in recent_travel.iterrows():
                status_class = f"status-{row['status']}"
                payment_class = f"status-{row.get('payment_status', 'pending')}"
                
                st.markdown(f"""
                <div class="dashboard-widget">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="color: #D32F2F; margin: 0;">{row['destination']}</h4>
                        <div>
                            <span class="status-badge {status_class}">{row['status'].upper()}</span>
                            <span class="status-badge {payment_class}">{row.get('payment_status', 'pending').upper()}</span>
                        </div>
                    </div>
                    <p style="margin: 5px 0;"><strong>Purpose:</strong> {row['purpose']}</p>
                    <p style="margin: 5px 0;"><strong>Dates:</strong> {row['departure_date']} to {row['arrival_date']}</p>
                    <p style="margin: 5px 0;"><strong>Cost:</strong> ₦{row.get('total_cost', 0):,.2f}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent travel requests")
    
    with col6:
        st.markdown("### Quick Actions")
        
        if st.button("📋 New Travel Request", use_container_width=True):
            st.session_state.selected = "Travel Request"
            st.rerun()
        
        if st.button("👤 Update Profile", use_container_width=True):
            st.session_state.selected = "My Profile"
            st.rerun()
        
        if st.button("📊 View Reports", use_container_width=True):
            st.session_state.selected = "Reports"
            st.rerun()
        
        if st.session_state.role == "Head of Administration":
            if st.button("💰 Process Payments", use_container_width=True):
                st.session_state.selected = "Payment Processing"
                st.rerun()
    
    conn.close()

def show_profile():
    """User profile page with update functionality"""
    st.markdown('<h1 class="sub-header">My Profile</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    user_data = pd.read_sql("SELECT * FROM users WHERE username = ?", 
                           conn, params=(st.session_state.username,)).iloc[0]
    
    # Display current profile
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if user_data['profile_pic']:
            st.image(user_data['profile_pic'], width=200, caption="Current Profile Picture")
        else:
            st.image("https://via.placeholder.com/200x200.png?text=No+Image", width=200)
    
    with col2:
        st.markdown(f"### {user_data['full_name']}")
        st.markdown(f"**Employee ID:** {user_data['employee_id']}")
        st.markdown(f"**Username:** {user_data['username']}")
        st.markdown(f"**Email:** {user_data['email']}")
        st.markdown(f"**Phone:** {user_data['phone'] or 'Not provided'}")
        st.markdown(f"**Department:** {user_data['department']}")
        st.markdown(f"**Grade:** {user_data['grade']}")
        st.markdown(f"**Role:** {user_data['role']}")
        
        # Bank details
        st.markdown("#### Bank Details")
        st.markdown(f"**Bank:** {user_data['bank_name'] or 'Not provided'}")
        st.markdown(f"**Account Number:** {user_data['account_number'] or 'Not provided'}")
        st.markdown(f"**Account Name:** {user_data['account_name'] or 'Not provided'}")
    
    st.markdown("---")
    
    # Update profile form
    st.markdown("### Update Profile Information")
    
    with st.form("update_profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_email = st.text_input("Email Address", value=user_data['email'])
            new_phone = st.text_input("Phone Number", value=user_data['phone'] or "")
            new_bank_name = st.text_input("Bank Name", value=user_data['bank_name'] or "")
        
        with col2:
            new_account_number = st.text_input("Account Number", value=user_data['account_number'] or "")
            new_account_name = st.text_input("Account Name", value=user_data['account_name'] or "")
            new_profile_pic = st.file_uploader("Update Profile Picture", type=['jpg', 'jpeg', 'png'])
        
        submitted = st.form_submit_button("Update Profile")
        
        if submitted:
            pic_data = user_data['profile_pic']
            if new_profile_pic:
                pic_data = new_profile_pic.read()
            
            c = conn.cursor()
            c.execute("""UPDATE users 
                         SET email = ?, phone = ?, bank_name = ?, account_number = ?, 
                             account_name = ?, profile_pic = ?, updated_at = CURRENT_TIMESTAMP 
                         WHERE username = ?""",
                     (new_email, new_phone, new_bank_name, new_account_number, 
                      new_account_name, pic_data, st.session_state.username))
            
            conn.commit()
            st.success("Profile updated successfully!")
            time.sleep(1)
            st.rerun()
    
    conn.close()

def travel_request_form():
    """Travel request form"""
    st.markdown('<h1 class="sub-header">New Travel Request</h1>', unsafe_allow_html=True)
    
    with st.form("travel_request"):
        st.markdown("### Travel Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            travel_type = st.selectbox("Travel Type*", ["Local", "International"])
            
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
                                   "Project Site Visit", "Client Visit", "Other"])
            
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
            
            st.info(f"**Duration:** {duration_days} days ({duration_nights} nights)")
        else:
            duration_days = 0
            duration_nights = 0
        
        # Additional information
        st.markdown("### Additional Information")
        additional_info = st.text_area("Additional Notes (Optional)")
        
        submitted = st.form_submit_button("Submit Request")
        
        if submitted:
            if not all([destination, purpose, mode_of_travel]):
                st.error("Please fill all required fields")
            elif arrival_date <= departure_date:
                st.error("Arrival date must be after departure date")
            else:
                # Calculate estimated cost
                estimated_cost = calculate_travel_costs(
                    st.session_state.grade, 
                    travel_type.lower(), 
                    duration_nights
                )
                
                # Show approval flow
                approval_flow = ["Head of Administration", "Chief Compliance Officer", 
                               "Chief Risk Officer", "ED"]  # Default flow
                
                st.info(f"""
                **Approval Flow:** {' → '.join(approval_flow)}
                **Estimated Cost:** ₦{estimated_cost:,.2f}
                """)
                
                # Insert travel request
                conn = sqlite3.connect('travel_app.db')
                c = conn.cursor()
                
                c.execute("""INSERT INTO travel_requests 
                          (username, travel_type, destination, city, purpose, 
                          mode_of_travel, departure_date, arrival_date, 
                          accommodation_needed, duration_days, duration_nights,
                          total_cost, current_approver, approval_flow) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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
                          estimated_cost,
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
                st.balloons()

def travel_history():
    """Travel history page with PDF download"""
    st.markdown('<h1 class="sub-header">Travel History</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        status_filter = st.selectbox("Status", ["All", "pending", "approved", "rejected"])
    with col2:
        payment_filter = st.selectbox("Payment", ["All", "pending", "paid"])
    with col3:
        type_filter = st.selectbox("Type", ["All", "local", "international"])
    with col4:
        year_filter = st.selectbox("Year", ["All"] + list(range(2020, datetime.datetime.now().year + 1)))
    
    # Build query
    query = """SELECT tr.*, tc.total_cost as approved_cost 
               FROM travel_requests tr 
               LEFT JOIN travel_costs tc ON tr.id = tc.request_id 
               WHERE tr.username = ?"""
    params = [st.session_state.username]
    
    if status_filter != "All":
        query += " AND tr.status = ?"
        params.append(status_filter)
    
    if payment_filter != "All":
        query += " AND tr.payment_status = ?"
        params.append(payment_filter)
    
    if type_filter != "All":
        query += " AND tr.travel_type = ?"
        params.append(type_filter)
    
    if year_filter != "All":
        query += " AND strftime('%Y', tr.created_at) = ?"
        params.append(str(year_filter))
    
    query += " ORDER BY tr.created_at DESC"
    
    travel_data = pd.read_sql(query, conn, params=params)
    
    if not travel_data.empty:
        # Export to Excel option
        if st.button("📊 Export to Excel"):
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                travel_data.to_excel(writer, sheet_name='Travel History', index=False)
            excel_buffer.seek(0)
            st.download_button(
                label="Download Excel File",
                data=excel_buffer,
                file_name=f"travel_history_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        for _, row in travel_data.iterrows():
            with st.expander(f"#{row['id']} - {row['destination']} ({row['status'].upper()})"):
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.markdown(f"**Purpose:** {row['purpose']}")
                    st.markdown(f"**Type:** {row['travel_type'].title()}")
                    st.markdown(f"**Mode:** {row['mode_of_travel']}")
                
                with col_b:
                    st.markdown(f"**Departure:** {row['departure_date']}")
                    st.markdown(f"**Arrival:** {row['arrival_date']}")
                    st.markdown(f"**Duration:** {row['duration_days']} days")
                
                with col_c:
                    st.markdown(f"**Status:** <span class='status-badge status-{row['status']}'>{row['status'].upper()}</span>", 
                               unsafe_allow_html=True)
                    st.markdown(f"**Payment:** <span class='status-badge status-{row['payment_status']}'>{row['payment_status'].upper()}</span>", 
                               unsafe_allow_html=True)
                    st.markdown(f"**Cost:** ₦{row.get('approved_cost', 0):,.2f}")
                
                # Generate PDF button
                if st.button(f"📄 Generate PDF Report", key=f"pdf_{row['id']}"):
                    pdf_buffer = generate_pdf_report(row['id'])
                    st.download_button(
                        label="Download PDF",
                        data=pdf_buffer,
                        file_name=f"travel_request_{row['id']}.pdf",
                        mime="application/pdf"
                    )
    else:
        st.info("No travel records found")
    
    conn.close()

def approvals_panel():
    """Approvals panel for approvers"""
    st.markdown('<h1 class="sub-header">Approvals Panel</h1>', unsafe_allow_html=True)
    
    approver_role = st.session_state.role
    
    conn = sqlite3.connect('travel_app.db')
    
    # Get pending approvals
    query = """SELECT tr.*, u.full_name, u.department, u.grade, u.employee_id 
               FROM travel_requests tr 
               JOIN users u ON tr.username = u.username 
               WHERE tr.current_approver = ? AND tr.status = 'pending'"""
    
    pending_approvals = pd.read_sql(query, conn, params=(approver_role,))
    
    if not pending_approvals.empty:
        st.markdown(f"### Pending Approvals ({len(pending_approvals)})")
        
        for _, row in pending_approvals.iterrows():
            st.markdown(f"""
            <div class="card">
                <h3 style="color: #D32F2F;">Travel Request #{row['id']}</h3>
                <p><strong>Requestor:</strong> {row['full_name']} ({row['employee_id']})</p>
                <p><strong>Department:</strong> {row['department']} | <strong>Grade:</strong> {row['grade']}</p>
                <p><strong>Destination:</strong> {row['destination']}</p>
                <p><strong>Purpose:</strong> {row['purpose']}</p>
                <p><strong>Dates:</strong> {row['departure_date']} to {row['arrival_date']}</p>
                <p><strong>Estimated Cost:</strong> ₦{row['total_cost']:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"✅ Approve", key=f"approve_{row['id']}", use_container_width=True):
                    update_approval_status(row['id'], "approved", approver_role)
                    st.success(f"Request #{row['id']} approved!")
                    time.sleep(1)
                    st.rerun()
            with col2:
                if st.button(f"❌ Reject", key=f"reject_{row['id']}", use_container_width=True):
                    update_approval_status(row['id'], "rejected", approver_role)
                    st.error(f"Request #{row['id']} rejected!")
                    time.sleep(1)
                    st.rerun()
            with col3:
                if st.button(f"📝 Request Info", key=f"info_{row['id']}", use_container_width=True):
                    st.info("Information request sent to employee")
    else:
        st.info("No pending approvals")
    
    conn.close()

def update_approval_status(request_id, status, approver_role):
    """Update approval status with enhanced flow"""
    conn = sqlite3.connect('travel_app.db')
    c = conn.cursor()
    
    # Update approval record
    c.execute("""UPDATE approvals 
                 SET status = ?, comments = ?, approved_at = CURRENT_TIMESTAMP 
                 WHERE request_id = ? AND approver_role = ?""",
             (status, f"Approved by {st.session_state.full_name}", request_id, approver_role))
    
    if status == "approved":
        # Get current approval flow
        c.execute("SELECT approval_flow FROM travel_requests WHERE id = ?", (request_id,))
        result = c.fetchone()
        
        if result:
            approval_flow = json.loads(result[0])
            current_index = approval_flow.index(approver_role)
            
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
                # Final approval - update status
                c.execute("""UPDATE travel_requests 
                             SET status = 'approved', current_approver = NULL 
                             WHERE id = ?""",
                         (request_id,))
                
                # Get cost for Head of Administration to process
                c.execute("SELECT total_cost FROM travel_requests WHERE id = ?", (request_id,))
                cost_result = c.fetchone()
                if cost_result:
                    total_cost = cost_result[0]
                    
                    # Create cost record for Head of Administration
                    c.execute("""INSERT INTO travel_costs 
                                 (request_id, total_cost, status) 
                                 VALUES (?, ?, ?)""",
                             (request_id, total_cost, "pending"))
    else:
        # Rejected - update status
        c.execute("""UPDATE travel_requests 
                     SET status = 'rejected', current_approver = NULL 
                     WHERE id = ?""",
                 (request_id,))
    
    conn.commit()
    conn.close()

def payment_processing():
    """Payment processing for Head of Administration"""
    if st.session_state.role not in ["Head of Administration", "Payables Officer", "admin"]:
        st.warning("Access denied")
        return
    
    st.markdown('<h1 class="sub-header">Payment Processing</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # Get approved requests needing payment processing
    query = """
        SELECT tr.*, u.full_name, u.employee_id, u.bank_name, u.account_number, u.account_name,
               tc.total_cost as approved_cost, tc.budgeted_cost, tc.budget_balance
        FROM travel_requests tr 
        JOIN users u ON tr.username = u.username 
        LEFT JOIN travel_costs tc ON tr.id = tc.request_id 
        WHERE tr.status = 'approved' 
        AND tr.payment_status = 'pending'
        AND (tc.id IS NOT NULL OR ? = 'Payables Officer')
    """
    
    approved_requests = pd.read_sql(query, conn, params=(st.session_state.role,))
    
    if not approved_requests.empty:
        for _, row in approved_requests.iterrows():
            with st.expander(f"#{row['id']} - {row['full_name']} - ₦{row.get('approved_cost', 0):,.2f}"):
                
                # Cost input form (for Head of Administration only)
                if st.session_state.role == "Head of Administration":
                    st.markdown("### Cost Approval & Budgeting")
                    
                    with st.form(f"cost_form_{row['id']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            flight_cost = st.number_input("Flight Cost (₦)", 
                                                         min_value=0.0, 
                                                         value=0.0,
                                                         key=f"flight_{row['id']}")
                            accommodation_cost = st.number_input("Accommodation Cost (₦)", 
                                                               min_value=0.0, 
                                                               value=0.0,
                                                               key=f"accommodation_{row['id']}")
                        
                        with col2:
                            transportation_cost = st.number_input("Transportation Cost (₦)", 
                                                                min_value=0.0, 
                                                                value=0.0,
                                                                key=f"transport_{row['id']}")
                            other_costs = st.number_input("Other Costs (₦)", 
                                                         min_value=0.0, 
                                                         value=0.0,
                                                         key=f"other_{row['id']}")
                        
                        # Budget section
                        st.markdown("### Budget Information")
                        col3, col4 = st.columns(2)
                        
                        with col3:
                            budgeted_cost = st.number_input("Budgeted Amount (₦)", 
                                                           min_value=0.0, 
                                                           value=row.get('approved_cost', 0),
                                                           key=f"budgeted_{row['id']}")
                        
                        with col4:
                            # Calculate budget balance
                            if 'budget_balance' in row and pd.notna(row['budget_balance']):
                                current_balance = row['budget_balance']
                            else:
                                # Get department budget
                                budget_data = pd.read_sql("""SELECT planned_budget, ytd_actual 
                                                           FROM budget 
                                                           WHERE department = ?""", 
                                                        conn, params=(row['department'],))
                                if not budget_data.empty:
                                    current_balance = budget_data.iloc[0]['planned_budget'] - budget_data.iloc[0]['ytd_actual']
                                else:
                                    current_balance = 0
                            
                            st.info(f"**Current Budget Balance:** ₦{current_balance:,.2f}")
                            
                            total_cost = flight_cost + accommodation_cost + transportation_cost + other_costs
                            new_balance = current_balance - total_cost
                            
                            if new_balance < 0:
                                st.error(f"**New Balance:** ₦{new_balance:,.2f} (Over budget!)")
                            else:
                                st.success(f"**New Balance:** ₦{new_balance:,.2f}")
                        
                        admin_notes = st.text_area("Administration Notes", key=f"notes_{row['id']}")
                        
                        if st.form_submit_button("Submit for Payment Approval"):
                            # Update travel costs
                            c = conn.cursor()
                            c.execute("""INSERT OR REPLACE INTO travel_costs 
                                       (request_id, grade, flight_cost, accommodation_cost, 
                                        transportation_cost, other_costs, total_cost, 
                                        budgeted_cost, budget_balance, admin_notes, status) 
                                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                     (row['id'], row['grade'], flight_cost, accommodation_cost,
                                      transportation_cost, other_costs, total_cost,
                                      budgeted_cost, new_balance, admin_notes, "pending_approval"))
                            
                            # Update approval flow based on total cost
                            payment_flow = get_payment_approval_flow(total_cost)
                            c.execute("""UPDATE travel_requests 
                                       SET approval_flow = ?, current_approver = ? 
                                       WHERE id = ?""",
                                     (json.dumps(payment_flow), payment_flow[0], row['id']))
                            
                            # Create approval records
                            for approver in payment_flow:
                                c.execute("""INSERT OR IGNORE INTO approvals 
                                           (request_id, approver_role, status) 
                                           VALUES (?, ?, ?)""",
                                         (row['id'], approver, "pending"))
                            
                            conn.commit()
                            st.success("Costs submitted for payment approval!")
                
                # Payment processing (for Payables Officer)
                if st.session_state.role == "Payables Officer":
                    st.markdown("### Payment Processing")
                    
                    with st.form(f"payment_form_{row['id']}"):
                        payment_method = st.selectbox("Payment Method", 
                                                    ["Bank Transfer", "Cheque", "Cash"])
                        reference_number = st.text_input("Reference Number")
                        payment_date = st.date_input("Payment Date", value=date.today())
                        
                        if st.form_submit_button("Mark as Paid"):
                            c = conn.cursor()
                            
                            # Update payment status
                            c.execute("""UPDATE travel_requests 
                                       SET payment_status = 'paid' 
                                       WHERE id = ?""",
                                     (row['id'],))
                            
                            # Record payment transaction
                            c.execute("""INSERT INTO payments 
                                       (request_id, amount, payment_date, payment_method, 
                                        reference_number, status, processed_by) 
                                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                                     (row['id'], row.get('approved_cost', 0), 
                                      payment_date.strftime("%Y-%m-%d"), 
                                      payment_method, reference_number, 
                                      "completed", st.session_state.username))
                            
                            # Update budget
                            update_budget(row['department'], row.get('approved_cost', 0), "expense")
                            
                            conn.commit()
                            st.success("Payment recorded successfully!")
    
    else:
        st.info("No approved requests pending payment processing")
    
    conn.close()

def budget_analytics():
    """Budget analytics dashboard"""
    st.markdown('<h1 class="sub-header">Budget Analytics</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # Get budget data
    budget_data = pd.read_sql("""SELECT * FROM budget 
                               ORDER BY department""", conn)
    
    if not budget_data.empty:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_budget = budget_data['planned_budget'].sum()
        total_actual = budget_data['ytd_actual'].sum()
        total_variance = budget_data['variance'].sum()
        avg_variance_percent = budget_data['variance_percentage'].mean()
        
        with col1:
            st.markdown('<div class="budget-card">', unsafe_allow_html=True)
            st.metric("Total Budget", f"₦{total_budget:,.0f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="budget-card">', unsafe_allow_html=True)
            st.metric("YTD Actual", f"₦{total_actual:,.0f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="budget-card">', unsafe_allow_html=True)
            st.metric("Total Variance", f"₦{total_variance:,.0f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="budget-card">', unsafe_allow_html=True)
            st.metric("Avg Variance %", f"{avg_variance_percent:.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Charts
        col5, col6 = st.columns(2)
        
        with col5:
            # Budget vs Actual by Department
            fig1 = px.bar(budget_data, x='department', y=['planned_budget', 'ytd_actual'],
                         title="Budget vs Actual by Department",
                         barmode='group')
            st.plotly_chart(fig1, use_container_width=True)
        
        with col6:
            # Variance Percentage
            fig2 = px.bar(budget_data, x='department', y='variance_percentage',
                         title="Variance Percentage by Department",
                         color='variance_percentage',
                         color_continuous_scale='RdYlGn')
            st.plotly_chart(fig2, use_container_width=True)
        
        # Detailed budget table
        st.markdown("### Detailed Budget Analysis")
        st.dataframe(budget_data.style.format({
            'planned_budget': '₦{:,.2f}',
            'ytd_budget': '₦{:,.2f}',
            'ytd_actual': '₦{:,.2f}',
            'variance': '₦{:,.2f}',
            'variance_percentage': '{:.2f}%'
        }))
        
        # Export option
        if st.button("📊 Export Budget Report"):
            csv = budget_data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"budget_report_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No budget data available")
    
    conn.close()

def budget_management():
    """Budget management for Head of Administration"""
    if st.session_state.role not in ["Head of Administration", "Budget Officer", "admin"]:
        st.warning("Access denied")
        return
    
    st.markdown('<h1 class="sub-header">Budget Management</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # Get current budget data
    budget_data = pd.read_sql("""SELECT * FROM budget 
                               ORDER BY department""", conn)
    
    # Budget update form
    st.markdown("### Update Department Budgets")
    
    with st.form("budget_update_form"):
        updated_data = []
        
        for _, row in budget_data.iterrows():
            st.markdown(f"#### {row['department']}")
            col1, col2 = st.columns(2)
            
            with col1:
                planned_budget = st.number_input(f"Planned Budget (₦)", 
                                                value=float(row['planned_budget']),
                                                key=f"planned_{row['department']}")
            
            with col2:
                ytd_budget = st.number_input(f"YTD Budget (₦)", 
                                            value=float(row['ytd_budget']),
                                            key=f"ytd_{row['department']}")
            
            updated_data.append({
                'department': row['department'],
                'planned_budget': planned_budget,
                'ytd_budget': ytd_budget
            })
        
        if st.form_submit_button("Update Budgets"):
            c = conn.cursor()
            for data in updated_data:
                c.execute("""UPDATE budget 
                           SET planned_budget = ?, ytd_budget = ?,
                               variance = planned_budget - ytd_actual,
                               variance_percentage = ((planned_budget - ytd_actual) / planned_budget * 100)
                           WHERE department = ?""",
                         (data['planned_budget'], data['ytd_budget'], data['department']))
            
            conn.commit()
            st.success("Budgets updated successfully!")
            time.sleep(1)
            st.rerun()
    
    # Add new budget allocation
    st.markdown("---")
    st.markdown("### Add New Budget Allocation")
    
    with st.form("new_budget_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_department = st.selectbox("Department", DEPARTMENTS)
        with col2:
            budget_year = st.number_input("Budget Year", 
                                         value=datetime.datetime.now().year,
                                         min_value=2020, max_value=2030)
        with col3:
            budget_month = st.selectbox("Budget Month", 
                                       list(range(1, 13)),
                                       format_func=lambda x: datetime.datetime(2000, x, 1).strftime('%B'))
        
        planned_amount = st.number_input("Planned Budget Amount (₦)", 
                                        min_value=0.0, 
                                        value=1000000.0)
        
        if st.form_submit_button("Add Budget Allocation"):
            c = conn.cursor()
            c.execute("""INSERT INTO budget 
                       (department, budget_year, budget_month, planned_budget, 
                        ytd_budget, ytd_actual, variance, variance_percentage) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                     (new_department, budget_year, budget_month, planned_amount,
                      0, 0, planned_amount, 100.0))
            
            conn.commit()
            st.success("New budget allocation added!")
            time.sleep(1)
            st.rerun()
    
    conn.close()

def reports_dashboard():
    """Reports and analytics dashboard"""
    st.markdown('<h1 class="sub-header">Reports & Analytics</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # Report type selection
    report_type = st.selectbox("Select Report Type", 
                              ["Travel Summary", "Department Analysis", 
                               "Payment Analysis", "Budget Utilization"])
    
    if report_type == "Travel Summary":
        # Travel summary report
        query = """SELECT tr.*, u.full_name, u.department, u.grade,
                          tc.total_cost as approved_cost, p.status as payment_status
                   FROM travel_requests tr 
                   JOIN users u ON tr.username = u.username 
                   LEFT JOIN travel_costs tc ON tr.id = tc.request_id 
                   LEFT JOIN payments p ON tr.id = p.request_id"""
        
        if st.session_state.role not in ["Head of Administration", "admin"]:
            query += " WHERE tr.username = ?"
            report_data = pd.read_sql(query, conn, params=(st.session_state.username,))
        else:
            report_data = pd.read_sql(query, conn)
        
        if not report_data.empty:
            # Summary statistics
            total_travel = len(report_data)
            total_cost = report_data['approved_cost'].sum()
            avg_cost = report_data['approved_cost'].mean()
            
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Total Travel Requests", total_travel)
            with col2: st.metric("Total Cost", f"₦{total_cost:,.2f}")
            with col3: st.metric("Average Cost", f"₦{avg_cost:,.2f}")
            
            # Display data
            st.dataframe(report_data[['id', 'full_name', 'department', 'destination', 
                                     'purpose', 'status', 'approved_cost', 'payment_status']])
            
            # Export options
            col4, col5 = st.columns(2)
            with col4:
                if st.button("📊 Export to Excel"):
                    excel_buffer = BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        report_data.to_excel(writer, sheet_name='Travel Summary', index=False)
                    excel_buffer.seek(0)
                    st.download_button(
                        label="Download Excel",
                        data=excel_buffer,
                        file_name="travel_summary.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            with col5:
                csv = report_data.to_csv(index=False)
                st.download_button(
                    label="📄 Download CSV",
                    data=csv,
                    file_name="travel_summary.csv",
                    mime="text/csv"
                )
    
    elif report_type == "Department Analysis":
        # Department-wise analysis
        query = """SELECT u.department, 
                          COUNT(tr.id) as total_requests,
                          SUM(CASE WHEN tr.status = 'approved' THEN 1 ELSE 0 END) as approved_requests,
                          SUM(CASE WHEN tr.status = 'pending' THEN 1 ELSE 0 END) as pending_requests,
                          SUM(tc.total_cost) as total_cost
                   FROM travel_requests tr 
                   JOIN users u ON tr.username = u.username 
                   LEFT JOIN travel_costs tc ON tr.id = tc.request_id 
                   GROUP BY u.department"""
        
        dept_data = pd.read_sql(query, conn)
        
        if not dept_data.empty:
            fig = px.bar(dept_data, x='department', y='total_cost',
                        title="Total Travel Cost by Department",
                        color='total_cost')
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(dept_data)
    
    conn.close()

def executive_dashboard():
    """Executive dashboard for MD/ED"""
    if st.session_state.role not in ["MD", "ED", "CFO/ED"]:
        st.warning("Access denied")
        return
    
    st.markdown('<h1 class="main-header">Executive Dashboard</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # High-level metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_requests = pd.read_sql("SELECT COUNT(*) as count FROM travel_requests", conn).iloc[0]['count']
    total_cost = pd.read_sql("SELECT SUM(total_cost) as total FROM travel_costs", conn).iloc[0]['total'] or 0
    pending_approvals = pd.read_sql("SELECT COUNT(*) as count FROM travel_requests WHERE status = 'pending'", conn).iloc[0]['count']
    paid_amount = pd.read_sql("SELECT SUM(amount) as total FROM payments WHERE status = 'completed'", conn).iloc[0]['total'] or 0
    
    with col1: st.metric("Total Requests", total_requests)
    with col2: st.metric("Total Cost", f"₦{total_cost:,.2f}")
    with col3: st.metric("Pending Approvals", pending_approvals)
    with col4: st.metric("Paid Amount", f"₦{paid_amount:,.2f}")
    
    # Recent high-value approvals needed
    st.markdown("### High-Value Approvals Pending")
    high_value_query = """SELECT tr.*, u.full_name, u.department, tc.total_cost
                         FROM travel_requests tr 
                         JOIN users u ON tr.username = u.username 
                         LEFT JOIN travel_costs tc ON tr.id = tc.request_id 
                         WHERE tr.status = 'pending' 
                         AND tc.total_cost > 5000000
                         ORDER BY tc.total_cost DESC"""
    
    high_value = pd.read_sql(high_value_query, conn)
    
    if not high_value.empty:
        for _, row in high_value.iterrows():
            st.markdown(f"""
            <div class="card">
                <h4 style="color: #D32F2F;">₦{row['total_cost']:,.2f} - {row['full_name']}</h4>
                <p><strong>Department:</strong> {row['department']}</p>
                <p><strong>Destination:</strong> {row['destination']}</p>
                <p><strong>Purpose:</strong> {row['purpose']}</p>
                <p><strong>Current Approver:</strong> {row['current_approver']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No high-value approvals pending")
    
    # Budget utilization
    st.markdown("### Budget Utilization Overview")
    budget_query = """SELECT department, planned_budget, ytd_actual, 
                             (ytd_actual/planned_budget*100) as utilization_percent
                      FROM budget 
                      WHERE planned_budget > 0"""
    
    budget_data = pd.read_sql(budget_query, conn)
    
    if not budget_data.empty:
        fig = px.bar(budget_data, x='department', y='utilization_percent',
                    title="Budget Utilization Percentage by Department",
                    color='utilization_percent')
        st.plotly_chart(fig, use_container_width=True)
    
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
