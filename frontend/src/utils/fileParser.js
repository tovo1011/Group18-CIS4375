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
 * Intelligently parse combined fragrance notes into top/middle/base
 * Splits allNotes string into thirds
 * Example: 'light apple, rose, carnation, jasmine, suede, musk, wood' →
 *   top: 'light apple, rose'  | middle: 'carnation, jasmine' | base: 'suede, musk, wood'
 * @param {string} allNotes - Combined notes string
 * @returns {Object} {topNotes, middleNotes, baseNotes}
 */
const intelligentlyParseNotes = (allNotes) => {
  if (!allNotes || !allNotes.trim()) {
    return { topNotes: '', middleNotes: '', baseNotes: '' }
  }

  // Remove parentheses and excess whitespace
  const cleaned = allNotes.replace(/[()]/g, '').trim()
  
  // Split by comma
  const notes = cleaned.split(',')
    .map(note => note.trim())
    .filter(note => note.length > 0)

  if (notes.length === 0) {
    return { topNotes: '', middleNotes: '', baseNotes: '' }
  }

  if (notes.length === 1) {
    return { topNotes: notes[0], middleNotes: '', baseNotes: '' }
  }

  if (notes.length === 2) {
    return { topNotes: notes[0], middleNotes: '', baseNotes: notes[1] }
  }

  // Split into thirds for 3+ notes
  const third = Math.ceil(notes.length / 3)
  const topNotes = notes.slice(0, third).join(', ')
  const middleNotes = notes.slice(third, third * 2).join(', ')
  const baseNotes = notes.slice(third * 2).join(', ')

  return { topNotes, middleNotes, baseNotes }
}

/**
 * Map raw file data to scent objects
 * Expects columns: Name, Top Notes, Middle Notes, Base Notes, Essential Oils (optional)
 * Falls back to intelligent parsing if top/middle/base are missing but allNotes is present
 * @param {Array} rawData - Array of objects from CSV/Excel parser
 * @returns {Array} Scent objects
 */
const mapToScentObjects = (rawData) => {
  if (!Array.isArray(rawData) || rawData.length === 0) {
    throw new Error('File is empty or invalid format')
  }

  // DEBUG: Log column names from first row
  if (rawData.length > 0) {
    console.log('CSV Column names:', Object.keys(rawData[0]))
  }

  // Map data and keep track of original indices for better error messages
  const scents = rawData
    .map((row, originalIndex) => {
      // Handle different column name variations
      const name = getColumnValue(row, ['Name', 'Scent Name', 'name', 'scentName'])
      let topNotes = getColumnValue(row, ['Top Notes', 'topNotes', 'topnotes', 'top'])
      let middleNotes = getColumnValue(row, ['Middle Notes', 'middleNotes', 'middlenotes', 'middle'])
      let baseNotes = getColumnValue(row, ['Base Notes', 'baseNotes', 'basenotes', 'base'])
      const essentialOils = getColumnValue(row, ['Essential Oils', 'essentialOils', 'essentialoils', 'oils', 'ingredients'])
      const allNotes = getColumnValue(row, ['Fragrance Notes', 'All Notes', 'allNotes', 'notes', 'fragrance'])

      // Skip completely empty rows (all fields empty)
      const hasAnyData = name || topNotes || middleNotes || baseNotes || essentialOils || allNotes
      if (!hasAnyData) {
        return null // Mark for filtering
      }

      // Skip rows without a scent name (required field) - silently ignore them
      if (!name || !name.trim()) {
        return null // Mark for filtering instead of throwing error
      }

      // If top/middle/base are all empty but allNotes exists, intelligently parse it
      if (!topNotes && !middleNotes && !baseNotes && allNotes) {
        const parsed = intelligentlyParseNotes(allNotes)
        topNotes = parsed.topNotes
        middleNotes = parsed.middleNotes
        baseNotes = parsed.baseNotes
        
        // DEBUG: Log parsing for first scent
        if (originalIndex === 1) { // Skip header row at index 0
          console.log(`Parsed scent '${name}':`)
          console.log('  allNotes:', allNotes)
          console.log('  topNotes:', topNotes)
          console.log('  middleNotes:', middleNotes)
          console.log('  baseNotes:', baseNotes)
        }
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
    .filter(scent => scent !== null) // Remove rows that were marked as empty

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
  // Get all keys from the row
  const rowKeys = Object.keys(row)
  
  // Try exact matches first
  for (const name of possibleNames) {
    if (row[name] !== undefined && row[name] !== null) {
      return String(row[name])
    }
  }
  
  // Try case-insensitive exact matches
  for (const rowKey of rowKeys) {
    for (const possibleName of possibleNames) {
      if (rowKey.toLowerCase() === possibleName.toLowerCase()) {
        if (row[rowKey] !== undefined && row[rowKey] !== null) {
          return String(row[rowKey])
        }
      }
    }
  }
  
  // Try partial/fuzzy matches for cases like "Fragrance Notes (top, middle, base)" or "Scent Name"
  // Check if possibleName is CONTAINED IN rowKey
  for (const rowKey of rowKeys) {
    for (const possibleName of possibleNames) {
      const lowerRowKey = rowKey.toLowerCase()
      const lowerPossibleName = possibleName.toLowerCase()
      // Match if possible name is contained in row key
      if (lowerRowKey.includes(lowerPossibleName)) {
        if (row[rowKey] !== undefined && row[rowKey] !== null) {
          return String(row[rowKey])
        }
      }
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

/**
 * Extract unique essential oils from scents data
 * Handles comma-separated oil names, removes duplicates and empty values
 * Example: "lemon, fir needle, gurjun balsam" → [{name: 'lemon'}, {name: 'fir needle'}, {name: 'gurjun balsam'}]
 * @param {Array} scents - Array of scent objects (from parseScentsFile or mapToScentObjects)
 * @returns {Array} Array of oil objects {name, status, description}
 */
export const extractEssentialOils = (scents) => {
  const oilSet = new Set()

  scents.forEach(scent => {
    if (scent.essentialOils && scent.essentialOils.trim()) {
      // Split by comma and process each oil
      const oils = scent.essentialOils.split(',')
        .map(oil => oil.trim())
        .filter(oil => oil.length > 0)

      oils.forEach(oil => {
        oilSet.add(oil)
      })
    }
  })

  // Convert set to array of oil objects
  const uniqueOils = Array.from(oilSet).map(oilName => ({
    name: oilName,
    status: 'active',
    description: `Imported from scent library`,
    supplierId: null // Will be set by user if needed
  }))

  return uniqueOils
}

/**
 * Validate parsed oils data
 * @param {Array} oils - Array of oil objects
 * @returns {Object} {valid: boolean, errors: Array<string>}
 */
export const validateOils = (oils) => {
  const errors = []

  if (!Array.isArray(oils)) {
    return { valid: false, errors: ['Oils data must be an array'] }
  }

  oils.forEach((oil, index) => {
    if (!oil.name || !oil.name.trim()) {
      errors.push(`Row ${index + 1}: Oil name is required`)
    }

    if (oil.name && oil.name.length > 255) {
      errors.push(`Row ${index + 1}: Oil name is too long (max 255 characters)`)
    }
  })

  return {
    valid: errors.length === 0,
    errors
  }
}
