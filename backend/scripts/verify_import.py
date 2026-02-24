
import openpyxl
import sqlite3
import os

def compare():
    excel_path = '../TITAN V.1.xlsx'
    db_path = 'titancare.db'
    
    if not os.path.exists(excel_path):
        print(f"Excel file not found at {excel_path}")
        return
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return

    # Load Excel
    print("Loading Excel...")
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    ws = wb['Sheet1']
    excel_data = []
    current_model = None
    for row in ws.iter_rows(min_row=4, values_only=True):
        model = row[0]
        if model:
            current_model = str(model).strip()
        
        # sub_model: prefer col B, fall back to col C
        sub_model = str(row[1]).strip() if row[1] else (str(row[2]).strip() if row[2] else None)
        price = row[3]
        excel_data.append({'model': current_model, 'sub_model': sub_model, 'price': price})
    print(f"Found {len(excel_data)} records in Excel.")

    # Load DB
    print("Loading DB...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT model, sub_model, starting_price FROM cars')
    db_rows = cursor.fetchall()
    conn.close()
    print(f"Found {len(db_rows)} records in DB.")

    # Compare
    print('\nFull Comparison (Excel vs DB):')
    header = f'{"Model":<20} | {"Sub-Model":<25} | {"Excel Price":<12} | {"DB Price":<12}'
    print(header)
    print('-' * len(header))

    matches = 0
    for i in range(len(excel_data)):
        e = excel_data[i]
        if i < len(db_rows):
            d = db_rows[i]
            d_price = f'{d[2]:,.0f}' if d[2] is not None else 'N/A'
            e_price = f'{e["price"]:,.0f}' if e["price"] is not None else 'N/A'
            
            model_match = str(e["model"]) == str(d[0])
            sub_match = str(e["sub_model"]) == str(d[1])
            price_match = (e["price"] == d[2]) or (e["price"] is None and d[2] is None)
            
            if model_match and sub_match and price_match:
                matches += 1
            
            print(f'{str(e["model"]):<20} | {str(e["sub_model"]):<25} | {e_price:<12} | {d_price:<12}')
        else:
            print(f'{str(e["model"]):<20} | {str(e["sub_model"]):<25} | {e["price"]:<12} | MISSING')

    print('\n' + '-' * 20)
    print(f"Total Matches: {matches}/{len(excel_data)}")
    if matches == len(excel_data):
        print("VERIFICATION SUCCESS: Data matches perfectly.")
    else:
        print("VERIFICATION FAILURE: Some records do not match.")

if __name__ == "__main__":
    compare()
