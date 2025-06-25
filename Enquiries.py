import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import plotly.express as px
import streamlit as st
import PIL.Image
import streamlit.components.v1 as components
import time
from PIL import Image
from rembg import remove
import datetime
import pickle
from pathlib import Path 
import streamlit_authenticator as stauth
from datetime import date
import email, smtplib, ssl
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.message import EmailMessage 
from email import encoders
from geopy.geocoders import Nominatim
from sklearn.preprocessing import LabelEncoder

#Page config setup



st.markdown('''<h3 style= "text-align:left; color:#8C98AF; ">RAISE ENQUIRIES</h3>''', unsafe_allow_html=True)

Home= st.Page('pages/Home-page.py', title= 'Home page', icon= '🏡')

if st.sidebar.button('Home', icon= '🏡'):
	st.switch_page(Home)

i = 100

amc_data= pd.read_csv(r"/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/DATA/AMC.csv")

user_data= pd.read_csv(r"//Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/DATA/user_data.csv")

enquiry_data= pd.read_csv(r"/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/DATA/enquiry_data.csv")

troubles_types= pd.read_csv(r"/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/DATA/troubles with priority.csv")

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

    file_path = Path("/Users/anishmnair/Desktop/Streamlit/My_new_app/BMTS-APP/secrets/hashed_pw.pkl")
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

# Defining name

if authentication_status() == True:
    name= st.session_state["name"]
    st.sidebar.write(f'Welcome **{name}**')
    
def user_type():
    data = user_data[user_data['Username'] == name]
    for user in data.User_type:
        user_type= user
    return user_type


def systems_name():
	data= troubles_types
	system_name= []
	for system in (data['System'].unique()):
		system_name.append(system)
	return system_name

def assigned_person():
	data= amc_data[amc_data['SYSTEM SHORTFORM'] == 	option6]
	data1 = data['AMC COMPANY']
	for team in data1:
		company = team 
	return company 

def team_personnel():
	data= amc_data[amc_data['SYSTEM SHORTFORM'] == 	option6]
	for name in data['PERSONNEL']:
		person=  name
	return person  

def team_desig():
	data= amc_data[amc_data['SYSTEM SHORTFORM'] == 	option6]
	for desig in data['DESIGNATION']:
		designation =  desig
	return designation

def team_contact():
	data= amc_data[amc_data['SYSTEM SHORTFORM'] == 	option6]
	for phone in data['CONTACT']:
		number =  phone
	return number

def team_email():
	data= amc_data[amc_data['SYSTEM SHORTFORM'] == 	option6]
	for mail in data['EMAIL']:
		email =  mail 
	return email 

def response():
    date_and_time= pd.to_datetime((datetime.datetime(int(year), int(month_num), int(day), int(hour), int(minutes), int(seconds))).strftime("%Y-%m-%d %H:%M:%S"))
    cob_time= pd.to_datetime((datetime.datetime(int(year), int(month_num), int(day), 17, 00, 00)).strftime("%Y-%m-%d %H:%M:%S"))
    duty_hours= datetime.timedelta(hours=9)
    non_duty= datetime.timedelta(hours= 15)
    day_hours= datetime.timedelta(hours=24)
    next_working= cob_time + non_duty
    res= 48
    time_change= datetime.timedelta(hours=res)
    new_time= date_and_time + time_change
    
    if new_time.strftime("%A") != 'Sunday':
        
        if new_time.hour >= cob_time.hour:
            proposed_time= next_working + (time_change- (cob_time- date_and_time))
            return proposed_time
        else:
            return new_time
    else:
        new_time = date_and_time + time_change + day_hours
        return new_time

