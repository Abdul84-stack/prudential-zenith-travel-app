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

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #D32F2F;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
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
        color: #D32F2F;
        text-align: center;
        font-size: 2rem;
        margin-bottom: 30px;
        font-weight: bold;
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
    }
    .stButton>button:hover {
        background: linear-gradient(to right, #B71C1C, #9A0007);
        transform: translateY(-3px);
    }
    .card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 25px;
        border-left: 6px solid #D32F2F;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    }
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border: 2px solid #D32F2F;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    }
    .approval-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 25px;
        font-size: 0.85rem;
        font-weight: bold;
        margin: 3px;
    }
    .pending-badge {
        background: #fff3cd;
        color: #856404;
        border: 1px solid #ffd54f;
    }
    .approved-badge {
        background: #d4edda;
        color: #155724;
        border: 1px solid #a3d9a5;
    }
    .rejected-badge {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f1aeb5;
    }
    .paid-badge {
        background: #d1ecf1;
        color: #0c5460;
        border: 1px solid #86cfda;
    }
    .company-logo {
        text-align: center;
        margin-bottom: 30px;
        padding: 20px;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        border: 2px solid #D32F2F;
    }
    .footer {
        text-align: center;
        color: #757575;
        font-size: 0.9rem;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 2px solid #e0e0e0;
    }
    .budget-bar {
        height: 25px;
        background: linear-gradient(90deg, #4CAF50, #8BC34A);
        border-radius: 12px;
        margin: 10px 0;
        overflow: hidden;
    }
    .travel-policy-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }
    .travel-policy-table th {
        background-color: #D32F2F;
        color: white;
        padding: 12px;
        text-align: center;
        border: 1px solid #ddd;
    }
    .travel-policy-table td {
        padding: 10px;
        text-align: center;
        border: 1px solid #ddd;
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
if 'show_registration' not in st.session_state:
    st.session_state.show_registration = False

# Constants
DEPARTMENTS = [
    "Administration", "Bancassurance", "Corporate Sales", "Agencies", 
    "Actuary", "Legal and Compliance", "Internal Audit", "Internal Control and Risk", 
    "Finance and Investment", "Commercial and Business Support", "HR", 
    "Claims and Underwriting", "Branding and Corp. Communication", "Customer Service", 
    "IT", "Office of CEO", "Office of Executive Director"
]

GRADES = ["MD", "ED", "GM", "DGM", "AGM", "PM", "SM", "MGR", "DM", "AM", "SO", "EA", "Officer"]

ROLES = ["Employee", "Head of Department", "Head of Administration", "Chief Commercial Officer", 
         "Chief Agency Officer", "Chief Compliance Officer", "Chief Risk Officer", 
         "CFO/ED", "ED", "MD", "Payables Officer", "admin"]

MARITAL_STATUS = ["Single", "Married", "Divorced", "Widowed", "Separated"]

# UPDATED: Nigerian states with comprehensive cities
NIGERIAN_STATES = {
    "Abia": ["Aba", "Umuahia", "Arochukwu", "Ohafia", "Bende", "Isuikwuato"],
    "Adamawa": ["Yola", "Mubi", "Jimeta", "Ganye", "Numan", "Mayo-Belwa"],
    "Lagos": ["Lagos Island", "Ikeja", "Badagry", "Epe", "Ikorodu", "Ojo", "Alimosho", "Mushin", "Surulere", "Apapa"],
    "FCT": ["Abuja", "Gwagwalada", "Kuje", "Bwari", "Kwali", "Abaji", "Karu", "Kubwa", "Lugbe", "Gwarimpa"],
    "Rivers": ["Port Harcourt", "Bonny", "Degema", "Okrika", "Oyigbo", "Ahoada", "Bori", "Omoku", "Elele"],
}

# Add more states as needed - simplified for brevity

# Complete list of countries
COUNTRIES = [
    "Afghanistan", "Albania", "Algeria", "Australia", "Austria", "Belgium", "Brazil", "Canada",
    "China", "Denmark", "Egypt", "Finland", "France", "Germany", "Ghana", "Greece", "India",
    "Indonesia", "Ireland", "Italy", "Japan", "Kenya", "Mexico", "Netherlands", "New Zealand",
    "Nigeria", "Norway", "Poland", "Portugal", "Russia", "Saudi Arabia", "Singapore", "South Africa",
    "Spain", "Sweden", "Switzerland", "Turkey", "United Arab Emirates", "United Kingdom", "United States"
]

# UPDATED: Local Travel Policy with new rates based on grade level
LOCAL_POLICY = {
    "MD": {"hotel": 650000, "feeding": 80000, "hotel_text": "NGN 650,000 per night", "feeding_text": "NGN 80,000 per meal per day"},
    "ED": {"hotel": 500000, "feeding": 80000, "hotel_text": "NGN 500,000 per night", "feeding_text": "NGN 80,000 per meal per day"},
    "GM": {"hotel": 350000, "feeding": 50000, "hotel_text": "NGN 350,000 per night", "feeding_text": "NGN 50,000 per meal per day"},
    "AGM-DGM": {"hotel": 250000, "feeding": 30000, "hotel_text": "NGN 250,000 per night", "feeding_text": "NGN 30,000 per meal per day"},
    "SM-PM": {"hotel": 150000, "feeding": 20000, "hotel_text": "NGN 150,000 per night", "feeding_text": "NGN 20,000 per meal per day"},
    "MGR": {"hotel": 100000, "feeding": 15000, "hotel_text": "NGN 100,000 per night", "feeding_text": "NGN 15,000 per meal per day"},
    "AM-DM": {"hotel": 80000, "feeding": 10000, "hotel_text": "NGN 80,000 per night", "feeding_text": "NGN 10,000 per meal per day"},
    "EA-SO": {"hotel": 75000, "feeding": 7000, "hotel_text": "NGN 75,000 per night", "feeding_text": "NGN 7,000 per meal per day"}
}

# International Travel Policy
USD_TO_NGN = 1400

INTERNATIONAL_POLICY = {
    "MD": {"accommodation": 500, "feeding": 200, "out_of_station": 200, "airport_taxi": 250,
           "accommodation_text": "$500/Night", "feeding_text": "$200/Day", 
           "out_of_station_text": "$200/Day", "airport_taxi_text": "$250 (One-time)"},
    "ED": {"accommodation": 200, "feeding": 150, "out_of_station": 150, "airport_taxi": 200,
           "accommodation_text": "$200/Night", "feeding_text": "$150/Day",
           "out_of_station_text": "$150/Day", "airport_taxi_text": "$200 (One-time)"},
    "AGM-GM": {"accommodation": 150, "feeding": 100, "out_of_station": 100, "airport_taxi": 150,
               "accommodation_text": "$150/Night", "feeding_text": "$100/Day",
               "out_of_station_text": "$100/Day", "airport_taxi_text": "$150 (One-time)"},
    "AM-PM": {"accommodation": 100, "feeding": 80, "out_of_station": 80, "airport_taxi": 100,
              "accommodation_text": "$100/Night", "feeding_text": "$80/day",
              "out_of_station_text": "$80/Day", "airport_taxi_text": "$100 (One-time)"},
    "EA-SO": {"accommodation": 100, "feeding": 50, "out_of_station": 60, "airport_taxi": 100,
              "accommodation_text": "$100/Night", "feeding_text": "$50/Day",
              "out_of_station_text": "$60/Day", "airport_taxi_text": "$100 (One-time)"}
}

ANNUAL_BUDGET = 120000000

class PDFReport(FPDF):
    def header(self):
        if self.page_no() == 1:
            self.set_font('Arial', 'B', 16)
            self.set_text_color(211, 47, 47)
            self.cell(0, 10, 'PRUDENTIAL ZENITH LIFE INSURANCE', 0, 1, 'C')
            self.set_font('Arial', 'B', 14)
            self.set_text_color(97, 97, 97)
            self.cell(0, 10, 'Travel Request Report', 0, 1, 'C')
            self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# Database initialization
def init_db():
    conn = sqlite3.connect('travel_app.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  full_name TEXT, username TEXT UNIQUE, email TEXT, password TEXT,
                  department TEXT, grade TEXT, role TEXT, profile_pic BLOB,
                  bank_name TEXT, account_number TEXT, account_name TEXT,
                  phone_number TEXT, date_of_birth DATE, place_of_birth TEXT,
                  passport_number TEXT, nationality TEXT, marital_status TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS travel_requests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER, username TEXT, travel_type TEXT,
                  destination TEXT, city TEXT, country TEXT, purpose TEXT,
                  mode_of_travel TEXT, departure_date DATE, arrival_date DATE,
                  accommodation_needed TEXT, duration_days INTEGER, duration_nights INTEGER,
                  status TEXT DEFAULT 'pending', current_approver TEXT,
                  approval_flow TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS travel_costs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  request_id INTEGER, grade TEXT,
                  per_diem_amount REAL, flight_cost REAL, airport_taxi_cost REAL,
                  total_cost REAL, budgeted_cost REAL, budget_balance REAL,
                  supporting_docs BLOB, admin_notes TEXT,
                  payment_status TEXT DEFAULT 'pending',
                  approved_by_admin BOOLEAN DEFAULT 0,
                  approved_by_compliance BOOLEAN DEFAULT 0,
                  approved_by_risk BOOLEAN DEFAULT 0,
                  approved_by_finance BOOLEAN DEFAULT 0,
                  approved_by_md BOOLEAN DEFAULT 0,
                  payment_approved_by TEXT, payment_approved_date DATE,
                  payment_completed BOOLEAN DEFAULT 0, payment_date DATE,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (request_id) REFERENCES travel_requests(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS approvals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  request_id INTEGER, approver_role TEXT, approver_name TEXT,
                  status TEXT, comments TEXT,
                  approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (request_id) REFERENCES travel_requests(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS budget
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  year INTEGER, total_budget REAL, utilized_budget REAL, balance REAL,
                  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS payments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  cost_id INTEGER, amount REAL, payment_method TEXT,
                  reference_number TEXT, paid_by TEXT, paid_date DATE,
                  status TEXT DEFAULT 'completed',
                  FOREIGN KEY (cost_id) REFERENCES travel_costs(id))''')
    
    # Create default users
    default_users = [
        ("CFO/Executive Director", "cfo_ed", "cfo@prudentialzenith.com", 
         make_hashes("0123456"), "Finance and Investment", "ED", "CFO/ED"),
        ("Managing Director", "md", "md@prudentialzenith.com", 
         make_hashes("123456"), "Office of CEO", "MD", "MD"),
        ("Chief Compliance Officer", "chief_compliance", "compliance@prudentialzenith.com",
         make_hashes("123456"), "Legal and Compliance", "DGM", "Chief Compliance Officer"),
        ("Chief Risk Officer", "chief_risk", "risk@prudentialzenith.com",
         make_hashes("123456"), "Internal Control and Risk", "DGM", "Chief Risk Officer"),
        ("Payables Officer", "payables", "payables@prudentialzenith.com",
         make_hashes("123456"), "Finance and Investment", "Officer", "Payables Officer"),
        ("Head of Administration", "head_admin", "admin@prudentialzenith.com",
         make_hashes("123456"), "Administration", "GM", "Head of Administration")
    ]
    
    for user in default_users:
        try:
            c.execute('''INSERT OR IGNORE INTO users 
                       (full_name, username, email, password, department, grade, role) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)''', user)
        except:
            pass
    
    current_year = datetime.datetime.now().year
    c.execute('''INSERT OR IGNORE INTO budget (year, total_budget, utilized_budget, balance)
                 VALUES (?, ?, 0, ?)''', (current_year, ANNUAL_BUDGET, ANNUAL_BUDGET))
    
    conn.commit()
    conn.close()

init_db()

def get_grade_category_for_local(grade):
    if grade == "MD": return "MD"
    elif grade == "ED": return "ED"
    elif grade == "GM": return "GM"
    elif grade in ["AGM", "DGM"]: return "AGM-DGM"
    elif grade in ["SM", "PM"]: return "SM-PM"
    elif grade == "MGR": return "MGR"
    elif grade in ["AM", "DM"]: return "AM-DM"
    else: return "EA-SO"

def get_grade_category_for_international(grade):
    if grade == "MD": return "MD"
    elif grade == "ED": return "ED"
    elif grade in ["AGM", "GM", "DGM"]: return "AGM-GM"
    elif grade in ["PM", "SM", "AM"]: return "AM-PM"
    else: return "EA-SO"

def get_approval_flow(department, grade, role):
    if department == "HR":
        return ["MD"]
    elif department == "Finance and Investment":
        return ["CFO/ED", "MD"]
    elif department == "Administration":
        if role == "Head of Administration":
            return ["MD"]
        return ["Head of Administration", "MD"]
    elif department == "Internal Control and Risk":
        return ["Chief Risk Officer", "MD"]
    elif department == "Legal and Compliance":
        return ["Chief Compliance Officer", "MD"]
    else:
        return ["Head of Department", "MD"]

def get_payment_approval_flow(total_amount):
    if total_amount > 5000000:
        return ["Head of Administration", "Chief Compliance Officer", "Chief Risk Officer", "MD"]
    else:
        return ["Head of Administration", "Chief Compliance Officer", "Chief Risk Officer", "ED"]

def calculate_travel_costs(grade, travel_type, duration_nights):
    if travel_type == "local":
        policy_category = get_grade_category_for_local(grade)
        policy = LOCAL_POLICY[policy_category]
        hotel_cost = policy["hotel"] * duration_nights
        feeding_cost = policy["feeding"] * 3 * duration_nights
        total = hotel_cost + feeding_cost
        return total, hotel_cost, feeding_cost, 0
    else:
        grade_category = get_grade_category_for_international(grade)
        policy = INTERNATIONAL_POLICY[grade_category]
        accommodation_cost = policy["accommodation"] * USD_TO_NGN * duration_nights
        feeding_cost = policy["feeding"] * USD_TO_NGN * duration_nights
        out_of_station_cost = policy["out_of_station"] * USD_TO_NGN * duration_nights
        airport_taxi_cost = policy["airport_taxi"] * USD_TO_NGN
        total = accommodation_cost + feeding_cost + out_of_station_cost + airport_taxi_cost
        return total, accommodation_cost, feeding_cost, airport_taxi_cost

def get_current_budget():
    conn = sqlite3.connect('travel_app.db')
    current_year = datetime.datetime.now().year
    c = conn.cursor()
    c.execute("SELECT * FROM budget WHERE year = ?", (current_year,))
    budget_record = c.fetchone()
    
    if budget_record:
        budget = {'year': budget_record[1], 'total_budget': budget_record[2], 
                  'utilized_budget': budget_record[3], 'balance': budget_record[4]}
    else:
        budget = {'year': current_year, 'total_budget': ANNUAL_BUDGET, 
                  'utilized_budget': 0, 'balance': ANNUAL_BUDGET}
    
    conn.close()
    return budget

def update_budget(amount):
    conn = sqlite3.connect('travel_app.db')
    c = conn.cursor()
    current_year = datetime.datetime.now().year
    c.execute("SELECT * FROM budget WHERE year = ?", (current_year,))
    budget = c.fetchone()
    
    if budget:
        c.execute('''UPDATE budget SET utilized_budget = utilized_budget + ?, 
                     balance = balance - ?, last_updated = CURRENT_TIMESTAMP
                     WHERE year = ?''', (amount, amount, current_year))
    else:
        c.execute('''INSERT INTO budget (year, total_budget, utilized_budget, balance)
                     VALUES (?, ?, ?, ?)''', (current_year, ANNUAL_BUDGET, amount, ANNUAL_BUDGET - amount))
    
    conn.commit()
    conn.close()
    return True

def get_pending_approvals_for_role(role):
    conn = sqlite3.connect('travel_app.db')
    approver_roles = ["CFO/ED", "Chief Risk Officer", "Chief Compliance Officer", 
                     "ED", "MD", "Head of Administration", "Head of Department"]
    
    if role in approver_roles:
        query = """
            SELECT tr.*, u.full_name, u.department, u.grade 
            FROM travel_requests tr 
            JOIN users u ON tr.user_id = u.id 
            WHERE tr.status = 'pending' AND tr.current_approver = ?
            ORDER BY tr.created_at DESC
        """
        approvals = pd.read_sql(query, conn, params=(role,))
    else:
        approvals = pd.DataFrame()
    
    conn.close()
    return approvals

def process_approval(request_id, action, comments=""):
    conn = sqlite3.connect('travel_app.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM travel_requests WHERE id = ?", (request_id,))
    request = c.fetchone()
    
    if not request:
        conn.close()
        return False, "Request not found"
    
    current_approver = request[15]
    approval_flow_json = request[16]
    
    try:
        approval_flow = json.loads(approval_flow_json)
    except:
        conn.close()
        return False, "Invalid approval flow data"
    
    if action == "approve":
        try:
            if current_approver:
                current_index = approval_flow.index(current_approver)
            else:
                current_index = -1
        except ValueError:
            current_index = -1
        
        if current_index + 1 < len(approval_flow):
            next_approver = approval_flow[current_index + 1]
            new_status = "pending"
            new_current_approver = next_approver
        else:
            new_status = "approved"
            new_current_approver = None
        
        c.execute("""UPDATE travel_requests SET status = ?, current_approver = ? WHERE id = ?""",
                 (new_status, new_current_approver, request_id))
        c.execute("""INSERT INTO approvals (request_id, approver_role, approver_name, status, comments) 
                     VALUES (?, ?, ?, ?, ?)""",
                 (request_id, st.session_state.role, st.session_state.full_name, "approved", comments))
        conn.commit()
        message = "Request approved successfully"
        
    elif action == "reject":
        c.execute("""UPDATE travel_requests SET status = 'rejected', current_approver = NULL WHERE id = ?""", (request_id,))
        c.execute("""INSERT INTO approvals (request_id, approver_role, approver_name, status, comments) 
                     VALUES (?, ?, ?, ?, ?)""",
                 (request_id, st.session_state.role, st.session_state.full_name, "rejected", comments))
        conn.commit()
        message = "Request rejected"
    
    conn.close()
    return True, message

def generate_pdf_report(request_id):
    conn = sqlite3.connect('travel_app.db')
    
    request_df = pd.read_sql("""
        SELECT tr.*, u.full_name, u.department, u.grade, u.email,
               u.bank_name, u.account_number, u.account_name
        FROM travel_requests tr JOIN users u ON tr.user_id = u.id WHERE tr.id = ?
    """, conn, params=(request_id,))
    
    if request_df.empty:
        conn.close()
        return None
    
    request_data = request_df.iloc[0]
    cost_data = pd.read_sql("SELECT * FROM travel_costs WHERE request_id = ?", conn, params=(request_id,))
    approvals = pd.read_sql("SELECT * FROM approvals WHERE request_id = ? ORDER BY approved_at", conn, params=(request_id,))
    conn.close()
    
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(211, 47, 47)
    pdf.cell(0, 10, 'Travel Request Details', 0, 1, 'L')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    def add_field(label, value):
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(66, 66, 66)
        pdf.cell(45, 8, f'{label}:', 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(33, 33, 33)
        value_str = str(value) if value else 'Not Provided'
        pdf.cell(0, 8, value_str, 0, 1)
    
    add_field("Request ID", f"TR-{request_data['id']:06d}")
    add_field("Employee", request_data['full_name'])
    add_field("Department", request_data['department'])
    add_field("Grade", request_data['grade'])
    add_field("Travel Type", request_data['travel_type'].title())
    add_field("Destination", request_data['destination'])
    add_field("Purpose", request_data['purpose'])
    add_field("Departure Date", request_data['departure_date'])
    add_field("Arrival Date", request_data['arrival_date'])
    add_field("Duration", f"{request_data['duration_days']} days ({request_data['duration_nights']} nights)")
    add_field("Status", request_data['status'].upper())
    
    if not cost_data.empty:
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(211, 47, 47)
        pdf.cell(0, 10, 'Cost Details', 0, 1, 'L')
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        cost = cost_data.iloc[0]
        add_field("Total Cost", f"NGN {cost['total_cost']:,.2f}")
        add_field("Payment Status", cost['payment_status'].upper())
    
    if not approvals.empty:
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(211, 47, 47)
        pdf.cell(0, 10, 'Approval History', 0, 1, 'L')
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        for _, approval in approvals.iterrows():
            add_field(approval['approver_role'], f"{approval['status'].upper()} - {approval['approved_at']}")
    
    return pdf.output(dest='S').encode('latin-1', errors='replace')

def show_local_travel_policy():
    st.markdown("### Local Travel Policy (Hotel & Feeding Allowances)")
    policy_data = {
        "Grade": ["MD/CEO", "ED", "GM", "AGM - DGM", "SM - PM", "MGR", "AM - DM", "EA – SO"],
        "Hotel Accommodation": ["NGN 650,000/night", "NGN 500,000/night", "NGN 350,000/night", 
                                "NGN 250,000/night", "NGN 150,000/night", "NGN 100,000/night",
                                "NGN 80,000/night", "NGN 75,000/night"],
        "Feeding Allowance": ["NGN 80,000/meal/day", "NGN 80,000/meal/day", "NGN 50,000/meal/day",
                              "NGN 30,000/meal/day", "NGN 20,000/meal/day", "NGN 15,000/meal/day",
                              "NGN 10,000/meal/day", "NGN 7,000/meal/day"]
    }
    st.table(pd.DataFrame(policy_data))

# ============ LOGIN FUNCTIONS ============

def login():
    st.markdown('<div class="company-logo">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">PRUDENTIAL ZENITH LIFE INSURANCE</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Travel Support Application</h2>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="login-title">🔐 USER LOGIN</h3>', unsafe_allow_html=True)
        
        username = st.text_input("Username / Employee ID")
        password = st.text_input("Password", type="password")
        
        col_a, col_b = st.columns(2)
        with col_a:
            login_btn = st.button("LOGIN", use_container_width=True, type="primary")
        with col_b:
            register_btn = st.button("CREATE ACCOUNT", use_container_width=True)
        
        st.markdown('<div class="quick-login">', unsafe_allow_html=True)
        st.markdown("**Test Credentials:**")
        st.markdown("- CFO/ED: `cfo_ed` / `0123456`")
        st.markdown("- MD: `md` / `123456`")
        st.markdown("- Head of Admin: `head_admin` / `123456`")
        st.markdown("- Payables: `payables` / `123456`")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if login_btn:
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
    st.markdown('<h2 class="sub-header">Create New Account</h2>', unsafe_allow_html=True)
    
    with st.form("registration_form"):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name*")
            username = st.text_input("Username*")
            email = st.text_input("Email*")
            phone_number = st.text_input("Phone Number*")
        with col2:
            password = st.text_input("Password*", type="password")
            confirm_password = st.text_input("Confirm Password*", type="password")
            department = st.selectbox("Department*", DEPARTMENTS)
            grade = st.selectbox("Grade*", GRADES)
            role = st.selectbox("Role*", ROLES)
        
        st.markdown("### Bank Details (Optional)")
        col3, col4 = st.columns(2)
        with col3:
            bank_name = st.text_input("Bank Name")
            account_number = st.text_input("Account Number")
        with col4:
            account_name = st.text_input("Account Name")
        
        submitted = st.form_submit_button("Create Account")
        
        if submitted:
            if not all([full_name, username, email, password, confirm_password, phone_number, department, grade, role]):
                st.error("Please fill all required fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                conn = sqlite3.connect('travel_app.db')
                c = conn.cursor()
                c.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
                if c.fetchone():
                    st.error("Username or email already exists")
                else:
                    c.execute("""INSERT INTO users (full_name, username, email, password, department, grade, role,
                               bank_name, account_number, account_name, phone_number) 
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                             (full_name, username, email, make_hashes(password), department, grade, role,
                              bank_name, account_number, account_name, phone_number))
                    conn.commit()
                    st.success("Account created! Please login.")
                    time.sleep(2)
                    st.session_state.show_registration = False
                    st.rerun()
                conn.close()

# ============ MAIN UI FUNCTIONS ============

def travel_request_form():
    st.markdown('<h1 class="sub-header">New Travel Request</h1>', unsafe_allow_html=True)
    show_local_travel_policy()
    st.markdown("---")
    
    travel_type = st.radio("Travel Type", ["Local", "International"], horizontal=True)
    
    with st.form("travel_request"):
        col1, col2 = st.columns(2)
        
        with col1:
            if travel_type == "Local":
                city = st.text_input("City*", placeholder="Enter city name")
                state = st.text_input("State*", placeholder="Enter state name")
                destination = f"{city}, {state}"
                country = "Nigeria"
            else:
                country = st.selectbox("Country*", COUNTRIES)
                city = st.text_input("City/Region*")
                destination = f"{city}, {country}"
            
            purpose = st.selectbox("Purpose*", ["Business Meeting", "Conference", "Training", "Project Site Visit", "Other"])
            if purpose == "Other":
                purpose = st.text_input("Specify purpose")
        
        with col2:
            mode_of_travel = st.selectbox("Mode of Travel*", ["Flight", "Road", "Train", "Water"])
            departure_date = st.date_input("Departure Date*", min_value=date.today())
            arrival_date = st.date_input("Arrival Date*", min_value=departure_date)
            accommodation = st.radio("Accommodation Needed?", ["Yes", "No"], horizontal=True)
        
        if departure_date and arrival_date:
            duration_days = (arrival_date - departure_date).days + 1
            duration_nights = (arrival_date - departure_date).days
            st.info(f"**Duration:** {duration_days} days ({duration_nights} nights)")
        else:
            duration_days = duration_nights = 0
        
        # Show policy and estimated cost
        if travel_type == "Local":
            policy = LOCAL_POLICY[get_grade_category_for_local(st.session_state.grade)]
            st.info(f"**Your Rate:** Hotel: {policy['hotel_text']} | Feeding: {policy['feeding_text']}")
            estimated_total, _, _, _ = calculate_travel_costs(st.session_state.grade, "local", duration_nights)
            st.metric("Estimated Total Cost", f"NGN{estimated_total:,.2f}")
        else:
            policy = INTERNATIONAL_POLICY[get_grade_category_for_international(st.session_state.grade)]
            st.info(f"**Your Rate:** Hotel: {policy['accommodation_text']} | Feeding: {policy['feeding_text']}")
            estimated_total, _, _, _ = calculate_travel_costs(st.session_state.grade, "international", duration_nights)
            st.metric("Estimated Total Cost", f"NGN{estimated_total:,.2f}")
        
        submitted = st.form_submit_button("Submit Request", type="primary")
        
        if submitted:
            if not all([destination, purpose, mode_of_travel, city]):
                st.error("Please fill all required fields")
            elif arrival_date <= departure_date:
                st.error("Arrival date must be after departure date")
            else:
                approval_flow = get_approval_flow(st.session_state.department, st.session_state.grade, st.session_state.role)
                
                conn = sqlite3.connect('travel_app.db')
                c = conn.cursor()
                c.execute("""INSERT INTO travel_requests 
                          (user_id, username, travel_type, destination, city, country, purpose, 
                           mode_of_travel, departure_date, arrival_date, accommodation_needed, 
                           duration_days, duration_nights, current_approver, approval_flow) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         (st.session_state.user_id, st.session_state.username, travel_type.lower(),
                          destination, city, country, purpose, mode_of_travel,
                          departure_date.strftime("%Y-%m-%d"), arrival_date.strftime("%Y-%m-%d"),
                          accommodation, duration_days, duration_nights,
                          approval_flow[0], json.dumps(approval_flow)))
                
                request_id = c.lastrowid
                c.execute("""INSERT INTO approvals (request_id, approver_role, approver_name, status) 
                          VALUES (?, ?, ?, ?)""", (request_id, approval_flow[0], "System", "pending"))
                conn.commit()
                conn.close()
                
                st.success("Travel request submitted!")
                st.info(f"**Approval Flow:** {' → '.join(approval_flow)}")

def travel_history():
    st.markdown('<h1 class="sub-header">Travel History</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    travel_data = pd.read_sql("""
        SELECT tr.*, tc.payment_status, tc.total_cost 
        FROM travel_requests tr LEFT JOIN travel_costs tc ON tr.id = tc.request_id 
        WHERE tr.user_id = ? ORDER BY tr.created_at DESC
    """, conn, params=(st.session_state.user_id,))
    
    if not travel_data.empty:
        for _, row in travel_data.iterrows():
            with st.expander(f"{row['destination']} - {row['status'].upper()} ({row['created_at'][:10]})"):
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.write(f"**Type:** {row['travel_type'].title()}")
                    st.write(f"**Purpose:** {row['purpose']}")
                with col_b:
                    st.write(f"**Dates:** {row['departure_date']} to {row['arrival_date']}")
                    st.write(f"**Duration:** {row['duration_days']} days")
                with col_c:
                    st.write(f"**Status:** {row['status'].upper()}")
                    if row.get('total_cost'):
                        st.write(f"**Cost:** NGN{row['total_cost']:,.2f}")
                
                if st.button(f"Download PDF", key=f"pdf_{row['id']}"):
                    pdf_bytes = generate_pdf_report(row['id'])
                    if pdf_bytes:
                        st.download_button("Click to Download", data=pdf_bytes, 
                                         file_name=f"travel_report_{row['id']}.pdf", mime="application/pdf")
    else:
        st.info("No travel records found")
    conn.close()

def show_approvals():
    if st.session_state.role not in ["MD", "ED", "CFO/ED", "Head of Department", "Head of Administration",
                                    "Chief Compliance Officer", "Chief Risk Officer"]:
        st.warning("Access denied")
        return
    
    st.markdown('<h1 class="sub-header">Pending Approvals</h1>', unsafe_allow_html=True)
    pending_approvals = get_pending_approvals_for_role(st.session_state.role)
    
    if not pending_approvals.empty:
        for _, row in pending_approvals.iterrows():
            with st.container():
                st.markdown(f"### Travel Request #{row['id']}")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Employee:** {row['full_name']}")
                    st.write(f"**Department:** {row['department']}")
                    st.write(f"**Destination:** {row['destination']}")
                with col2:
                    st.write(f"**Purpose:** {row['purpose']}")
                    st.write(f"**Dates:** {row['departure_date']} to {row['arrival_date']}")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"Approve", key=f"approve_{row['id']}", type="primary"):
                        success, message = process_approval(row['id'], "approve")
                        if success:
                            st.success(message)
                            time.sleep(1)
                            st.rerun()
                with col_b:
                    if st.button(f"Reject", key=f"reject_{row['id']}"):
                        comments = st.text_area("Reason", key=f"reason_{row['id']}")
                        if st.button("Confirm Reject", key=f"confirm_{row['id']}"):
                            if comments:
                                success, message = process_approval(row['id'], "reject", comments)
                                if success:
                                    st.error(message)
                                    time.sleep(1)
                                    st.rerun()
    else:
        st.success("No pending approvals!")

def admin_panel():
    if st.session_state.role not in ["Head of Administration", "admin"]:
        st.warning("Access denied")
        return
    
    st.markdown('<h1 class="sub-header">Admin Panel - Cost Management</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    approved_requests = pd.read_sql("""
        SELECT tr.*, u.full_name, u.grade, u.department, tc.id as cost_id 
        FROM travel_requests tr JOIN users u ON tr.user_id = u.id 
        LEFT JOIN travel_costs tc ON tr.id = tc.request_id 
        WHERE tr.status = 'approved' AND (tc.id IS NULL OR tc.payment_status IN ('pending', 'draft'))
        ORDER BY tr.created_at DESC
    """, conn)
    
    if not approved_requests.empty:
        for _, row in approved_requests.iterrows():
            with st.expander(f"{row['full_name']} - {row['destination']}"):
                budget = get_current_budget()
                estimated_total, per_diem, flight_cost_val, airport_taxi = calculate_travel_costs(
                    row['grade'], row['travel_type'], row['duration_nights'])
                
                with st.form(f"cost_form_{row['id']}"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Per Diem Amount", f"NGN{per_diem:,.2f}")
                        flight_cost = st.number_input("Flight Cost (NGN)", min_value=0.0, value=float(flight_cost_val))
                        if row['travel_type'] == 'international':
                            st.metric("Airport Taxi", f"NGN{airport_taxi:,.2f}")
                    
                    with col_b:
                        total_cost = per_diem + flight_cost + (airport_taxi if row['travel_type'] == 'international' else 0)
                        st.metric("Total Cost", f"NGN{total_cost:,.2f}")
                        budget_after = budget['balance'] - total_cost
                        st.metric("Budget Balance After", f"NGN{budget_after:,.0f}")
                        if budget_after < 0:
                            st.warning(f"Exceeds budget by NGN{-budget_after:,.0f}")
                    
                    admin_notes = st.text_area("Admin Notes")
                    
                    if st.form_submit_button("Submit for Payment Approval", type="primary"):
                        c = conn.cursor()
                        c.execute("""INSERT OR REPLACE INTO travel_costs 
                                   (request_id, grade, per_diem_amount, flight_cost, airport_taxi_cost,
                                    total_cost, budgeted_cost, budget_balance, admin_notes, 
                                    payment_status, approved_by_admin) 
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', 1)""",
                                 (row['id'], row['grade'], per_diem, flight_cost, 
                                  airport_taxi if row['travel_type'] == 'international' else 0,
                                  total_cost, total_cost, budget_after, admin_notes))
                        conn.commit()
                        st.success("Submitted for payment approval!")
                        time.sleep(1)
                        st.rerun()
    else:
        st.info("No approved requests pending cost input")
    conn.close()

def payment_approvals():
    if st.session_state.role not in ["Head of Administration", "Chief Compliance Officer", 
                                    "Chief Risk Officer", "CFO/ED", "MD"]:
        st.warning("Access denied")
        return
    
    st.markdown('<h1 class="sub-header">Payment Approvals</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # Determine which approvals to show based on role
    if st.session_state.role == "Head of Administration":
        query = """
            SELECT tc.*, tr.destination, tr.purpose, u.full_name, u.department, u.grade, tr.travel_type
            FROM travel_costs tc JOIN travel_requests tr ON tc.request_id = tr.id
            JOIN users u ON tr.user_id = u.id
            WHERE tc.payment_status = 'pending' AND tc.approved_by_admin = 1 AND tc.approved_by_compliance = 0
            ORDER BY tc.created_at DESC
        """
    elif st.session_state.role == "Chief Compliance Officer":
        query = """
            SELECT tc.*, tr.destination, tr.purpose, u.full_name, u.department, u.grade, tr.travel_type
            FROM travel_costs tc JOIN travel_requests tr ON tc.request_id = tr.id
            JOIN users u ON tr.user_id = u.id
            WHERE tc.payment_status = 'pending' AND tc.approved_by_admin = 1 AND tc.approved_by_compliance = 0
            ORDER BY tc.created_at DESC
        """
    elif st.session_state.role == "Chief Risk Officer":
        query = """
            SELECT tc.*, tr.destination, tr.purpose, u.full_name, u.department, u.grade, tr.travel_type
            FROM travel_costs tc JOIN travel_requests tr ON tc.request_id = tr.id
            JOIN users u ON tr.user_id = u.id
            WHERE tc.payment_status = 'pending' AND tc.approved_by_compliance = 1 AND tc.approved_by_risk = 0
            ORDER BY tc.created_at DESC
        """
    elif st.session_state.role in ["CFO/ED", "MD"]:
        query = """
            SELECT tc.*, tr.destination, tr.purpose, u.full_name, u.department, u.grade, tr.travel_type
            FROM travel_costs tc JOIN travel_requests tr ON tc.request_id = tr.id
            JOIN users u ON tr.user_id = u.id
            WHERE tc.payment_status = 'pending' AND tc.approved_by_risk = 1 AND tc.approved_by_finance = 0
            ORDER BY tc.created_at DESC
        """
    else:
        query = "SELECT * FROM travel_costs WHERE 1=0"
    
    pending_payments = pd.read_sql(query, conn)
    
    if not pending_payments.empty:
        for _, row in pending_payments.iterrows():
            with st.container():
                st.markdown(f"### Payment Request #{row['id']}")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Employee:** {row['full_name']}")
                    st.write(f"**Department:** {row['department']}")
                    st.write(f"**Destination:** {row['destination']}")
                with col2:
                    st.write(f"**Total Cost:** NGN{row['total_cost']:,.2f}")
                    st.write(f"**Budget Balance After:** NGN{row['budget_balance']:,.2f}")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"Approve Payment", key=f"approve_pay_{row['id']}", type="primary"):
                        c = conn.cursor()
                        if st.session_state.role == "Head of Administration":
                            c.execute("UPDATE travel_costs SET approved_by_compliance = 1 WHERE id = ?", (row['id'],))
                        elif st.session_state.role == "Chief Compliance Officer":
                            c.execute("UPDATE travel_costs SET approved_by_compliance = 1 WHERE id = ?", (row['id'],))
                        elif st.session_state.role == "Chief Risk Officer":
                            c.execute("UPDATE travel_costs SET approved_by_risk = 1 WHERE id = ?", (row['id'],))
                        elif st.session_state.role == "CFO/ED":
                            c.execute("""UPDATE travel_costs SET approved_by_finance = 1, payment_status = 'approved',
                                       payment_approved_by = ?, payment_approved_date = DATE('now') WHERE id = ?""",
                                     (st.session_state.full_name, row['id']))
                        elif st.session_state.role == "MD":
                            c.execute("""UPDATE travel_costs SET approved_by_md = 1, payment_status = 'approved',
                                       payment_approved_by = ?, payment_approved_date = DATE('now') WHERE id = ?""",
                                     (st.session_state.full_name, row['id']))
                        
                        c.execute("""INSERT INTO approvals (request_id, approver_role, approver_name, status, comments)
                                   VALUES (?, ?, ?, ?, ?)""",
                                 (row['request_id'], st.session_state.role, st.session_state.full_name, 
                                  "approved", f"Payment approved - NGN{row['total_cost']:,.2f}"))
                        conn.commit()
                        st.success("Payment approved!")
                        time.sleep(1)
                        st.rerun()
                
                with col_b:
                    if st.button(f"Reject Payment", key=f"reject_pay_{row['id']}"):
                        c = conn.cursor()
                        c.execute("UPDATE travel_costs SET payment_status = 'rejected' WHERE id = ?", (row['id'],))
                        c.execute("""INSERT INTO approvals (request_id, approver_role, approver_name, status, comments)
                                   VALUES (?, ?, ?, ?, ?)""",
                                 (row['request_id'], st.session_state.role, st.session_state.full_name, 
                                  "rejected", "Payment rejected"))
                        conn.commit()
                        st.error("Payment rejected!")
                        time.sleep(1)
                        st.rerun()
    else:
        st.info("No pending payment approvals")
    conn.close()

def payment_processing():
    if st.session_state.role != "Payables Officer":
        st.warning("Access denied")
        return
    
    st.markdown('<h1 class="sub-header">Payment Processing</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    approved_payments = pd.read_sql("""
        SELECT tc.*, tr.destination, u.full_name, u.bank_name, u.account_number, u.account_name
        FROM travel_costs tc JOIN travel_requests tr ON tc.request_id = tr.id
        JOIN users u ON tr.user_id = u.id
        WHERE tc.payment_status = 'approved' AND tc.payment_completed = 0
        ORDER BY tc.payment_approved_date DESC
    """, conn)
    
    if not approved_payments.empty:
        for _, row in approved_payments.iterrows():
            with st.expander(f"Payment #{row['id']} - {row['full_name']} - NGN{row['total_cost']:,.2f}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Employee:** {row['full_name']}")
                    st.write(f"**Destination:** {row['destination']}")
                    st.write(f"**Amount:** NGN{row['total_cost']:,.2f}")
                with col2:
                    st.write(f"**Bank:** {row['bank_name'] or 'Not provided'}")
                    st.write(f"**Account:** {row['account_number'] or 'Not provided'}")
                
                with st.form(f"process_{row['id']}"):
                    payment_method = st.selectbox("Payment Method", ["Bank Transfer", "Cheque", "Cash"])
                    reference_number = st.text_input("Reference Number")
                    payment_date = st.date_input("Payment Date", value=date.today())
                    
                    if st.form_submit_button("Mark as Paid", type="primary"):
                        c = conn.cursor()
                        c.execute("""UPDATE travel_costs SET payment_status = 'paid', payment_completed = 1,
                                   payment_date = ? WHERE id = ?""",
                                 (payment_date.strftime("%Y-%m-%d"), row['id']))
                        c.execute("""INSERT INTO payments (cost_id, amount, payment_method, reference_number, paid_by, paid_date)
                                   VALUES (?, ?, ?, ?, ?, ?)""",
                                 (row['id'], row['total_cost'], payment_method, reference_number,
                                  st.session_state.full_name, payment_date.strftime("%Y-%m-%d")))
                        update_budget(row['total_cost'])
                        conn.commit()
                        st.success("Payment completed! Budget updated.")
                        time.sleep(1)
                        st.rerun()
    else:
        st.info("No payments pending processing")
    conn.close()

def show_dashboard():
    st.markdown('<h1 class="main-header">Dashboard Overview</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    col1, col2, col3, col4 = st.columns(4)
    
    total = pd.read_sql("SELECT COUNT(*) FROM travel_requests WHERE user_id = ?", conn, params=(st.session_state.user_id,)).iloc[0,0]
    pending = pd.read_sql("SELECT COUNT(*) FROM travel_requests WHERE user_id = ? AND status = 'pending'", conn, params=(st.session_state.user_id,)).iloc[0,0]
    approved = pd.read_sql("SELECT COUNT(*) FROM travel_requests WHERE user_id = ? AND status = 'approved'", conn, params=(st.session_state.user_id,)).iloc[0,0]
    
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px;">
        <div class="metric-card"><h3 style="color:#D32F2F">{total}</h3><p>Total Travel</p></div>
        <div class="metric-card"><h3 style="color:#FF9800">{pending}</h3><p>Pending</p></div>
        <div class="metric-card"><h3 style="color:#4CAF50">{approved}</h3><p>Approved</p></div>
    </div>
    """, unsafe_allow_html=True)
    
    show_local_travel_policy()
    conn.close()

def show_profile():
    st.markdown('<h1 class="sub-header">My Profile</h1>', unsafe_allow_html=True)
    conn = sqlite3.connect('travel_app.db')
    user = pd.read_sql("SELECT * FROM users WHERE username = ?", conn, params=(st.session_state.username,)).iloc[0]
    
    st.write(f"**Name:** {user['full_name']}")
    st.write(f"**Username:** {user['username']}")
    st.write(f"**Email:** {user['email']}")
    st.write(f"**Phone:** {user['phone_number'] or 'Not provided'}")
    st.write(f"**Department:** {user['department']}")
    st.write(f"**Grade:** {user['grade']}")
    st.write(f"**Role:** {user['role']}")
    if user['bank_name']:
        st.write(f"**Bank:** {user['bank_name']} - {user['account_number']}")
    conn.close()

def profile_update():
    st.markdown('<h1 class="sub-header">Update Profile</h1>', unsafe_allow_html=True)
    conn = sqlite3.connect('travel_app.db')
    user = pd.read_sql("SELECT * FROM users WHERE username = ?", conn, params=(st.session_state.username,)).iloc[0]
    
    with st.form("update_form"):
        full_name = st.text_input("Full Name", value=user['full_name'])
        email = st.text_input("Email", value=user['email'])
        phone_number = st.text_input("Phone Number", value=user['phone_number'] or "")
        bank_name = st.text_input("Bank Name", value=user['bank_name'] or "")
        account_number = st.text_input("Account Number", value=user['account_number'] or "")
        account_name = st.text_input("Account Name", value=user['account_name'] or "")
        
        if st.form_submit_button("Update"):
            c = conn.cursor()
            c.execute("""UPDATE users SET full_name = ?, email = ?, phone_number = ?,
                       bank_name = ?, account_number = ?, account_name = ? WHERE username = ?""",
                     (full_name, email, phone_number, bank_name, account_number, account_name, st.session_state.username))
            conn.commit()
            st.session_state.full_name = full_name
            st.success("Profile updated!")
            time.sleep(1)
            st.rerun()
    conn.close()

def payment_status():
    st.markdown('<h1 class="sub-header">Payment Status</h1>', unsafe_allow_html=True)
    conn = sqlite3.connect('travel_app.db')
    payments = pd.read_sql("""
        SELECT tr.destination, tc.total_cost, tc.payment_status, tc.payment_date
        FROM travel_requests tr JOIN travel_costs tc ON tr.id = tc.request_id
        WHERE tr.user_id = ?
    """, conn, params=(st.session_state.user_id,))
    
    if not payments.empty:
        for _, row in payments.iterrows():
            st.markdown(f"""
            <div class="card">
                <h4>{row['destination']}</h4>
                <p>Amount: NGN{row['total_cost']:,.2f}</p>
                <p>Status: <span class="{row['payment_status']}-badge">{row['payment_status'].upper()}</span></p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No payment records found")
    conn.close()

def analytics_dashboard():
    st.markdown('<h1 class="sub-header">Analytics Dashboard</h1>', unsafe_allow_html=True)
    conn = sqlite3.connect('travel_app.db')
    
    data = pd.read_sql("""
        SELECT tr.travel_type, tr.status, tc.total_cost
        FROM travel_requests tr LEFT JOIN travel_costs tc ON tr.id = tc.request_id
        WHERE tr.user_id = ?
    """, conn, params=(st.session_state.user_id,))
    
    if not data.empty:
        col1, col2 = st.columns(2)
        with col1:
            status_counts = data['status'].value_counts()
            fig = px.pie(values=status_counts.values, names=status_counts.index, title="Requests by Status")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            type_counts = data['travel_type'].value_counts()
            fig = px.bar(x=type_counts.index, y=type_counts.values, title="Local vs International")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available")
    conn.close()

def budget_analytics():
    if st.session_state.role not in ["Head of Administration", "admin"]:
        st.warning("Access denied")
        return
    
    st.markdown('<h1 class="sub-header">Budget Analytics</h1>', unsafe_allow_html=True)
    budget = get_current_budget()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Budget", f"NGN{budget['total_budget']:,.0f}")
    with col2:
        st.metric("Utilized", f"NGN{budget['utilized_budget']:,.0f}")
    with col3:
        st.metric("Balance", f"NGN{budget['balance']:,.0f}")
    
    utilization = (budget['utilized_budget'] / budget['total_budget']) * 100
    st.markdown(f"""
    <div style="margin-top: 20px;">
        <div style="display: flex; justify-content: space-between;">
            <span>Budget Utilization</span>
            <span>{utilization:.1f}%</span>
        </div>
        <div class="budget-bar" style="width: {min(utilization, 100)}%;"></div>
    </div>
    """, unsafe_allow_html=True)

def compliance_approvals():
    payment_approvals()

def risk_approvals():
    payment_approvals()

def final_approvals():
    payment_approvals()

# ============ MAIN APP ============

def dashboard():
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 15px; background: #D32F2F; border-radius: 10px;">
            <h3 style="color: white;">PRUDENTIAL ZENITH</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: white; padding: 15px; border-radius: 10px; margin: 15px 0;">
            <h4 style="color:#D32F2F;">{st.session_state.full_name}</h4>
            <p>Role: {st.session_state.role}</p>
            <p>Grade: {st.session_state.grade}</p>
        </div>
        """, unsafe_allow_html=True)
        
        menu = ["Dashboard", "My Profile", "Update Profile", "Travel Request", "Travel History", "Payment Status", "Analytics"]
        
        if st.session_state.role in ["MD", "ED", "CFO/ED", "Head of Department", "Head of Administration", "Chief Compliance Officer", "Chief Risk Officer"]:
            menu.append("Approvals")
        
        if st.session_state.role == "Head of Administration":
            menu.extend(["Admin Panel", "Payment Approvals", "Budget Analytics"])
        elif st.session_state.role == "Chief Compliance Officer":
            menu.append("Compliance Approvals")
        elif st.session_state.role == "Chief Risk Officer":
            menu.append("Risk Approvals")
        elif st.session_state.role in ["CFO/ED", "MD"]:
            menu.append("Final Approvals")
        elif st.session_state.role == "Payables Officer":
            menu.append("Payment Processing")
        
        selected = option_menu("Navigation", menu, icons=["house"]*len(menu), menu_icon="compass", default_index=0)
        
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    
    # Route to selected page
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

def main():
    try:
        if not st.session_state.logged_in:
            if st.session_state.get('show_registration', False):
                registration_form()
            else:
                login()
        else:
            dashboard()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.button("Restart", on_click=lambda: st.rerun())

if __name__ == "__main__":
    main()
