const ifct2017 = require('ifct2017');
const fs = require('fs');
const path = require('path');

async function main() {
    console.log('Loading IFCT 2017 data...');
    await ifct2017.compositions.load();
    
    const csvPath = ifct2017.compositions.csv();
    console.log('CSV path:', csvPath);
    
    const csvContent = fs.readFileSync(csvPath, 'utf8');
    const lines = csvContent.split('\n');
    console.log(`Total lines: ${lines.length}`);
    
    // Proper CSV parser that handles quoted fields with commas inside
    function parseCSVLine(line) {
        const fields = [];
        let current = '';
        let inQuotes = false;
        
        for (let i = 0; i < line.length; i++) {
            const char = line[i];
            if (char === '"') {
                inQuotes = !inQuotes;
            } else if (char === ',' && !inQuotes) {
                fields.push(current.trim());
                current = '';
            } else {
                current += char;
            }
        }
        fields.push(current.trim());
        return fields;
    }
    
    // Parse headers
    const headers = parseCSVLine(lines[0]);
    console.log('First 8 headers:', headers.slice(0, 8));
    
    // Parse all rows
    const allFoods = [];
    for (let i = 1; i < lines.length; i++) {
        if (!lines[i].trim()) continue;
        const values = parseCSVLine(lines[i]);
        const food = {};
        headers.forEach((header, index) => {
            food[header] = values[index] !== undefined ? values[index] : null;
        });
        allFoods.push(food);
    }
    
    console.log(`Parsed ${allFoods.length} items`);
    
    // Show first item to verify
    const first = allFoods[0];
    console.log('\nFirst item verification:');
    Object.keys(first).slice(0, 10).forEach(k => {
        console.log(`  '${k}' = '${first[k]}'`);
    });
    
    // Save
    const outputPath = path.join(__dirname, '..', 'data', 'raw', 'ifct2017.json');
    fs.writeFileSync(outputPath, JSON.stringify(allFoods, null, 2));
    console.log(`\n✅ Saved ${allFoods.length} items to ifct2017.json`);
}

main().catch(console.error);