import csv
import io
import re
import traceback
from openpyxl import load_workbook


def process_file(file_content, file_type, product_name, product_sku_base, default_price, brand, gender, suppliers, sheet_name=None):
    try:
        if file_type == 'csv':
            return process_csv(file_content, product_name, product_sku_base, default_price, brand, gender, suppliers)
        elif file_type == 'xlsx':
            return process_excel(file_content, product_name, product_sku_base, default_price, brand, gender, suppliers, sheet_name)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    except Exception as e:
        print(f"Error in process_file: {str(e)}")
        traceback.print_exc()
        raise
    
def process_csv(file_content, product_name, product_sku_base, default_price, brand, gender, suppliers):
    reader = csv.DictReader(io.StringIO(file_content.decode('utf-8-sig')))
    return process_data(reader, product_name, product_sku_base, default_price, brand, gender, suppliers)

def process_excel(file_content, product_name, product_sku_base, default_price, brand, gender, suppliers, sheet_name=None):
    wb = load_workbook(filename=io.BytesIO(file_content))
    
    if sheet_name:
        if sheet_name not in wb.sheetnames:
            raise ValueError(f"Sheet '{sheet_name}' not found in the workbook")
        ws = wb[sheet_name]
    else:
        ws = wb.active
    
    rows = list(ws.iter_rows(values_only=True))
    header = rows[0]
    reader = [dict(zip(header, row)) for row in rows[1:]]
    return process_data(reader, product_name, product_sku_base, default_price, brand, gender, suppliers)

def process_data(reader, product_name, product_sku_base, default_price, brand, gender, suppliers):
    try:
        processed_data = {}
        current_product = None
        current_price = None
        
        size_map = {'XS': 'XSmall', 'SM': 'Small', 'ME': 'Medium', 'LA': 'Large', 'XL': 'X Large'}
        
        for row in reader:
            product_sku = row['Product SKU']
            
            # Check if this is a product row or an item row
            if not any(size in product_sku for size in ['XS', 'SM', 'ME', 'LA', 'XL']):
                # This is a product row
                color = ' '.join(row['Product Name'].split()[1:])
                current_product = product_sku
                current_price = row['Price'].replace('€', '').strip()
                
                if current_product not in processed_data:
                    processed_data[current_product] = {
                        'Product': product_name,
                        'Color': color,
                        'Brand': brand,
                        'Gender': gender,
                        'Suppliers': suppliers,
                        'Items': {}
                    }
            else:
                # This is an item row
                size_identifier = product_sku.split('-')[-1]
                full_size = re.search(r'\[S\]Size=(.*?)(?=\s|$)', row['Product Name']).group(1)
                size = size_map.get(size_identifier, full_size.split()[0])
                
                color_identifier = row['MPN'][-3:]
                item_sku = f"{product_sku_base}-{color_identifier}-{size_identifier}"
                
                processed_data[current_product]['Items'][item_sku] = {
                    'Size': size_identifier,
                    'FullSize': size,
                    'Stock': row['Stock'] or '0',
                    'MPN': row['MPN'],
                    'GTIN': row['GTIN'] or '',
                    'Price': current_price or default_price,
                    'Status': row['Status'] or ''
                }
        
        # Ensure all sizes are present for each product
        all_sizes = ['XS', 'SM', 'ME', 'LA', 'XL']
        for product_sku, product_data in processed_data.items():
            color_identifier = next(iter(product_data['Items'].values()))['MPN'][-3:]
            for size in all_sizes:
                item_sku = f"{product_sku_base}-{color_identifier}-{size}"
                if item_sku not in product_data['Items']:
                    product_data['Items'][item_sku] = {
                        'Size': size,
                        'FullSize': size_map[size],
                        'Stock': '0',
                        'MPN': '',
                        'GTIN': '',
                        'Price': current_price or default_price,
                        'Status': ''
                    }
        
        return processed_data
    except Exception as e:
        raise Exception(f"Error processing data: {str(e)}")
    
