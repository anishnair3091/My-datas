import streamlit as st  
import pandas as pd  
import numpy as np 
import matplotlib.pyplot as plt  
import seaborn as sns; sns.set()
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt 
import matplotlib
from sklearn.preprocessing import LabelEncoder
import datetime
import pickle
from pathlib import Path 
import streamlit_authenticator as stauth
import streamlit.components.v1 as components

#Page config setup

st.set_page_config(page_title= 'View Enquiries', layout= 'wide', initial_sidebar_state= 'collapsed', page_icon= '🎫')


Enquiry_page = st.Page('pages/Enquiries-Dashboard.py', title= 'Sales Dashboard', icon = '📈')

if st.sidebar.button('Home'):
	st.switch_page(Enquiry_page)

page_bg_img= f"""
<style>
.st-emotion-cache-1yiq2ps{{
	background-image: url("https://w0.peakpx.com/wallpaper/323/21/HD-wallpaper-plain-white-abstract.jpg");
	
	background-size: 100vw 100vh;  # This sets the size to cover 100% of the viewport width and height
    background-position: center;  
    background-repeat: no-repeat;

}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)


st.markdown('''<h1><img src="https://png.pngtree.com/png-vector/20230227/ourmid/pngtree-golden-ticket-png-image_6621563.png" alt="" width="80" height="80"> VIEW ENQUIRIES</h1>''', unsafe_allow_html= True)

st.markdown('''<p style= "text-align: left; font-size: 30px; font-weight: bold; position: relative;">VIEW ENQUIRIES</p>''', unsafe_allow_html= True)

st.markdown('<style>' + open('/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/html/styles/styles-new.css').read() + '</style>', unsafe_allow_html=True)

enquiry_data= pd.read_csv(r"/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/DATA/enquiry_data.csv")

AMC_data= pd.read_csv(r"/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/DATA/AMC.csv")

user_data= pd.read_csv(r"/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/DATA/user_data.csv")


def authentication_status():
    users= []
    user_ids= []
    usertypes= []
    for user, ids, types in zip(user_data.Username, user_data.User_id, user_data.User_type):
        users.append(user)
        user_ids.append(ids)
        usertypes.append(types)

    # Load credentials except passwords

    names= users
    usernames= user_ids
    usertype= usertypes

    # Load passwords

    file_path = Path("/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/secrets/hashed_pw.pkl")
    with file_path.open('rb') as file:
        hashed_passwords= pickle.load(file)

    # Transform credentials as a dictionary

    credentials = {"usernames":{}}
    for un, name, pswd, char in zip(usernames, names, hashed_passwords, usertype):   
        user_dict = {"name":name, "password" : pswd, "role":char}
        credentials["usernames"].update({un:user_dict})

    authenticator= stauth.Authenticate(credentials, "", "", cookie_expiry_days=30)
    name, authentication_status, username= authenticator.login('main', 'Login')
    return authentication_status

if st.session_state['authentication_status']:

	our_data= st.session_state['keys101']


for sys in our_data['System']:
	systemname = sys

for sla in our_data['SLA']:
	if sla == 'SLA met':
		slas = 'SLA not exceeded' 
		our_data['SLA'].replace(sla, slas, inplace=True)

	elif sla == 'SLA not met':
		slas = 'SLA exceeded'
		our_data['SLA'].replace(sla, slas, inplace=True)

# Defining name

if authentication_status() == True:
    name= st.session_state["name"]
    st.sidebar.write(f'Welcome **{name}**')
    
def user_type():
    data = user_data[user_data['Username'] == name]
    for user in data.User_type:
        user_type= user
    return user_type

def Organization():
	for org in our_data.Organization:
		Organization = org 	
		return Organization

def Project():
	for proj in our_data.Project:
		Project= proj 
		return Project

def System():
	for sys in our_data.System:
		System= sys 	
		return System

def Job_type():
	for job in our_data['Job type']:
		jobtype= job
		return jobtype

def scope():
	for job in our_data['Scope']:
		scopetype= job
		return scopetype

def Enqref():
	for ref in our_data['Enquiry_ref']:
		enquref= ref 
		return enquref

def Date():
	for date in our_data['Created date']:
		Date= date 	
		return Date 

def enquiry_status():
	for status in our_data['Enquiry status']:
		enquirystatus= status 
		return enquirystatus

def response():
	for res in our_data.Response:
		response = res  
		return response

def SLA():
	for sla in our_data['SLA']:
		sla_status = sla  
		return sla_status

def time_remaining():
	for res in our_data['Time_remaining_secs']:
		time_remain= res

		return time_remain

def assigned_company():
	for com in our_data['Company']:
		assignedcompany= com  
		return assignedcompany
	else:
		return None


def image():
	for link in our_data.Picture:
		image= link  
		return image


def actual_completion():
	for completion in pd.to_datetime(our_data['Actual_Completion_time']):
		if completion != pd.NaT:
			actualcompletion = completion
			return actualcompletion
		elif completion == NaT: 
			actualcompletion= 'Not yet done'
			return actualcompletion



def status_placeholder():
	for status in our_data.Status:
		placeholder= status 
		return placeholder

def get_current_gps_coordinates():
    g = geocoder.ip('me')#this function is used to find the current information using our IP Add
    if g.latlng is not None: #g.latlng tells if the coordiates are found or not
        return g.latlng
    else:
        return None

def secondsToText(secs):

    days = secs//86400
    hours = (secs - days*86400)//3600
    minutes = (secs - days*86400 - hours*3600)//60
    seconds = secs - days*86400 - hours*3600 - minutes*60
    result = ("{} days, ".format(days) if days else "") + \
    ("{} hours, ".format(hours) if hours else "") + \
    ("{} minutes, ".format(minutes) if minutes else "") + \
    ("{} seconds, ".format(np.round(seconds, decimals=0)) if seconds else "")
    return result

timeremain= secondsToText(time_remaining())

container = st.container(height= 1050, border=True)



with container:

	col1, col2= st.columns(2)

	with col1:
	
		st.write("Enquiry raised by:")
		info1 = st.info(Organization())

		st.write("Assigned to:")
		info2= st.info(assigned_company())

		st.write("Enquiry ref")
		info3= st.info(Enqref())

		st.write("Created date:")
		info3= st.info(Date())

		st.write("Job type:")
		info4= st.info(Job_type())

		st.write("Scope of Work:")
		info4= st.info(scope())

		st.write("System name:")
		info5= st.info(systemname)

		st.write("Enquiry status:")
		info6= st.info(enquiry_status())

		st.write("Quote Expected Date and Time:")
		info7= st.info(response())

	with col2:

		st.write("SLA Current status:")
		info8= st.info(SLA())

		st.write("Actual Completion time:")
		info9= st.info(actual_completion())

		st.write("Time remaining:")
		if time_remaining() < 0:
			info10= st.info(f''':red[{timeremain}]''')
		else:
			info10= st.info(f'''{timeremain}''')

		

		

		




		