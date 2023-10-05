console.log("Data loaded from data.js:");
console.log(data);

window.addEventListener('load', handleFileSelect);

function handleFileSelect() {
    populateTable(data);
}

function populateTable(data) {
    const headers = Object.keys(data[0]);

    const highPriorityTable = document.getElementById('highPriorityTable');
    const mediumLowPriorityTable = document.getElementById('mediumLowPriorityTable');

    // Create headers for both tables
    createHeaders(headers, highPriorityTable);
    createHeaders(headers, mediumLowPriorityTable);

    // Populate data
    const highPriorityTbody = highPriorityTable.querySelector('tbody');
    const mediumLowPriorityTbody = mediumLowPriorityTable.querySelector('tbody');

    data.forEach((row) => {
        const tr = document.createElement('tr');

        headers.forEach((header) => {
            const td = document.createElement('td');
            td.textContent = row[header];
            tr.appendChild(td);
        });

        // Add row to the appropriate table based on priority
        if (row['Priority'] === '🔴 High') {
            highPriorityTbody.appendChild(tr);
        } else {
            mediumLowPriorityTbody.appendChild(tr);
        }
    });
}

function createHeaders(headers, table) {
    const thead = table.querySelector('thead');
    const headerRow = document.createElement('tr');

    headers.forEach((header) => {
        const th = document.createElement('th');
        th.textContent = header;
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
}

console.log("Hello World!")