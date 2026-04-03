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

# Custom CSS with RED and GREY color scheme
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
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border: 2px solid #D32F2F;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
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
    .travel-policy-table tr:nth-child(even) {
        background-color: #f9f9f9;
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

# Marital Status options
MARITAL_STATUS = ["Single", "Married", "Divorced", "Widowed", "Separated"]

# UPDATED: Nigerian states with comprehensive cities
NIGERIAN_STATES = {
    "Abia": ["Aba", "Umuahia", "Arochukwu", "Ohafia", "Bende", "Isuikwuato", "Abiriba", "Mbawsi", "Amasiri", "Item", "Ovim", "Ozu Abam", "Amaekpu", "Igbere", "Nkporo", "Abam", "Ohafor", "Uzuakoli", "Osisioma", "Obingwa", "Ugwuoba"],
    "Adamawa": ["Yola", "Mubi", "Jimeta", "Ganye", "Numan", "Mayo-Belwa", "Michika", "Gombi", "Hong", "Song", "Shelleng", "Guyuk", "Lamurde", "Demsa", "Fufore", "Madagali", "Maiha", "Jada", "Toungo", "Kojoli", "Bachure", "Bazza"],
    "Akwa Ibom": ["Uyo", "Eket", "Ikot Ekpene", "Oron", "Ikot Abasi", "Abak", "Etinan", "Essien Udim", "Mkpat Enin", "Okobo", "Udung Uko", "Urue Offong", "Nsit Ibom", "Nsit Ubium", "Ibesikpo Asutan", "Oruk Anam", "Eastern Obolo", "Ibeno", "Mbo", "Ukanafun", "Onna", "Esit Eket"],
    "Anambra": ["Awka", "Onitsha", "Nnewi", "Aguata", "Ogidi", "Ekwulobia", "Ozubulu", "Oba", "Oko", "Nkpor", "Obosi", "Umunze", "Alor", "Ihiala", "Ukpo", "Abagana", "Enugwu Ukwu", "Nawfia", "Awkuzu", "Umuoji", "Nimo", "Agulu"],
    "Bauchi": ["Bauchi", "Azare", "Jama'are", "Katagum", "Misau", "Ningi", "Darazo", "Gamawa", "Dambam", "Giade", "Itas", "Shira", "Tafawa Balewa", "Bogoro", "Dass", "Toro", "Warji", "Zaki", "Ganjuwa", "Kirfi", "Alkaleri", "Burra"],
    "Bayelsa": ["Yenagoa", "Brass", "Ogbia", "Sagbama", "Ekeremor", "Nembe", "Amassoma", "Odi", "Kaiama", "Okpoama", "Twon-Brass", "Akassa", "Agudama", "Ekeki", "Opolo", "Swali", "Okutukutu", "Akenfa", "Amarata", "Igbogene", "Ebikeme", "Ogu"],
    "Benue": ["Makurdi", "Gboko", "Otukpo", "Katsina-Ala", "Vandeikya", "Adikpo", "Aliade", "Oju", "Okpoga", "Ushongo", "Lessel", "Mkar", "Yandev", "Zaki Biam", "Buruku", "Gbajimba", "Tse-Agberagba", "Ugba", "Ukum", "Logo", "Kwande", "Konshisha"],
    "Borno": ["Maiduguri", "Bama", "Dikwa", "Gwoza", "Monguno", "Biu", "Konduga", "Damboa", "Askira", "Uba", "Chibok", "Kwaya Kusar", "Shani", "Kaga", "Kukawa", "Marte", "Gubio", "Guzamala", "Mobbar", "Abadam", "Ngala", "Kala Balge"],
    "Cross River": ["Calabar", "Ugep", "Ogoja", "Obudu", "Ikom", "Akamkpa", "Obubra", "Odukpani", "Akpabuyo", "Bakassi", "Biase", "Abi", "Yala", "Boki", "Etung", "Bekwarra", "Obanliku", "Odukpani", "Akamkpa", "Calabar South", "Ikpai", "Uwet"],
    "Delta": ["Asaba", "Warri", "Sapele", "Ughelli", "Burutu", "Agbor", "Ozoro", "Kwale", "Obiaruku", "Abraka", "Oleh", "Patani", "Bomadi", "Koko", "Ogwashi-Uku", "Issele-Uku", "Ubulu-Uku", "Illah", "Igbodo", "Ebu", "Oghara", "Effurun"],
    "Ebonyi": ["Abakaliki", "Afikpo", "Onueke", "Edda", "Ishielu", "Ezza", "Ikwo", "Ohaozara", "Uburu", "Okposi", "Amasiri", "Onicha", "Ivo", "Effium", "Nkalagu", "Isu", "Onyege", "Agbaja", "Ndiegu", "Okoffia", "Ezzamgbo", "Iboko"],
    "Edo": ["Benin City", "Auchi", "Ekpoma", "Igueben", "Uromi", "Irrua", "Oredo", "Ubiaja", "Abudu", "Igarra", "Sabongida-Ora", "Agenebode", "Okpella", "Fugar", "Ewu", "Uzebba", "Igbanke", "Ogwa", "Ehor", "Ohosu", "Afuze", "Iuleha"],
    "Ekiti": ["Ado-Ekiti", "Ikere", "Ijero-Ekiti", "Oye", "Ikole", "Efon", "Ise", "Emure", "Aramoko", "Ipoti", "Omuo", "Otun", "Ode", "Ilave", "Igbemo", "Iworoko", "Are", "Ayede", "Ogotun", "Usi", "Itapa", "Ilupeju"],
    "Enugu": ["Enugu", "Nsukka", "Agbani", "Udi", "Oji-River", "Awgu", "Enugu Ezike", "Ezeagu", "Aku", "Obolo", "Obollo-Afor", "Ikem", "Amagunze", "Eha-Amufu", "Mburubu", "Ogbede", "Ukehe", "Nike", "Abor", "Ihe", "Ugwuoba", "Owelli"],
    "FCT": ["Abuja", "Gwagwalada", "Kuje", "Bwari", "Kwali", "Abaji", "Karu", "Kubwa", "Lugbe", "Gwarimpa", "Wuse", "Maitama", "Asokoro", "Jabi", "Utako", "Garki", "Nyanya", "Karshi", "Dutse", "Bwari", "Kurudu", "Kado"],
    "Gombe": ["Gombe", "Kaltungo", "Bajoga", "Dukku", "Nafada", "Billiri", "Akko", "Yamaltu", "Deba", "Pindiga", "Dadinkowa", "Kumo", "Hinna", "Bara", "Dukul", "Liji", "Jekadafari", "Pantami", "Arawa", "Tumu", "Gona", "Kwami"],
    "Imo": ["Owerri", "Orlu", "Okigwe", "Mgbidi", "Oguta", "Mbaise", "Ohaji", "Orodo", "Umuahia", "Nkwerre", "Awo-Omamma", "Osu", "Owerrinta", "Ihite", "Orodo", "Amaigbo", "Arondizuogu", "Aboh", "Nnenasa", "Eziama", "Umuguma", "Ihiagwa"],
    "Jigawa": ["Dutse", "Hadejia", "Gumel", "Kazaure", "Ringim", "Birnin Kudu", "Babura", "Garki", "Miga", "Maigatari", "Gwaram", "Buji", "Jahun", "Gwiwa", "Yankwashi", "Auyo", "Kafin Hausa", "Kiri Kasama", "Taura", "Sule Tankarkar", "Guri", "Kaugama"],
    "Kaduna": ["Kaduna", "Zaria", "Kafanchan", "Saminaka", "Makarf", "Birnin Gwari", "Jema'a", "Ikara", "Kagarko", "Kachia", "Soba", "Giwa", "Kubau", "Kudan", "Lere", "Makarfi", "Sabon Gari", "Zangon Kataf", "Kaura", "Jaba", "Chikun", "Igabi"],
    "Kano": ["Kano", "Wudil", "Gaya", "Dawakin Kudu", "Bichi", "Rano", "Kura", "Karaye", "Gezawa", "Minjibir", "Dambatta", "Makoda", "Garko", "Ajingi", "Albasu", "Bagwai", "Bebeji", "Dala", "Dawakin Tofa", "Doguwa", "Fagge", "Gabasawa"],
    "Katsina": ["Katsina", "Funtua", "Daura", "Malumfashi", "Kankia", "Dutsinma", "Musawa", "Mani", "Bakori", "Danja", "Faskari", "Jibia", "Kaita", "Batagarawa", "Batsari", "Baure", "Bindawa", "Charanchi", "Dan Musa", "Ingawa", "Kafur", "Kankara"],
    "Kebbi": ["Birnin Kebbi", "Argungu", "Yelwa", "Zuru", "Gwandu", "Jega", "Bagudo", "Koko", "Danko", "Sakaba", "Fakai", "Ngaski", "Shanga", "Arewa", "Bunza", "Kalgo", "Maiyama", "Suru", "Augie", "Wasagu", "Dakingari", "Mahuta"],
    "Kogi": ["Lokoja", "Okene", "Idah", "Kabba", "Ankpa", "Dekina", "Ajaokuta", "Ogaminana", "Anyigba", "Ogori", "Isanlu", "Egbe", "Iyamoye", "Mopa", "Odo-Ere", "Ogugu", "Olamaboro", "Olowa", "Okenne", "Ayangba", "Koton-Karfe", "Gegu"],
    "Kwara": ["Ilorin", "Offa", "Omu-Aran", "Patigi", "Lafiagi", "Jebba", "Kaiama", "Oke-Ode", "Ajasse Ipo", "Oro", "Araromi", "Bode Saadu", "Gure", "Idofian", "Igbaja", "Ila", "Ilorin South", "Malete", "Oke Onigbin", "Oko", "Osi", "Share"],
    "Lagos": ["Lagos Island", "Ikeja", "Badagry", "Epe", "Ikorodu", "Ojo", "Alimosho", "Mushin", "Surulere", "Apapa", "Ajeromi", "Amuwo Odofin", "Agege", "Ifako-Ijaiye", "Kosofe", "Lagos Mainland", "Somolu", "Oshodi", "Isolo", "Victoria Island", "Lekki", "Ajegunle"],
    "Nasarawa": ["Lafia", "Keffi", "Akwanga", "Nasarawa", "Karu", "Doma", "Toto", "Wamba", "Kokona", "Awe", "Obi", "Eggon", "Keana", "Nasarawa Eggon", "Gudi", "Agwada", "Assakio", "Azara", "Daddare", "Gidan Waya", "Udegi", "Riri"],
    "Niger": ["Minna", "Suleja", "Bida", "Kontagora", "Lapai", "Agaie", "Mokwa", "Wushishi", "Rijau", "Magama", "Mariga", "Shiroro", "Paikoro", "Gurara", "Chanchaga", "Bosso", "Katcha", "Edati", "Lavun", "Gbako", "Agwara", "Borgu"],
    "Ogun": ["Abeokuta", "Sagamu", "Ijebu-Ode", "Ilaro", "Aiyetoro", "Ado-Odo", "Otta", "Ijebu-Igbo", "Owode", "Ifo", "Agbara", "Ikenne", "Imeko", "Ota", "Odogbolu", "Ewekoro", "Obafemi", "Odeda", "Remo North", "Ipokia", "Ijebu North", "Ogun Waterside"],
    "Ondo": ["Akure", "Ondo City", "Owo", "Okitipupa", "Ore", "Oka", "Ifon", "Idanre", "Igbokoda", "Ikare", "Oba Ile", "Isua", "Ese Odo", "Irele", "Odigbo", "Akoko", "Ose", "Oke Igbo", "Ayede", "Ilara", "Iju", "Oda"],
    "Osun": ["Osogbo", "Ile-Ife", "Ilesa", "Iwo", "Ede", "Ikirun", "Ejigbo", "Iragbiji", "Ikire", "Gbongan", "Modakeke", "Apomu", "Ipetumodu", "Otan-Ayegbaju", "Ode-Omu", "Ijebu-Jesa", "Esa-Oke", "Okuku", "Oluponna", "Ila Orangun", "Iree", "Esa-Odo"],
    "Oyo": ["Ibadan", "Ogbomosho", "Oyo", "Iseyin", "Saki", "Okeho", "Igbo-Ora", "Kishi", "Koso", "Fiditi", "Awe", "Lalupon", "Moniya", "Eruwa", "Lanlate", "Igbeti", "Sepeteri", "Iganna", "Tede", "Agbang", "Oje", "Orelope"],
    "Plateau": ["Jos", "Bukuru", "Pankshin", "Shendam", "Langtang", "Barkin Ladi", "Mangu", "Wase", "Bokkos", "Kanke", "Kanam", "Riyom", "Qua'an Pan", "Mikang", "Bassa", "Jos East", "Jos North", "Jos South", "Langtang North", "Langtang South", "Pyem", "Ron"],
    "Rivers": ["Port Harcourt", "Bonny", "Degema", "Okrika", "Oyigbo", "Ahoada", "Bori", "Omoku", "Elele", "Emohua", "Ikwerre", "Khana", "Gokana", "Tai", "Opobo", "Andoni", "Asari-Toru", "Akuku-Toru", "Abua-Odual", "Ogu Bolo", "Eleme", "Obio-Akpor"],
    "Sokoto": ["Sokoto", "Tambuwal", "Wurno", "Gwadabawa", "Illela", "Binji", "Goronyo", "Isa", "Rabah", "Sabon Birni", "Shagari", "Silame", "Tangaza", "Tureta", "Wamako", "Bodinga", "Dange Shuni", "Gada", "Gudu", "Kware", "Kebbe", "Yabo"],
    "Taraba": ["Jalingo", "Bali", "Takum", "Wukari", "Serti", "Mutum Biyu", "Ibi", "Lau", "Gembu", "Zing", "Yorro", "Donga", "Ussa", "Kurmi", "Gassol", "Ardo Kola", "Karim Lamido", "Lau", "Sardauna", "Bali", "Gashaka", "Poli"],
    "Yobe": ["Damaturu", "Potiskum", "Gashua", "Geidam", "Nguru", "Bade", "Fika", "Gujba", "Gulani", "Tarmuwa", "Yunusari", "Bursari", "Karasuwa", "Machina", "Nangere", "Yusufari", "Jakusko", "Fune", "Barde", "Borsari", "Giedam", "Kanamma"],
    "Zamfara": ["Gusau", "Kaura Namoda", "Talata Mafara", "Anka", "Bukkuyum", "Maru", "Bungudu", "Tsafe", "Shinkafi", "Zurmi", "Bakura", "Maradun", "Gummi", "Birnin Magaji", "Kaura", "Kiyawa", "Mada", "Moriki", "Ruwan Bore", "Wanke", "Gusau", "Kaura"]
}

# UPDATED: Complete list of all countries
COUNTRIES = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia", 
    "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", 
    "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", 
    "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", 
    "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Congo", "Costa Rica", 
    "Côte d'Ivoire", "Croatia", "Cuba", "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica", 
    "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", 
    "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", 
    "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hungary", 
    "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", 
    "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea, North", "Korea, South", "Kosovo", "Kuwait", 
    "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", 
    "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", 
    "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", 
    "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", 
    "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Palestine", 
    "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar", 
    "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", 
    "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", 
    "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", 
    "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "Taiwan", 
    "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", 
    "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", 
    "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican City", "Venezuela", "Vietnam", "Yemen", 
    "Zambia", "Zimbabwe"
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

# UPDATED: International Travel Policy with new rates and exchange rate
USD_TO_NGN = 1400  # Exchange rate: USD 1 = NGN 1,400

INTERNATIONAL_POLICY = {
    "MD": {
        "accommodation": 500,
        "feeding": 200,
        "out_of_station": 200,
        "airport_taxi": 250,
        "total_usd": 1150,
        "total_ngn": 1150 * USD_TO_NGN,
        "accommodation_text": "$500 Per/Night",
        "feeding_text": "$200/Day",
        "out_of_station_text": "$200/Day",
        "airport_taxi_text": "$250 (One-time, round trip)"
    },
    "ED": {
        "accommodation": 200,
        "feeding": 150,
        "out_of_station": 150,
        "airport_taxi": 200,
        "total_usd": 700,
        "total_ngn": 700 * USD_TO_NGN,
        "accommodation_text": "$200/Night",
        "feeding_text": "$150/Day",
        "out_of_station_text": "$150/Day",
        "airport_taxi_text": "$200 (One-time, round trip)"
    },
    "AGM-GM": {
        "accommodation": 150,
        "feeding": 100,
        "out_of_station": 100,
        "airport_taxi": 150,
        "total_usd": 500,
        "total_ngn": 500 * USD_TO_NGN,
        "accommodation_text": "$150/Night",
        "feeding_text": "$100/Day",
        "out_of_station_text": "$100/Day",
        "airport_taxi_text": "$150 (One-time, round trip)"
    },
    "AM-PM": {
        "accommodation": 100,
        "feeding": 80,
        "out_of_station": 80,
        "airport_taxi": 100,
        "total_usd": 360,
        "total_ngn": 360 * USD_TO_NGN,
        "accommodation_text": "$100/Night",
        "feeding_text": "$80/day",
        "out_of_station_text": "$80/Day",
        "airport_taxi_text": "$100 (One-time, round trip)"
    },
    "EA-SO": {
        "accommodation": 100,
        "feeding": 50,
        "out_of_station": 60,
        "airport_taxi": 100,
        "total_usd": 310,
        "total_ngn": 310 * USD_TO_NGN,
        "accommodation_text": "$100/Night",
        "feeding_text": "$50/Day",
        "out_of_station_text": "$60/Day",
        "airport_taxi_text": "$100 (One-time, round trip)"
    }
}

# Budget configuration
ANNUAL_BUDGET = 120000000  # NGN 120,000,000

class PDFReport(FPDF):
    def header(self):
        # Only add header if not on first page or if first page content is not duplicated
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
        self.cell(45, 8, f'{label}:', 0, 0)
        self.set_font('Arial', '', 10)
        self.set_text_color(33, 33, 33)
        
        if isinstance(value, bytes):
            value = value.decode('utf-8', errors='ignore')
        else:
            value = str(value)
        
        value = value.replace('NGN', 'NGN ')
        
        if self.get_string_width(value) > 150:
            self.multi_cell(0, 8, value, 0, 1)
        else:
            self.cell(0, 8, value, 0, 1)

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
                  bank_name TEXT,
                  account_number TEXT,
                  account_name TEXT,
                  phone_number TEXT,
                  date_of_birth DATE,
                  place_of_birth TEXT,
                  passport_number TEXT,
                  nationality TEXT,
                  marital_status TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Travel requests table
    c.execute('''CREATE TABLE IF NOT EXISTS travel_requests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  username TEXT,
                  travel_type TEXT,
                  destination TEXT,
                  city TEXT,
                  country TEXT,
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
    
    # Travel costs table
    c.execute('''CREATE TABLE IF NOT EXISTS travel_costs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  request_id INTEGER,
                  grade TEXT,
                  per_diem_amount REAL,
                  flight_cost REAL,
                  airport_taxi_cost REAL,
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
    
    # Create default users
    default_users = [
        ("CFO/Executive Director", "cfo_ed", "cfo@prudentialzenith.com", 
         make_hashes("0123456"), "Finance and Investment", "ED", "CFO/ED"),
        ("Managing Director", "md", "md@prudentialzenith.com", 
         make_hashes("123456"), "Office of CEO", "MD", "MD"),
        ("Chief Commercial Officer", "chief_commercial", "commercial@prudentialzenith.com",
         make_hashes("123456"), "Corporate Sales", "DGM", "Chief Commercial Officer"),
        ("Chief Agency Officer", "chief_agency", "agency@prudentialzenith.com",
         make_hashes("123456"), "Agencies", "DGM", "Chief Agency Officer"),
        ("Chief Compliance Officer", "chief_compliance", "compliance@prudentialzenith.com",
         make_hashes("123456"), "Legal and Compliance", "DGM", "Chief Compliance Officer"),
        ("Chief Risk Officer", "chief_risk", "risk@prudentialzenith.com",
         make_hashes("123456"), "Internal Control and Risk", "DGM", "Chief Risk Officer"),
        ("Payables Officer", "payables", "payables@prudentialzenith.com",
         make_hashes("123456"), "Finance and Investment", "Officer", "Payables Officer"),
        ("Executive Director", "ed", "ed@prudentialzenith.com",
         make_hashes("123456"), "Office of Executive Director", "ED", "ED"),
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
    
    # Initialize budget for current year
    current_year = datetime.datetime.now().year
    c.execute('''INSERT OR IGNORE INTO budget (year, total_budget, utilized_budget, balance)
                 VALUES (?, ?, 0, ?)''', (current_year, ANNUAL_BUDGET, ANNUAL_BUDGET))
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

def get_grade_category_for_local(grade):
    """Map grade to local policy category"""
    if grade == "MD":
        return "MD"
    elif grade == "ED":
        return "ED"
    elif grade == "GM":
        return "GM"
    elif grade in ["AGM", "DGM"]:
        return "AGM-DGM"
    elif grade in ["SM", "PM"]:
        return "SM-PM"
    elif grade == "MGR":
        return "MGR"
    elif grade in ["AM", "DM"]:
        return "AM-DM"
    else:
        return "EA-SO"

def get_grade_category_for_international(grade):
    """Map grade to international policy category"""
    if grade == "MD":
        return "MD"
    elif grade == "ED":
        return "ED"
    elif grade in ["AGM", "GM", "DGM"]:
        return "AGM-GM"
    elif grade in ["PM", "SM", "AM"]:
        return "AM-PM"
    else:
        return "EA-SO"

def get_approval_flow(department, grade, role):
    """Determine approval flow based on department and role"""
    
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
    elif department == "Internal Audit":
        return ["Chief Risk Officer", "MD"]
    elif department == "Legal and Compliance":
        return ["Chief Compliance Officer", "MD"]
    elif department == "Corporate Sales":
        return ["Chief Commercial Officer", "MD"]
    elif department == "Agencies":
        return ["Chief Agency Officer", "MD"]
    elif department == "Office of CEO":
        return ["MD"]
    elif department == "Office of Executive Director":
        return ["ED", "MD"]
    else:
        return ["Head of Department", "MD"]

def get_payment_approval_flow(total_amount):
    """Get payment approval flow based on amount"""
    if total_amount > 5000000:
        return ["Head of Administration", "Chief Compliance Officer", "Chief Risk Officer", "MD"]
    else:
        return ["Head of Administration", "Chief Compliance Officer", "Chief Risk Officer", "ED"]

def calculate_travel_costs(grade, travel_type, duration_nights):
    """Calculate travel costs based on policy"""
    if travel_type == "local":
        # Get policy based on grade
        policy_category = get_grade_category_for_local(grade)
        policy = LOCAL_POLICY[policy_category]
        
        hotel_cost = policy["hotel"] * duration_nights
        feeding_cost = policy["feeding"] * 3 * duration_nights  # 3 meals per day
        total = hotel_cost + feeding_cost
        return total, hotel_cost, feeding_cost, 0
    else:
        # International travel
        grade_category = get_grade_category_for_international(grade)
        policy = INTERNATIONAL_POLICY[grade_category]
        
        accommodation_cost = policy["accommodation"] * USD_TO_NGN * duration_nights
        feeding_cost = policy["feeding"] * USD_TO_NGN * duration_nights
        out_of_station_cost = policy["out_of_station"] * USD_TO_NGN * duration_nights
        airport_taxi_cost = policy["airport_taxi"] * USD_TO_NGN
        
        total = accommodation_cost + feeding_cost + out_of_station_cost + airport_taxi_cost
        
        return total, accommodation_cost, feeding_cost, airport_taxi_cost

def get_current_budget():
    """Get current budget information"""
    conn = sqlite3.connect('travel_app.db')
    current_year = datetime.datetime.now().year
    
    c = conn.cursor()
    c.execute("SELECT * FROM budget WHERE year = ?", (current_year,))
    budget_record = c.fetchone()
    
    if budget_record:
        columns = ['id', 'year', 'total_budget', 'utilized_budget', 'balance', 'last_updated']
        budget = dict(zip(columns, budget_record))
    else:
        budget = {
            'id': None,
            'year': current_year,
            'total_budget': ANNUAL_BUDGET,
            'utilized_budget': 0,
            'balance': ANNUAL_BUDGET,
            'last_updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    # Calculate utilized budget from paid payments
    c.execute('''SELECT SUM(total_cost) as total_paid 
                 FROM travel_costs 
                 WHERE payment_status = 'paid' 
                 AND strftime('%Y', payment_date) = ?''', 
              (str(current_year),))
    paid_result = c.fetchone()
    
    if paid_result and paid_result[0]:
        paid_amount = paid_result[0]
        if paid_amount != budget['utilized_budget']:
            budget['utilized_budget'] = paid_amount
            budget['balance'] = budget['total_budget'] - paid_amount
            c.execute('''UPDATE budget 
                         SET utilized_budget = ?, balance = ?
                         WHERE year = ?''',
                     (paid_amount, budget['total_budget'] - paid_amount, current_year))
            conn.commit()
    
    conn.close()
    return budget

def update_budget(amount):
    """Update budget after payment"""
    conn = sqlite3.connect('travel_app.db')
    c = conn.cursor()
    current_year = datetime.datetime.now().year
    
    c.execute("SELECT * FROM budget WHERE year = ?", (current_year,))
    budget = c.fetchone()
    
    if budget:
        c.execute('''UPDATE budget 
                     SET utilized_budget = utilized_budget + ?, 
                         balance = balance - ?,
                         last_updated = CURRENT_TIMESTAMP
                     WHERE year = ?''', 
                 (amount, amount, current_year))
    else:
        c.execute('''INSERT INTO budget (year, total_budget, utilized_budget, balance)
                     VALUES (?, ?, ?, ?)''',
                 (current_year, ANNUAL_BUDGET, amount, ANNUAL_BUDGET - amount))
    
    conn.commit()
    conn.close()
    return True

def get_pending_approvals_for_role(role):
    """Get all pending approvals for a specific role"""
    conn = sqlite3.connect('travel_app.db')
    
    approver_roles = ["CFO/ED", "Chief Risk Officer", "Chief Compliance Officer", 
                     "Chief Commercial Officer", "Chief Agency Officer", "ED", "MD",
                     "Head of Administration", "Head of Department"]
    
    if role in approver_roles:
        query = """
            SELECT tr.*, u.full_name, u.department, u.grade 
            FROM travel_requests tr 
            JOIN users u ON tr.user_id = u.id 
            WHERE tr.status = 'pending' 
            AND tr.current_approver = ?
            ORDER BY tr.created_at DESC
        """
        approvals = pd.read_sql(query, conn, params=(role,))
    else:
        approvals = pd.DataFrame()
    
    conn.close()
    return approvals

def process_approval(request_id, action, comments=""):
    """Process approval or rejection of a travel request"""
    conn = sqlite3.connect('travel_app.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM travel_requests WHERE id = ?", (request_id,))
    request = c.fetchone()
    
    if not request:
        conn.close()
        return False, "Request not found"
    
    current_status = request[14]
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
        
        c.execute("""
            UPDATE travel_requests 
            SET status = ?, current_approver = ? 
            WHERE id = ?
        """, (new_status, new_current_approver, request_id))
        
        c.execute("""
            INSERT INTO approvals 
            (request_id, approver_role, approver_name, status, comments) 
            VALUES (?, ?, ?, ?, ?)
        """, (request_id, st.session_state.role, st.session_state.full_name, 
              "approved", comments))
        
        conn.commit()
        message = "Request approved successfully"
        
    elif action == "reject":
        c.execute("""
            UPDATE travel_requests 
            SET status = 'rejected', current_approver = NULL 
            WHERE id = ?
        """, (request_id,))
        
        c.execute("""
            INSERT INTO approvals 
            (request_id, approver_role, approver_name, status, comments) 
            VALUES (?, ?, ?, ?, ?)
        """, (request_id, st.session_state.role, st.session_state.full_name, 
              "rejected", comments))
        
        conn.commit()
        message = "Request rejected"
    
    conn.close()
    return True, message

def generate_pdf_report(request_id):
    """Generate PDF report for travel request"""
    conn = sqlite3.connect('travel_app.db')
    
    request_query = """
        SELECT tr.*, u.full_name, u.department, u.grade, u.email,
               u.bank_name, u.account_number, u.account_name,
               u.date_of_birth, u.place_of_birth, u.passport_number, u.nationality, u.marital_status
        FROM travel_requests tr
        JOIN users u ON tr.user_id = u.id
        WHERE tr.id = ?
    """
    request_df = pd.read_sql(request_query, conn, params=(request_id,))
    
    if request_df.empty:
        conn.close()
        return None
        
    request_data = request_df.iloc[0]
    
    cost_query = "SELECT * FROM travel_costs WHERE request_id = ?"
    cost_data = pd.read_sql(cost_query, conn, params=(request_id,))
    
    approval_query = "SELECT * FROM approvals WHERE request_id = ? ORDER BY approved_at"
    approvals = pd.read_sql(approval_query, conn, params=(request_id,))
    
    conn.close()
    
    # Create PDF
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Request details
    pdf.add_section_title("Travel Request Details")
    
    pdf.add_field("Request ID", f"TR-{int(request_data['id']):06d}")
    pdf.add_field("Employee", request_data['full_name'])
    pdf.add_field("Department", request_data['department'])
    pdf.add_field("Grade", request_data['grade'])
    pdf.add_field("Travel Type", request_data['travel_type'].title() if request_data['travel_type'] else 'N/A')
    pdf.add_field("Destination", request_data['destination'])
    pdf.add_field("Purpose", request_data['purpose'])
    pdf.add_field("Mode of Travel", request_data['mode_of_travel'])
    pdf.add_field("Departure Date", request_data['departure_date'])
    pdf.add_field("Arrival Date", request_data['arrival_date'])
    pdf.add_field("Duration", f"{request_data['duration_days']} days ({request_data['duration_nights']} nights)")
    pdf.add_field("Accommodation", request_data['accommodation_needed'])
    pdf.add_field("Status", request_data['status'].upper() if request_data['status'] else 'N/A')
    
    # Cost details
    if not cost_data.empty:
        pdf.ln(5)
        pdf.add_section_title("Cost Details")
        cost = cost_data.iloc[0]
        pdf.add_field("Per Diem Amount", f"NGN {float(cost['per_diem_amount']):,.2f}" if cost['per_diem_amount'] else 'N/A')
        pdf.add_field("Flight Cost", f"NGN {float(cost['flight_cost']):,.2f}" if cost['flight_cost'] else 'N/A')
        if cost.get('airport_taxi_cost'):
            pdf.add_field("Airport Taxi", f"NGN {float(cost['airport_taxi_cost']):,.2f}")
        pdf.add_field("Total Cost", f"NGN {float(cost['total_cost']):,.2f}" if cost['total_cost'] else 'N/A')
        pdf.add_field("Payment Status", cost['payment_status'].upper() if cost['payment_status'] else 'N/A')
    
    # Approval history
    if not approvals.empty:
        pdf.ln(5)
        pdf.add_section_title("Approval History")
        for _, approval in approvals.iterrows():
            pdf.add_field(approval['approver_role'], 
                         f"{approval['status'].upper()} - {approval['approved_at']}")
    
    # Employee details
    pdf.ln(5)
    pdf.add_section_title("Employee Details")
    pdf.add_field("Date of Birth", request_data.get('date_of_birth', 'Not Provided'))
    pdf.add_field("Place of Birth", request_data.get('place_of_birth', 'Not Provided'))
    pdf.add_field("Nationality", request_data.get('nationality', 'Not Provided'))
    pdf.add_field("Marital Status", request_data.get('marital_status', 'Not Provided'))
    
    # Bank details
    pdf.ln(5)
    pdf.add_section_title("Bank Details")
    pdf.add_field("Bank Name", request_data.get('bank_name', 'Not Provided'))
    pdf.add_field("Account Number", request_data.get('account_number', 'Not Provided'))
    pdf.add_field("Account Name", request_data.get('account_name', 'Not Provided'))
    
    return pdf.output(dest='S').encode('latin-1', errors='replace')

def show_local_travel_policy():
    """Display local travel policy table"""
    st.markdown("### Local Travel Policy (Hotel & Feeding Allowances)")
    
    policy_data = {
        "Grade": ["MD/CEO", "ED", "GM", "AGM - DGM", "SM - PM", "MGR", "AM - DM", "EA – SO"],
        "Hotel Accommodation": [
            "NGN 650,000 per night",
            "NGN 500,000 per night",
            "NGN 350,000 per night",
            "NGN 250,000 per night",
            "NGN 150,000 per night",
            "NGN 100,000 per night",
            "NGN 80,000 per night",
            "NGN 75,000 per night"
        ],
        "Feeding Allowance": [
            "NGN 80,000 per meal per day",
            "NGN 80,000 per meal per day",
            "NGN 50,000 per meal per day",
            "NGN 30,000 per meal per day",
            "NGN 20,000 per meal per day",
            "NGN 15,000 per meal per day",
            "NGN 10,000 per meal per day",
            "NGN 7,000 per meal per day"
        ]
    }
    
    df = pd.DataFrame(policy_data)
    st.table(df)

# ============ MAIN UI FUNCTIONS ============

def login():
    """Login page"""
    st.markdown('<div class="company-logo">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">PRUDENTIAL ZENITH LIFE INSURANCE</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Travel Support Application</h2>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<p class="welcome-text">Secure access to travel management system for authorized personnel only</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="login-title">🔐 USER LOGIN</h3>', unsafe_allow_html=True)
        
        username = st.text_input("**Username / Employee ID**", placeholder="Enter your username")
        password = st.text_input("**Password**", type="password", placeholder="Enter your password")
        
        col_a, col_b = st.columns(2)
        with col_a:
            login_btn = st.button("**LOGIN**", use_container_width=True, type="primary")
        with col_b:
            register_btn = st.button("**CREATE ACCOUNT**", use_container_width=True)
        
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
    
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown('Prudential Zenith Life Insurance • Travel Management System v2.0')
    st.markdown('© 2024 All Rights Reserved')
    st.markdown('</div>', unsafe_allow_html=True)

def registration_form():
    """User registration form"""
    st.markdown('<h2 class="sub-header">Create New Account</h2>', unsafe_allow_html=True)
    
    with st.form("registration_form"):
        st.markdown("### Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name*")
            username = st.text_input("Username (Employee ID)*")
            email = st.text_input("Email Address*")
            date_of_birth = st.date_input("Date of Birth*", min_value=date(1900, 1, 1), max_value=date.today())
            place_of_birth = st.text_input("Place of Birth*")
        
        with col2:
            password = st.text_input("Password*", type="password")
            confirm_password = st.text_input("Confirm Password*", type="password")
            passport_number = st.text_input("International Passport Number")
            nationality = st.selectbox("Nationality*", COUNTRIES, index=COUNTRIES.index("Nigeria") if "Nigeria" in COUNTRIES else 0)
            marital_status = st.selectbox("Marital Status*", MARITAL_STATUS)
        
        st.markdown("### Employment Details")
        col3, col4 = st.columns(2)
        with col3:
            department = st.selectbox("Department*", DEPARTMENTS)
            grade = st.selectbox("Grade*", GRADES)
        with col4:
            role = st.selectbox("Role*", ROLES)
            phone_number = st.text_input("Phone Number*")
        
        st.markdown("### Bank Details (Optional but recommended for payments)")
        col5, col6 = st.columns(2)
        with col5:
            bank_name = st.text_input("Bank Name")
            account_number = st.text_input("Account Number")
        with col6:
            account_name = st.text_input("Account Name")
        
        profile_pic = st.file_uploader("Profile Picture (Optional)", type=['jpg', 'jpeg', 'png'])
        
        submitted = st.form_submit_button("Create Account")
        
        if submitted:
            if not all([full_name, username, email, password, confirm_password, department, grade, role, 
                       phone_number, date_of_birth, place_of_birth, nationality, marital_status]):
                st.error("Please fill in all required fields")
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
                                  profile_pic, bank_name, account_number, account_name, phone_number,
                                  date_of_birth, place_of_birth, passport_number, nationality, marital_status) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                             (full_name, username, email, make_hashes(password), 
                              department, grade, role, pic_data, bank_name, 
                              account_number, account_name, phone_number,
                              date_of_birth.strftime("%Y-%m-%d"), place_of_birth, 
                              passport_number, nationality, marital_status))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success("Account created successfully! Please login.")
                    time.sleep(2)
                    st.session_state.show_registration = False
                    st.rerun()

def travel_request_form():
    """Travel request form"""
    st.markdown('<h1 class="sub-header">New Travel Request</h1>', unsafe_allow_html=True)
    
    # Show policy table
    show_local_travel_policy()
    st.markdown("---")
    
    travel_type = st.radio("Travel Type", ["Local", "International"], horizontal=True)
    
    with st.form("travel_request"):
        col1, col2 = st.columns(2)
        
        with col1:
            if travel_type == "Local":
                # For local travel, user can input city directly
                city = st.text_input("City*", placeholder="Enter city name (e.g., Lagos, Abuja, Port Harcourt)")
                state = st.text_input("State*", placeholder="Enter state name")
                destination = f"{city}, {state}"
                country = "Nigeria"
            else:
                country = st.selectbox("Country*", COUNTRIES, index=COUNTRIES.index("United Kingdom") if "United Kingdom" in COUNTRIES else 0)
                city = st.text_input("City/Region*", placeholder="Enter city name")
                destination = f"{city}, {country}"
            
            purpose_options = ["Business Meeting", "Conference", "Training", "Project Site Visit", "Other"]
            purpose = st.selectbox("Purpose*", purpose_options)
            
            if purpose == "Other":
                purpose = st.text_input("Specify purpose")
        
        with col2:
            mode_options = ["Flight", "Road", "Train", "Water", "Other"]
            mode_of_travel = st.selectbox("Mode of Travel*", mode_options)
            
            departure_date = st.date_input("Departure Date*", min_value=date.today())
            arrival_date = st.date_input("Arrival Date*", min_value=departure_date)
            
            accommodation = st.radio("Accommodation Needed?", ["Yes", "No"], horizontal=True)
        
        if departure_date and arrival_date:
            duration_days = (arrival_date - departure_date).days + 1
            duration_nights = (arrival_date - departure_date).days
            
            st.info(f"**Duration:** {duration_days} days ({duration_nights} nights)")
        else:
            duration_days = 0
            duration_nights = 0
        
        # Show policy information based on grade
        if travel_type == "Local":
            policy_category = get_grade_category_for_local(st.session_state.grade)
            policy = LOCAL_POLICY[policy_category]
            col_a, col_b = st.columns(2)
            with col_a:
                st.info(f"**Hotel Accommodation:** {policy['hotel_text']}")
            with col_b:
                st.info(f"**Feeding Allowance:** {policy['feeding_text']} (per meal)")
            
            estimated_total, hotel_cost, feeding_cost, _ = calculate_travel_costs(
                st.session_state.grade, travel_type.lower(), duration_nights)
            st.metric("Estimated Total Cost", f"NGN{estimated_total:,.2f}")
            
        else:
            grade_category = get_grade_category_for_international(st.session_state.grade)
            policy = INTERNATIONAL_POLICY[grade_category]
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.info(f"**Hotel:** {policy['accommodation_text']}")
            with col_b:
                st.info(f"**Feeding:** {policy['feeding_text']}")
            with col_c:
                st.info(f"**Out of Station:** {policy['out_of_station_text']}")
            with col_d:
                st.info(f"**Airport Taxi:** {policy['airport_taxi_text']}")
            
            estimated_total, accommodation_cost, feeding_cost, airport_taxi_cost = calculate_travel_costs(
                st.session_state.grade, travel_type.lower(), duration_nights)
            
            col_e, col_f, col_g = st.columns(3)
            with col_e:
                st.metric("Per Day Total", f"${policy['total_usd']:,.0f} (NGN{policy['total_ngn']:,.0f})")
            with col_f:
                st.metric("Trip Total", f"NGN{estimated_total:,.2f}")
            with col_g:
                st.metric("Airport Taxi (One-time)", f"NGN{airport_taxi_cost:,.0f}")
        
        submitted = st.form_submit_button("Submit Request", type="primary")
        
        if submitted:
            if not all([destination, purpose, mode_of_travel, city]):
                st.error("Please fill all required fields")
            elif arrival_date <= departure_date:
                st.error("Arrival date must be after departure date")
            else:
                approval_flow = get_approval_flow(
                    st.session_state.department, 
                    st.session_state.grade, 
                    st.session_state.role
                )
                
                conn = sqlite3.connect('travel_app.db')
                c = conn.cursor()
                
                c.execute("""INSERT INTO travel_requests 
                          (user_id, username, travel_type, destination, city, country, purpose, 
                          mode_of_travel, departure_date, arrival_date, 
                          accommodation_needed, duration_days, duration_nights, 
                          current_approver, approval_flow) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         (st.session_state.user_id,
                          st.session_state.username, 
                          travel_type.lower(), 
                          destination, 
                          city, 
                          country,
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
                
                c.execute("""INSERT INTO approvals 
                          (request_id, approver_role, approver_name, status) 
                          VALUES (?, ?, ?, ?)""",
                         (request_id, approval_flow[0], "System", "pending"))
                
                conn.commit()
                conn.close()
                
                st.success("✅ Travel request submitted successfully!")
                st.info(f"**Approval Flow:** {' → '.join(approval_flow)}")

def travel_history():
    """Travel history page"""
    st.markdown('<h1 class="sub-header">Travel History</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
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
                        st.markdown(f"**Total Cost:** NGN{row['total_cost']:,.2f}")
                
                if st.button(f"📄 Download PDF Report", key=f"pdf_{row['id']}"):
                    pdf_bytes = generate_pdf_report(row['id'])
                    if pdf_bytes:
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

def show_approvals():
    """Display pending approvals"""
    if st.session_state.role not in ["MD", "ED", "CFO/ED", "Head of Department", "Head of Administration",
                                    "Chief Commercial Officer", "Chief Agency Officer",
                                    "Chief Compliance Officer", "Chief Risk Officer"]:
        st.warning("You don't have approval privileges")
        return
    
    st.markdown('<h1 class="sub-header">Pending Approvals</h1>', unsafe_allow_html=True)
    
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
                
                try:
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
                except:
                    st.markdown("**Approval Flow:** Not available")
                
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
                        comments = st.text_area("Reason for rejection", key=f"reason_{row['id']}")
                        if st.button(f"Confirm Reject", key=f"confirm_{row['id']}"):
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

def dashboard():
    """Main dashboard"""
    st.markdown('<h1 class="main-header">Dashboard Overview</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
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
    
    # Show local travel policy
    show_local_travel_policy()
    
    st.markdown("---")
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

def profile_update():
    """User profile update form"""
    st.markdown('<h1 class="sub-header">Update Profile</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    user_data = pd.read_sql("SELECT * FROM users WHERE username = ?", 
                           conn, params=(st.session_state.username,)).iloc[0]
    
    with st.form("profile_update_form"):
        st.markdown("### Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name*", value=user_data['full_name'])
            email = st.text_input("Email Address*", value=user_data['email'])
            phone_number = st.text_input("Phone Number*", value=user_data['phone_number'] or "")
        
        with col2:
            bank_name = st.text_input("Bank Name", value=user_data['bank_name'] or "")
            account_number = st.text_input("Account Number", value=user_data['account_number'] or "")
            account_name = st.text_input("Account Name", value=user_data['account_name'] or "")
        
        profile_pic = st.file_uploader("Update Profile Picture", type=['jpg', 'jpeg', 'png'])
        
        if user_data['profile_pic']:
            st.image(user_data['profile_pic'], width=150, caption="Current Profile Picture")
        
        submitted = st.form_submit_button("Update Profile")
        
        if submitted:
            if not all([full_name, email, phone_number]):
                st.error("Please fill in all required fields")
            else:
                pic_data = user_data['profile_pic']
                if profile_pic:
                    pic_data = profile_pic.read()
                
                c = conn.cursor()
                c.execute("""UPDATE users 
                             SET full_name = ?, email = ?, phone_number = ?,
                                 bank_name = ?, account_number = ?, account_name = ?,
                                 profile_pic = ?
                             WHERE username = ?""",
                         (full_name, email, phone_number, bank_name, 
                          account_number, account_name, pic_data,
                          st.session_state.username))
                
                conn.commit()
                conn.close()
                
                st.session_state.full_name = full_name
                st.success("Profile updated successfully!")
                time.sleep(2)
                st.rerun()

def payment_status():
    """Payment status page"""
    st.markdown('<h1 class="sub-header">Payment Status</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    query = """
        SELECT tr.id, tr.destination, tr.purpose, tr.departure_date, tr.arrival_date,
               tc.total_cost, tc.payment_status, tc.payment_completed,
               tc.payment_date, tc.payment_approved_by
        FROM travel_requests tr
        LEFT JOIN travel_costs tc ON tr.id = tc.request_id
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
                <p><strong>Amount:</strong> NGN{row['total_cost']:,.2f}</p>
                {f"<p><strong>Approved By:</strong> {row['payment_approved_by']}</p>" if row['payment_approved_by'] else ""}
                {f"<p><strong>Payment Date:</strong> {row['payment_date']}</p>" if row['payment_date'] else ""}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No payment records found")
    
    conn.close()

def analytics_dashboard():
    """Analytics dashboard"""
    st.markdown('<h1 class="sub-header">Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('travel_app.db')
    
    try:
        travel_data = pd.read_sql("""
            SELECT tr.*, u.department, u.grade, u.full_name,
                   tc.total_cost, tc.payment_status
            FROM travel_requests tr 
            JOIN users u ON tr.user_id = u.id
            LEFT JOIN travel_costs tc ON tr.id = tc.request_id
            WHERE tr.user_id = ? AND tr.status != 'draft'
        """, conn, params=(st.session_state.user_id,))
        
        if not travel_data.empty:
            travel_data['departure_date'] = pd.to_datetime(travel_data['departure_date'])
            travel_data['month'] = travel_data['departure_date'].dt.strftime('%Y-%m')
            
            col1, col2 = st.columns(2)
            
            with col1:
                status_counts = travel_data['status'].value_counts()
                fig1 = px.pie(values=status_counts.values, names=status_counts.index,
                             title="Travel Requests by Status",
                             color=status_counts.index)
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                type_counts = travel_data['travel_type'].value_counts()
                fig2 = px.bar(x=type_counts.index, y=type_counts.values,
                             title="Local vs International Travel",
                             color=type_counts.index,
                             labels={'x': 'Type', 'y': 'Count'})
                st.plotly_chart(fig2, use_container_width=True)
            
            col3, col4 = st.columns(2)
            
            with col3:
                monthly_counts = travel_data.groupby('month').size().reset_index(name='count')
                fig3 = px.line(monthly_counts, x='month', y='count',
                              title="Monthly Travel Requests Trend",
                              markers=True)
                st.plotly_chart(fig3, use_container_width=True)
            
            with col4:
                cost_data = travel_data.dropna(subset=['total_cost'])
                if not cost_data.empty:
                    fig4 = px.bar(cost_data, x='destination', y='total_cost',
                                 title="Cost by Destination",
                                 color='total_cost',
                                 labels={'total_cost': 'Total Cost (NGN)'})
                    st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No data available for analytics")
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")
    finally:
        conn.close()

def admin_panel():
    """Admin panel placeholder"""
    st.markdown('<h1 class="sub-header">Admin Panel</h1>', unsafe_allow_html=True)
    st.info("Admin panel functionality available for authorized users.")

def payment_approvals():
    """Payment approvals placeholder"""
    st.markdown('<h1 class="sub-header">Payment Approvals</h1>', unsafe_allow_html=True)
    st.info("Payment approvals functionality available for authorized users.")

def budget_analytics():
    """Budget analytics placeholder"""
    st.markdown('<h1 class="sub-header">Budget Analytics</h1>', unsafe_allow_html=True)
    
    budget = get_current_budget()
    utilization = (budget['utilized_budget'] / budget['total_budget']) * 100 if budget['total_budget'] > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Budget", f"NGN{budget['total_budget']:,.0f}")
    with col2:
        st.metric("Utilized", f"NGN{budget['utilized_budget']:,.0f}")
    with col3:
        st.metric("Balance", f"NGN{budget['balance']:,.0f}")
    
    st.markdown(f"""
    <div style="margin-top: 20px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span style="color: #616161;">Budget Utilization</span>
            <span style="color: #616161; font-weight: bold;">{utilization:.1f}%</span>
        </div>
        <div class="budget-bar" style="width: {min(utilization, 100)}%; height: 25px;"></div>
    </div>
    """, unsafe_allow_html=True)

def compliance_approvals():
    """Compliance approvals placeholder"""
    st.markdown('<h1 class="sub-header">Compliance Approvals</h1>', unsafe_allow_html=True)
    st.info("Compliance approvals functionality available for authorized users.")

def risk_approvals():
    """Risk approvals placeholder"""
    st.markdown('<h1 class="sub-header">Risk Approvals</h1>', unsafe_allow_html=True)
    st.info("Risk approvals functionality available for authorized users.")

def final_approvals():
    """Final approvals placeholder"""
    st.markdown('<h1 class="sub-header">Final Approvals</h1>', unsafe_allow_html=True)
    st.info("Final approvals functionality available for authorized users.")

def payment_processing():
    """Payment processing placeholder"""
    st.markdown('<h1 class="sub-header">Payment Processing</h1>', unsafe_allow_html=True)
    st.info("Payment processing functionality available for authorized users.")

def main():
    try:
        if not st.session_state.logged_in:
            if st.session_state.get('show_registration', False):
                registration_form()
            else:
                login()
        else:
            # Sidebar navigation
            with st.sidebar:
                st.markdown("""
                <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #D32F2F 0%, #B71C1C 100%); border-radius: 10px; margin-bottom: 20px;">
                    <h3 style="color: white; margin-bottom: 5px;">PRUDENTIAL ZENITH</h3>
                    <p style="color: rgba(255,255,255,0.9); font-size: 0.9rem;">Travel Management System</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="background: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <div style="text-align: center;">
                        <h4 style="color: #D32F2F; margin-bottom: 10px;">{st.session_state.full_name}</h4>
                        <p style="color: #616161; margin: 5px 0;"><strong>Role:</strong> {st.session_state.role}</p>
                        <p style="color: #616161; margin: 5px 0;"><strong>Grade:</strong> {st.session_state.grade}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                menu_options = ["Dashboard", "My Profile", "Update Profile", "Travel Request", 
                               "Travel History", "Payment Status", "Analytics"]
                
                approver_roles = ["MD", "ED", "CFO/ED", "Head of Department", "Head of Administration",
                                 "Chief Commercial Officer", "Chief Agency Officer",
                                 "Chief Compliance Officer", "Chief Risk Officer"]
                
                if st.session_state.role in approver_roles:
                    menu_options.append("Approvals")
                
                if st.session_state.role == "Head of Administration":
                    menu_options.extend(["Admin Panel", "Payment Approvals", "Budget Analytics"])
                elif st.session_state.role == "Chief Compliance Officer":
                    menu_options.extend(["Compliance Approvals"])
                elif st.session_state.role == "Chief Risk Officer":
                    menu_options.extend(["Risk Approvals"])
                elif st.session_state.role in ["CFO/ED", "MD"]:
                    menu_options.extend(["Final Approvals"])
                elif st.session_state.role == "Payables Officer":
                    menu_options.extend(["Payment Processing"])
                
                icons_map = {
                    "Dashboard": "house", "My Profile": "person", "Update Profile": "pencil",
                    "Travel Request": "airplane", "Travel History": "clock-history",
                    "Payment Status": "credit-card", "Analytics": "graph-up",
                    "Approvals": "check-circle", "Admin Panel": "gear", "Payment Approvals": "check-circle",
                    "Budget Analytics": "calculator", "Compliance Approvals": "shield-check",
                    "Risk Approvals": "shield-exclamation", "Final Approvals": "check-square",
                    "Payment Processing": "cash"
                }
                
                icons = [icons_map.get(opt, "circle") for opt in menu_options]
                
                selected = option_menu(
                    menu_title="Navigation",
                    options=menu_options,
                    icons=icons,
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
                
                if st.button("🚪 Logout", use_container_width=True, type="primary"):
                    st.session_state.logged_in = False
                    st.session_state.username = ''
                    st.session_state.role = ''
                    st.rerun()
            
            # Main content routing
            if selected == "Dashboard":
                dashboard()
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
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.button("🔄 Restart App", on_click=lambda: st.rerun())

if __name__ == "__main__":
    main()