def time_remaining():
	respone_time= response()
	current_time= pd.to_datetime((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S"))
	time_diff= respone_time - current_time

	return time_diff

def time_remaining_secs():
	secs= time_remaining().total_seconds()
	return secs


col1, col2 = st.columns(2, border=True)

with col1:
	option1= st.selectbox(f"**Organization name:** :red[*]", options= name, placeholder='Select or enter the Organization name here', accept_new_options=True)
	option2= st.selectbox(f"**Project Name:** :red[*]", options= ['The Guild'], index= None, placeholder='Select or Enter your Project name here', accept_new_options= True)
	option3= st.selectbox(f"**Location:** :red[*]", options= ['DIFC'], index= None,  placeholder='Select or Enter your project Location here', accept_new_options=True)
	option12= st.selectbox(f"**Emirate:** :red[*]", ['DUBAI', 'SHARJAH', 'AJMAN', 'ABUDHABI', 'UMM AL QUWAIN', 'FUJAIRAH', 'RAS AL KHAIMAH'], placeholder= 'Select emirate', accept_new_options=True)
	option4= st.text_input(f"**Project details:** :", value=None, placeholder= 'Enter your unit/office/retail name here')
	option5= st.selectbox(f"**Job type:** :red[*]", ['New construction project', 'Fitout', 'Renovation', 'Refurbishment', 'Supply Only'], index= None, placeholder= 'Select a job type or enter a new one', accept_new_options= True)
	option6= st.selectbox(f"**System name:**", options= systems_name(), placeholder= 'Select the system name')
	option7= st.text_input(f"**Scope:** :red[*]", value= None, placeholder="Enter the scope details with BOQ(if available) below")
	option8= st.file_uploader(f"**Upload your files- Drwg/BOQ/Specifications**")

with col2:
	
	option9= st.text_input(f"**Email id:** :red[*]", value= None, placeholder='Enter your valid official Email id for communication')
	option10= st.text_input(f"**Contact no:**", value=None, placeholder='Enter your contact number if to be contacted through phone')
	if st.button("Submit"):
		if ((option1 != None) & (option2 != None)) & (option3 != None)  & ((option5 != None) & (option6 != None)) & ((option7 != None) or (option8 != None)) & ((option9 != None) & (option12 != None)):
			
			progress_text = "The enquiry is being assigned to the respective team."
			my_bar = st.progress(0, text=progress_text)
			for percent_complete in range(100):
				time.sleep(0.01)
				my_bar.progress(percent_complete + 1, text=progress_text)
			time.sleep(1)
			my_bar.empty() 
			st.success(f'The enquiry is assigned successfully. Contact details of the team/personel will be displayed below shortly', icon="✅")
			x= datetime.datetime.now()
			month= x.strftime("%B")
			year= x.year
			day= x.strftime("%d")
			weekday= x.strftime("%A")
			time= x.strftime("%X")
			hour= x.strftime("%H")
			minutes= x.strftime("%M")
			month_num= x.strftime("%m")
			date= date.today()
			seconds= x.strftime("%S")
			enquiry_ref= f'Enq/Ref/{i + len(enquiry_data)}'
			loc = Nominatim(user_agent= 'Geopy Library')
			datetime_data= x.strftime("%Y-%m-%d %H:%M:%S") 

			Lat= []
			Long= []

			location = option3
			#entering the location name
			getLoc= loc.geocode(location)
			if getLoc is not None:
				Lat.append(getLoc.latitude)
				Long.append(getLoc.longitude)
			else:
				Lat.append(None)
				Long.append(None)

			 


			
		else:

			st.warning(f"Please enter the mandatory options to proceed further", icon= '⚠️')

		row1= st.columns(1)
		for col in row1:
			container1= col.container(height= 50, border=False)
			container1.write(f'The ticket is assigned to company named M/s. {assigned_person()}')
			container2= st.container(height= 80, border=False)
			container2.text(f'Name: Mr. {team_personnel()}\nDesignation: {team_desig()}\nContact: {team_contact()}\nEmail: {team_email()}')

	
			st.success(f'Thanks for your enquiry! {assigned_person()} will contact you soon for any queries or clarifications. Else, the quote will reach to you in 2-3 working days time')

			SUBJECT = f'{option2} - {option5}'
			body= f'''
Dear Mr. {team_personnel()}, 

An Enquiry with ref {assigned_person()}/Ser/Tic/{i + len(enquiry_data)} has been assigned to you. Brief of the scope is provided below
{option5}. 
Please arrange to share the proposal at the earliest. For any clarifications, please feel free to contact on below.

Thanks & Regards
{name}
{option9}'''
			FROM= 'anish.nair3091@gmail.com'
			TO= team_email()
			copy_email = 'anish.nair3091@gmail.com'
			password = "eeas zmof lnjg ricm"
			port= 465

			message = MIMEMultipart()
			message['Subject'] = SUBJECT
			message['To']= TO 
			message['FROM'] = FROM 
			message['Cc'] = copy_email

			message.attach(MIMEText(body, "plain"))

			if option8 != None:
				file= option8
				filename= file.read()

				
				part= MIMEBase("application", "octet-stream")
				part.set_payload(filename)

				encoders.encode_base64(part)

				part.add_header("Content-Disposition", f"attachment; filename= {filename}",)

				message.attach(part)



			context = ssl.create_default_context()

			with smtplib.SMTP_SSL('smtp.gmail.com', port, context=context) as server:
				server.login(FROM, password)
				server.sendmail(FROM, TO, message.as_string())

		enquiry= {'Organization': option1, 'Project' : option2, 'Project Location': option3, 'Job name': option4, 'Enquiry_ref': enquiry_ref, 'Job type': option5, 'System' : option6, 'Scope' : option7, 'Email_id' : option9, 'Contact no:' : option10, 'Created date': date, 'Enquiry status': 'Under review', 'Company': assigned_person(), 'Monthname': month, 'Month': month_num, 'Year': year, 'Day': day, 'Weekday': weekday, 'Time': time, 'Hour': hour, 'Minutes': minutes, 'Site_lat': Lat, 'Site_long' : Long, 'Datetime': datetime_data, 'Response': response(), 'Time_remaining': time_remaining(), 'Time_remaining_secs':time_remaining_secs() }	

		enquiry_df= pd.DataFrame(enquiry, index=[0])
		enquiry_data = pd.concat([enquiry_data, enquiry_df], axis= 0)

		

		times2= []
		data2= enquiry_data[enquiry_data['Enquiry status'] == 'Quoted']
		for time, his in zip(pd.to_datetime(data2['Response']), pd.to_datetime(data2['Actual_Completion_time'])) :
		    
		    time_diff = time- his
		    times2.append(time_diff.total_seconds())

		data2['Time_remaining_secs']= times2

		

		#To distinguish tickets based on SLA status

		SLAs = []
		for secs in enquiry_data['Time_remaining_secs']:
			if secs > 0:
				SLA= 'SLA met'
				SLAs.append(SLA)
			elif secs <= 0:
				SLA= 'SLA not met'
				SLAs.append(SLA)

		enquiry_data['SLA'] = SLAs

		dummy_variable= pd.get_dummies(enquiry_data['Enquiry status'])
		encoder1= LabelEncoder()
		encoder2= LabelEncoder()
		encoder3= LabelEncoder()

		encoder1.fit(dummy_variable['Under review'])
		encoder2.fit(dummy_variable['Moved for estimation'])
		encoder3.fit(dummy_variable['Quoted'])
		enquiry_data['Under review']= encoder1.transform(dummy_variable['Under review'])
		enquiry_data['Moved for estimation']= encoder2.transform(dummy_variable['Moved for estimation'])
		enquiry_data['Quoted'] = encoder3.transform(dummy_variable['Quoted'])

		

		dummy_variable2= pd.get_dummies(enquiry_data['SLA'])
		encoder3= LabelEncoder()
		encoder4= LabelEncoder()

		encoder3.fit(dummy_variable2['SLA met'])
		encoder4.fit(dummy_variable2['SLA not met'])
		enquiry_data['SLA met'] = encoder3.transform(dummy_variable2['SLA met'])
		enquiry_data['SLA not met'] = encoder4.transform(dummy_variable2['SLA not met'])



		enquiry_data.to_csv('/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/DATA/enquiry_data.csv', index=False)
