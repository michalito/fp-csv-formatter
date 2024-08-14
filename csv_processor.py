import csv
import io
import re

def process_csv(file_content, product_name, product_sku_base, default_price):
    try:
        reader = csv.DictReader(io.StringIO(file_content.decode('utf-8-sig')))
        processed_data = {}
        current_product = None
        current_price = None
        
        size_map = {'XS': 'XSmall', 'SM': 'Small', 'ME': 'Medium', 'LA': 'Large', 'XL': 'X Large'}
        
        for row in reader:
            product_sku = row['Product SKU']
            
            # Check if this is a product row or an item row
            if not any(size in product_sku for size in ['XS', 'SM', 'ME', 'LA', 'XL']):
                # This is a product row
                product_name = row['Product Name'].split()[0]
                color = ' '.join(row['Product Name'].split()[1:])
                current_product = product_sku
                current_price = row['Price'].replace('€', '').strip()
                
                if current_product not in processed_data:
                    processed_data[current_product] = {
                        'Product': product_name,
                        'Color': color,
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
        raise Exception(f"Error processing CSV: {str(e)}")
    
def convert_to_variants_expert_format(file_content):
    input_file = io.StringIO(file_content.decode('utf-8-sig'))
    reader = csv.DictReader(input_file)
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        'Entry Type', 'Entry Name', 'Item Group Name', 'Attribute 1 Name', 'Attribute 1 Option',
        'Attribute 2 Name', 'Attribute 2 Option', 'Attribute 3 Name', 'Attribute 3 Option',
        'Quantity', 'Unit', 'Min Level', 'Price', 'Notes', 'Tags', 'Primary Folder',
        'Subfolder-level1', 'Subfolder-level2', 'Subfolder-level3', 'Subfolder-level4',
        'Photo1', 'Photo2', 'Photo3', 'Photo4', 'Photo5', 'Photo6', 'Photo7', 'Photo8',
        'Barcode/QR1-Data', 'Barcode/QR1-Type', 'Barcode/QR2-Data', 'Barcode/QR2-Type'
    ])
    writer.writeheader()

    for row in reader:
        product_name = row['Product']
        color = row['Color']
        size = row['Size']
        quantity = row['Stock']
        price = row['Price']
        barcode = row['GTIN']

        new_row = {
            'Entry Type': 'Item',
            'Entry Name': product_name,
            'Item Group Name': product_name,
            'Attribute 1 Name': 'Color',
            'Attribute 1 Option': color,
            'Attribute 2 Name': 'Size',
            'Attribute 2 Option': size,
            'Quantity': quantity,
            'Unit': 'Unit',
            'Min Level': '2',
            'Price': price,
            'Barcode/QR1-Data': '',
            'Barcode/QR1-Type': '',
            'Barcode/QR2-Data': barcode,
            'Barcode/QR2-Type': 'org.iso.Code128' if barcode else ''
        }
        writer.writerow(new_row)

    return output.getvalue()

def generate_csv(processed_data):
    try:
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['Product', 'Item', 'Item SKU', 'Color', 'Size', 'Stock', 'MPN', 'GTIN', 'Price', 'Status'])
        
        for product_sku, product_data in processed_data.items():
            product = product_data['Product']
            color = product_data['Color']
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
                    item_data['Status']
                ])
        
        return output.getvalue()
    except Exception as e:
        raise Exception(f"Error generating CSV: {str(e)}")

def get_initial_product_info(file_content):
    try:
        reader = csv.DictReader(io.StringIO(file_content.decode('utf-8-sig')))
        first_row = next(reader)
        product_name = first_row['Product Name'].split()[0]
        product_sku_base = first_row['Product SKU'].split('-')[0]
        return product_name, product_sku_base
    except Exception as e:
        raise Exception(f"Error getting initial product info: {str(e)}")