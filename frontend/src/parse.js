import fs from 'fs';
import csv from 'csv-parser';

const results = [];
let id = 3;

fs.createReadStream('T4 Scents Fragrance Oil List-1.csv')
  .pipe(csv())
  .on('data', (data) => {
    if (data['Scent Name'] && data['Scent Name'].trim()) {
      results.push({
        id: id++,
        name: data['Scent Name'].trim(),
        topNotes: '',
        middleNotes: '',
        baseNotes: '',
        allNotes: data['Fragrance Notes (top, middle, base)'].trim(),
        essentialOils: data['Essential Oils'].trim(),
        createdBy: 'admin@t4scents.com',
        createdAt: '2025-01-15',
        archivedAt: null
      });
    }
  })
  .on('end', () => {
    fs.writeFileSync('scentsData.js', 'export default ' + JSON.stringify(results, null, 2));
    console.log('Data written to scentsData.js');
  });