import Papa from 'papaparse'
import * as XLSX from 'xlsx'

/**
 * Parse CSV, XLSX, or XLS file and return array of scent objects
 * @param {File} file - The file to parse
 * @returns {Promise<Array>} Array of parsed scent objects
 */
export const parseScentsFile = async (file) => {
  const extension = file.name.split('.').pop().toLowerCase()

  if (extension === 'csv') {
    return parseCSV(file)
  } else if (extension === 'xlsx' || extension === 'xls') {
    return parseExcel(file)
  } else {
    throw new Error(`Unsupported file format: .${extension}`)
  }
}

/**
 * Parse CSV file
 * @param {File} file
 * @returns {Promise<Array>}
 */
const parseCSV = (file) => {
  return new Promise((resolve, reject) => {
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        try {
          const scents = mapToScentObjects(results.data)
          resolve(scents)
        } catch (err) {
          reject(err)
        }
      },
      error: (error) => {
        reject(new Error(`CSV parsing failed: ${error.message}`))
      }
    })
  })
}

/**
 * Parse Excel file (.xlsx or .xls)
 * @param {File} file
 * @returns {Promise<Array>}
 */
const parseExcel = async (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()

    reader.onload = (e) => {
      try {
        const data = e.target.result
        const workbook = XLSX.read(data, { type: 'array' })
        const worksheet = workbook.Sheets[workbook.SheetNames[0]]
        const jsonData = XLSX.utils.sheet_to_json(worksheet)
        const scents = mapToScentObjects(jsonData)
        resolve(scents)
      } catch (err) {
        reject(new Error(`Excel parsing failed: ${err.message}`))
      }
    }

    reader.onerror = () => {
      reject(new Error('Failed to read file'))
    }

    reader.readAsArrayBuffer(file)
  })
}

/**
 * Map raw file data to scent objects
 * Expects columns: Name, Top Notes, Middle Notes, Base Notes, Essential Oils (optional)
 * @param {Array} rawData - Array of objects from CSV/Excel parser
 * @returns {Array} Scent objects
 */
const mapToScentObjects = (rawData) => {
  if (!Array.isArray(rawData) || rawData.length === 0) {
    throw new Error('File is empty or invalid format')
  }

  const scents = rawData
    .filter(row => {
      // Skip empty rows
      return Object.values(row).some(val => val && String(val).trim())
    })
    .map((row, index) => {
      // Handle different column name variations
      const name = getColumnValue(row, ['Name', 'Scent Name', 'name', 'scentName'])
      const topNotes = getColumnValue(row, ['Top Notes', 'topNotes', 'topnotes', 'top'])
      const middleNotes = getColumnValue(row, ['Middle Notes', 'middleNotes', 'middlenotes', 'middle'])
      const baseNotes = getColumnValue(row, ['Base Notes', 'baseNotes', 'basenotes', 'base'])
      const essentialOils = getColumnValue(row, ['Essential Oils', 'essentialOils', 'essentialoils', 'oils', 'ingredients'])
      const allNotes = getColumnValue(row, ['Fragrance Notes', 'All Notes', 'allNotes', 'notes', 'fragrance'])

      // Validate required field
      if (!name || !name.trim()) {
        throw new Error(`Row ${index + 1}: Missing scent name`)
      }

      return {
        name: name.trim(),
        topNotes: topNotes ? topNotes.trim() : '',
        middleNotes: middleNotes ? middleNotes.trim() : '',
        baseNotes: baseNotes ? baseNotes.trim() : '',
        allNotes: allNotes ? allNotes.trim() : '',
        essentialOils: essentialOils ? essentialOils.trim() : '',
        createdBy: '', // Will be set by backend
        createdAt: '', // Will be set by backend
        archivedAt: null
      }
    })

  if (scents.length === 0) {
    throw new Error('No valid scent records found in file')
  }

  return scents
}

/**
 * Try to get column value with multiple possible names (case-insensitive)
 * @param {Object} row - Data row object
 * @param {Array<string>} possibleNames - Possible column names to try
 * @returns {string} Column value or empty string
 */
const getColumnValue = (row, possibleNames) => {
  for (const name of possibleNames) {
    if (row[name] !== undefined && row[name] !== null) {
      return String(row[name])
    }
  }
  return ''
}

/**
 * Validate parsed scents data
 * @param {Array} scents - Array of scent objects
 * @returns {Object} {valid: boolean, errors: Array<string>}
 */
export const validateScents = (scents) => {
  const errors = []

  if (!Array.isArray(scents) || scents.length === 0) {
    return { valid: false, errors: ['No scents provided'] }
  }

  scents.forEach((scent, index) => {
    if (!scent.name || !scent.name.trim()) {
      errors.push(`Row ${index + 1}: Scent name is required`)
    }

    if (scent.name && scent.name.length > 255) {
      errors.push(`Row ${index + 1}: Scent name is too long (max 255 characters)`)
    }
  })

  return {
    valid: errors.length === 0,
    errors
  }
}