def convert_to_odoo(file_content, file_type):
    if file_type == 'csv':
        input_file = io.StringIO(file_content.decode('utf-8-sig'))
        reader = csv.DictReader(input_file)
    elif file_type == 'xlsx':
        wb = load_workbook(filename=io.BytesIO(file_content))
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        header = rows[0]
        reader = [dict(zip(header, row)) for row in rows[1:]]
    else:
        raise ValueError("Unsupported file type")
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        'External_ID', 'base_sku', 'Internal Reference', 'Name', 'Product Category (External_ID)',
        'Barcode', 'Supplier Product Code', 'Published', 'Color', 'Size', 'Sales Price', 'Cost',
        'Weight', 'Package Length (cm)', 'Package Width (cm)', 'Package Height (cm)', 'Brand',
        'Gender', 'Suppliers', 'Primary Supplier', 'Description'
    ])
    writer.writeheader()

    for row in reader:
        if int(row['Stock']) == 0:
            continue

        product_name = row['Product']
        color = row['Color']
        size = row['Size']
        sku = row['Item SKU']
        price = row['Price']
        barcode = row['GTIN']
        mpn = row['MPN']
        status = row['Status']
        brand = row['Brand']
        gender = row['Gender']
        suppliers = row['Suppliers']

        base_sku = sku.rsplit('-', 2)[0]
        external_id = f"product_{sku.replace('-', '_')}"

        new_row = {
            'External_ID': external_id,
            'base_sku': base_sku,
            'Internal Reference': sku,
            'Name': f"{product_name} - {color} ({size})",
            'Product Category (External_ID)': 'category_apparel',  # You may want to implement a mapping for this
            'Barcode': barcode,
            'Supplier Product Code': mpn,
            'Published': '1' if status.lower() == 'active' else '0',
            'Color': color,
            'Size': size,
            'Sales Price': price,
            'Cost': '',  # You may want to add this information to your input CSV
            'Weight': '',  # You may want to add this information to your input CSV
            'Package Length (cm)': '',  # You may want to add this information to your input CSV
            'Package Width (cm)': '',  # You may want to add this information to your input CSV
            'Package Height (cm)': '',  # You may want to add this information to your input CSV
            'Brand': brand,
            'Gender': gender,
            'Suppliers': suppliers,
            'Primary Supplier': suppliers,  # maybe update if in the future need more than one
            'Description': ''  # You may want to add this information to your input CSV
        }
        writer.writerow(new_row)

    return output.getvalue()

def generate_csv(processed_data):
    try:
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['Product', 'Item', 'Item SKU', 'Color', 'Size', 'Stock', 'MPN', 'GTIN', 'Price', 'Status', 'Brand', 'Gender', 'Suppliers'])
        
        for product_sku, product_data in processed_data.items():
            product = product_data['Product']
            color = product_data['Color']
            brand = product_data['Brand']
            gender = product_data['Gender']
            suppliers = product_data['Suppliers']
            for item_sku, item_data in product_data['Items'].items():
                item = f"{product} {color} {item_data['Size']}"
                writer.writerow([
                    product,
                    item,
                    item_sku,
                    color,
                    item_data['FullSize'],
                    item_data['Stock'],
                    item_data['MPN'],
                    item_data['GTIN'],
                    item_data['Price'],
                    item_data['Status'],
                    brand,
                    gender,
                    suppliers
                ])
        
        return output.getvalue()
    except Exception as e:
        raise Exception(f"Error generating CSV: {str(e)}")
    
def get_excel_sheet_names(file_content):
    wb = load_workbook(filename=io.BytesIO(file_content))
    return wb.sheetnames

def get_initial_product_info(file_content, file_type, sheet_name=None):
    if file_type == 'csv':
        return get_initial_product_info_csv(file_content)
    elif file_type == 'xlsx':
        return get_initial_product_info_excel(file_content, sheet_name)
    else:
        raise ValueError("Unsupported file type")

def get_initial_product_info_csv(file_content):
    try:
        reader = csv.DictReader(io.StringIO(file_content.decode('utf-8-sig')))
        first_row = next(reader)
        product_name = first_row['Product Name'].split()[0]
        product_sku_base = first_row['Product SKU'].split('-')[0]
        return product_name, product_sku_base
    except Exception as e:
        raise Exception(f"Error getting initial product info from CSV: {str(e)}")

def get_initial_product_info_excel(file_content, sheet_name=None):
    try:
        wb = load_workbook(filename=io.BytesIO(file_content))
        if sheet_name:
            if sheet_name not in wb.sheetnames:
                raise ValueError(f"Sheet '{sheet_name}' not found in the workbook")
            ws = wb[sheet_name]
        else:
            ws = wb.active
        
        first_row = next(ws.iter_rows(values_only=True))
        header = first_row
        data_row = next(ws.iter_rows(values_only=True))
        first_row_dict = dict(zip(header, data_row))
        
        product_name = first_row_dict['Product Name'].split()[0]
        product_sku_base = first_row_dict['Product SKU'].split('-')[0]
        return product_name, product_sku_base
    except Exception as e:
        raise Exception(f"Error getting initial product info from Excel: {str(e)}")