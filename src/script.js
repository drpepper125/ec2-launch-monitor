// Get today's date in YYYY-MM-DD format
const TODAY = new Date().toISOString().split('T')[0];

// Load CSV data from Lambda-generated reports
async function loadCSVData() {
  console.log('Loading CSV data...');
  
  try {
    // Try to load today's CSV file from Lambda reports
    const response = await fetch(`ec2-launch-reports/2025/08/ec2-instances-${TODAY}.csv`);
    
    if (response.ok) {
      const csvText = await response.text();
      console.log('Lambda CSV loaded successfully');
      return csvText;
    }
    
    // If Lambda report not found, fall back to static data
    console.log('Lambda report not found, loading static data...');
    const staticResponse = await fetch('data/servers.csv');
    
    if (staticResponse.ok) {
      const csvText = await staticResponse.text();
      console.log('Static CSV loaded successfully');
      return csvText;
    }
    
    throw new Error('No CSV data available');
    
  } catch (error) {
    console.error('Error loading CSV:', error);
    return 'Error,Message\nNo Data,"Failed to load CSV files"';
  }
}

// Render CSV data to table
function renderTable(csvText) {
  console.log('Rendering table...');
  
  const lines = csvText.trim().split('\n');
  if (lines.length === 0) return '<p>No data available</p>';
  
  let table = '<table class="data-table">';
  
  lines.forEach((line, index) => {
    const row = parseCSVLine(line);
    
    table += '<tr>';
    row.forEach((cell) => {
      const cleanCell = cell.trim().replace(/^"|"$/g, '');
      
      if (index === 0) {
        table += `<th>${cleanCell}</th>`;
      } else {
        let cellContent = cleanCell;
        
        // Add status styling
        if (cleanCell.toLowerCase() === 'running') {
          cellContent = `<span class="status-running">${cleanCell}</span>`;
        } else if (cleanCell.toLowerCase() === 'stopped') {
          cellContent = `<span class="status-stopped">${cleanCell}</span>`;
        } else if (cleanCell.toLowerCase() === 'pending') {
          cellContent = `<span class="status-pending">${cleanCell}</span>`;
        }
        
        table += `<td>${cellContent}</td>`;
      }
    });
    table += '</tr>';
  });
  
  table += '</table>';
  return table;
}

// Initialize the page
async function initializePage() {
  console.log('Initializing page...');
  
  const container = document.getElementById('table-container');
  if (!container) {
    console.error('table-container element not found!');
    return;
  }
  
  container.innerHTML = '<p>Loading data...</p>';
  
  try {
    const csvText = await loadCSVData();
    const table = renderTable(csvText);
    container.innerHTML = table;
    console.log('Page initialized successfully');
    
  } catch (error) {
    console.error('Failed to initialize page:', error);
    container.innerHTML = `<p>Error loading data: ${error.message}</p>`;
  }
}

// Load data when page loads
document.addEventListener('DOMContentLoaded', initializePage);

function parseCSVLine(line) {
  const result = [];
  let current = '';
  let inQuotes = false;
  
  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    
    if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === ',' && !inQuotes) {
      result.push(current);
      current = '';
    } else {
      current += char;
    }
  }
  
  result.push(current);
  return result;
}
