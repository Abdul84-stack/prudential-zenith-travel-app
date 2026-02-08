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
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

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
</style>
""", unsafe_allow_html=True)

# Helper function to format currency
def format_currency(amount, currency_type="NGN"):
    """Format currency with appropriate symbol"""
    if currency_type == "USD":
        return f"${amount:,.2f}"
    else:  # NGN
        return f"₦{amount:,.2f}"

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
    if total_amount > 5000000:  # Greater than 5 million
        return ["Head of Administration", "Chief Compliance Officer", "Chief Risk Officer", "MD"]
    else:  # 5 million or less
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

def generate_pdf_report(request_data, cost_data, user_data):
    """Generate PDF report for travel request using reportlab"""
    # Create a temporary file for PDF
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_path = temp_file.name
    temp_file.close()
    
    # Create document
    doc = SimpleDocTemplate(
        temp_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#D32F2F'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#616161'),
        spaceBefore=20,
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=5
    )
    
    bold_style = ParagraphStyle(
        'CustomBold',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=5,
        fontName='Helvetica-Bold'
    )
    
    # Story to hold elements
    story = []
    
    # Title
    story.append(Paragraph("PRUDENTIAL ZENITH TRAVEL REQUEST REPORT", title_style))
    story.append(Paragraph("Travel Management System", heading_style))
    story.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    story.append(Spacer(1, 20))
    
    # Employee Information
    story.append(Paragraph("Employee Information", heading_style))
    
    employee_info = [
        ["Name:", user_data.get('full_name', 'N/A')],
        ["Employee ID:", user_data.get('employee_id', 'N/A')],
        ["Department:", user_data.get('department', 'N/A')],
        ["Grade:", user_data.get('grade', 'N/A')],
    ]
    
    employee_table = Table(employee_info, colWidths=[100, 300])
    employee_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#616161')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(employee_table)
    story.append(Spacer(1, 20))
    
    # Travel Details
    story.append(Paragraph("Travel Details", heading_style))
    
    travel_info = [
        ["Destination:", f"{request_data.get('city', 'N/A')}, {request_data.get('state', 'N/A')}"],
        ["Purpose:", request_data.get('purpose', 'N/A')],
        ["Travel Type:", request_data.get('travel_type', 'N/A').title()],
        ["Mode of Travel:", request_data.get('mode_of_travel', 'N/A')],
        ["Departure Date:", str(request_data.get('departure_date', 'N/A'))],
        ["Arrival Date:", str(request_data.get('arrival_date', 'N/A'))],
        ["Duration:", f"{request_data.get('duration_days', 0)} days ({request_data.get('duration_nights', 0)} nights)"],
        ["Accommodation:", request_data.get('accommodation_needed', 'N/A')],
    ]
    
    travel_table = Table(travel_info, colWidths=[100, 300])
    travel_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#616161')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(travel_table)
    story.append(Spacer(1, 20))
    
    # Cost Details if available
    if cost_data:
        story.append(Paragraph("Cost Details", heading_style))
        
        # Determine currency based on travel type
        currency_type = "USD" if request_data.get('travel_type') == 'international' else "NGN"
        
        cost_info = [
            ["Flight Cost:", format_currency(cost_data.get('flight_cost', 0), currency_type)],
            ["Per Diem Amount:", format_currency(cost_data.get('per_diem_amount', 0), currency_type)],
            ["Total Cost:", f"<b>{format_currency(cost_data.get('total_cost', 0), currency_type)}</b>"],
            ["Budget Balance:", format_currency(cost_data.get('budget_balance', 0), currency_type)],
        ]
        
        cost_table = Table(cost_info, colWidths=[100, 300])
        cost_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#616161')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TEXTCOLOR', (1, 2), (1, 2), colors.HexColor('#D32F2F')),
        ]))
        
        story.append(cost_table)
        story.append(Spacer(1, 20))
    
    # Approval Status
    story.append(Paragraph("Approval Status", heading_style))
    
    status_info = [
        ["Request Status:", request_data.get('status', 'N/A').upper()],
        ["Payment Status:", cost_data.get('payment_status', 'N/A') if cost_data else 'N/A'],
        ["Current Approver:", request_data.get('current_approver', 'N/A')],
    ]
    
    status_table = Table(status_info, colWidths=[100, 300])
    status_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#616161')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(status_table)
    story.append(Spacer(1, 30))
    
    # Footer
    footer_text = "Prudential Zenith Life Insurance • Travel Management System • This is an official document"
    story.append(Paragraph(footer_text, ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )))
    
    # Build PDF
    doc.build(story)
    
    return temp_path

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

# Main application functions (login, registration_form, dashboard, etc.)
# Note: I'll show the updated parts where currency formatting is used

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
        
        # Quick login info with ALL credentials including MD and ED
        st.markdown('<div class="quick-login">', unsafe_allow_html=True)
        st.markdown('<h4>🔑 Quick Login (Test Credentials)</h4>', unsafe_allow_html=True)
        st.markdown("""
        - **Head of Admin**: Username: `head_admin` | Password: `123456`
        - **Compliance**: Username: `chief_compliance` | Password: `123456`
        - **Risk Officer**: Username: `chief_risk` | Password: `123456`
        - **Payables**: Username: `payables` | Password: `123456`
        - **CFO/ED**: Username: `cfo_ed` | Password: `0123456`
        - **MD**: Username: `md` | Password: `123456`
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Authentication logic
        if login_btn:
            if not username or not password:
                st.error("⚠️ Please enter both username and password")
            else:
                # Check database for user credentials
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
                    st.session_state.employee_id = user[8]
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

