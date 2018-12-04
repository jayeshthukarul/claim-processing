import PyPDF2
import sys
import re
import nltk
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import itertools

#global function for file blocks

file_parts={}

#this function will read pdf files

def readFile(file):
	text=""
	fileObj=open(file, 'rb')
	fileReader=PyPDF2.PdfFileReader(fileObj)
	pageNumber=fileReader.numPages

	#create page object
	for i in range(pageNumber):

		pageObj=fileReader.getPage(i)

		#get text
		text=text+pageObj.extractText()

	fileObj.close()

	return text


#this function will  clean data and divide it into different blocks

def processData(text):

	#this part will seperate file into different blocks

	seprator=["DAMAGE SURVEY REPORT", "GENERAL INFORMATION", "DEFINITION OF TERMS", "PARTIES INVOLVED", "CIRCUMSTANCES", "DETAILS ABOUT THE SURVEY",
	"ASPECT OF THE DAMAGE", "NATURE OF THE DAMAGE", "Summary", "Financial worksheet"]

	replace_val=re.findall(re.compile(r'\n'), text)
	for j in range(len(replace_val)):
	        text=text.replace(replace_val[j], "")

	file_parts = {}
	sep_last_index=len(seprator)-1

	for i in range(len(seprator)):
	    if(i<sep_last_index):
	        temp_text_list=re.split(seprator[i], text)
	        temp_text_list=re.split(seprator[i+1], temp_text_list[1])
	        file_parts[seprator[i]]=temp_text_list[0]
	    else:
	        temp_text_list=re.split(seprator[i], text)
	        file_parts[seprator[i]]=temp_text_list[1]


	#this part  will clean data with regex

	reg_expr=[re.compile(r'\n'), re.compile(r'---+'), re.compile(r'TOP|QUALITY\s+AUTO\s+SURVEY\s+\d\s+\|\s+Page')]

	for i in range(len(reg_expr)):
	    for key in file_parts:
	        replace_val=re.findall(reg_expr[i], file_parts[key])
	        for j in range(len(replace_val)):
	            file_parts[key]=file_parts[key].replace(replace_val[j], "")

	#to remove multiple whitespaces
	reg_white_space=re.compile(r'\s\s+')
	for key in file_parts:
	    replace_val=re.findall(reg_white_space, file_parts[key])
	    for j in range(len(replace_val)):
	        file_parts[key]=file_parts[key].replace(replace_val[j], " ")

	return file_parts

######this function will extract facts from Damage Survey Report
def getDamageReportData(text):
	
	file_number=re.search(r'FILE NUMBER\s+\d+', text)
	policy_number=re.search(r'POLICY NUMBER\s+[\d|\w]+', text)

	damage_report={"file_number":file_number,
	"policy_number":policy_number}

	for keys in damage_report:
	    temp_var=damage_report[keys]
	    if temp_var:
	        temp_var=temp_var.group().split()
	        temp_var=temp_var[len(temp_var)-1]
	        damage_report[keys]=temp_var
	    else:
	        print("Data not present for"+temp_var)
	# print policy_number.group()	


	return damage_report["file_number"], damage_report["policy_number"]

def getGeneralInfo(text):

	survey_prepared_for=re.search(r'SURVEY\s+PREPARED\s+FOR\s+\w+', text)
	vehicle_make=re.search(r'VEHICLE\s+MAKE\s+\w+', text)
	vehicle_model=re.search(r'VEHICLE\s+MODEL\s+\w+', text)
	vehicle_rating=re.search(r'OVERALL\s+VEHICLE\s+RATING\s+\.\s+\w+', text)
	vehicle_market_value=re.search(r'ESTIMATED\s+MARKET\s+VALUE\s+\W+\d+[\,|\d+]\d+', text)
	vehicle_claim_value=re.search(r'ESTIMATED\s+REPLACEMENT\s+COST\s+[\.|\,|\s+]\s+\W+\d+[\.|\,|\s+]\d+', text)
	vehicle_model_year=re.search(r'MODEL\s+YEAR\s+\d+', text)

	general_info={"survey_prepared_for":survey_prepared_for,
	"vehicle_make":vehicle_make,
	"vehicle_model":vehicle_model,
	"vehicle_rating":vehicle_rating,
	"vehicle_market_value":vehicle_market_value,
	"vehicle_claim_value":vehicle_claim_value,
	"vehicle_model_year":vehicle_model_year}


	# print general_info

	for keys in general_info:
	    temp_var=general_info[keys]
	    if temp_var:
	        temp_var=temp_var.group().split()
	        temp_var=temp_var[len(temp_var)-1]
	        general_info[keys]=temp_var
	    else:
	        print("Data not present for"+temp_var[keys])

	return general_info["survey_prepared_for"], general_info["vehicle_make"], general_info["vehicle_model"], general_info["vehicle_rating"], general_info["vehicle_market_value"], general_info["vehicle_claim_value"].replace(".", "").replace("$", ""), general_info["vehicle_model_year"]

