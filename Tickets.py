import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from st_on_hover_tabs import on_hover_tabs 
import time
from rembg import remove
import extra_streamlit_components as stx  
import datetime
from datetime import date
from sklearn.preprocessing import LabelEncoder
import cv2
from io import StringIO
import email, smtplib, ssl
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.message import EmailMessage 
from email import encoders
import pickle
from pathlib import Path 
import streamlit_authenticator as stauth
from geopy.geocoders import Nominatim

#Page config setup



st.markdown('''<h3 style= "text-align:left; color:#8C98AF; ">CREATE TICKETS</h3>''', unsafe_allow_html=True)

Home= st.Page('pages/Home-page.py', title= 'Home page', icon= '🏡')

if st.sidebar.button('Home', icon= '🏡'):
	st.switch_page(Home)

i = 244 


history_data= pd.read_csv(r'/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/DATA/History.csv')


troubles_types= pd.read_csv(r"/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/DATA/troubles with priority.csv")

priority_response= pd.read_csv(r"/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/DATA/priority_response.csv")

user_data= pd.read_csv(r"/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/DATA/user_data.csv")

amc_data= pd.read_csv(r"/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/DATA/AMC.csv")



# User Authentication

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



	
def systems_name(option2):
	data= troubles_types
	system_name= []
	for system in (data['System'].unique()):
		system_name.append(system)
	return system_name

def troubles_name(option3):
	troubles_type = []
	
	data1= troubles_types[troubles_types['System'] == option3]
	Troubles= data1['Troubles'].unique()
	return Troubles
	

def team_assign(option2):
	data= amc_data[amc_data['SYSTEM SHORTFORM'] == 	option3]
	data1 = data['AMC COMPANY']
	for team in data1:
		company = team 
	return company 	

def team_personnel():
	data= amc_data[amc_data['SYSTEM SHORTFORM'] == 	option3]
	for name in data['PERSONNEL']:
		person=  name
	return person  

def team_desig(option2):
	data= amc_data[amc_data['SYSTEM SHORTFORM'] == 	option3]
	for desig in data['DESIGNATION']:
		designation =  desig
	return designation

def team_contact(option2):
	data= amc_data[amc_data['SYSTEM SHORTFORM'] == 	option3]
	for phone in data['CONTACT']:
		number =  phone
	return number

def team_email(option2):
	data= amc_data[amc_data['SYSTEM SHORTFORM'] == 	option3]
	for mail in data['EMAIL']:
		email =  mail 
	return email  

def priority_level(option4):
	data1 = troubles_types[troubles_types['Troubles'] == option4]
	for prior in data1.Priority.values:
		priority_level = prior
	return priority_level

def response(option5):
    data1 = priority_response[priority_response['PRIORITY '] == priority_level(option4)]
    date_and_time= datetime.datetime(int(year), int(month_num), int(day), int(hour), int(minutes))
    cob_time= datetime.datetime(int(year), int(month_num), int(day), 17, 00)
    duty_hours= datetime.timedelta(hours=9)
    non_duty= datetime.timedelta(hours= 15)
    day_hours= datetime.timedelta(hours=24)
    next_working= cob_time + non_duty
    for res in data1['RESPONSE TIME(HR)']:
        time_change= datetime.timedelta(hours=res)
        new_time= date_and_time + time_change
        if option5 !='P1':
            if new_time.strftime("%A") != 'Sunday':
                
                if new_time.hour >= cob_time.hour:
                    proposed_time= next_working + (time_change- (cob_time- date_and_time))
                    return proposed_time
                else:
                    return new_time
            else:
                new_time = date_and_time + time_change + day_hours
                return new_time
        else:
            return new_time

def resolution(option5):
    data1 = priority_response[priority_response['PRIORITY '] == priority_level(option4)]
    date_and_time= datetime.datetime(int(year), int(month_num), int(day), int(hour), int(minutes))
    cob_time= datetime.datetime(int(year), int(month_num), int(day), 17, 00)
    duty_hours= datetime.timedelta(hours=9)
    non_duty= datetime.timedelta(hours= 15)
    day_hours= datetime.timedelta(hours=24)
    next_working= cob_time + non_duty
    for res in data1['RESOLUTION TIME(HR)']:
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
	respone_time= response(option5)
	current_time= datetime.datetime.now()
	time_diff= respone_time - current_time

	return time_diff

def ticket_number():
	ticket_no = []
	for ref in history_data.Ticket_ref:
	    no = ref.split("/")
	    for number in no:
	        tic= number
	    ticket_no.append(tic)
	    ticketnumber= int(max(ticket_no)) + 1 
	    return ticketnumber 
		



