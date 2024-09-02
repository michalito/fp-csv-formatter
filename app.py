from flask import Flask, request, send_file, render_template, jsonify
from csv_processor import process_csv, generate_csv, get_initial_product_info, convert_to_odoo
import io
import traceback
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/get_product_info', methods=['POST'])
def get_product_info():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        if file:
            file_content = file.read()
            try:
                product_name, product_sku_base = get_initial_product_info(file_content)
                return jsonify({'product_name': product_name, 'product_sku_base': product_sku_base})
            except Exception as e:
                app.logger.error(f"Error in get_initial_product_info: {str(e)}")
                app.logger.error(traceback.format_exc())
                return jsonify({'error': f'Error processing file: {str(e)}'}), 400
        return jsonify({'error': 'Invalid file'}), 400
    except Exception as e:
        app.logger.error(f"Unexpected error in get_product_info: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/process', methods=['POST'])
def process():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400
        file = request.files['file']
        product_name = request.form.get('product_name')
        product_sku_base = request.form.get('product_sku_base')
        default_price = request.form.get('default_price', '0')
        brand = request.form.get('brand', '')
        gender = request.form.get('gender', '')
        suppliers = request.form.get('suppliers', '')
        
        if file and product_name and product_sku_base:
            file_content = file.read()
            try:
                processed_data = process_csv(file_content, product_name, product_sku_base, default_price, brand, gender, suppliers)
                output_csv = generate_csv(processed_data)
                
                return send_file(
                    io.BytesIO(output_csv.encode()),
                    mimetype='text/csv',
                    as_attachment=True,
                    attachment_filename='processed_inventory.csv'
                )
            except Exception as e:
                app.logger.error(f"Error processing CSV: {str(e)}")
                app.logger.error(traceback.format_exc())
                return jsonify({'error': f'Error processing CSV: {str(e)}'}), 400
        
        return jsonify({'error': 'Missing required data'}), 400
    except Exception as e:
        app.logger.error(f"Unexpected error in process: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/convert_to_odoo', methods=['POST'])
def convert_to_odoo_route():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        if file:
            file_content = file.read()
            try:
                odoo_csv = convert_to_odoo(file_content)
                
                return send_file(
                    io.BytesIO(odoo_csv.encode()),
                    mimetype='text/csv',
                    as_attachment=True,
                    attachment_filename='odoo_inventory.csv'
                )
            except Exception as e:
                app.logger.error(f"Error converting to Odoo format: {str(e)}")
                app.logger.error(traceback.format_exc())
                return jsonify({'error': f'Error converting to Odoo format: {str(e)}'}), 400
        return jsonify({'error': 'Invalid file'}), 400
    except Exception as e:
        app.logger.error(f"Unexpected error in convert_to_odoo: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)