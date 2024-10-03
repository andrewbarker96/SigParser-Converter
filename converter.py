import pandas as pd
import re
import os
import phonenumbers
import json


# Load SigParser Data
try:
    data = pd.read_csv('SigParser.csv')
except FileNotFoundError:
    print("Error: SigParser.csv not found")
    exit(1)


# Filter out invalid contacts
data = data[data['Contact Status'] == 'Valid']

# Remove Slashes & Quotes from strings
# def remove_slashes(data):
#     for col in data.select_dtypes(include=['object']).columns:
#         data[col] = data[col].str.replace('/', ' ', regex=False)
#     return data

# def remove_quotes(data):
#     for col in data.select_dtypes(include=['object']).columns:
#         data[col] = data[col].str.replace('"', '', regex=False)
#         data[col] = data[col].str.replace("'", '', regex=False)
#     return data

# def set_nan(data):
#     for col in data.select_dtypes(include=['object']).columns:
#         data[col] = data[col].replace('', None)
#     return data
# data = set_nan(data)


# Format Phone Numbers to be +1XXXXXXXXXX
def format_phone_number(phone):
    if pd.isna(phone):
        return None
    phone = str(phone).strip() # Convert to string and strip whitespace
    phone = re.sub(r'\D', '', phone)
    if len(phone) > 10:
        phone = f'+1{phone[-10:]}'
    if len(phone) == 10:
        phone = f'+1{phone}'
    return phone


# Validate Phone Number
def validate_phone_number(phone):
    if pd.isna(phone):  # Check if the value is NaN
        return None
    try:
        parsed_number = phonenumbers.parse(phone, 'US')
        return phonenumbers.is_valid_number(parsed_number)
    except phonenumbers.phonenumberutil.NumberParseException:
        return False
    

# Apply phone formatting and validation to all phone columns
phone_columns = ['Home Phone', 'Office Phone', 'Direct Phone', 'Mobile Phone', 'Fax Phone']
for col in phone_columns:
    # Format the phone number
    data[col] = data[col].apply(format_phone_number)
    # Validate the phone number and replace invalid numbers with None
    data[col] = data[col].apply(lambda x: x if validate_phone_number(x) else None)

# Rename all columns to match typical database infrastructure
data.rename(columns={
    "Contact Status": "status",
    "Name Prefix": "prefix",
    "First Name": "firstName",
    "Last Name": "lastName",
    "Name Suffix": "suffix",
    "Company Name": "company",
    "Job Title": "title",
    "Email Address": "email",
    "Home Phone": "homePhone",
    "Office Phone": "officePhone",
    "Direct Phone": "directPhone",
    "Mobile Phone": "mobilePhone",
    "Fax Phone": "fax",
    "SigParser Contact ID": "uid",
    "Interaction Status": "interactionStatus", # If email has occured in last 365 days. 
}, inplace=True)


# Column Headers for new file
filtered_columns = ['uid', 'prefix', 'firstName', 'lastName', 'suffix', 'title', 'company', 'email', 'homePhone', 'officePhone', 'directPhone', 'mobilePhone', 'fax', ]
filtered_data = data[filtered_columns]


# Save to StockContacts.csv
csv_file = 'StockContacts.csv'
if os.path.exists(csv_file):
    previous_data = pd.read_csv(csv_file)
    try:
        filtered_data.to_csv(csv_file, index=False)
        print("StockContacts.csv updated successfully")
    except Exception as e:
        print(f'Error: Unable to write to StockContacts.csv. {e}')
else:
    print("StockContacts.csv does not exist. Creating StockContacts.csv")
    try:
        filtered_data.to_csv(csv_file, index=False)
        ('StockContacts.csv created successfully')
    except Exception as e:
        print(f'Error: Unable to write to StockContacts.csv. {e}')


# Assuming 'filtered_data' is your DataFrame
filtered_data = filtered_data.fillna('')

# Save to StockContacts.json
json_file = 'StockContacts.json'
if os.path.exists(json_file):
    previous_data = pd.read_json(json_file)
    
    if not filtered_data.equals(previous_data):
        print("Changes Detected. Updating filtered_contacts.json")
        filtered_data.to_json(json_file, orient='records', indent=2)
        print(filtered_data)
    else:
        print("No Changes Detected. filtered_contacts.json is up to date")
else:
    print("filtered_contacts.json does not exist. Creating filtered_contacts.json")
    filtered_data.to_json(json_file, orient='records', indent=2)
