import pandas as pd
import json
import os
import numpy as np
from dotenv import load_dotenv
from supabase import create_client, Client

# ---------------------------------------------
#       Load Variables for DB Connection
# ---------------------------------------------

load_dotenv()

# Creating Supabase Client
url: str = os.environ.get('SUPABASE_URL')
key: str = os.environ.get('SUPABASE_KEY')
supabase: Client = create_client(url, key)

json_file = 'StockContacts.json'

try:
    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    print(f'Successfully loaded {len(json_data)} records from {json_file}')
except FileNotFoundError:
    print(f'Error: {json_file} not found')
    exit(1)
except json.JSONDecodeError as e:
    print(f'Error: Unable to load records from {json_file}. {e}')
    exit(1)
except Exception as e:
    print(f'Error reading {json_file}: {e}')
    exit(1)

new = []
updates = []

for record in json_data:
    uid = record.get('uid')
    if uid:
        updates.append(record)
    else:
        new.append(record)
        
batch_size = 100

count = 0

for i in range(0, len(updates), batch_size):
    batch_data = updates[i:i + batch_size]
    try:
        response = (
            supabase
            .table('contacts')
            .upsert(batch_data)
            .execute()
            )
        
    except Exception as e:
        print(f'Error: Unable to update records. {e}')
        exit(1)
    
for i in range(0, len(new), batch_size):
    batch_data = new[i:i + batch_size]
    try:
        response = (
            supabase
            .table('contacts')
            .insert(batch_data)
            .execute()
            )
        
    except Exception as e:
        print(f'Error: Unable to insert records. {e}')
        exit(1)

print(f'{len(updates)} records changed...\nDatabase updated successfully!')