# Updated travel_request_form with currency display
def travel_request_form():
    """Travel request form with updated cities"""
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

# Updated travel_history with PDF download and currency formatting
def travel_history():
    """Travel history with payment status and PDF download"""
    st.markdown('<h1 class="sub-header">Travel History</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # Get all travel requests for user
    query = """
    SELECT tr.*, tc.payment_status, tc.total_cost, tc.flight_cost, tc.per_diem_amount, tc.budget_balance
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
                
                # PDF Download button
                if st.button("📄 Download PDF Report", key=f"pdf_{row['id']}"):
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
                        'grade': user_data[6] if user_data else st.session_state.grade
                    }
                    
                    cost_dict = {}
                    if cost_data:
                        cost_dict = {
                            'flight_cost': cost_data[5],
                            'per_diem_amount': cost_data[4],
                            'total_cost': cost_data[7],
                            'budget_balance': cost_data[6],
                            'payment_status': cost_data[13]
                        }
                    
                    # Generate PDF
                    try:
                        pdf_file = generate_pdf_report(row, cost_dict, user_dict)
                        
                        # Download
                        with open(pdf_file, 'rb') as f:
                            st.download_button(
                                label="Click to Download PDF",
                                data=f,
                                file_name=f"travel_report_{row['id']}.pdf",
                                mime="application/pdf",
                                key=f"download_{row['id']}"
                            )
                        
                        # Clean up
                        os.unlink(pdf_file)
                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")
    else:
        st.info("No travel history found")
    
    conn.close()

# Updated admin_payment_requests with currency formatting
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
                        st.write("**Budget Information**")
                        budgeted_cost = st.number_input("Budgeted Cost (NGN)", min_value=0.0, step=1000.0,
                                                       key=f"budget_{row['id']}")
                        ytd_budget = st.number_input("YTD Budget (NGN)", min_value=0.0, step=1000.0,
                                                    key=f"ytd_budget_{row['id']}")
                        ytd_actual = st.number_input("YTD Actual (NGN)", min_value=0.0, step=1000.0,
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

# Updated payments_panel with currency formatting
def payments_panel():
    """Payables officer panel to mark payments as paid"""
    if st.session_state.role != "Payables":
        st.warning("Access denied. Only Payables officer can access this page.")
        return
    
    st.markdown('<h1 class="sub-header">Payments Management</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # Get approved payment requests
    query = """
    SELECT tc.*, tr.username, u.full_name, u.employee_id, u.department,
           u.bank_name, u.account_number, u.account_name, tr.travel_type
    FROM travel_costs tc
    JOIN travel_requests tr ON tc.request_id = tr.id
    JOIN users u ON tr.username = u.username
    WHERE tc.status = 'approved'
    AND tc.payment_status = 'pending'
    ORDER BY tc.created_at DESC
    """
    
    df = pd.read_sql(query, conn)
    
    if not df.empty:
        st.write(f"Found {len(df)} approved payment(s) pending processing")
        
        for _, row in df.iterrows():
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Determine currency based on travel type
                    currency_type = "USD" if row['travel_type'] == 'international' else "NGN"
                    
                    st.markdown(f"""
                    <div class="card approved">
                        <h4>Payment Request #{row['id']}</h4>
                        <p><strong>Employee:</strong> {row['full_name']} ({row['employee_id']})</p>
                        <p><strong>Department:</strong> {row['department']}</p>
                        <p><strong>Bank Details:</strong> {row['bank_name']} - {row['account_number']} ({row['account_name']})</p>
                        <p><strong>Total Amount:</strong> {format_currency(row['total_cost'], currency_type)}</p>
                        <p><strong>Flight Cost:</strong> {format_currency(row['flight_cost'], currency_type)}</p>
                        <p><strong>Per Diem:</strong> {format_currency(row['per_diem_amount'], currency_type)}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("Mark as Paid", key=f"paid_{row['id']}"):
                        c = conn.cursor()
                        c.execute("""UPDATE travel_costs 
                                  SET payment_status = 'paid', 
                                      paid_by = ?,
                                      paid_at = CURRENT_TIMESTAMP
                                  WHERE id = ?""",
                                 (st.session_state.full_name, row['id']))
                        conn.commit()
                        st.success("Payment marked as paid!")
                        time.sleep(1)
                        st.rerun()
    else:
        st.info("No payments pending processing")
    
    conn.close()

# Updated budget_analytics with currency formatting
def budget_analytics():
    """Budget analytics dashboard"""
    st.markdown('<h1 class="sub-header">Budget Analytics</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # Get budget data
    query = """
    SELECT department, year, month, 
           SUM(planned_budget) as planned_budget,
           SUM(actual_spent) as actual_spent,
           SUM(ytd_budget) as ytd_budget,
           SUM(ytd_actual) as ytd_actual,
           SUM(variance) as variance,
           AVG(variance_percentage) as variance_percentage
    FROM budgets
    GROUP BY department, year, month
    ORDER BY year DESC, month DESC
    """
    
    df = pd.read_sql(query, conn)
    
    if not df.empty:
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_budget = df['planned_budget'].sum()
            st.metric("Total Planned Budget", f"₦{total_budget:,.2f}")
        
        with col2:
            total_actual = df['actual_spent'].sum()
            st.metric("Total Actual Spent", f"₦{total_actual:,.2f}")
        
        with col3:
            total_variance = df['variance'].sum()
            st.metric("Total Variance", f"₦{total_variance:,.2f}")
        
        with col4:
            avg_variance_pct = df['variance_percentage'].mean()
            st.metric("Avg Variance %", f"{avg_variance_pct:.1f}%")
        
        st.markdown("---")
        
        # Detailed table
        st.subheader("Budget Details by Department")
        
        # Format the dataframe with NGN currency
        display_df = df.copy()
        display_df['planned_budget'] = display_df['planned_budget'].apply(lambda x: f"₦{x:,.2f}")
        display_df['actual_spent'] = display_df['actual_spent'].apply(lambda x: f"₦{x:,.2f}")
        display_df['ytd_budget'] = display_df['ytd_budget'].apply(lambda x: f"₦{x:,.2f}")
        display_df['ytd_actual'] = display_df['ytd_actual'].apply(lambda x: f"₦{x:,.2f}")
        display_df['variance'] = display_df['variance'].apply(lambda x: f"₦{x:,.2f}")
        display_df['variance_percentage'] = display_df['variance_percentage'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(display_df)
        
        # Export to Excel
        if st.button("📥 Export to Excel"):
            excel_file = io.BytesIO()
            df.to_excel(excel_file, index=False)
            excel_file.seek(0)
            st.download_button(
                label="Download Budget Report",
                data=excel_file,
                file_name="budget_analytics.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        # Visualization
        st.markdown("---")
        st.subheader("Budget vs Actual Visualization")
        
        fig = go.Figure(data=[
            go.Bar(name='Planned Budget (NGN)', x=df['department'], y=df['planned_budget']),
            go.Bar(name='Actual Spent (NGN)', x=df['department'], y=df['actual_spent'])
        ])
        fig.update_layout(barmode='group', title='Budget vs Actual by Department (NGN)')
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("No budget data available")
    
    conn.close()

# Updated analytics_dashboard with currency formatting
def analytics_dashboard():
    """Main analytics dashboard"""
    st.markdown('<h1 class="sub-header">Travel Analytics</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    # Get comprehensive travel data
    query = """
    SELECT tr.*, u.department, u.grade, 
           tc.total_cost, tc.flight_cost, tc.payment_status,
           CASE 
               WHEN tc.payment_status = 'paid' THEN 'Paid'
               WHEN tr.status = 'approved' AND tc.id IS NOT NULL THEN 'Approved for Payment'
               WHEN tr.status = 'approved' THEN 'Approved'
               WHEN tr.status = 'pending' THEN 'Pending'
               ELSE 'Rejected'
           END as overall_status
    FROM travel_requests tr
    LEFT JOIN users u ON tr.username = u.username
    LEFT JOIN travel_costs tc ON tr.id = tc.request_id
    ORDER BY tr.created_at DESC
    """
    
    df = pd.read_sql(query, conn)
    
    if not df.empty:
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_requests = len(df)
            st.metric("Total Requests", total_requests)
        
        with col2:
            approved_count = len(df[df['status'] == 'approved'])
            st.metric("Approved", approved_count)
        
        with col3:
            paid_count = len(df[df['payment_status'] == 'paid'])
            st.metric("Paid", paid_count)
        
        with col4:
            total_cost = df['total_cost'].sum()
            st.metric("Total Cost", f"₦{total_cost:,.2f}")
        
        st.markdown("---")
        
        # Export to Excel
        if st.button("📥 Export All Data to Excel"):
            excel_file = io.BytesIO()
            df.to_excel(excel_file, index=False)
            excel_file.seek(0)
            st.download_button(
                label="Download Full Report",
                data=excel_file,
                file_name="travel_analytics_full.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        # Tabs for different analytics
        tab1, tab2, tab3, tab4 = st.tabs(["Department Analysis", "Cost Analysis", "Timeline", "Geographic"])
        
        with tab1:
            dept_analysis = df.groupby('department').agg({
                'id': 'count',
                'total_cost': 'sum'
            }).rename(columns={'id': 'count'})
            
            fig1 = px.bar(dept_analysis, x=dept_analysis.index, y='count',
                         title='Travel Requests by Department')
            st.plotly_chart(fig1, use_container_width=True)
            
            fig2 = px.pie(df, names='status', title='Request Status Distribution')
            st.plotly_chart(fig2, use_container_width=True)
        
        with tab2:
            cost_by_dept = df.groupby('department')['total_cost'].sum().reset_index()
            fig3 = px.bar(cost_by_dept, x='department', y='total_cost',
                         title='Total Travel Cost by Department (NGN)')
            st.plotly_chart(fig3, use_container_width=True)
        
        with tab3:
            df['month'] = pd.to_datetime(df['created_at']).dt.to_period('M')
            monthly = df.groupby('month').agg({
                'id': 'count',
                'total_cost': 'sum'
            }).reset_index()
            monthly['month'] = monthly['month'].astype(str)
            
            fig4 = px.line(monthly, x='month', y='id',
                          title='Monthly Travel Requests')
            st.plotly_chart(fig4, use_container_width=True)
        
        with tab4:
            state_counts = df.groupby('state').size().reset_index(name='count')
            fig5 = px.choropleth(state_counts, 
                                locations=state_counts['state'],
                                locationmode='country names',
                                color='count',
                                hover_name='state',
                                title='Travel Requests by State')
            st.plotly_chart(fig5, use_container_width=True)
    
    else:
        st.info("No travel data available for analytics")
    
    conn.close()

# [Other functions remain the same as before - show_dashboard, show_profile, approvals_panel, update_approval_status, 
# payment_approvals_panel, admin_panel, manage_users, registration_form, dashboard, main]

# Note: Due to character limits, I've shown the most important updated functions.
# The remaining functions (show_dashboard, show_profile, approvals_panel, etc.) would follow the same pattern.
# They would be included in the full implementation with proper currency formatting.

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
