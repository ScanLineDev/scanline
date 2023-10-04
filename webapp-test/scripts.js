document.getElementById('csvFileInput').addEventListener('change', handleFileSelect);

function handleFileSelect(event) {
    const file = event.target.files[0];
    // const file = '../reviewme/ailinter/saved_reviews/organized_feedback_dict_20231001-230452.csv'; // Replace with your file path
    const reader = new FileReader();

    reader.onload = function(e) {
        const csvData = e.target.result;
        populateTable(csvData);
    };

    reader.readAsText(file);
}

function populateTable(csvData) {
    const rows = csvData.split('\n');
    const headers = rows[0].split(',');

    const table = document.getElementById('dataTable');

    // Create headers and filter dropdowns
    const thead = table.querySelector('thead');
    const headerRow = document.createElement('tr');
    const filterRow = document.createElement('tr');

    headers.forEach((header, index) => {
        const th = document.createElement('th');
        th.textContent = header;
        headerRow.appendChild(th);

        const td = document.createElement('td');
        
        if (header === 'Error Category' || header === 'Priority') {
            const div = document.createElement('div');
            div.className = 'dropdown';
            const select = document.createElement('select');
            select.setAttribute('multiple', 'multiple');
            const divContent = document.createElement('div');
            divContent.className = 'dropdown-content';
            divContent.appendChild(select);
            div.appendChild(divContent);
            td.appendChild(div);
            select.addEventListener('change', handleFilter);
        }

        filterRow.appendChild(td);
    });

    thead.appendChild(headerRow);
    thead.appendChild(filterRow);

    // Populate data
    const tbody = table.querySelector('tbody');
    let errorCategories = new Set();
    let priorities = new Set();

    for (let i = 1; i < rows.length; i++) {
        const cols = rows[i].split(',');
        const tr = document.createElement('tr');

        cols.forEach((col, index) => {
            const td = document.createElement('td');
            td.textContent = col;
            tr.appendChild(td);

            // populate error categories and priorities for dropdowns
            if (headers[index] === 'Error Category') errorCategories.add(col);
            if (headers[index] === 'Priority') priorities.add(col);
        });

        tbody.appendChild(tr);
    }

    // Populate dropdowns with unique values
    const errorCategoryDropdown = thead.querySelectorAll('select')[0];
    errorCategories.forEach(cat => {
        const option = document.createElement('option');
        option.textContent = option.value = cat;
        errorCategoryDropdown.appendChild(option);
    });

    const priorityDropdown = thead.querySelectorAll('select')[1];
    priorities.forEach(pri => {
        const option = document.createElement('option');
        option.textContent = option.value = pri;
        priorityDropdown.appendChild(option);
    });
}

function handleFilter() {
    const errorCategoryValues = Array.from(document.querySelector('thead select:nth-child(1)').selectedOptions).map(opt => opt.value.toLowerCase());
    const priorityValues = Array.from(document.querySelector('thead select:nth-child(2)').selectedOptions).map(opt => opt.value.toLowerCase());

    const tbody = document.getElementById('dataTable').querySelector('tbody');

    Array.from(tbody.rows).forEach(row => {
        const errorCategoryCell = row.cells[0].textContent.toLowerCase();
        const priorityCell = row.cells[1].textContent.toLowerCase();

        if ((errorCategoryValues.length === 0 || errorCategoryValues.includes(errorCategoryCell)) &&
            (priorityValues.length === 0 || priorityValues.includes(priorityCell))) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}