if st.session_state['authentication_status']:
	if user_type() == 'customer' or user_type() == 'Admin':

		col1, col2 = st.columns([.7, .3], gap= 'small', border=True)

		with col1:

			option1= st.selectbox('Organization name:', options= name, placeholder= 'Select the Organization name and press submit')
			option2= st.selectbox('Project name:', options= ['The Guild'], index=None, placeholder= 'Select the project name')
			option7= st.selectbox('Project location:', options= ['DIFC'], index= None, placeholder='Select the project location')
			option3= st.selectbox('System type:', options= systems_name(option2), index=None, placeholder= 'Select the system name')
			option4= st.selectbox('Troubles name:', options= troubles_name(option3), index= None, placeholder= 'Select the trouble name')
			



			if col1.button('Submit'):

				if option4!=None:
					progress_text = "Ticket creation in progress. Please wait."
					my_bar = st.progress(0, text=progress_text)
					for percent_complete in range(100):
						time.sleep(0.01)
						my_bar.progress(percent_complete + 1, text=progress_text)
					time.sleep(1)
					my_bar.empty() 
					st.success(f'The ticket is created successfully. Ticket ref:{i + len(history_data)}', icon="✅")
					time.sleep(2)
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
					iso_calendar= date.isocalendar()
					week_num= iso_calendar[1]
					ticket_num= i + len(history_data)
					
				 
					        
					loc = Nominatim(user_agent="Geopy Library")

					Lat = []
					Long= []
					
					location= option7
					
					    
				    # entering the location name
					getLoc = loc.geocode(location)
					if getLoc is not None:
						Lat.append(getLoc.latitude)
						Long.append(getLoc.longitude)
					else:
						Lat.append(None)
						Long.append(None)

					

						
				else:
					st.write('Please enter trouble details')


					
				with col2:

					row1= st.columns(1)
					for col in row1:
						container1= col.container(height= 50, border=False)
						container1.write(f'The ticket is assigned to company named M/s. {team_assign(option2)}')
						container2= st.container(height= 80, border=False)
						container2.text(f'Name: Mr. {team_personnel()}\nDesignation: {team_desig(option2)}\nContact: {team_contact(option2)}\nEmail: {team_email(option2)}')


					SUBJECT = f'{option2} - {option4}'
					body= f'''
Dear Mr. {team_personnel()}, 

A Complaint with ref {team_assign(option2)}/Ser/Tic/{i + len(history_data)} has been assigned to you. Brief of the trouble is {option4}. Please arrange to complete the job within the SLA period.

Thanks & Regards
{name}'''
					FROM= 'anish.nair3091@gmail.com'
					TO= team_email(option2)
					copy_email = 'anish.nair3091@gmail.com'
					password = "eeas zmof lnjg ricm"
					port= 465

					message = MIMEMultipart()
					message['Subject'] = SUBJECT
					message['To']= TO 
					message['FROM'] = FROM 
					message['Cc'] = copy_email

					message.attach(MIMEText(body, "plain"))

					filename= None

					if filename != None:

						with open(filename, "rb") as attachment:
							part= MIMEBase("application", "octet-stream")
							part.set_payload(attachment.read())

						encoders.encode_base64(part)

						part.add_header("Content-Disposition", f"attachment; filename= {filename}",)

						message.attach(part)



					context = ssl.create_default_context()

					with smtplib.SMTP_SSL('smtp.gmail.com', port, context=context) as server:
						server.login(FROM, password)
						server.sendmail(FROM, TO, message.as_string())
					
					st.write('Priority level:')
					option5= st.info(priority_level(option4))
					st.write('Team Visit time: ')
					option6= st.info(f'Within {response(option5)}')
					i = i + 1
					current_time = datetime.datetime.now()
					time_diff = (response(option5)- current_time).total_seconds()

					data = {'Organization': option1, 'Project': option2, 'System': option3, 'Troubles_Name': option4, 'AMC_Company': team_assign(option2), 'Ticket_ref': f'{team_assign(option2)}/Ser/Tic/{i + len(history_data)}', 'Date': date, 'Status': 'Open', 'Months': month_num,'Year': year, 'Month': month, 'Day': day, 'Weekday': weekday, 'Time' : time, 'Priority': priority_level(option4), 'Response': response(option5), 'Resolve': resolution(option5), 'Time Remaining':time_remaining(), 'Actual_Completion_time': '', 'Response_time_difference': '', 'Person_lat': '', 'Person_long': '', 'Site_lat': Lat, 'Site_long': Long, 'Person_login' :'', 'Assigned_Person': '', 'Time_remaining_secs': 'time_diff', 'SLA': '', 'Week_Num' : week_num, 'Ticket_num': ticket_num}

					
					history = pd.DataFrame(data, index=[0])


					history_data = pd.concat([history_data, history], axis= 0)

					times= []
					data= history_data[history_data['Status'] == 'Open']
					for time in pd.to_datetime(data['Response']):
					    current_time = datetime.datetime.now()
					    time_diff = time- current_time
					    times.append(time_diff.total_seconds())

					data['Time_remaining_secs']= times

					times1= []
					data1= history_data[history_data['Status'] == 'Close']
					for time, his in zip(pd.to_datetime(data1['Response']), pd.to_datetime(data1['Actual_Completion_time'])) :
					    
					    time_diff = time- his
					    times1.append(time_diff.total_seconds())

					data1['Time_remaining_secs']= times1

					history_data = pd.concat([data1, data], axis= 0)

					#To distinguish tickets based on SLA status

					SLAs = []
					for secs in history_data['Time_remaining_secs']:
						if secs > 0:
							SLA= 'SLA met'
							SLAs.append(SLA)
						elif secs <= 0:
							SLA= 'SLA not met'
							SLAs.append(SLA)

					history_data['SLA'] = SLAs

					dummy_variable= pd.get_dummies(history_data['Status'])
					encoder1= LabelEncoder()
					encoder2= LabelEncoder()

					encoder1.fit(dummy_variable['Open'])
					encoder2.fit(dummy_variable['Close'])
					history_data['Open']= encoder1.transform(dummy_variable['Open'])
					history_data['Close']= encoder2.transform(dummy_variable['Close'])

					

					dummy_variable2= pd.get_dummies(history_data['SLA'])
					encoder3= LabelEncoder()
					encoder4= LabelEncoder()

					encoder3.fit(dummy_variable2['SLA met'])
					encoder4.fit(dummy_variable2['SLA not met'])
					history_data['SLA met'] = encoder3.transform(dummy_variable2['SLA met'])
					history_data['SLA not met'] = encoder4.transform(dummy_variable2['SLA not met'])

	 				
					
					
				history_data.to_csv('/Users/anishmnair/Desktop/Streamlit/My_new_app/Customer-app/New/DATA/History.csv', index= False)

	