######this function will extrac info prom parties involved
def getPartInvolve(text):

	party_survey_prepared_for=re.search(r'SURVEY\s+PREPARED\s+FOR\s+\w+', text)
	party_vehicle_make=re.search(r'VEHICLE\s+MAKE\s+\w+', text)
	party_vehicle_model=re.search(r'VEHICLE\s+MODEL\s+\w+', text)
	party_vehicle_rating=re.search(r'OVERALL\s+VEHICLE\s+RATING\s+\.\s+\w+', text)
	party_vehicle_market_value=re.search(r'ESTIMATED\s+MARKET\s+VALUE\s+\W+\d+[\,|\d+]\d+', text)
	party_vehicle_claim_value=re.search(r'ESTIMATED\s+REPLACEMENT\s+COST\s+[\.|\,|\s+]\s+\W+\d+[\.|\,|\s+]\d+', text)
	party_vehicle_model_year=re.search(r'MODEL\s+YEAR\s+\d+', text)

	party_involved={"party_survey_prepared_for":party_survey_prepared_for,
	"party_vehicle_make":party_vehicle_make,
	"party_vehicle_model":party_vehicle_model,
	"party_vehicle_rating":party_vehicle_rating,
	"party_vehicle_market_value":party_vehicle_market_value,
	"party_vehicle_claim_value":party_vehicle_claim_value,
	"party_vehicle_model_year":party_vehicle_model_year}

	for keys in party_involved:
	    temp_var=party_involved[keys]
	    if temp_var:
	        temp_var=temp_var.group().split()
	        temp_var=temp_var[len(temp_var)-1]
	        party_involved[keys]=temp_var
	    else:
	        print("Data not present for"+temp_var)

	return party_survey_prepared_for, party_vehicle_make, party_vehicle_model, party_vehicle_rating, party_vehicle_market_value, party_vehicle_claim_value, party_vehicle_model_year

######this function will tell if police was informed
def policeInformed(text):
	#convert into lower case
	text=text.lower()

	#remove punctuations
	remove_punct=list(string.punctuation)

	for i in range(len(remove_punct)):
	    text=text.replace(remove_punct[i], "")

	#remove whitespace
	text = text.strip()
	    
	#to remove stop words

	remove_words=set(stopwords.words('english'))

	tokens=word_tokenize(text)

	wordtokens=[word for word in tokens if not word in remove_words]
	circum_word_combo=list(itertools.combinations(wordtokens, 2))

	#to check values 

	check ="police informed statement called"
	check=word_tokenize(check)
	check=list(itertools.combinations(check, 2))

	if set(circum_word_combo) & set(check):
	    return "Yes"
	else:
	    return "No"

####this function will tell collison type
def collisonType(text):
	#convert into lower case
	text=text.lower()

	#remove punctuations
	remove_punct=list(string.punctuation)

	for i in range(len(remove_punct)):
	    text=text.replace(remove_punct[i], "")

	#remove whitespace
	text = text.strip()
	    
	#to remove stop words

	remove_words=set(stopwords.words('english'))

	tokens=word_tokenize(text)

	wordtokens=[word for word in tokens if not word in remove_words]

	damage_combo=list(itertools.combinations(wordtokens, 2))

	#to get collision type

	front_collision="collision clash damage front"
	front_collision=word_tokenize(front_collision)
	front_collision=list(itertools.combinations(front_collision, 2))

	side_collision="collision clash damage side left right"
	side_collision=word_tokenize(side_collision)
	side_collision=list(itertools.combinations(side_collision, 2))

	rear_collision="collision clash damage rear back"
	rear_collision=word_tokenize(rear_collision)
	rear_collision=list(itertools.combinations(rear_collision, 2))

	if set(damage_combo) & set(front_collision):
	    return "Front Collision"
	if set(damage_combo) & set(side_collision):
	    return "Side Collision"
	if set(damage_combo) & set(rear_collision):
	    return "Rear Collision"

###this function will tell property and body damage
def damageNature(text):

	#convert into lower case
	text=text.lower()

	#remove punctuations
	remove_punct=list(string.punctuation)

	for i in range(len(remove_punct)):
	    text=text.replace(remove_punct[i], "")

	#remove whitespace
	text = text.strip()
	    
	#to remove stop words

	remove_words=set(stopwords.words('english'))

	tokens=word_tokenize(text)

	wordtokens=[word for word in tokens if not word in remove_words]

	word_combo=list(itertools.combinations(wordtokens, 2))

	# print word_combo

	#to get damage type

	property_damage="property damage accident harm property"
	property_damage=word_tokenize(property_damage)
	property_damage=list(itertools.combinations(property_damage, 2))

	body_damage="body injured hurt blow casualty body"
	body_damage=word_tokenize(body_damage)
	body_damage=list(itertools.combinations(body_damage, 2))

	if set(word_combo) & set(property_damage):
		property_damage="Yes"
	else:
		property_damage="No"

	if set(word_combo) & set(body_damage):
		body_damage=1
	else:
		body_damage=0

	return property_damage, body_damage

#this function will tell the incident type
def incidentType(text):

	party_survey_prepared_for=re.search(r'SURVEY\s+PREPARED\s+FOR\s+\w+', text)
	collision=""
	vehicle_involved=0
	if party_survey_prepared_for:
		collision="Multi-vehicle Collision"
		vehicle_involved=2
	else:
		collision="Single Vehicle Collision"
		vehicle_involved=1
	return collision, vehicle_involved

def incidentSeverity(text):
	condition=re.search(r'OVERALL\s+VEHICLE\s+RATING\s+\.\s+\w+', text)

	condition=condition.group().split()
	condition=condition[len(condition)-1]

	if condition=="FAIR" or condition=="GOOD":
	    return "Minor Damage"
	if condition=="EXCELLENT":
	    return "Trivial Damage"
	if condition=="POOR":
	    return "Major Damage"