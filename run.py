import pandas as pd
import re
import os
import phonenumbers
import json
from dotenv import load_dotenv
from supabase import create_client, Client

class ContactConverter:
    def __init__(self, csv_file: str, json_file: str):
        self.csv_file = csv_file
        self.json_file = json_file
        load_dotenv()

        # Creating Supabase Client
        self.supabase_url: str = os.getenv('SUPABASE_URL')
        self.supabase_key: str = os.getenv('SUPABASE_KEY')
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

    # Format Phone Numbers to be +1XXXXXXXXXX
    def format_phone_number(self, phone):
        if pd.isna(phone):
            return None
        phone = str(phone).strip()  # Convert to string and strip whitespace
        phone = re.sub(r'\D', '', phone)
        if len(phone) > 10:
            phone = f'+1{phone[-10:]}'
        elif len(phone) == 10:
            phone = f'+1{phone}'
        return phone

    # Validate Phone Number
    def validate_phone_number(self, phone):
        if pd.isna(phone):  # Check if the value is NaN
            return None
        try:
            parsed_number = phonenumbers.parse(phone, 'US')
            return phonenumbers.is_valid_number(parsed_number)
        except phonenumbers.phonenumberutil.NumberParseException:
            return False

    # Process the CSV and convert phone numbers
    def process_csv(self):
        try:
            data = pd.read_csv(self.csv_file)
        except FileNotFoundError:
            print(f"Error: {self.csv_file} not found")
            return False

        # Filter out invalid contacts
        data = data[data['Contact Status'] == 'Valid']

        phone_columns = ['Home Phone', 'Office Phone', 'Direct Phone', 'Mobile Phone', 'Fax Phone']
        for col in phone_columns:
            data[col] = data[col].apply(self.format_phone_number)
            data[col] = data[col].apply(lambda x: x if self.validate_phone_number(x) else None)

        # Rename columns
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
            "Interaction Status": "interactionStatus",
        }, inplace=True)

        filtered_columns = ['uid', 'prefix', 'firstName', 'lastName', 'suffix', 'title', 'company', 'email', 
                            'homePhone', 'officePhone', 'directPhone', 'mobilePhone', 'fax']
        filtered_data = data[filtered_columns]
        filtered_data = filtered_data.fillna('')

        return filtered_data

    # Save to JSON
    def save_to_json(self, data):
        try:
            if os.path.exists(self.json_file):
                previous_data = pd.read_json(self.json_file)
                if not data.equals(previous_data):
                    data.to_json(self.json_file, orient='records')
                    print(f"{self.json_file} updated successfully")
                else:
                    print(f"No changes detected. {self.json_file} not updated")
            else:
                print(f"Creating {self.json_file}")
                data.to_json(self.json_file, orient='records', indent=2)
        except Exception as e:
            print(f"Error: Unable to write to {self.json_file}. {e}")
            return False
        return True

    # Upload data to Supabase
    def upload_to_supabase(self):
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            print(f'Successfully loaded {len(json_data)} records from {self.json_file}')
        except FileNotFoundError:
            print(f"Error: {self.json_file} not found")
            return False
        except json.JSONDecodeError as e:
            print(f"Error: Unable to load records from {self.json_file}. {e}")
            return False

        new_records = []
        updates = []

        for record in json_data:
            uid = record.get('uid')
            if uid:
                updates.append(record)
            else:
                new_records.append(record)

        # Batch update and insert
        batch_size = 100
        for i in range(0, len(updates), batch_size):
            batch_data = updates[i:i + batch_size]
            try:
                self.supabase.table('contacts').upsert(batch_data).execute()
            except Exception as e:
                print(f"Error: Unable to update records. {e}")
                return False

        for i in range(0, len(new_records), batch_size):
            batch_data = new_records[i:i + batch_size]
            try:
                self.supabase.table('contacts').insert(batch_data).execute()
            except Exception as e:
                print(f"Error: Unable to insert records. {e}")
                return False

        print(f"Uploaded {len(json_data)} records to the database\nProcess Completed Successfully")
        os.remove(self.json_file)
        return True

    # Main function to run the conversion and upload
    def run(self):
        data = self.process_csv()
        if data is not None:
            if self.save_to_json(data):
                self.upload_to_supabase()


# Example usage in a desktop app
if __name__ == "__main__":
    converter = ContactConverter('SigParser.csv', 'StockContacts.json')
    converter.run()
