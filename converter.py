import pandas as pd
import re
import os
import phonenumbers

data = pd.read_csv('SigParser.csv')

data = data[data['Contact Status'] == 'Valid']

def remove_slashes(data):
    for col in data.select_dtypes(include=['object']).columns:
        data[col] = data[col].str.replace('/', ' ', regex=False)
    return data
data = remove_slashes(data)

def remove_quotes(data):
    for col in data.select_dtypes(include=['object']).columns:
        data[col] = data[col].str.replace('"', '', regex=False)
        data[col] = data[col].str.replace("'", '', regex=False)
    return data


# Format Phone Numbers
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
        return False
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
    
    
# Check if at least one number is present for required fields
def check_required_numbers(row):
    if pd.isna(row['Office Phone']) and pd.isna(row['Direct Phone']) and pd.isna(row['Mobile Phone']):
        return False
    return True
data = data[data.apply(check_required_numbers, axis=1)]


# Drop Duplicate Phone Numbers for each Contact
def remove_duplicate_numbers(row):
    phone_numbers = {
        'Home Phone': row['Home Phone'],
        'Office Phone': row['Office Phone'],
        'Direct Phone': row['Direct Phone'],
        'Mobile Phone': row['Mobile Phone']
    }

    # Find duplicates and retain unique numbers
    seen = set()
    duplicates = set()

    # Identify duplicates
    for key, number in phone_numbers.items():
        if pd.notna(number) and number in seen:
            duplicates.add(number)
        seen.add(number)

    # Remove duplicates, keeping only one number per contact
    unique_numbers = []
    for key, number in phone_numbers.items():
        if pd.notna(number) and number not in duplicates:
            unique_numbers.append(number)
        elif number in duplicates and number not in unique_numbers:
            unique_numbers.append(number)  # Keep one instance of the duplicate

    # If no numbers remain, ensure at least one is retained
    if len(unique_numbers) == 0 and pd.notna(row['Office Phone']):
        unique_numbers.append(row['Office Phone'])  # Retain the office phone as a fallback

    # Clear all phone fields and then set unique numbers
    row['Home Phone'] = row['Office Phone'] = row['Direct Phone'] = row['Mobile Phone'] = ''
    
    if unique_numbers:
        # Assign the first unique number to Office Phone, or others as needed
        row['Direct Phone'] = unique_numbers[0]  # You can choose how to assign
        # if len(unique_numbers) > 1:
        #     row['Office Phone'] = unique_numbers[1]  # Assign second unique to Mobile if available
        # # Optionally assign to other fields if desired

    return row

# Apply function to remove duplicate numbers
data = data.apply(remove_duplicate_numbers, axis=1)


data.rename(columns={
    "Contact Status": "Status",
    "Full Name": "FullName",
    "Company Name": "Company",
    "Name Prefix": "Prefix",
    "First Name": "FirstName",
    "Last Name": "LastName",
    "Name Suffix": "Suffix",
    "Job Title": "JobTitle",
    "Email Address": "Email",
    "Home Phone": "HomeNumber",
    "Office Phone": "CompanyMainNumber",
    "Direct Phone": "BusinessNumber",
    "Mobile Phone": "MobileNumber",
    "Fax Phone": "Fax",
    "SigParser Contact ID": "UID",
    "Interaction Status": "InteractionStatus", # If email has occured in last 365 days. 
}, inplace=True)


# Combine Prefix and First Name
data['FirstName'] = data.apply(lambda x: f'{x["Prefix"]} {x["FirstName"]}'.strip() if pd.notna(x["Prefix"]) else x["FirstName"], axis=1)


# Combine Last Name and Suffix
data['LastName'] = data.apply(lambda x: f'{x["LastName"]} {x["Suffix"]}'.strip() if pd.notna(x["Suffix"]) else x["LastName"], axis=1)


# Column Headers for new file. 
filtered_columns = ['FirstName', 'LastName', 'JobTitle', 'Company', 'Email', 'HomeNumber', 'BusinessNumber', 'MobileNumber', 'CompanyMainNumber']
filtered_data = data[filtered_columns]


filtered_file = 'filtered_contacts.csv'
if os.path.exists(filtered_file):
    previous_data = pd.read_csv(filtered_file)
    
    if not filtered_data.equals(previous_data):
        print("Changes Detected. Updating filtered_contacts.csv")
        filtered_data.to_csv(filtered_file, index=False)
    else:
        print("No Changes Detected. filtered_contacts.csv is up to date")
else:
    print("filtered_contacts.csv does not exist. Creating filtered_contacts.csv")
    filtered_data.to_csv(filtered_file, index=False)

