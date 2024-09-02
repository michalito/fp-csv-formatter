# CSV Processor Application

This application is a Flask-based web service designed to process and transform CSV files for inventory management. It provides functionality to convert between different CSV formats and extract product information.

## Features

- CSV transformation for inventory management
- Automatic product information extraction
- Conversion to "Variants Expert" format
- Web interface for easy file upload and processing
- Dockerized for easy deployment

## Prerequisites

- Python 3.9 or higher
- Docker (optional, for containerized deployment)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/csv-processor.git
   cd csv-processor
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

### Local Development

1. Start the Flask application:
   ```
   python app.py
   ```

2. Open a web browser and navigate to `http://localhost:5000`

### Using Docker

1. Build the Docker image:
   ```
   docker build -t csv-processor .
   ```

2. Run the Docker container:
   ```
   docker run -p 5000:5000 csv-processor
   ```

3. Open a web browser and navigate to `http://localhost:5000`

## Usage

1. On the main page, you'll see two sections: "Process CSV" and "Convert to Variants Expert Format"
2. To process a CSV:
   - Click "Choose File" in the "Process CSV" section
   - Select your CSV file
   - Click "Process CSV"
   - Confirm the product information in the modal that appears
   - The processed CSV will be downloaded automatically
3. To convert to Variants Expert format:
   - Click "Choose File" in the "Convert to Variants Expert Format" section
   - Select your CSV file
   - Click "Convert"
   - The converted CSV will be downloaded automatically

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.