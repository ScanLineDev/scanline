// document.getElementById('csvFileInput').addEventListener('change', handleFileSelect);

window.addEventListener('load', handleFileSelect);

function handleFileSelect() {
    const filePath = "http://[::]:8000/organized_feedback_dict_CURRENT.csv"; // Replace with your file path

    fetch(filePath)
        .then(response => response.text())
        .then(data => {
            populateTable(data);
        })
        .catch(error => console.error('Error:', error));
}


function populateTable(csvData) {
    const rows = csvData.split('\n');
    const headers = rows[0].split(',');

    const highPriorityTable = document.getElementById('highPriorityTable');
    const mediumLowPriorityTable = document.getElementById('mediumLowPriorityTable');

    // Create headers for both tables
    createHeaders(headers, highPriorityTable);
    createHeaders(headers, mediumLowPriorityTable);

    // Populate data
    const highPriorityTbody = highPriorityTable.querySelector('tbody');
    const mediumLowPriorityTbody = mediumLowPriorityTable.querySelector('tbody');

    for (let i = 1; i < rows.length; i++) {
        const cols = rows[i].split(',');
        const tr = document.createElement('tr');

        cols.forEach((col, index) => {
            const td = document.createElement('td');
            // set a newline between the emoji and the name so it always displays emoji above the word.not happening right now.
            if (headers[index] === 'Priority') {
                const priorityParts = col.split(' ');
                col = priorityParts[0] + '\n' + priorityParts[1];
            }
            td.textContent = col;
            tr.appendChild(td);
        });

        // Add row to the appropriate table based on priority
        if (cols[headers.indexOf('Priority')] === '🔴 High') {
            highPriorityTbody.appendChild(tr);
        } else {
            mediumLowPriorityTbody.appendChild(tr);
        }
    }

    // Call the script here, after the table has been populated
    let text = document.body.innerHTML;
    let regex = /`([^`]*)`/gs; // Matches text between backticks across multiple lines
    let newText = text.replace(regex, function(match, p1) {
        return '<span class="code-text">' + p1 + '</span>';
    });
    document.body.innerHTML = newText;
}

function createHeaders(headers, table) {
    const thead = table.querySelector('thead');
    const headerRow = document.createElement('tr');

    headers.forEach((header, index) => {
        const th = document.createElement('th');
        th.textContent = header;
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
}

console.log("Hello World!")

// // Fetch CSV data from given path and populate the table
// try {
//     populateTable("organized_feedback_dict_20231001-230452.csv");
// } catch (error) {
//     console.error("Error loading CSV:", error);
// }

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