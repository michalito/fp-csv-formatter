document.addEventListener('DOMContentLoaded', function() {
    const processForm = document.getElementById('processForm');
    const convertForm = document.getElementById('convertForm');
    const errorMessage = document.getElementById('errorMessage');
    const convertErrorMessage = document.getElementById('convertErrorMessage');
    const modal = document.getElementById('modal');
    const confirmForm = document.getElementById('confirmForm');
    const fileInput = processForm.querySelector('input[type="file"]');
    const sheetSelect = document.getElementById('sheetSelect');

    function displayError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }

    function clearError() {
        errorMessage.textContent = '';
        errorMessage.style.display = 'none';
    }

    fileInput.addEventListener('change', function(e) {
        clearError();
        const file = e.target.files[0];
        if (file && file.name.match(/\.(xlsx|xls)$/)) {
            const formData = new FormData();
            formData.append('file', file);

            fetch('/get_excel_sheets', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                sheetSelect.innerHTML = '<option value="">Select a sheet</option>';
                data.sheets.forEach(sheet => {
                    const option = document.createElement('option');
                    option.value = sheet;
                    option.textContent = sheet;
                    sheetSelect.appendChild(option);
                });
                sheetSelect.style.display = 'block';
            })
            .catch(error => {
                displayError(error.message || 'An error occurred while processing the Excel file');
                sheetSelect.style.display = 'none';
            });
        } else {
            sheetSelect.style.display = 'none';
        }
    });

    processForm.addEventListener('submit', function(e) {
        e.preventDefault();
        clearError();
        const formData = new FormData(this);

        fetch('/get_product_info', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            document.getElementById('product_name').value = data.product_name;
            document.getElementById('product_sku_base').value = data.product_sku_base;
            document.getElementById('default_price').value = '0'; // Set default price to 0
            document.getElementById('brand').value = ''; // Initialize brand field
            document.getElementById('gender').value = ''; // Initialize gender field
            document.getElementById('suppliers').value = ''; // Initialize suppliers field
            modal.style.display = 'block';
        })
        .catch(error => {
            displayError(error.message || 'An error occurred while processing the file');
        });
    });

    confirmForm.addEventListener('submit', function(e) {
        e.preventDefault();
        modal.style.display = 'none';
        
        const formData = new FormData(processForm);
        formData.set('product_name', document.getElementById('product_name').value);
        formData.set('product_sku_base', document.getElementById('product_sku_base').value);
        formData.set('default_price', document.getElementById('default_price').value);
        formData.set('wholesale_price', document.getElementById('wholesale_price').value);
        formData.set('consignment_price', document.getElementById('consignment_price').value);
        formData.set('cost', document.getElementById('cost').value);
        formData.set('weight', document.getElementById('weight').value);
        formData.set('brand', document.getElementById('brand').value);
        formData.set('gender', document.getElementById('gender').value);
        formData.set('suppliers', document.getElementById('suppliers').value);
    
        fetch('/process', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'processed_inventory.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            errorMessage.textContent = error.error || 'An error occurred';
        });
    });

    convertForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);

        fetch('/convert_to_odoo', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'odoo_inventory.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            convertErrorMessage.textContent = error.error || 'An error occurred';
        });
    });



    // Close the modal if the user clicks outside of it
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const convertForm = document.getElementById('convertForm');
    const generateOdooButton = document.getElementById('generateOdooButton');
    const categoryModal = document.getElementById('categoryModal');
    const categoryForm = document.getElementById('categoryForm');
    const convertErrorMessage = document.getElementById('convertErrorMessage');

    generateOdooButton.addEventListener('click', function(e) {
        e.preventDefault();
        categoryModal.style.display = 'block';
    });

    categoryForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(convertForm);
        formData.append('primaryCategory', document.getElementById('primaryCategory').value);
        formData.append('secondaryCategory', document.getElementById('secondaryCategory').value);
        formData.append('tertiaryCategory', document.getElementById('tertiaryCategory').value);

        fetch('/convert_to_odoo', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'odoo_inventory.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            categoryModal.style.display = 'none';
        })
        .catch(error => {
            convertErrorMessage.textContent = error.error || 'An error occurred';
            categoryModal.style.display = 'none';
        });
    });

    // Close the modal if the user clicks outside of it
    window.onclick = function(event) {
        if (event.target == categoryModal) {
            categoryModal.style.display = "none";
        }
    }
});