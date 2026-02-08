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
from fpdf import FPDF
import tempfile
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Prudential Zenith Travel App",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with RED and GREY color scheme - Enhanced
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
        background: linear-gradient(135deg, #D32F2F 0%, #B71C1C 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #424242;
        margin-top: 1rem;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: 600;
    }
    .login-container {
        background: linear-gradient(145deg, #ffffff, #f5f5f5);
        border-radius: 20px;
        padding: 40px;
        margin-top: 20px;
        box-shadow: 0 10px 30px rgba(211, 47, 47, 0.15);
        border: 2px solid #D32F2F;
    }
    .login-title {
        background: linear-gradient(135deg, #D32F2F 0%, #B71C1C 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 2rem;
        margin-bottom: 30px;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #E0E0E0;
        padding: 12px 15px;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    .stTextInput>div>div>input:focus {
        border-color: #D32F2F;
        box-shadow: 0 0 0 3px rgba(211, 47, 47, 0.1);
    }
    .stButton>button {
        background: linear-gradient(to right, #D32F2F, #B71C1C);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 14px 28px;
        border: none;
        width: 100%;
        transition: all 0.3s ease;
        font-size: 16px;
        box-shadow: 0 4px 15px rgba(211, 47, 47, 0.3);
    }
    .stButton>button:hover {
        background: linear-gradient(to right, #B71C1C, #9A0007);
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(211, 47, 47, 0.4);
    }
    .card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 25px;
        border-left: 6px solid #D32F2F;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        transition: transform 0.3s ease;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    .approved {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 6px solid #28a745;
    }
    .pending {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 6px solid #ffc107;
    }
    .rejected {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-left: 6px solid #dc3545;
    }
    .profile-img {
        border-radius: 50%;
        width: 150px;
        height: 150px;
        object-fit: cover;
        border: 4px solid #D32F2F;
        box-shadow: 0 4px 15px rgba(211, 47, 47, 0.2);
    }
    .company-logo {
        text-align: center;
        margin-bottom: 30px;
        padding: 20px;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        border: 2px solid #D32F2F;
    }
    .welcome-text {
        text-align: center;
        color: #616161;
        font-size: 1.3rem;
        margin-bottom: 40px;
        font-weight: 500;
    }
    .quick-login {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        padding: 20px;
        margin-top: 25px;
        border-left: 4px solid #D32F2F;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .footer {
        text-align: center;
        color: #757575;
        font-size: 0.9rem;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 2px solid #e0e0e0;
    }
    .approval-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 25px;
        font-size: 0.85rem;
        font-weight: bold;
        margin: 3px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .pending-badge {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        color: #856404;
        border: 1px solid #ffd54f;
    }
    .approved-badge {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        border: 1px solid #a3d9a5;
    }
    .rejected-badge {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        border: 1px solid #f1aeb5;
    }
    .paid-badge {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        color: #0c5460;
        border: 1px solid #86cfda;
    }
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border: 2px solid #D32F2F;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    }
    .tab-container {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f5f5f5;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        border: 1px solid #e0e0e0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #D32F2F !important;
        color: white !important;
    }
    /* Budget progress bar */
    .budget-bar {
        height: 25px;
        background: linear-gradient(90deg, #4CAF50, #8BC34A);
        border-radius: 12px;
        margin: 10px 0;
        overflow: hidden;
    }
    .budget-bar-over {
        background: linear-gradient(90deg, #F44336, #E53935);
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
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# Constants
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
    "Head of Department", "Team Lead", "Team Member", "Head of Administration",
    "Payables Officer"
]

# Updated Nigerian states with more cities
NIGERIAN_STATES = {
    "Abia": ["Aba", "Umuahia", "Arochukwu", "Ohafia"],
    "Adamawa": ["Yola", "Mubi", "Jimeta", "Ganye", "Numan"],
    "Akwa Ibom": ["Uyo", "Eket", "Ikot Ekpene", "Oron", "Ikot Abasi"],
    "Anambra": ["Awka", "Onitsha", "Nnewi", "Aguata", "Ogidi"],
    "Bauchi": ["Bauchi", "Azare", "Jama'are", "Katagum", "Misau"],
    "Bayelsa": ["Yenagoa", "Brass", "Ogbia", "Sagbama", "Ekeremor"],
    "Benue": ["Makurdi", "Gboko", "Otukpo", "Katsina-Ala", "Vandeikya"],
    "Borno": ["Maiduguri", "Bama", "Dikwa", "Gwoza", "Monguno"],
    "Cross River": ["Calabar", "Ugep", "Ogoja", "Obudu", "Ikom"],
    "Delta": ["Asaba", "Warri", "Sapele", "Ughelli", "Burutu"],
    "Ebonyi": ["Abakaliki", "Afikpo", "Onueke", "Edda", "Ishielu"],
    "Edo": ["Benin City", "Auchi", "Ekpoma", "Igueben", "Uromi"],
    "Ekiti": ["Ado-Ekiti", "Ikere", "Ijun-Ekiti", "Oye", "Ikole"],
    "Enugu": ["Enugu", "Nsukka", "Agbani", "Udi", "Oji-River"],
    "FCT": ["Abuja", "Gwagwalada", "Kuje", "Bwari", "Kwali"],
    "Gombe": ["Gombe", "Kaltungo", "Bajoga", "Dukku", "Nafada"],
    "Imo": ["Owerri", "Orlu", "Okigwe", "Mgbidi", "Oguta"],
    "Jigawa": ["Dutse", "Hadejia", "Gumel", "Kazaure", "Ringim"],
    "Kaduna": ["Kaduna", "Zaria", "Kafanchan", "Saminaka", "Makarf"],
    "Kano": ["Kano", "Wudil", "Gaya", "Dawakin Kudu", "Bichi"],
    "Katsina": ["Katsina", "Funtua", "Daura", "Malumfashi", "Kankia"],
    "Kebbi": ["Birnin Kebbi", "Argungu", "Yelwa", "Zuru", "Gwandu"],
    "Kogi": ["Lokoja", "Okene", "Idah", "Kabba", "Ankpa"],
    "Kwara": ["Ilorin", "Offa", "Omu-Aran", "Patigi", "Lafiagi"],
    "Lagos": ["Lagos", "Ikeja", "Badagry", "Epe", "Ikorodu"],
    "Nasarawa": ["Lafia", "Keffi", "Akwanga", "Nasarawa", "Karu"],
    "Niger": ["Minna", "Suleja", "Bida", "Kontagora", "Lapai"],
    "Ogun": ["Abeokuta", "Sagamu", "Ijebu-Ode", "Ilaro", "Aiyetoro"],
    "Ondo": ["Akure", "Ondo", "Owo", "Okitipupa", "Ore"],
    "Osun": ["Osogbo", "Ife", "Ilesa", "Iwo", "Ede"],
    "Oyo": ["Ibadan", "Ogbomosho", "Oyo", "Iseyin", "Saki"],
    "Plateau": ["Jos", "Bukuru", "Pankshin", "Shendam", "Langtang"],
    "Rivers": ["Port Harcourt", "Bonny", "Degema", "Okrika", "Oyigbo"],
    "Sokoto": ["Sokoto", "Tambuwal", "Wurno", "Gwadabawa", "Illela"],
    "Taraba": ["Jalingo", "Bali", "Takum", "Wukari", "Serti"],
    "Yobe": ["Damaturu", "Potiskum", "Gashua", "Geidam", "Nguru"],
    "Zamfara": ["Gusau", "Kaura Namoda", "Talata Mafara", "Anka", "Bukkuyum"]
}

# Travel policies (updated with full details)
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

# Budget configuration
ANNUAL_BUDGET = 120000000  # NGN 120,000,000

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(211, 47, 47)  # Red color
        self.cell(0, 10, 'PRUDENTIAL ZENITH LIFE INSURANCE', 0, 1, 'C')
        self.set_font('Arial', 'B', 14)
        self.set_text_color(97, 97, 97)  # Grey color
        self.cell(0, 10, 'Travel Request Report', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def add_section_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(211, 47, 47)
        self.cell(0, 10, title, 0, 1, 'L')
        self.set_draw_color(211, 47, 47)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)
    
    def add_field(self, label, value):
        self.set_font('Arial', 'B', 10)
        self.set_text_color(66, 66, 66)
        self.cell(40, 8, f'{label}:', 0, 0)
        self.set_font('Arial', '', 10)
        self.set_text_color(33, 33, 33)
        self.multi_cell(0, 8, str(value), 0, 1)

# Database initialization with enhanced schema
def init_db():
    conn = sqlite3.connect('travel_app.db')
    c = conn.cursor()
    
    # Users table with additional fields
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
                  bank_name TEXT,
                  account_number TEXT,
                  account_name TEXT,
                  phone_number TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Travel requests table
    c.execute('''CREATE TABLE IF NOT EXISTS travel_requests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
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
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    # Travel costs table with payment tracking
    c.execute('''CREATE TABLE IF NOT EXISTS travel_costs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  request_id INTEGER,
                  grade TEXT,
                  per_diem_amount REAL,
                  flight_cost REAL,
                  total_cost REAL,
                  budgeted_cost REAL,
                  budget_balance REAL,
                  supporting_docs BLOB,
                  admin_notes TEXT,
                  payment_status TEXT DEFAULT 'pending',
                  finance_status TEXT DEFAULT 'pending',
                  approved_by_admin BOOLEAN DEFAULT 0,
                  approved_by_compliance BOOLEAN DEFAULT 0,
                  approved_by_risk BOOLEAN DEFAULT 0,
                  approved_by_finance BOOLEAN DEFAULT 0,
                  approved_by_md BOOLEAN DEFAULT 0,
                  payment_approved_by TEXT,
                  payment_approved_date DATE,
                  payment_completed BOOLEAN DEFAULT 0,
                  payment_date DATE,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (request_id) REFERENCES travel_requests(id))''')
    
    # Approvals table
    c.execute('''CREATE TABLE IF NOT EXISTS approvals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  request_id INTEGER,
                  approver_role TEXT,
                  approver_name TEXT,
                  status TEXT,
                  comments TEXT,
                  approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (request_id) REFERENCES travel_requests(id))''')
    
    # Budget table
    c.execute('''CREATE TABLE IF NOT EXISTS budget
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  year INTEGER,
                  total_budget REAL,
                  utilized_budget REAL,
                  balance REAL,
                  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Payment transactions table
    c.execute('''CREATE TABLE IF NOT EXISTS payments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  cost_id INTEGER,
                  amount REAL,
                  payment_method TEXT,
                  reference_number TEXT,
                  paid_by TEXT,
                  paid_date DATE,
                  status TEXT DEFAULT 'completed',
                  FOREIGN KEY (cost_id) REFERENCES travel_costs(id))''')
    
    # Create default users if they don't exist
    default_users = [
        ("CFO/Executive Director", "cfo_ed", "cfo@prudentialzenith.com", 
         make_hashes("0123456"), "Finance and Investment", "ED", "CFO/ED"),
        ("Managing Director", "md", "md@prudentialzenith.com", 
         make_hashes("123456"), "Office of CEO", "MD", "MD"),
        ("Head of Administration", "head_admin", "head.admin@prudentialzenith.com",
         make_hashes("123456"), "Administration", "DGM", "Head of Administration"),
        ("Chief Compliance Officer", "chief_compliance", "compliance@prudentialzenith.com",
         make_hashes("123456"), "Legal and Compliance", "DGM", "Chief Compliance Officer"),
        ("Chief Risk Officer", "chief_risk", "risk@prudentialzenith.com",
         make_hashes("123456"), "Internal Control and Risk", "DGM", "Chief Risk Officer"),
        ("Payables Officer", "payables", "payables@prudentialzenith.com",
         make_hashes("123456"), "Finance and Investment", "Officer", "Payables Officer")
    ]
    
    for user in default_users:
        try:
            c.execute('''INSERT OR IGNORE INTO users 
                       (full_name, username, email, password, department, grade, role) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)''', user)
        except:
            pass
    
    # Initialize budget for current year
    current_year = datetime.datetime.now().year
    c.execute('''INSERT OR IGNORE INTO budget (year, total_budget, utilized_budget, balance)
                 VALUES (?, ?, 0, ?)''', (current_year, ANNUAL_BUDGET, ANNUAL_BUDGET))
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

def get_approval_flow(department, grade, role):
    """Determine approval flow based on department and role"""
    if department == "Finance and Investment":
        return ["Head of Department", "CFO/ED", "MD"]
    elif department == "Administration":
        return ["Head of Department", "CFO/ED", "MD"]
    elif department in ["Internal Control and Risk", "Internal Audit"]:
        return ["Head of Department", "Chief Risk Officer", "MD"]
    elif department == "HR":
        return ["Head of Department", "MD"]
    elif department == "Agencies":
        return ["Head of Department", "Chief Agency Officer", "MD"]
    elif department == "Legal and Compliance":
        return ["Head of Department", "Chief Compliance Officer", "MD"]
    elif department == "Corporate Sales":
        return ["Head of Department", "Chief Commercial Officer", "MD"]
    elif department == "Office of Executive Director":
        return ["Head of Department", "ED", "MD"]
    elif department == "Office of CEO":
        return ["Head of Department", "MD"]
    else:
        # Default for other departments
        return ["Head of Department", "CFO/ED", "MD"]

def get_payment_approval_flow(total_amount):
    """Get payment approval flow based on amount"""
    if total_amount > 5000000:  # Above 5 million
        return ["Head of Administration", "Chief Compliance Officer", "Chief Risk Officer", "MD"]
    else:
        return ["Head of Administration", "Chief Compliance Officer", "Chief Risk Officer", "ED"]

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
            feeding_cost = policy["feeding"] * 3 * duration_nights
            total = hotel_cost + feeding_cost
        else:
            total = 0  # Receipt required
        return total
    else:
        policy = INTERNATIONAL_POLICY[grade_category]
        return policy["total"] * duration_nights

def get_current_budget():
    """Get current budget information"""
    conn = sqlite3.connect('travel_app.db')
    current_year = datetime.datetime.now().year
    budget = pd.read_sql("SELECT * FROM budget WHERE year = ?", 
                        conn, params=(current_year,)).iloc[0]
    conn.close()
    return budget

def update_budget(amount):
    """Update budget after payment"""
    conn = sqlite3.connect('travel_app.db')
    c = conn.cursor()
    current_year = datetime.datetime.now().year
    c.execute('''UPDATE budget 
                 SET utilized_budget = utilized_budget + ?, 
                     balance = balance - ? 
                 WHERE year = ?''', 
             (amount, amount, current_year))
    conn.commit()
    conn.close()

def generate_pdf_report(request_id):
    """Generate PDF report for travel request"""
    conn = sqlite3.connect('travel_app.db')
    
    # Get request details
    request_query = """
        SELECT tr.*, u.full_name, u.department, u.grade, u.email,
               u.bank_name, u.account_number, u.account_name
        FROM travel_requests tr
        JOIN users u ON tr.user_id = u.id
        WHERE tr.id = ?
    """
    request_data = pd.read_sql(request_query, conn, params=(request_id,)).iloc[0]
    
    # Get cost details
    cost_query = """
        SELECT * FROM travel_costs WHERE request_id = ?
    """
    cost_data = pd.read_sql(cost_query, conn, params=(request_id,))
    
    # Get approval history
    approval_query = """
        SELECT * FROM approvals WHERE request_id = ? ORDER BY approved_at
    """
    approvals = pd.read_sql(approval_query, conn, params=(request_id,))
    
    conn.close()
    
    # Create PDF
    pdf = PDFReport()
    pdf.add_page()
    
    # Add request details
    pdf.add_section_title("Travel Request Details")
    pdf.add_field("Request ID", f"TR-{request_id:06d}")
    pdf.add_field("Employee", request_data['full_name'])
    pdf.add_field("Department", request_data['department'])
    pdf.add_field("Grade", request_data['grade'])
    pdf.add_field("Travel Type", request_data['travel_type'].title())
    pdf.add_field("Destination", request_data['destination'])
    pdf.add_field("Purpose", request_data['purpose'])
    pdf.add_field("Mode of Travel", request_data['mode_of_travel'])
    pdf.add_field("Departure Date", request_data['departure_date'])
    pdf.add_field("Arrival Date", request_data['arrival_date'])
    pdf.add_field("Duration", f"{request_data['duration_days']} days ({request_data['duration_nights']} nights)")
    pdf.add_field("Accommodation", request_data['accommodation_needed'])
    pdf.add_field("Status", request_data['status'].upper())
    
    # Add cost details if available
    if not cost_data.empty:
        pdf.add_section_title("Cost Details")
        cost = cost_data.iloc[0]
        pdf.add_field("Per Diem Amount", f"₦{cost['per_diem_amount']:,.2f}")
        pdf.add_field("Flight Cost", f"₦{cost['flight_cost']:,.2f}")
        pdf.add_field("Total Cost", f"₦{cost['total_cost']:,.2f}")
        pdf.add_field("Payment Status", cost['payment_status'].upper())
        pdf.add_field("Budgeted Cost", f"₦{cost['budgeted_cost']:,.2f}" if cost['budgeted_cost'] else "N/A")
        pdf.add_field("Budget Balance", f"₦{cost['budget_balance']:,.2f}" if cost['budget_balance'] else "N/A")
    
    # Add approval history
    if not approvals.empty:
        pdf.add_section_title("Approval History")
        for _, approval in approvals.iterrows():
            pdf.add_field(f"{approval['approver_role']}", 
                         f"{approval['status'].upper()} - {approval['approved_at']}")
    
    # Add employee bank details
    pdf.add_section_title("Employee Bank Details")
    pdf.add_field("Bank Name", request_data['bank_name'] or "Not Provided")
    pdf.add_field("Account Number", request_data['account_number'] or "Not Provided")
    pdf.add_field("Account Name", request_data['account_name'] or "Not Provided")
    
    # Generate PDF in memory
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    return pdf_bytes

def get_pending_approvals_for_role(role):
    """Get all pending approvals for a specific role"""
    conn = sqlite3.connect('travel_app.db')
    
    # For CFO/ED role
    if role == "CFO/ED":
        query = """
            SELECT tr.*, u.full_name, u.department, u.grade 
            FROM travel_requests tr 
            JOIN users u ON tr.user_id = u.id 
            WHERE tr.status = 'pending' 
            AND tr.current_approver = 'CFO/ED'
            ORDER BY tr.created_at DESC
        """
        approvals = pd.read_sql(query, conn, params=())
    
    # For MD role
    elif role == "MD":
        query = """
            SELECT tr.*, u.full_name, u.department, u.grade 
            FROM travel_requests tr 
            JOIN users u ON tr.user_id = u.id 
            WHERE tr.status = 'pending' 
            AND tr.current_approver = 'MD'
            ORDER BY tr.created_at DESC
        """
        approvals = pd.read_sql(query, conn, params=())
    
    # For Head of Department role - users who are Heads of their departments
    elif role == "Head of Department":
        # Get users who are Heads of their departments
        query = """
            SELECT tr.*, u.full_name, u.department, u.grade 
            FROM travel_requests tr 
            JOIN users u ON tr.user_id = u.id 
            WHERE tr.status = 'pending' 
            AND tr.current_approver = 'Head of Department'
            AND u.department = ?
            ORDER BY tr.created_at DESC
        """
        approvals = pd.read_sql(query, conn, params=(st.session_state.department,))
    
    # For other specific roles like Chief Compliance Officer, etc.
    else:
        query = """
            SELECT tr.*, u.full_name, u.department, u.grade 
            FROM travel_requests tr 
            JOIN users u ON tr.user_id = u.id 
            WHERE tr.status = 'pending' 
            AND tr.current_approver = ?
            ORDER BY tr.created_at DESC
        """
        approvals = pd.read_sql(query, conn, params=(role,))
    
    conn.close()
    return approvals
def process_approval(request_id, action, comments=""):
    """Process approval or rejection of a travel request"""
    conn = sqlite3.connect('travel_app.db')
    c = conn.cursor()
    
    # Get current request details
    c.execute("SELECT * FROM travel_requests WHERE id = ?", (request_id,))
    request = c.fetchone()
    
    if not request:
        conn.close()
        return False, "Request not found"
    
    # Get approval flow
    approval_flow = json.loads(request[15])  # Column 15 is approval_flow
    current_approver = request[13]  # Column 13 is current_approver
    
    # Find current approver index
    try:
        current_index = approval_flow.index(current_approver) if current_approver else -1
    except ValueError:
        conn.close()
        return False, f"Approval flow error: {current_approver} not found in {approval_flow}"
    
    if action == "approve":
        # Move to next approver or complete
        if current_index + 1 < len(approval_flow):
            next_approver = approval_flow[current_index + 1]
            new_status = "pending"
            current_approver = next_approver
        else:
            new_status = "approved"
            current_approver = None
        
        # Update request
        c.execute("""
            UPDATE travel_requests 
            SET status = ?, current_approver = ? 
            WHERE id = ?
        """, (new_status, current_approver, request_id))
        
        # Record approval
        c.execute("""
            INSERT INTO approvals 
            (request_id, approver_role, approver_name, status, comments) 
            VALUES (?, ?, ?, ?, ?)
        """, (request_id, st.session_state.role, st.session_state.full_name, 
              "approved", comments))
        
        message = "Request approved"
        
    elif action == "reject":
        # Update request to rejected
        c.execute("""
            UPDATE travel_requests 
            SET status = 'rejected', current_approver = NULL 
            WHERE id = ?
        """, (request_id,))
        
        # Record rejection
        c.execute("""
            INSERT INTO approvals 
            (request_id, approver_role, approver_name, status, comments) 
            VALUES (?, ?, ?, ?, ?)
        """, (request_id, st.session_state.role, st.session_state.full_name, 
              "rejected", comments))
        
        message = "Request rejected"
    
    conn.commit()
    conn.close()
    return True, message

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
        
        # Quick login info
        st.markdown('<div class="quick-login">', unsafe_allow_html=True)
        st.markdown('<h4>🔑 Quick Login (Test Credentials)</h4>', unsafe_allow_html=True)
        st.markdown("""
        - **CFO/ED**: Username: `cfo_ed` | Password: `0123456`
        - **MD**: Username: `md` | Password: `123456`
        - **Head of Admin**: Username: `head_admin` | Password: `123456`
        - **Chief Compliance**: Username: `chief_compliance` | Password: `123456`
        - **Chief Risk**: Username: `chief_risk` | Password: `123456`
        - **Payables**: Username: `payables` | Password: `123456`
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Authentication logic
        if login_btn:
            if not username or not password:
                st.error("⚠️ Please enter both username and password")
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
                    st.session_state.user_id = user[0]
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
    st.markdown('Prudential Zenith Life Insurance • Travel Management System v2.0')
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
            grade = st.selectbox("Grade*", GRADES)
        
        with col2:
            password = st.text_input("Password*", type="password")
            confirm_password = st.text_input("Confirm Password*", type="password")
            role = st.selectbox("Role*", ROLES)
            phone_number = st.text_input("Phone Number")
        
        st.markdown("### Bank Details (Optional)")
        col3, col4 = st.columns(2)
        with col3:
            bank_name = st.text_input("Bank Name")
            account_number = st.text_input("Account Number")
        with col4:
            account_name = st.text_input("Account Name")
        
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
                                 (full_name, username, email, password, department, grade, role, 
                                  profile_pic, bank_name, account_number, account_name, phone_number) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                             (full_name, username, email, make_hashes(password), 
                              department, grade, role, pic_data, bank_name, 
                              account_number, account_name, phone_number))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success("Account created successfully! Please login.")
                    time.sleep(2)
                    st.session_state.show_registration = False
                    st.rerun()

def profile_update():
    """Profile update form"""
    st.markdown('<h1 class="sub-header">Update Profile</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    user_data = pd.read_sql("SELECT * FROM users WHERE username = ?", 
                           conn, params=(st.session_state.username,)).iloc[0]
    
    with st.form("profile_update_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name*", value=user_data['full_name'])
            username = st.text_input("Username (Employee ID)*", value=user_data['username'])
            email = st.text_input("Email Address*", value=user_data['email'])
            phone_number = st.text_input("Phone Number", value=user_data['phone_number'] or "")
        
        with col2:
            bank_name = st.text_input("Bank Name", value=user_data['bank_name'] or "")
            account_number = st.text_input("Account Number", value=user_data['account_number'] or "")
            account_name = st.text_input("Account Name", value=user_data['account_name'] or "")
        
        profile_pic = st.file_uploader("Update Profile Picture", type=['jpg', 'jpeg', 'png'])
        
        # Display current profile picture
        if user_data['profile_pic']:
            st.image(user_data['profile_pic'], width=150, caption="Current Profile Picture")
        
        submitted = st.form_submit_button("Update Profile")
        
        if submitted:
            if not all([full_name, username, email]):
                st.error("Please fill in all required fields")
            else:
                # Update profile picture
                pic_data = user_data['profile_pic']
                if profile_pic:
                    pic_data = profile_pic.read()
                
                # Update user
                c = conn.cursor()
                c.execute("""UPDATE users 
                             SET full_name = ?, email = ?, phone_number = ?,
                                 bank_name = ?, account_number = ?, account_name = ?,
                                 profile_pic = ?
                             WHERE username = ?""",
                         (full_name, email, phone_number, bank_name, 
                          account_number, account_name, pic_data, st.session_state.username))
                
                conn.commit()
                conn.close()
                
                # Update session state
                st.session_state.full_name = full_name
                
                st.success("Profile updated successfully!")
                time.sleep(2)
                st.rerun()

def dashboard():
    """Main dashboard"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #D32F2F 0%, #B71C1C 100%); border-radius: 10px; margin-bottom: 20px;">
            <h3 style="color: white; margin-bottom: 5px;">PRUDENTIAL ZENITH</h3>
            <p style="color: rgba(255,255,255,0.9); font-size: 0.9rem;">Travel Management System</p>
        </div>
        """, unsafe_allow_html=True)
        
        # User info card
        st.markdown(f"""
        <div style="background: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <div style="text-align: center;">
                <h4 style="color: #D32F2F; margin-bottom: 10px;">{st.session_state.full_name}</h4>
                <p style="color: #616161; margin: 5px 0;"><strong>Role:</strong> {st.session_state.role}</p>
                <p style="color: #616161; margin: 5px 0;"><strong>Dept:</strong> {st.session_state.department}</p>
                <p style="color: #616161; margin: 5px 0;"><strong>Grade:</strong> {st.session_state.grade}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        menu_options = ["Dashboard", "My Profile", "Update Profile", "Travel Request", 
                       "Travel History", "Payment Status", "Analytics"]
        
        # Add Approvals based on role
        if st.session_state.role in ["MD", "ED", "CFO/ED", "Head of Department", 
                                    "Chief Commercial Officer", "Chief Agency Officer",
                                    "Chief Compliance Officer", "Chief Risk Officer"]:
            menu_options.append("Approvals")
        
        # Role-based navigation
        if st.session_state.role in ["Head of Administration", "admin"]:
            menu_options.extend(["Admin Panel", "Payment Approvals", "Budget Analytics"])
        elif st.session_state.role == "Chief Compliance Officer":
            menu_options.extend(["Compliance Approvals"])
        elif st.session_state.role == "Chief Risk Officer":
            menu_options.extend(["Risk Approvals"])
        elif st.session_state.role in ["CFO/ED", "MD"]:
            menu_options.extend(["Final Approvals"])
        elif st.session_state.role == "Payables Officer":
            menu_options.extend(["Payment Processing"])
        
        selected = option_menu(
            menu_title="Navigation",
            options=menu_options,
            icons=["house", "person", "pencil", "airplane", "clock-history", "credit-card", "graph-up",
                   "check-circle", "gear", "check-circle", "calculator", "shield-check", "shield-exclamation", 
                   "check-square", "cash"] if st.session_state.role in ["Head of Administration", "admin"] else
                   ["house", "person", "pencil", "airplane", "clock-history", "credit-card", "graph-up",
                   "check-circle"],
            menu_icon="compass",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "#D32F2F", "font-size": "18px"}, 
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "2px", "padding": "10px 15px",
                           "border-radius": "8px", "--hover-color": "#f0f0f0"},
                "nav-link-selected": {"background-color": "#D32F2F", "color": "white", "font-weight": "bold"},
            }
        )
        
        # Budget info for admin
        if st.session_state.role in ["Head of Administration", "admin"]:
            budget = get_current_budget()
            utilization = (budget['utilized_budget'] / budget['total_budget']) * 100
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                        padding: 15px; border-radius: 10px; margin-top: 20px; border-left: 4px solid #D32F2F;">
                <h5 style="color: #424242; margin-bottom: 10px;">💰 Budget Overview</h5>
                <p style="color: #616161; margin: 5px 0; font-size: 0.9rem;">
                    <strong>Total:</strong> ₦{budget['total_budget']:,.0f}
                </p>
                <p style="color: #616161; margin: 5px 0; font-size: 0.9rem;">
                    <strong>Utilized:</strong> ₦{budget['utilized_budget']:,.0f}
                </p>
                <p style="color: #616161; margin: 5px 0; font-size: 0.9rem;">
                    <strong>Balance:</strong> ₦{budget['balance']:,.0f}
                </p>
                <div style="background: #e0e0e0; height: 8px; border-radius: 4px; margin-top: 10px;">
                    <div style="background: {'#4CAF50' if utilization < 80 else '#F44336'}; 
                                width: {min(utilization, 100)}%; height: 100%; border-radius: 4px;"></div>
                </div>
                <p style="color: #616161; margin-top: 5px; font-size: 0.8rem; text-align: center;">
                    {utilization:.1f}% utilized
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            st.session_state.logged_in = False
            st.session_state.username = ''
            st.session_state.role = ''
            st.rerun()
    
    # Main content based on selection
    if selected == "Dashboard":
        show_dashboard()
    elif selected == "My Profile":
        show_profile()
    elif selected == "Update Profile":
        profile_update()
    elif selected == "Travel Request":
        travel_request_form()
    elif selected == "Travel History":
        travel_history()
    elif selected == "Payment Status":
        payment_status()
    elif selected == "Analytics":
        analytics_dashboard()
    elif selected == "Approvals":
        show_approvals()
    elif selected == "Admin Panel":
        admin_panel()
    elif selected == "Payment Approvals":
        payment_approvals()
    elif selected == "Budget Analytics":
        budget_analytics()
    elif selected == "Compliance Approvals":
        compliance_approvals()
    elif selected == "Risk Approvals":
        risk_approvals()
    elif selected == "Final Approvals":
        final_approvals()
    elif selected == "Payment Processing":
        payment_processing()

def show_dashboard():
    """Dashboard overview"""
    st.markdown('<h1 class="main-header">Dashboard Overview</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_travel = pd.read_sql("SELECT COUNT(*) as count FROM travel_requests WHERE user_id = ?", 
                                  conn, params=(st.session_state.user_id,)).iloc[0]['count']
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #D32F2F;">{total_travel}</h3>
            <p style="color: #616161;">Total Travel</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        pending = pd.read_sql("""SELECT COUNT(*) as count FROM travel_requests 
                               WHERE user_id = ? AND status = 'pending'""", 
                             conn, params=(st.session_state.user_id,)).iloc[0]['count']
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #FF9800;">{pending}</h3>
            <p style="color: #616161;">Pending</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        approved = pd.read_sql("""SELECT COUNT(*) as count FROM travel_requests 
                                WHERE user_id = ? AND status = 'approved'""", 
                              conn, params=(st.session_state.user_id,)).iloc[0]['count']
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #4CAF50;">{approved}</h3>
            <p style="color: #616161;">Approved</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if st.session_state.role in ["Head of Administration", "admin"]:
            pending_payments = pd.read_sql("""SELECT COUNT(*) as count FROM travel_costs 
                                            WHERE payment_status = 'pending'""", conn).iloc[0]['count']
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #9C27B0;">{pending_payments}</h3>
                <p style="color: #616161;">Pending Payments</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            paid = pd.read_sql("""SELECT COUNT(*) as count FROM travel_costs tc
                                JOIN travel_requests tr ON tc.request_id = tr.id
                                WHERE tr.user_id = ? AND tc.payment_status = 'paid'""", 
                              conn, params=(st.session_state.user_id,)).iloc[0]['count']
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #2196F3;">{paid}</h3>
                <p style="color: #616161;">Paid</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent travel requests
    st.markdown("### Recent Travel Requests")
    recent_travel = pd.read_sql("""SELECT * FROM travel_requests 
                                 WHERE user_id = ? 
                                 ORDER BY created_at DESC LIMIT 5""", 
                               conn, params=(st.session_state.user_id,))
    
    if not recent_travel.empty:
        for _, row in recent_travel.iterrows():
            status_color = {
                'approved': '#28a745',
                'pending': '#ffc107',
                'rejected': '#dc3545'
            }.get(row['status'], '#616161')
            
            st.markdown(f"""
            <div class="card" style="border-left-color: {status_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="color: #D32F2F; margin: 0;">{row['destination']}</h4>
                    <span class="approval-badge {row['status']}-badge">{row['status'].upper()}</span>
                </div>
                <p><strong>Type:</strong> {row['travel_type'].title()} | <strong>Purpose:</strong> {row['purpose']}</p>
                <p><strong>Dates:</strong> {row['departure_date']} to {row['arrival_date']} ({row['duration_days']} days)</p>
                <p><strong>Current Approver:</strong> {row['current_approver'] if row['current_approver'] else 'Completed'}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No travel requests yet")
    
    # Budget overview for admin
    if st.session_state.role in ["Head of Administration", "admin"]:
        st.markdown("---")
        st.markdown("### Budget Overview")
        
        budget = get_current_budget()
        col5, col6, col7 = st.columns(3)
        
        with col5:
            st.metric("Total Budget", f"₦{budget['total_budget']:,.0f}")
        with col6:
            st.metric("Utilized", f"₦{budget['utilized_budget']:,.0f}")
        with col7:
            st.metric("Balance", f"₦{budget['balance']:,.0f}")
        
        # Progress bar
        utilization = (budget['utilized_budget'] / budget['total_budget']) * 100
        st.markdown(f"""
        <div style="margin-top: 20px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="color: #616161;">Budget Utilization</span>
                <span style="color: #616161; font-weight: bold;">{utilization:.1f}%</span>
            </div>
            <div class="budget-bar{' budget-bar-over' if utilization > 100 else ''}" 
                 style="width: {min(utilization, 100)}%;">
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    conn.close()

def show_profile():
    """User profile page"""
    st.markdown('<h1 class="sub-header">My Profile</h1>', unsafe_allow_html=True)
    
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
        st.markdown(f"**Phone:** {user_data['phone_number'] or 'Not provided'}")
        st.markdown(f"**Department:** {user_data['department']}")
        st.markdown(f"**Grade:** {user_data['grade']}")
        st.markdown(f"**Role:** {user_data['role']}")
        
        if user_data['bank_name'] and user_data['account_number']:
            st.markdown("### Bank Details")
            st.markdown(f"**Bank:** {user_data['bank_name']}")
            st.markdown(f"**Account Number:** {user_data['account_number']}")
            st.markdown(f"**Account Name:** {user_data['account_name']}")
    
    conn.close()

def travel_request_form():
    """Travel request form"""
    st.markdown('<h1 class="sub-header">New Travel Request</h1>', unsafe_allow_html=True)
    
    travel_type = st.radio("Travel Type", ["Local", "International"], horizontal=True)
    
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
            
            accommodation = st.radio("Accommodation Needed?", ["Yes", "No"], horizontal=True)
        
        # Auto-calculate duration
        if departure_date and arrival_date:
            duration_days = (arrival_date - departure_date).days + 1
            duration_nights = (arrival_date - departure_date).days
            
            st.info(f"**Duration:** {duration_days} days ({duration_nights} nights)")
        else:
            duration_days = 0
            duration_nights = 0
        
        submitted = st.form_submit_button("Submit Request", type="primary")
        
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
                          (user_id, username, travel_type, destination, city, purpose, 
                          mode_of_travel, departure_date, arrival_date, 
                          accommodation_needed, duration_days, duration_nights, 
                          current_approver, approval_flow) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         (st.session_state.user_id,
                          st.session_state.username, 
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
                          (request_id, approver_role, approver_name, status) 
                          VALUES (?, ?, ?, ?)""",
                         (request_id, approval_flow[0], "System", "pending"))
                
                conn.commit()
                conn.close()
                
                st.success("✅ Travel request submitted successfully!")
                st.info(f"**Approval Flow:** {' → '.join(approval_flow)}")
                
                # Calculate estimated costs
                grade_category = get_grade_category(st.session_state.grade)
                
                if travel_type == "Local":
                    policy = LOCAL_POLICY[grade_category]
                    st.markdown("### Estimated Allowances (Local)")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Hotel Allowance", 
                                 f"₦{policy['hotel']:,}/night" if isinstance(policy['hotel'], int) else policy['hotel'])
                    with col_b:
                        st.metric("Feeding Allowance",
                                 f"₦{policy['feeding']:,}/meal" if isinstance(policy['feeding'], int) else policy['feeding'])
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
    with col3:
        year_filter = st.selectbox("Filter by Year", 
                                  ["All"] + list(range(2023, datetime.datetime.now().year + 2)))
    
    # Build query
    query = """SELECT tr.*, tc.payment_status, tc.total_cost 
               FROM travel_requests tr 
               LEFT JOIN travel_costs tc ON tr.id = tc.request_id 
               WHERE tr.user_id = ?"""
    params = [st.session_state.user_id]
    
    if status_filter != "All":
        query += " AND tr.status = ?"
        params.append(status_filter)
    
    if type_filter != "All":
        query += " AND tr.travel_type = ?"
        params.append(type_filter)
    
    if year_filter != "All":
        query += " AND strftime('%Y', tr.created_at) = ?"
        params.append(str(year_filter))
    
    query += " ORDER BY tr.created_at DESC"
    
    travel_data = pd.read_sql(query, conn, params=params)
    
    if not travel_data.empty:
        # Export button
        if st.button("📊 Export to Excel"):
            excel_file = travel_data.to_excel(index=False)
            st.download_button(
                label="Download Excel",
                data=excel_file,
                file_name=f"travel_history_{st.session_state.username}_{date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        for _, row in travel_data.iterrows():
            with st.expander(f"{row['destination']} - {row['status'].upper()} ({row['created_at'][:10]})", expanded=False):
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.markdown(f"**Request ID:** TR-{row['id']:06d}")
                    st.markdown(f"**Type:** {row['travel_type'].title()}")
                    st.markdown(f"**Purpose:** {row['purpose']}")
                    st.markdown(f"**Mode:** {row['mode_of_travel']}")
                
                with col_b:
                    st.markdown(f"**Departure:** {row['departure_date']}")
                    st.markdown(f"**Arrival:** {row['arrival_date']}")
                    st.markdown(f"**Duration:** {row['duration_days']} days")
                    st.markdown(f"**Accommodation:** {row['accommodation_needed']}")
                
                with col_c:
                    status_badge = f"<span class='approval-badge {row['status']}-badge'>{row['status'].upper()}</span>"
                    st.markdown(f"**Status:** {status_badge}", unsafe_allow_html=True)
                    
                    if pd.notna(row['payment_status']):
                        payment_badge = f"<span class='approval-badge {row['payment_status']}-badge'>{row['payment_status'].upper()}</span>"
                        st.markdown(f"**Payment:** {payment_badge}", unsafe_allow_html=True)
                    
                    if pd.notna(row['total_cost']):
                        st.markdown(f"**Total Cost:** ₦{row['total_cost']:,.2f}")
                
                # Download PDF button
                if st.button(f"📄 Download Report", key=f"pdf_{row['id']}"):
                    pdf_bytes = generate_pdf_report(row['id'])
                    st.download_button(
                        label="Click to Download PDF",
                        data=pdf_bytes,
                        file_name=f"travel_report_{row['id']}.pdf",
                        mime="application/pdf",
                        key=f"download_{row['id']}"
                    )
                
                st.markdown("---")
    else:
        st.info("No travel records found")
    
    conn.close()

def payment_status():
    """Payment status page"""
    st.markdown('<h1 class="sub-header">Payment Status</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # Get payment data for user
    query = """
        SELECT tr.id, tr.destination, tr.purpose, tr.departure_date, tr.arrival_date,
               tc.total_cost, tc.payment_status, tc.payment_completed,
               tc.payment_date, tc.payment_approved_by
        FROM travel_requests tr
        JOIN travel_costs tc ON tr.id = tc.request_id
        WHERE tr.user_id = ? AND tc.total_cost IS NOT NULL
        ORDER BY tr.created_at DESC
    """
    
    payment_data = pd.read_sql(query, conn, params=(st.session_state.user_id,))
    
    if not payment_data.empty:
        for _, row in payment_data.iterrows():
            status_color = {
                'paid': '#28a745',
                'approved': '#17a2b8',
                'pending': '#ffc107',
                'rejected': '#dc3545'
            }.get(row['payment_status'], '#616161')
            
            st.markdown(f"""
            <div class="card" style="border-left-color: {status_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="color: #D32F2F; margin: 0;">{row['destination']}</h4>
                    <span class="approval-badge {row['payment_status']}-badge">
                        {row['payment_status'].upper()}
                    </span>
                </div>
                <p><strong>Purpose:</strong> {row['purpose']}</p>
                <p><strong>Dates:</strong> {row['departure_date']} to {row['arrival_date']}</p>
                <p><strong>Amount:</strong> ₦{row['total_cost']:,.2f}</p>
                {f"<p><strong>Approved By:</strong> {row['payment_approved_by']}</p>" if row['payment_approved_by'] else ""}
                {f"<p><strong>Payment Date:</strong> {row['payment_date']}</p>" if row['payment_date'] else ""}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No payment records found")
    
    conn.close()

def show_approvals():
    """Display pending approvals for the current user's role"""
    if st.session_state.role not in ["MD", "ED", "CFO/ED", "Head of Department", 
                                    "Chief Commercial Officer", "Chief Agency Officer",
                                    "Chief Compliance Officer", "Chief Risk Officer"]:
        st.warning("You don't have approval privileges")
        return
    
    st.markdown('<h1 class="sub-header">Pending Approvals</h1>', unsafe_allow_html=True)
    
    # Get pending approvals for current role
    pending_approvals = get_pending_approvals_for_role(st.session_state.role)
    
    if not pending_approvals.empty:
        st.info(f"You have {len(pending_approvals)} pending approval(s)")
        
        for _, row in pending_approvals.iterrows():
            with st.container():
                st.markdown(f"### 📋 Travel Request #{row['id']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Employee:** {row['full_name']}")
                    st.markdown(f"**Department:** {row['department']}")
                    st.markdown(f"**Grade:** {row['grade']}")
                    st.markdown(f"**Type:** {row['travel_type'].title()}")
                    st.markdown(f"**Destination:** {row['destination']}")
                
                with col2:
                    st.markdown(f"**Purpose:** {row['purpose']}")
                    st.markdown(f"**Mode of Travel:** {row['mode_of_travel']}")
                    st.markdown(f"**Departure:** {row['departure_date']}")
                    st.markdown(f"**Arrival:** {row['arrival_date']}")
                    st.markdown(f"**Duration:** {row['duration_days']} days")
                    st.markdown(f"**Accommodation:** {row['accommodation_needed']}")
                
                # Show approval flow
                approval_flow = json.loads(row['approval_flow'])
                current_index = approval_flow.index(row['current_approver']) if row['current_approver'] in approval_flow else -1
                
                st.markdown("**Approval Flow:**")
                cols = st.columns(len(approval_flow))
                for i, approver in enumerate(approval_flow):
                    with cols[i]:
                        if i < current_index:
                            st.markdown(f"✅ {approver}")
                        elif i == current_index:
                            st.markdown(f"⏳ **{approver}** (Current - YOU)")
                        else:
                            st.markdown(f"⏭️ {approver}")
                
                # Approval actions
                st.markdown("---")
                col_a, col_b = st.columns(2)
                
                with col_a:
                    if st.button(f"✅ Approve", key=f"approve_{row['id']}", type="primary"):
                        success, message = process_approval(row['id'], "approve")
                        if success:
                            st.success(message)
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(message)
                
                with col_b:
                    if st.button(f"❌ Reject", key=f"reject_{row['id']}"):
                        comments = st.text_input("Reason for rejection", key=f"reject_reason_{row['id']}")
                        if comments:
                            success, message = process_approval(row['id'], "reject", comments)
                            if success:
                                st.error(message)
                                time.sleep(2)
                                st.rerun()
                        else:
                            st.warning("Please provide a reason for rejection")
                
                st.markdown("---")
    else:
        st.success("🎉 No pending approvals! You're all caught up.")
def admin_panel():
    """Admin panel for managing travel costs"""
    if st.session_state.role not in ["Head of Administration", "admin"]:
        st.warning("Access denied")
        return
    
    st.markdown('<h1 class="sub-header">Admin Panel - Travel Cost Management</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # Get approved travel requests needing cost input
    query = """
        SELECT tr.*, u.full_name, u.grade, u.department, tc.id as cost_id 
        FROM travel_requests tr 
        JOIN users u ON tr.user_id = u.id 
        LEFT JOIN travel_costs tc ON tr.id = tc.request_id 
        WHERE tr.status = 'approved' 
        AND (tc.id IS NULL OR tc.payment_status = 'pending' OR tc.payment_status = 'draft')
        ORDER BY tr.created_at DESC
    """
    
    approved_requests = pd.read_sql(query, conn)
    
    if not approved_requests.empty:
        for _, row in approved_requests.iterrows():
            with st.expander(f"{row['full_name']} - {row['destination']} ({row['travel_type']})", expanded=False):
                
                # Get current budget
                budget = get_current_budget()
                
                # Calculate estimated costs
                grade_category = get_grade_category(row['grade'])
                estimated_cost = calculate_travel_costs(row['grade'], row['travel_type'], row['duration_nights'])
                
                # Cost input form
                with st.form(f"cost_form_{row['id']}"):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        flight_cost = st.number_input("Flight Cost (NGN)", 
                                                     min_value=0.0, 
                                                     value=0.0,
                                                     key=f"flight_{row['id']}")
                        
                        budgeted_cost = st.number_input("Budgeted Cost (NGN)",
                                                       min_value=0.0,
                                                       value=float(estimated_cost) + 100000,
                                                       key=f"budget_{row['id']}")
                    
                    with col_b:
                        budget_balance = budget['balance'] - budgeted_cost
                        st.metric("Current Budget Balance", f"₦{budget['balance']:,.0f}")
                        st.metric("After This Request", f"₦{budget_balance:,.0f}", 
                                 delta=f"-₦{budgeted_cost:,.0f}")
                    
                    supporting_docs = st.file_uploader("Supporting Documents", 
                                                      type=['pdf', 'jpg', 'png'],
                                                      key=f"docs_{row['id']}")
                    
                    admin_notes = st.text_area("Admin Notes", key=f"notes_{row['id']}")
                    
                    col_c, col_d = st.columns(2)
                    with col_c:
                        submit_btn = st.form_submit_button("Submit for Payment Approval", type="primary")
                    with col_d:
                        save_btn = st.form_submit_button("Save as Draft")
                    
                    if submit_btn or save_btn:
                        total_cost = estimated_cost + flight_cost
                        
                        c = conn.cursor()
                        
                        # Check if cost record exists
                        c.execute("SELECT id FROM travel_costs WHERE request_id = ?", (row['id'],))
                        existing_cost = c.fetchone()
                        
                        if not existing_cost:
                            # Insert new cost record
                            c.execute("""INSERT INTO travel_costs 
                                       (request_id, grade, per_diem_amount, flight_cost, 
                                        total_cost, budgeted_cost, budget_balance,
                                        admin_notes, payment_status, approved_by_admin) 
                                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                     (row['id'], row['grade'], estimated_cost, flight_cost,
                                      total_cost, budgeted_cost, budget_balance,
                                      admin_notes, "pending" if submit_btn else "draft", 1))
                        else:
                            # Update existing cost record
                            c.execute("""UPDATE travel_costs 
                                       SET per_diem_amount = ?, flight_cost = ?, 
                                           total_cost = ?, budgeted_cost = ?, budget_balance = ?,
                                           admin_notes = ?, payment_status = ?, approved_by_admin = 1 
                                       WHERE request_id = ?""",
                                     (estimated_cost, flight_cost, total_cost, budgeted_cost,
                                      budget_balance, admin_notes, 
                                      "pending" if submit_btn else "draft", row['id']))
                        
                        # Create approval record
                        if submit_btn:
                            c.execute("""INSERT INTO approvals 
                                       (request_id, approver_role, approver_name, status, comments)
                                       VALUES (?, ?, ?, ?, ?)""",
                                     (row['id'], "Head of Administration", st.session_state.full_name,
                                      "approved", "Costs submitted for payment approval"))
                        
                        conn.commit()
                        
                        if submit_btn:
                            st.success("✅ Costs submitted for payment approval!")
                            st.info("**Next:** Chief Compliance Officer approval")
                        else:
                            st.info("💾 Draft saved successfully")
                        
                        time.sleep(2)
                        st.rerun()
    else:
        st.info("No approved requests pending cost input")
    
    conn.close()

def payment_approvals():
    """Payment approval workflow"""
    if st.session_state.role not in ["Head of Administration", "Chief Compliance Officer", 
                                    "Chief Risk Officer", "CFO/ED", "MD", "admin"]:
        st.warning("Access denied")
        return
    
    st.markdown('<h1 class="sub-header">Payment Approvals</h1>', unsafe_allow_html=True)
    
    # Role-based filtering
    if st.session_state.role == "Head of Administration":
        status_filter = "approved_by_admin = 1 AND approved_by_compliance = 0"
    elif st.session_state.role == "Chief Compliance Officer":
        status_filter = "approved_by_admin = 1 AND approved_by_compliance = 0"
    elif st.session_state.role == "Chief Risk Officer":
        status_filter = "approved_by_admin = 1 AND approved_by_compliance = 1 AND approved_by_risk = 0"
    elif st.session_state.role in ["CFO/ED", "MD"]:
        status_filter = "approved_by_admin = 1 AND approved_by_compliance = 1 AND approved_by_risk = 1 AND approved_by_finance = 0"
    else:
        status_filter = "1=1"
    
    conn = sqlite3.connect('travel_app.db')
    
    query = f"""
        SELECT tc.*, tr.destination, tr.purpose, u.full_name, u.department, u.grade
        FROM travel_costs tc
        JOIN travel_requests tr ON tc.request_id = tr.id
        JOIN users u ON tr.user_id = u.id
        WHERE tc.payment_status = 'pending' AND {status_filter}
        ORDER BY tc.created_at DESC
    """
    
    pending_payments = pd.read_sql(query, conn)
    
    if not pending_payments.empty:
        for _, row in pending_payments.iterrows():
            with st.container():
                st.markdown(f"### 💰 Payment Request #{row['id']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Employee:** {row['full_name']}")
                    st.markdown(f"**Department:** {row['department']}")
                    st.markdown(f"**Grade:** {row['grade']}")
                    st.markdown(f"**Destination:** {row['destination']}")
                    st.markdown(f"**Purpose:** {row['purpose']}")
                
                with col2:
                    st.markdown(f"**Per Diem:** ₦{row['per_diem_amount']:,.2f}")
                    st.markdown(f"**Flight Cost:** ₦{row['flight_cost']:,.2f}")
                    st.markdown(f"**Total Cost:** ₦{row['total_cost']:,.2f}")
                    st.markdown(f"**Budgeted:** ₦{row['budgeted_cost']:,.2f}")
                    st.markdown(f"**Budget Balance:** ₦{row['budget_balance']:,.2f}")
                
                # Get payment approval flow
                approval_flow = get_payment_approval_flow(row['total_cost'])
                
                # Show current approval position
                current_stage = 0
                if row['approved_by_admin']:
                    current_stage += 1
                if row['approved_by_compliance']:
                    current_stage += 1
                if row['approved_by_risk']:
                    current_stage += 1
                
                st.markdown("**Approval Progress:**")
                cols = st.columns(len(approval_flow))
                for i, approver in enumerate(approval_flow):
                    with cols[i]:
                        if i < current_stage:
                            st.markdown(f"✅ {approver}")
                        elif i == current_stage:
                            st.markdown(f"⏳ **{approver}** (Current)")
                        else:
                            st.markdown(f"⏭️ {approver}")
                
                # Approval actions
                if (st.session_state.role == "Head of Administration" and not row['approved_by_compliance']) or \
                   (st.session_state.role == "Chief Compliance Officer" and row['approved_by_admin'] and not row['approved_by_compliance']) or \
                   (st.session_state.role == "Chief Risk Officer" and row['approved_by_compliance'] and not row['approved_by_risk']) or \
                   (st.session_state.role in ["CFO/ED", "MD"] and row['approved_by_risk'] and not row['approved_by_finance']):
                    
                    st.markdown("---")
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        if st.button(f"✅ Approve Payment", key=f"approve_pay_{row['id']}", type="primary"):
                            c = conn.cursor()
                            
                            # Update based on role
                            if st.session_state.role == "Head of Administration":
                                c.execute("UPDATE travel_costs SET approved_by_compliance = 1 WHERE id = ?", (row['id'],))
                            elif st.session_state.role == "Chief Compliance Officer":
                                c.execute("UPDATE travel_costs SET approved_by_compliance = 1 WHERE id = ?", (row['id'],))
                            elif st.session_state.role == "Chief Risk Officer":
                                c.execute("UPDATE travel_costs SET approved_by_risk = 1 WHERE id = ?", (row['id'],))
                            elif st.session_state.role == "CFO/ED":
                                if row['total_cost'] <= 5000000:
                                    c.execute("""UPDATE travel_costs 
                                               SET approved_by_finance = 1, payment_status = 'approved',
                                                   payment_approved_by = ?, payment_approved_date = DATE('now')
                                               WHERE id = ?""", 
                                             (st.session_state.full_name, row['id']))
                                else:
                                    c.execute("UPDATE travel_costs SET approved_by_finance = 1 WHERE id = ?", (row['id'],))
                            elif st.session_state.role == "MD":
                                c.execute("""UPDATE travel_costs 
                                           SET approved_by_md = 1, payment_status = 'approved',
                                               payment_approved_by = ?, payment_approved_date = DATE('now')
                                           WHERE id = ?""", 
                                         (st.session_state.full_name, row['id']))
                            
                            # Record approval
                            c.execute("""INSERT INTO approvals 
                                       (request_id, approver_role, approver_name, status, comments)
                                       VALUES (?, ?, ?, ?, ?)""",
                                     (row['request_id'], st.session_state.role, 
                                      st.session_state.full_name, "approved",
                                      f"Payment approved - ₦{row['total_cost']:,.2f}"))
                            
                            conn.commit()
                            st.success("✅ Payment approved!")
                            time.sleep(2)
                            st.rerun()
                    
                    with col_b:
                        if st.button(f"❌ Reject", key=f"reject_pay_{row['id']}"):
                            c = conn.cursor()
                            c.execute("""UPDATE travel_costs 
                                       SET payment_status = 'rejected',
                                           payment_approved_by = ?, payment_approved_date = DATE('now')
                                       WHERE id = ?""", 
                                     (st.session_state.full_name, row['id']))
                            
                            c.execute("""INSERT INTO approvals 
                                       (request_id, approver_role, approver_name, status, comments)
                                       VALUES (?, ?, ?, ?, ?)""",
                                     (row['request_id'], st.session_state.role, 
                                      st.session_state.full_name, "rejected",
                                      "Payment rejected"))
                            
                            conn.commit()
                            st.error("❌ Payment rejected!")
                            time.sleep(2)
                            st.rerun()
                
                st.markdown("---")
    else:
        st.info("No pending payment approvals for your role")
    
    conn.close()

def compliance_approvals():
    """Compliance approval page"""
    if st.session_state.role != "Chief Compliance Officer":
        st.warning("Access denied")
        return
    
    payment_approvals()

def risk_approvals():
    """Risk approval page"""
    if st.session_state.role != "Chief Risk Officer":
        st.warning("Access denied")
        return
    
    payment_approvals()

def final_approvals():
    """Final approval page for CFO/ED and MD"""
    if st.session_state.role not in ["CFO/ED", "MD"]:
        st.warning("Access denied")
        return
    
    payment_approvals()

def payment_processing():
    """Payment processing for Payables Officer"""
    if st.session_state.role != "Payables Officer":
        st.warning("Access denied")
        return
    
    st.markdown('<h1 class="sub-header">Payment Processing</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # Get approved payments
    query = """
        SELECT tc.*, tr.destination, u.full_name, u.bank_name, u.account_number, u.account_name
        FROM travel_costs tc
        JOIN travel_requests tr ON tc.request_id = tr.id
        JOIN users u ON tr.user_id = u.id
        WHERE tc.payment_status = 'approved' AND tc.payment_completed = 0
        ORDER BY tc.payment_approved_date DESC
    """
    
    approved_payments = pd.read_sql(query, conn)
    
    if not approved_payments.empty:
        for _, row in approved_payments.iterrows():
            with st.expander(f"Payment #{row['id']} - {row['full_name']} - ₦{row['total_cost']:,.2f}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Employee:** {row['full_name']}")
                    st.markdown(f"**Destination:** {row['destination']}")
                    st.markdown(f"**Amount:** ₦{row['total_cost']:,.2f}")
                    st.markdown(f"**Approved By:** {row['payment_approved_by']}")
                    st.markdown(f"**Approved Date:** {row['payment_approved_date']}")
                
                with col2:
                    st.markdown(f"**Bank:** {row['bank_name'] or 'Not provided'}")
                    st.markdown(f"**Account Number:** {row['account_number'] or 'Not provided'}")
                    st.markdown(f"**Account Name:** {row['account_name'] or 'Not provided'}")
                
                # Process payment
                with st.form(f"process_payment_{row['id']}"):
                    payment_method = st.selectbox("Payment Method", 
                                                 ["Bank Transfer", "Cheque", "Cash"])
                    reference_number = st.text_input("Reference Number")
                    payment_date = st.date_input("Payment Date", value=date.today())
                    
                    if st.form_submit_button("✅ Mark as Paid", type="primary"):
                        c = conn.cursor()
                        
                        # Update payment status
                        c.execute("""UPDATE travel_costs 
                                   SET payment_status = 'paid', payment_completed = 1,
                                       payment_date = ?
                                   WHERE id = ?""",
                                 (payment_date.strftime("%Y-%m-%d"), row['id']))
                        
                        # Record payment transaction
                        c.execute("""INSERT INTO payments 
                                   (cost_id, amount, payment_method, reference_number, paid_by, paid_date)
                                   VALUES (?, ?, ?, ?, ?, ?)""",
                                 (row['id'], row['total_cost'], payment_method, 
                                  reference_number, st.session_state.full_name,
                                  payment_date.strftime("%Y-%m-%d")))
                        
                        # Update budget
                        update_budget(row['total_cost'])
                        
                        # Record approval
                        c.execute("""INSERT INTO approvals 
                                   (request_id, approver_role, approver_name, status, comments)
                                   VALUES (?, ?, ?, ?, ?)""",
                                 (row['request_id'], "Payables Officer", 
                                  st.session_state.full_name, "completed",
                                  f"Payment processed - ₦{row['total_cost']:,.2f}"))
                        
                        conn.commit()
                        st.success("✅ Payment marked as completed!")
                        time.sleep(2)
                        st.rerun()
    else:
        st.info("No payments pending processing")
    
    conn.close()

def budget_analytics():
    """Budget analytics dashboard"""
    if st.session_state.role not in ["Head of Administration", "admin"]:
        st.warning("Access denied")
        return
    
    st.markdown('<h1 class="sub-header">Budget Analytics</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # Get budget data
    budget = get_current_budget()
    
    # Summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #D32F2F;">₦{budget['total_budget']:,.0f}</h3>
            <p style="color: #616161;">Total Budget</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #4CAF50;">₦{budget['utilized_budget']:,.0f}</h3>
            <p style="color: #616161;">YTD Actual</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #2196F3;">₦{budget['balance']:,.0f}</h3>
            <p style="color: #616161;">Budget Balance</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        utilization = (budget['utilized_budget'] / budget['total_budget']) * 100
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {'#4CAF50' if utilization < 80 else '#F44336'};">{utilization:.1f}%</h3>
            <p style="color: #616161;">Utilization Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Detailed analytics
    col5, col6 = st.columns(2)
    
    with col5:
        # Monthly expenditure
        monthly_query = """
            SELECT strftime('%Y-%m', tc.created_at) as month,
                   SUM(tc.total_cost) as monthly_expense
            FROM travel_costs tc
            WHERE tc.payment_status = 'paid'
            GROUP BY strftime('%Y-%m', tc.created_at)
            ORDER BY month
        """
        monthly_data = pd.read_sql(monthly_query, conn)
        
        if not monthly_data.empty:
            fig1 = px.bar(monthly_data, x='month', y='monthly_expense',
                         title="Monthly Expenditure",
                         color='monthly_expense',
                         labels={'monthly_expense': 'Amount (₦)'})
            st.plotly_chart(fig1, use_container_width=True)
    
    with col6:
        # Department-wise expenditure
        dept_query = """
            SELECT u.department, SUM(tc.total_cost) as dept_expense
            FROM travel_costs tc
            JOIN travel_requests tr ON tc.request_id = tr.id
            JOIN users u ON tr.user_id = u.id
            WHERE tc.payment_status = 'paid'
            GROUP BY u.department
            ORDER BY dept_expense DESC
        """
        dept_data = pd.read_sql(dept_query, conn)
        
        if not dept_data.empty:
            fig2 = px.pie(dept_data, values='dept_expense', names='department',
                         title="Expenditure by Department")
            st.plotly_chart(fig2, use_container_width=True)
    
    # Detailed transaction table
    st.markdown("### Detailed Transactions")
    transactions_query = """
        SELECT tc.id, u.full_name, u.department, tr.destination,
               tc.total_cost, tc.payment_status, tc.payment_date,
               tc.payment_approved_by
        FROM travel_costs tc
        JOIN travel_requests tr ON tc.request_id = tr.id
        JOIN users u ON tr.user_id = u.id
        WHERE tc.total_cost IS NOT NULL
        ORDER BY tc.created_at DESC
    """
    transactions = pd.read_sql(transactions_query, conn)
    
    if not transactions.empty:
        # Export button
        if st.button("📊 Export to Excel"):
            excel_file = transactions.to_excel(index=False)
            st.download_button(
                label="Download Excel",
                data=excel_file,
                file_name=f"budget_analytics_{date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        st.dataframe(transactions, use_container_width=True)
    else:
        st.info("No transactions found")
    
    conn.close()

def analytics_dashboard():
    """Analytics dashboard for all users"""
    st.markdown('<h1 class="sub-header">Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # Role-based analytics
    if st.session_state.role in ["Head of Administration", "admin"]:
        # Full analytics for admin
        travel_data = pd.read_sql("""
            SELECT tr.*, u.department, u.grade, u.full_name,
                   tc.total_cost, tc.payment_status
            FROM travel_requests tr 
            JOIN users u ON tr.user_id = u.id
            LEFT JOIN travel_costs tc ON tr.id = tc.request_id
            WHERE tr.status != 'draft'
        """, conn)
    else:
        # Limited analytics for regular users
        travel_data = pd.read_sql("""
            SELECT tr.*, u.department, u.grade, u.full_name,
                   tc.total_cost, tc.payment_status
            FROM travel_requests tr 
            JOIN users u ON tr.user_id = u.id
            LEFT JOIN travel_costs tc ON tr.id = tc.request_id
            WHERE tr.user_id = ? AND tr.status != 'draft'
        """, conn, params=(st.session_state.user_id,))
    
    if not travel_data.empty:
        # Convert dates
        travel_data['departure_date'] = pd.to_datetime(travel_data['departure_date'])
        travel_data['month'] = travel_data['departure_date'].dt.strftime('%Y-%m')
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Travel by department
            dept_counts = travel_data['department'].value_counts().head(10)
            fig1 = px.bar(x=dept_counts.index, y=dept_counts.values,
                         title="Top Departments by Travel",
                         color=dept_counts.values,
                         labels={'x': 'Department', 'y': 'Count'})
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Travel by status
            status_counts = travel_data['status'].value_counts()
            fig2 = px.pie(values=status_counts.values, names=status_counts.index,
                         title="Travel Requests by Status",
                         color=status_counts.index)
            st.plotly_chart(fig2, use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            # Monthly trend
            monthly_counts = travel_data.groupby('month').size().reset_index(name='count')
            fig3 = px.line(monthly_counts, x='month', y='count',
                          title="Monthly Travel Requests Trend",
                          markers=True)
            st.plotly_chart(fig3, use_container_width=True)
        
        with col4:
            # Travel by type
            type_counts = travel_data['travel_type'].value_counts()
            fig4 = px.bar(x=type_counts.index, y=type_counts.values,
                         title="Local vs International Travel",
                         color=type_counts.index,
                         labels={'x': 'Type', 'y': 'Count'})
            st.plotly_chart(fig4, use_container_width=True)
        
        # Cost analysis for admin
        if st.session_state.role in ["Head of Administration", "admin"]:
            st.markdown("---")
            st.markdown("### Cost Analysis")
            
            cost_data = travel_data.dropna(subset=['total_cost'])
            
            if not cost_data.empty:
                col5, col6 = st.columns(2)
                
                with col5:
                    # Cost by department
                    dept_costs = cost_data.groupby('department')['total_cost'].sum().reset_index()
                    dept_costs = dept_costs.sort_values('total_cost', ascending=False).head(10)
                    fig5 = px.bar(dept_costs, x='department', y='total_cost',
                                 title="Top Departments by Cost",
                                 color='total_cost',
                                 labels={'total_cost': 'Total Cost (₦)'})
                    st.plotly_chart(fig5, use_container_width=True)
                
                with col6:
                    # Payment status
                    payment_counts = cost_data['payment_status'].value_counts()
                    fig6 = px.pie(values=payment_counts.values, names=payment_counts.index,
                                 title="Payment Status Distribution",
                                 color=payment_counts.index)
                    st.plotly_chart(fig6, use_container_width=True)
    
    else:
        st.info("No data available for analytics")
    
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


