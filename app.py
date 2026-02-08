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
import tempfile

# Page configuration
st.set_page_config(
    page_title="Prudential Zenith Travel App",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Password hashing functions (defined first to avoid NameError)
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# Custom CSS with enhanced UI/UX
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
    .paid {
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
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
    .metric-card {
        background: linear-gradient(135deg, #f5f5f5, #ffffff);
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
        border: 1px solid #e0e0e0;
        text-align: center;
    }
    .tab-content {
        padding: 20px;
        border: 1px solid #ddd;
        border-radius: 5px;
        margin-top: 10px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f0f0;
        border-radius: 5px 5px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #D32F2F;
        color: white;
    }
    /* Currency styling */
    .currency-ngn {
        color: #D32F2F;
        font-weight: bold;
    }
    .currency-usd {
        color: #28a745;
        font-weight: bold;
    }
    /* PDF Report Styling */
    .pdf-report {
        background: white;
        padding: 40px;
        margin: 20px 0;
        font-family: Arial, sans-serif;
        border: 2px solid #D32F2F;
        border-radius: 10px;
    }
    .pdf-header {
        text-align: center;
        border-bottom: 3px solid #D32F2F;
        padding-bottom: 20px;
        margin-bottom: 30px;
    }
    .pdf-title {
        color: #D32F2F;
        font-size: 28px;
        margin: 0 0 10px 0;
        font-weight: bold;
    }
    .pdf-subtitle {
        color: #616161;
        font-size: 16px;
        margin: 5px 0;
    }
    .pdf-section {
        margin: 25px 0;
        padding: 20px;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        background: #f9f9f9;
    }
    .pdf-section-title {
        color: #D32F2F;
        font-size: 20px;
        border-bottom: 2px solid #D32F2F;
        padding-bottom: 10px;
        margin-bottom: 15px;
        font-weight: bold;
    }
    .pdf-row {
        display: flex;
        margin: 12px 0;
        padding: 8px 0;
        border-bottom: 1px dotted #ddd;
    }
    .pdf-label {
        font-weight: bold;
        color: #616161;
        width: 200px;
        min-width: 200px;
    }
    .pdf-value {
        color: #333;
        flex: 1;
    }
    .pdf-footer {
        text-align: center;
        color: #757575;
        font-size: 12px;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #e0e0e0;
    }
    .pdf-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
    }
    .pdf-table th {
        background-color: #D32F2F;
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: bold;
    }
    .pdf-table td {
        padding: 10px;
        border-bottom: 1px solid #ddd;
    }
    .pdf-table tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    .pdf-table tr:hover {
        background-color: #f5f5f5;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to format currency
def format_currency(amount, currency_type="NGN"):
    """Format currency with appropriate symbol"""
    if amount is None:
        return "N/A"
    
    try:
        amount = float(amount)
        if currency_type == "USD":
            return f"${amount:,.2f}"
        else:  # NGN
            return f"₦{amount:,.2f}"
    except:
        return "N/A"

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
    "Head of Department", "Team Lead", "Team Member", "Head of Administration",
    "Payables"
]

# Nigerian states and ALL cities
NIGERIAN_STATES = {
    "Abia": ["Aba", "Umuahia", "Arochukwu", "Ohafia", "Bende", "Isuikwuato"],
    "Adamawa": ["Yola", "Mubi", "Jimeta", "Ganye", "Numan", "Michika", "Mayo-Belwa"],
    "Akwa Ibom": ["Uyo", "Eket", "Ikot Ekpene", "Oron", "Abak", "Ikot Abasi", "Etinan"],
    "Anambra": ["Awka", "Onitsha", "Nnewi", "Ekulu", "Agulu", "Ihiala", "Ozubulu"],
    "Bauchi": ["Bauchi", "Azare", "Jama'are", "Katagum", "Misau", "Ningi"],
    "Bayelsa": ["Yenagoa", "Brass", "Ogbia", "Sagbama", "Nembe", "Ekeremor"],
    "Benue": ["Makurdi", "Gboko", "Otukpo", "Katsina-Ala", "Zaki Biam", "Adikpo"],
    "Borno": ["Maiduguri", "Bama", "Dikwa", "Askira", "Biu", "Monguno"],
    "Cross River": ["Calabar", "Ikom", "Ogoja", "Obudu", "Ugep", "Akamkpa"],
    "Delta": ["Asaba", "Warri", "Sapele", "Agbor", "Ughelli", "Burutu", "Koko"],
    "Ebonyi": ["Abakaliki", "Afikpo", "Onueke", "Ezza", "Ishielu", "Ikwo"],
    "Edo": ["Benin City", "Auchi", "Ekpoma", "Irrua", "Ubiaja", "Igueben"],
    "Ekiti": ["Ado-Ekiti", "Ikere", "Ise", "Emure", "Aramoko", "Igbara Odo"],
    "Enugu": ["Enugu", "Nsukka", "Agbani", "Awgu", "Udi", "Oji River"],
    "FCT": ["Abuja", "Gwagwalada", "Kuje", "Kubwa", "Lugbe", "Maitama"],
    "Gombe": ["Gombe", "Bajoga", "Kaltungo", "Dukku", "Deba", "Nafada"],
    "Imo": ["Owerri", "Orlu", "Okigwe", "Mgbidi", "Oguta", "Awo Omamma"],
    "Jigawa": ["Dutse", "Hadejia", "Birnin Kudu", "Gumel", "Kazaure", "Ringim"],
    "Kaduna": ["Kaduna", "Zaria", "Kafanchan", "Makarfi", "Saminaka", "Kagoro"],
    "Kano": ["Kano", "Bichi", "Dawakin Tofa", "Gaya", "Rano", "Wudil"],
    "Katsina": ["Katsina", "Daura", "Funtua", "Malumfashi", "Dutsinma", "Kankia"],
    "Kebbi": ["Birnin Kebbi", "Argungu", "Yauri", "Zuru", "Kamba", "Bagudo"],
    "Kogi": ["Lokoja", "Okene", "Idah", "Kabba", "Ajaokuta", "Ankpa"],
    "Kwara": ["Ilorin", "Offa", "Omu-Aran", "Jebba", "Lafiagi", "Patigi"],
    "Lagos": ["Lagos", "Ikeja", "Ikorodu", "Badagry", "Epe", "Lekki", "Victoria Island"],
    "Nasarawa": ["Lafia", "Keffi", "Akwanga", "Nasarawa", "Karu", "Doma"],
    "Niger": ["Minna", "Bida", "Suleja", "Kontagora", "Lapai", "Agaie"],
    "Ogun": ["Abeokuta", "Sagamu", "Ijebu Ode", "Ilaro", "Ota", "Ifo"],
    "Ondo": ["Akure", "Ondo", "Owo", "Okitipupa", "Irele", "Idanre"],
    "Osun": ["Osogbo", "Ile-Ife", "Ilesa", "Ede", "Iwo", "Ikire"],
    "Oyo": ["Ibadan", "Ogbomoso", "Oyo", "Iseyin", "Saki", "Kishi"],
    "Plateau": ["Jos", "Bukuru", "Shendam", "Pankshin", "Barkin Ladi", "Langtang"],
    "Rivers": ["Port Harcourt", "Bonny", "Degema", "Okrika", "Oyigbo", "Eleme"],
    "Sokoto": ["Sokoto", "Tambuwal", "Wurno", "Gwadabawa", "Bodinga", "Illela"],
    "Taraba": ["Jalingo", "Bali", "Wukari", "Takum", "Serti", "Gembu"],
    "Yobe": ["Damaturu", "Potiskum", "Gashua", "Geidam", "Nguru", "Buni Yadi"],
    "Zamfara": ["Gusau", "Kaura Namoda", "Bungudu", "Anka", "Talata Mafara", "Maru"]
}

# Travel policies - Updated with proper currency symbols
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
if 'employee_id' not in st.session_state:
    st.session_state.employee_id = ''

# Helper functions
def get_approval_flow(total_amount):
    """Determine payment approval flow based on amount"""
    if total_amount > 5000000:  # Greater than 5 million NGN
        return ["Head of Administration", "Chief Compliance Officer", "Chief Risk Officer", "MD"]
    else:  # 5 million NGN or less
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
            feeding_cost = policy["feeding"] * 3 * duration_nights  # 3 meals per day
            total = hotel_cost + feeding_cost
        else:
            total = 0  # Receipt required
        return total
    else:
        policy = INTERNATIONAL_POLICY[grade_category]
        # For international travel, return USD amount
        return policy["total"] * duration_nights

def generate_html_report(request_data, cost_data, user_data):
    """Generate HTML report for travel request that looks like a PDF"""
    # Determine currency based on travel type
    currency_type = "USD" if request_data.get('travel_type') == 'international' else "NGN"
    
    html_content = f"""
    <div class="pdf-report">
        <div class="pdf-header">
            <h1 class="pdf-title">PRUDENTIAL ZENITH TRAVEL REQUEST REPORT</h1>
            <p class="pdf-subtitle">Travel Management System</p>
            <p class="pdf-subtitle">Report ID: TR{request_data.get('id', '0000')}</p>
            <p class="pdf-subtitle">Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="pdf-section">
            <h2 class="pdf-section-title">Employee Information</h2>
            <table class="pdf-table">
                <tr>
                    <th>Field</th>
                    <th>Details</th>
                </tr>
                <tr>
                    <td>Full Name</td>
                    <td>{user_data.get('full_name', 'N/A')}</td>
                </tr>
                <tr>
                    <td>Employee ID</td>
                    <td>{user_data.get('employee_id', 'N/A')}</td>
                </tr>
                <tr>
                    <td>Department</td>
                    <td>{user_data.get('department', 'N/A')}</td>
                </tr>
                <tr>
                    <td>Grade</td>
                    <td>{user_data.get('grade', 'N/A')}</td>
                </tr>
                <tr>
                    <td>Bank Details</td>
                    <td>{user_data.get('bank_name', 'N/A')} - {user_data.get('account_number', 'N/A')} ({user_data.get('account_name', 'N/A')})</td>
                </tr>
            </table>
        </div>
        
        <div class="pdf-section">
            <h2 class="pdf-section-title">Travel Details</h2>
            <table class="pdf-table">
                <tr>
                    <th>Field</th>
                    <th>Details</th>
                </tr>
                <tr>
                    <td>Destination</td>
                    <td>{request_data.get('city', 'N/A')}, {request_data.get('state', 'N/A')}</td>
                </tr>
                <tr>
                    <td>Purpose of Travel</td>
                    <td>{request_data.get('purpose', 'N/A')}</td>
                </tr>
                <tr>
                    <td>Travel Type</td>
                    <td>{request_data.get('travel_type', 'N/A').upper()}</td>
                </tr>
                <tr>
                    <td>Mode of Travel</td>
                    <td>{request_data.get('mode_of_travel', 'N/A')}</td>
                </tr>
                <tr>
                    <td>Departure Date</td>
                    <td>{request_data.get('departure_date', 'N/A')}</td>
                </tr>
                <tr>
                    <td>Arrival Date</td>
                    <td>{request_data.get('arrival_date', 'N/A')}</td>
                </tr>
                <tr>
                    <td>Duration</td>
                    <td>{request_data.get('duration_days', 0)} days ({request_data.get('duration_nights', 0)} nights)</td>
                </tr>
                <tr>
                    <td>Accommodation Needed</td>
                    <td>{request_data.get('accommodation_needed', 'N/A')}</td>
                </tr>
            </table>
        </div>
    """
    
    if cost_data:
        html_content += f"""
        <div class="pdf-section">
            <h2 class="pdf-section-title">Cost Details ({currency_type})</h2>
            <table class="pdf-table">
                <tr>
                    <th>Item</th>
                    <th>Amount</th>
                </tr>
                <tr>
                    <td>Flight Cost</td>
                    <td>{format_currency(cost_data.get('flight_cost', 0), currency_type)}</td>
                </tr>
                <tr>
                    <td>Per Diem Amount</td>
                    <td>{format_currency(cost_data.get('per_diem_amount', 0), currency_type)}</td>
                </tr>
                <tr style="background-color: #f0f8ff; font-weight: bold;">
                    <td>TOTAL COST</td>
                    <td style="color: #D32F2F; font-size: 16px;">{format_currency(cost_data.get('total_cost', 0), currency_type)}</td>
                </tr>
                <tr>
                    <td>Budgeted Cost (NGN)</td>
                    <td>{format_currency(cost_data.get('budgeted_cost', 0), 'NGN')}</td>
                </tr>
                <tr>
                    <td>Budget Balance (NGN)</td>
                    <td>{format_currency(cost_data.get('budget_balance', 0), 'NGN')}</td>
                </tr>
            </table>
        </div>
        """
    
    html_content += f"""
        <div class="pdf-section">
            <h2 class="pdf-section-title">Approval Status</h2>
            <table class="pdf-table">
                <tr>
                    <th>Status Type</th>
                    <th>Status</th>
                </tr>
                <tr>
                    <td>Travel Request Status</td>
                    <td><strong>{request_data.get('status', 'N/A').upper()}</strong></td>
                </tr>
                <tr>
                    <td>Payment Status</td>
                    <td><strong>{cost_data.get('payment_status', 'N/A') if cost_data else 'N/A'}</strong></td>
                </tr>
                <tr>
                    <td>Current Approver</td>
                    <td>{request_data.get('current_approver', 'N/A')}</td>
                </tr>
                <tr>
                    <td>Request Date</td>
                    <td>{request_data.get('created_at', 'N/A')}</td>
                </tr>
            </table>
        </div>
        
        <div class="pdf-footer">
            <p>Prudential Zenith Life Insurance • Travel Management System v2.0</p>
            <p>This is an official document generated by the system. For verification, contact the Administration Department.</p>
            <p>© {datetime.datetime.now().year} Prudential Zenith Life Insurance. All rights reserved.</p>
        </div>
    </div>
    """
    
    return html_content

# Database initialization with new tables
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
                  employee_id TEXT,
                  bank_name TEXT,
                  account_number TEXT,
                  account_name TEXT,
                  profile_pic BLOB,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Travel requests table
    c.execute('''CREATE TABLE IF NOT EXISTS travel_requests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  employee_id TEXT,
                  travel_type TEXT,
                  destination TEXT,
                  state TEXT,
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
    
    # Travel costs table with budget fields
    c.execute('''CREATE TABLE IF NOT EXISTS travel_costs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  request_id INTEGER,
                  grade TEXT,
                  per_diem_amount REAL,
                  flight_cost REAL,
                  budgeted_cost REAL,
                  budget_balance REAL,
                  total_cost REAL,
                  supporting_docs BLOB,
                  admin_notes TEXT,
                  status TEXT DEFAULT 'pending',
                  approval_flow TEXT,
                  current_approver TEXT,
                  payment_status TEXT DEFAULT 'pending',
                  paid_by TEXT,
                  paid_at TIMESTAMP,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (request_id) REFERENCES travel_requests(id))''')
    
    # Approvals table for payment approval chain
    c.execute('''CREATE TABLE IF NOT EXISTS approvals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  request_id INTEGER,
                  cost_id INTEGER,
                  approver_role TEXT,
                  approver_name TEXT,
                  status TEXT,
                  comments TEXT,
                  approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (request_id) REFERENCES travel_requests(id),
                  FOREIGN KEY (cost_id) REFERENCES travel_costs(id))''')
    
    # Budget table for analytics
    c.execute('''CREATE TABLE IF NOT EXISTS budgets
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  department TEXT,
                  year INTEGER,
                  month INTEGER,
                  planned_budget REAL,
                  actual_spent REAL,
                  ytd_budget REAL,
                  ytd_actual REAL,
                  variance REAL,
                  variance_percentage REAL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create default users with new roles - INCLUDING MD and ED
    default_users = [
        ("CFO/Executive Director", "cfo_ed", "cfo@prudentialzenith.com", 
         make_hashes("0123456"), "Finance and Investment", "ED", "ED", "ED001",
         "Zenith Bank", "1234567890", "CFO ED", None),
        ("Managing Director", "md", "md@prudentialzenith.com", 
         make_hashes("123456"), "Office of CEO", "MD", "MD", "MD001",
         "Zenith Bank", "0987654321", "Managing Director", None),
        ("Head of Administration", "head_admin", "head.admin@prudentialzenith.com",
         make_hashes("123456"), "Administration", "DGM", "Head of Administration", "HA001",
         "Zenith Bank", "1122334455", "Head Admin", None),
        ("Chief Compliance Officer", "chief_compliance", "compliance@prudentialzenith.com",
         make_hashes("123456"), "Legal and Compliance", "DGM", "Chief Compliance Officer", "CCO001",
         "Zenith Bank", "2233445566", "Chief Compliance", None),
        ("Chief Risk Officer", "chief_risk", "risk@prudentialzenith.com",
         make_hashes("123456"), "Internal Control and Risk", "DGM", "Chief Risk Officer", "CRO001",
         "Zenith Bank", "3344556677", "Chief Risk", None),
        ("Payables Officer", "payables", "payables@prudentialzenith.com",
         make_hashes("123456"), "Finance and Investment", "AM", "Payables", "PAY001",
         "Zenith Bank", "4455667788", "Payables Officer", None),
    ]
    
    for user in default_users:
        try:
            c.execute('''INSERT OR IGNORE INTO users 
                       (full_name, username, email, password, department, grade, role, 
                        employee_id, bank_name, account_number, account_name, profile_pic) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', user)
        except:
            pass
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Note: Due to character limits, I'll show the most important updated functions.
# The complete implementation would include all functions from the previous version.

def travel_request_form():
    """Travel request form with updated cities and currency display"""
    st.markdown('<h1 class="sub-header">Travel Request Form</h1>', unsafe_allow_html=True)
    
    with st.form("travel_request_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            travel_type = st.selectbox("Travel Type*", ["local", "international"])
            purpose = st.text_area("Purpose of Travel*", height=100)
            mode_of_travel = st.selectbox("Mode of Travel*", ["Flight", "Road", "Rail"])
            accommodation_needed = st.selectbox("Accommodation Needed*", ["Yes", "No"])
            
            # Updated state and city selection
            state = st.selectbox("State*", list(NIGERIAN_STATES.keys()))
            if state:
                city = st.selectbox("City*", NIGERIAN_STATES[state])
            else:
                city = st.text_input("City*")
            
            destination = st.text_input("Destination Address*")
        
        with col2:
            departure_date = st.date_input("Departure Date*", min_value=date.today())
            arrival_date = st.date_input("Arrival Date*", min_value=date.today())
            
            if departure_date and arrival_date:
                duration = (arrival_date - departure_date).days
                duration_nights = max(0, duration - 1) if duration > 0 else 0
                st.info(f"Duration: {duration} days ({duration_nights} nights)")
            else:
                duration_nights = 0
            
            # Calculate estimated cost with proper currency
            if st.button("Calculate Estimated Cost"):
                estimated_cost = calculate_travel_costs(st.session_state.grade, travel_type, duration_nights)
                if travel_type == "international":
                    currency_symbol = "USD"
                    currency_display = f"${estimated_cost:,.2f}"
                    currency_class = "currency-usd"
                else:
                    currency_symbol = "NGN"
                    currency_display = f"₦{estimated_cost:,.2f}"
                    currency_class = "currency-ngn"
                
                st.markdown(f'<div class="{currency_class}">Estimated Cost: {currency_display} ({currency_symbol})</div>', unsafe_allow_html=True)
        
        submitted = st.form_submit_button("Submit Travel Request")
        
        if submitted:
            if not all([purpose, destination, city, state, mode_of_travel]):
                st.error("Please fill in all required fields (*)")
            elif departure_date >= arrival_date:
                st.error("Arrival date must be after departure date")
            else:
                conn = sqlite3.connect('travel_app.db')
                c = conn.cursor()
                
                # Insert travel request
                c.execute("""INSERT INTO travel_requests 
                          (username, employee_id, travel_type, destination, state, city, purpose, 
                           mode_of_travel, departure_date, arrival_date, accommodation_needed,
                           duration_days, duration_nights, current_approver)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         (st.session_state.username, st.session_state.employee_id, travel_type,
                          destination, state, city, purpose, mode_of_travel,
                          departure_date, arrival_date, accommodation_needed,
                          duration, duration_nights, "Head of Department"))
                
                request_id = c.lastrowid
                
                # Create initial approval record
                c.execute("""INSERT INTO approvals (request_id, approver_role, status)
                          VALUES (?, ?, ?)""",
                         (request_id, "Head of Department", "pending"))
                
                conn.commit()
                conn.close()
                
                st.success("Travel request submitted successfully!")
                time.sleep(2)
                st.rerun()

def travel_history():
    """Travel history with payment status and HTML report download"""
    st.markdown('<h1 class="sub-header">Travel History</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # Get all travel requests for user
    query = """
    SELECT tr.*, tc.payment_status, tc.total_cost, tc.flight_cost, tc.per_diem_amount, 
           tc.budget_balance, tc.budgeted_cost
    FROM travel_requests tr
    LEFT JOIN travel_costs tc ON tr.id = tc.request_id
    WHERE tr.username = ?
    ORDER BY tr.created_at DESC
    """
    
    df = pd.read_sql(query, conn, params=(st.session_state.username,))
    
    if not df.empty:
        # Add download button
        if st.button("📥 Export to Excel"):
            excel_file = io.BytesIO()
            df.to_excel(excel_file, index=False)
            excel_file.seek(0)
            st.download_button(
                label="Download Excel File",
                data=excel_file,
                file_name=f"travel_history_{st.session_state.username}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        # Display each travel request
        for _, row in df.iterrows():
            with st.expander(f"{row['destination']} - {row['departure_date']} to {row['arrival_date']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Purpose:** {row['purpose']}")
                    st.write(f"**Type:** {row['travel_type']}")
                    st.write(f"**Destination:** {row['city']}, {row['state']}")
                    st.write(f"**Mode:** {row['mode_of_travel']}")
                    st.write(f"**Accommodation:** {row['accommodation_needed']}")
                
                with col2:
                    status_color = {
                        'approved': 'green',
                        'pending': 'orange',
                        'rejected': 'red'
                    }.get(row['status'], 'gray')
                    
                    st.write(f"**Status:** :{status_color}[{row['status'].upper()}]")
                    st.write(f"**Payment Status:** {row['payment_status'] or 'N/A'}")
                    
                    # Display costs with proper currency
                    currency_type = "USD" if row['travel_type'] == 'international' else "NGN"
                    
                    if row['total_cost']:
                        st.write(f"**Total Cost:** {format_currency(row['total_cost'], currency_type)}")
                    else:
                        st.write("**Total Cost:** N/A")
                    
                    if row['flight_cost']:
                        st.write(f"**Flight Cost:** {format_currency(row['flight_cost'], currency_type)}")
                    else:
                        st.write("**Flight Cost:** N/A")
                    
                    if row['budgeted_cost']:
                        st.write(f"**Budgeted Cost:** {format_currency(row['budgeted_cost'], 'NGN')}")
                    
                    if row['budget_balance']:
                        st.write(f"**Budget Balance:** {format_currency(row['budget_balance'], 'NGN')}")
                
                # PDF Report button
                if st.button("📄 Generate Report", key=f"report_{row['id']}"):
                    # Get user data
                    c = conn.cursor()
                    c.execute("SELECT * FROM users WHERE username = ?", (st.session_state.username,))
                    user_data = c.fetchone()
                    
                    # Get cost data
                    c.execute("SELECT * FROM travel_costs WHERE request_id = ?", (row['id'],))
                    cost_data = c.fetchone()
                    
                    # Convert to dictionaries
                    user_dict = {
                        'full_name': user_data[1] if user_data else st.session_state.full_name,
                        'employee_id': user_data[8] if user_data else st.session_state.employee_id,
                        'department': user_data[5] if user_data else st.session_state.department,
                        'grade': user_data[6] if user_data else st.session_state.grade,
                        'bank_name': user_data[9] if user_data else "",
                        'account_number': user_data[10] if user_data else "",
                        'account_name': user_data[11] if user_data else ""
                    }
                    
                    cost_dict = {}
                    if cost_data:
                        cost_dict = {
                            'flight_cost': cost_data[5],
                            'per_diem_amount': cost_data[4],
                            'total_cost': cost_data[7],
                            'budget_balance': cost_data[6],
                            'budgeted_cost': cost_data[5],
                            'payment_status': cost_data[13]
                        }
                    
                    # Generate HTML report
                    html_report = generate_html_report(row, cost_dict, user_dict)
                    
                    # Display report
                    st.markdown("### Travel Request Report (PDF Style)")
                    st.markdown(html_report, unsafe_allow_html=True)
                    
                    # Option to download as HTML (can be printed as PDF from browser)
                    html_bytes = html_report.encode('utf-8')
                    st.download_button(
                        label="📥 Download as HTML (Print as PDF)",
                        data=html_bytes,
                        file_name=f"travel_report_{row['id']}.html",
                        mime="text/html",
                        key=f"download_{row['id']}",
                        help="Download and open in browser, then use 'Print > Save as PDF'"
                    )
    else:
        st.info("No travel history found")
    
    conn.close()

def admin_payment_requests():
    """Head of Administration: Payment request initiation with budget"""
    if st.session_state.role != "Head of Administration":
        st.warning("Access denied. Only Head of Administration can access this page.")
        return
    
    st.markdown('<h1 class="sub-header">Payment Request Initiation</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # Get approved travel requests without cost entry
    query = """
    SELECT tr.*, u.full_name, u.department, u.grade, u.employee_id
    FROM travel_requests tr
    JOIN users u ON tr.username = u.username
    WHERE tr.status = 'approved'
    AND tr.id NOT IN (SELECT request_id FROM travel_costs)
    ORDER BY tr.created_at DESC
    """
    
    df = pd.read_sql(query, conn)
    
    if not df.empty:
        st.write(f"Found {len(df)} approved travel request(s) pending cost entry")
        
        for _, row in df.iterrows():
            with st.expander(f"Request #{row['id']} - {row['full_name']} ({row['employee_id']})"):
                with st.form(f"cost_form_{row['id']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Travel Details**")
                        st.write(f"Destination: {row['destination']}, {row['city']}")
                        st.write(f"Purpose: {row['purpose']}")
                        st.write(f"Dates: {row['departure_date']} to {row['arrival_date']}")
                        st.write(f"Duration: {row['duration_days']} days")
                        st.write(f"Grade: {row['grade']}")
                        
                        # Budget information
                        st.write("**Budget Information (NGN)**")
                        budgeted_cost = st.number_input("Budgeted Cost", min_value=0.0, step=1000.0,
                                                       key=f"budget_{row['id']}")
                        ytd_budget = st.number_input("YTD Budget", min_value=0.0, step=1000.0,
                                                    key=f"ytd_budget_{row['id']}")
                        ytd_actual = st.number_input("YTD Actual", min_value=0.0, step=1000.0,
                                                    key=f"ytd_actual_{row['id']}")
                    
                    with col2:
                        st.write("**Cost Details**")
                        
                        # Determine currency based on travel type
                        currency_type = "USD" if row['travel_type'] == 'international' else "NGN"
                        currency_label = f" ({currency_type})"
                        
                        flight_cost = st.number_input(f"Flight Cost{currency_label}", min_value=0.0, step=1000.0,
                                                     key=f"flight_{row['id']}")
                        per_diem = st.number_input(f"Per Diem Amount{currency_label}", min_value=0.0, step=1000.0,
                                                  key=f"perdiem_{row['id']}")
                        
                        # Calculate total and budget balance
                        total_cost = flight_cost + per_diem
                        budget_balance = budgeted_cost - total_cost
                        
                        st.write(f"**Total Cost:** {format_currency(total_cost, currency_type)}")
                        st.write(f"**Budget Balance:** {format_currency(budget_balance, 'NGN')}")
                        
                        supporting_docs = st.file_uploader("Supporting Documents", 
                                                          type=['pdf', 'jpg', 'jpeg', 'png'],
                                                          key=f"docs_{row['id']}")
                        admin_notes = st.text_area("Admin Notes", key=f"notes_{row['id']}")
                    
                    submitted = st.form_submit_button("Submit Payment Request")
                    
                    if submitted:
                        # Determine approval flow based on total amount
                        approval_flow = get_approval_flow(total_cost)
                        
                        # Save travel cost
                        c = conn.cursor()
                        c.execute("""INSERT INTO travel_costs 
                                  (request_id, grade, per_diem_amount, flight_cost, 
                                   budgeted_cost, budget_balance, total_cost, admin_notes,
                                   approval_flow, current_approver)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                 (row['id'], row['grade'], per_diem, flight_cost,
                                  budgeted_cost, budget_balance, total_cost, admin_notes,
                                  json.dumps(approval_flow), approval_flow[0]))
                        
                        cost_id = c.lastrowid
                        
                        # Create budget record
                        variance = ytd_budget - ytd_actual
                        variance_percentage = (variance / ytd_budget * 100) if ytd_budget > 0 else 0
                        
                        c.execute("""INSERT INTO budgets 
                                  (department, year, month, planned_budget, actual_spent,
                                   ytd_budget, ytd_actual, variance, variance_percentage)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                 (row['department'], datetime.datetime.now().year,
                                  datetime.datetime.now().month, budgeted_cost, total_cost,
                                  ytd_budget, ytd_actual, variance, variance_percentage))
                        
                        # Create initial payment approval record
                        c.execute("""INSERT INTO approvals (request_id, cost_id, approver_role, status)
                                  VALUES (?, ?, ?, ?)""",
                                 (row['id'], cost_id, approval_flow[0], "pending"))
                        
                        conn.commit()
                        
                        st.success("Payment request submitted for approval!")
                        time.sleep(2)
                        st.rerun()
    else:
        st.info("No approved travel requests pending cost entry")
    
    conn.close()

# [Other functions would be included here - they remain similar to previous versions]
# For brevity, I'm showing the key updated functions. The complete code would include:
# - login()
# - registration_form()
# - dashboard()
# - show_dashboard()
# - show_profile()
# - approvals_panel()
# - update_approval_status()
# - payment_approvals_panel()
# - payments_panel()
# - budget_analytics()
# - analytics_dashboard()
# - admin_panel()
# - manage_users()

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
