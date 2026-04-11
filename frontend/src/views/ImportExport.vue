<template>
  <div class="import-export">
    <div class="view-header">
      <h2>📤 Import / Export</h2>
      <p>Upload scent data from Excel or download your library as CSV</p>
    </div>



    <div class="sections">
      <!-- Import Section -->
      <div class="section import-section">
        <h3>📥 Import Scents from Excel</h3>
        <div class="instructions">
          <p><strong>Supported format:</strong> .xlsx, .xls, .csv</p>
          <p><strong>Required columns:</strong> Name, Top Notes, Middle Notes, Base Notes</p>
          <p><strong>Optional columns:</strong> Essential Oils - will be automatically added to your Essential Oils library</p>
          <p><strong>Note:</strong> If you have combined fragrance notes (like "citrus, vanilla, musk"), they will be intelligently split into top, middle, and base notes.</p>
          <table class="example-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Top Notes</th>
                <th>Middle Notes</th>
                <th>Base Notes</th>
                <th>Supplier</th>
                <th>Essential Oils</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Rose Elegance</td>
                <td>Bergamot, Lemon</td>
                <td>Rose, Jasmine</td>
                <td>Sandalwood, Musk</td>
                <td>Global Florals Inc</td>
                <td>rose oil, sandalwood oil</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="upload-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleFileDrop">
          <input
            ref="fileInput"
            type="file"
            accept=".xlsx,.xls,.csv"
            style="display: none"
            @change="handleFileSelect"
          />
          <div class="upload-content">
            <span class="upload-icon">📁</span>
            <p>Click to select or drag and drop your file here</p>
            <p class="small">Maximum file size: 10MB</p>
          </div>
        </div>

        <div v-if="uploadStatus" :class="`status status-${uploadStatus.type}`" style="white-space: pre-wrap; word-break: break-word;">
          {{ uploadStatus.message }}
        </div>

        <button
          v-if="selectedFile"
          :disabled="uploading"
          class="btn btn-primary"
          @click="handleImport"
        >
          {{ uploading ? 'Importing...' : 'Import Data' }}
        </button>
      </div>

      <!-- Export Section -->
      <div class="section export-section">
        <h3>📤 Export Scents as CSV</h3>
        <div class="instructions">
          <p>Download your complete scent library with all fragrance details.</p>
          <p>The CSV file will include:</p>
          <ul>
            <li>Scent name and formulas (top, middle, base notes)</li>
            <li>Associated essential oils</li>
            <li>Creation date and creator</li>
          </ul>
        </div>

        <div class="export-options">
          <label>
            <input v-model="exportFormat" type="radio" value="csv" />
            CSV (.csv)
          </label>
          <label>
            <input v-model="exportFormat" type="radio" value="json" />
            JSON (.json)
          </label>
        </div>

        <button class="btn btn-primary" @click="handleExport">
          📥 Download {{ exportFormat.toUpperCase() }}
        </button>

        <div v-if="exportMessage" :class="`status status-${exportMessage.type}`">
          {{ exportMessage.message }}
        </div>
      </div>
    </div>

    <!-- Import History -->
    <div class="import-history">
      <h3>📊 Recent Imports</h3>
      <div v-if="importHistory.length > 0" class="history-table">
        <table>
          <thead>
            <tr>
              <th>File Name</th>
              <th>Records</th>
              <th>Status</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in importHistory" :key="idx">
              <td>{{ item.filename }}</td>
              <td>{{ item.rows }}</td>
              <td>
                <span :class="`badge badge-${item.status.toLowerCase()}`">
                  {{ item.status }}
                </span>
              </td>
              <td>{{ item.date }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="empty-state">
        <p>No imports yet.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useScentStore } from '../stores/scents'
import { useEssentialOilStore } from '../stores/essential-oils'
import { parseScentsFile, validateScents, extractEssentialOils, validateOils } from '../utils/fileParser'
import axios from 'axios'

const authStore = useAuthStore()
const scentStore = useScentStore()
const essentialOilStore = useEssentialOilStore()

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const fileInput = ref(null)
const selectedFile = ref(null)
const uploading = ref(false)
const uploadStatus = ref(null)
const exportFormat = ref('csv')
const exportMessage = ref(null)
const importHistory = ref([
  {
    filename: 'scents_batch_01.xlsx',
    rows: 12,
    status: 'Success',
    date: '2025-02-10'
  },
  {
    filename: 'new_formulas.csv',
    rows: 5,
    status: 'Success',
    date: '2025-02-05'
  }
])

onMounted(async () => {
  // Fetch essential oils on component load to ensure store is populated
  if (essentialOilStore.oils.length === 0) {
    try {
      await essentialOilStore.fetchOils()
    } catch (err) {
      console.warn('Failed to fetch essential oils on mount:', err)
    }
  }
})

const triggerFileInput = () => {
  fileInput.value.click()
}

const handleFileDrop = (e) => {
  const files = e.dataTransfer.files
  if (files.length > 0) {
    selectedFile.value = files[0]
  }
}

const handleFileSelect = (e) => {
  selectedFile.value = e.target.files[0]
}

const handleImport = async () => {
  if (!selectedFile.value) return

  uploading.value = true
  uploadStatus.value = null

  try {
    // Parse file
    console.log(`Parsing file: ${selectedFile.value.name}`)
    const parsed = await parseScentsFile(selectedFile.value)

    // Validate parsed data
    const validation = validateScents(parsed)
    if (!validation.valid) {
      const errorMsg = validation.errors.join('\n')
      throw new Error(`Validation failed:\n${errorMsg}`)
    }

    console.log(`Successfully parsed ${parsed.length} scents`)
    console.log('All parsed scents:', JSON.stringify(parsed, null, 2))

    // Extract essential oils
    console.log('Extracting essential oils from scents...')
    const oils = extractEssentialOils(parsed)
    const oilValidation = validateOils(oils)
    if (!oilValidation.valid) {
      console.warn('Oil validation warnings:', oilValidation.errors)
    }
    console.log(`Extracted ${oils.length} unique oils:`, oils)

    // Create essential oils first
    let createdOilsCount = 0
    let oilCreationErrors = []
    if (oils.length > 0) {
      console.log('Creating essential oils...')
      for (const oil of oils) {
        try {
          await essentialOilStore.addOil(oil)
          createdOilsCount++
          console.log(`Created oil: ${oil.name}`)
        } catch (err) {
          oilCreationErrors.push(`Failed to create oil "${oil.name}": ${err.message}`)
          console.warn(`Error creating oil "${oil.name}":`, err)
        }
      }
    }

    // Send parsed scents directly to backend (bypass preview modal)
    console.log('Sending scents to backend import endpoint...')
    const response = await axios.post(
      `${API_URL}/scents/import`,
      {
        scents: parsed,
        filename: selectedFile.value.name,
        filesize: selectedFile.value.size
      },
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      }
    )

    // Handle API response
    const result = response.data
    const importedCount = result.imported !== undefined ? result.imported : 0
    const errors = result.errors || []

    console.log('Import result:', { importedCount, totalRows: parsed.length, errors })

    // Refresh scents from store/API
    console.log('Fetching scents after import...')
    try {
      await scentStore.fetchScents()
      console.log('Scents after fetch:', scentStore.scents.length, 'scents loaded')
    } catch (err) {
      console.warn('Failed to fetch scents after import:', err)
    }

    // Add to import history
    importHistory.value.unshift({
      filename: selectedFile.value.name,
      rows: importedCount,
      status: errors.length > 0 ? 'Partial' : 'Success',
      date: new Date().toISOString().split('T')[0]
    })

    // Show success message
    let message = `✅ Successfully imported ${importedCount} scents`
    if (createdOilsCount > 0) {
      message += ` and added ${createdOilsCount} essential oils`
    }
    if (errors.length > 0) {
      message += `\n⚠️ ${errors.length} rows had issues:\n`
      message += errors.slice(0, 3).map(e => `  • ${e}`).join('\n')
      if (errors.length > 3) {
        message += `\n  ... and ${errors.length - 3} more`
      }
      console.warn('Import errors:', errors)
    }
    if (oilCreationErrors.length > 0) {
      message += `\n⚠️ ${oilCreationErrors.length} oils had issues`
      console.warn('Oil creation errors:', oilCreationErrors)
    }

    uploadStatus.value = {
      type: errors.length > 0 ? 'warning' : 'success',
      message
    }

    // Clear state
    selectedFile.value = null
    if (fileInput.value) fileInput.value.value = ''

  } catch (error) {
    console.error('Import error:', error)

    let errorMsg = error.message
    if (error.response?.data?.error) {
      errorMsg = error.response.data.error
    } else if (error.response?.data?.details) {
      errorMsg = error.response.data.details
    }

    uploadStatus.value = {
      type: 'error',
      message: `❌ Import failed: ${errorMsg}`
    }
  } finally {
    uploading.value = false
  }
}

const handleExport = () => {
  const scents = scentStore.scents.filter(s => !s.archivedAt)

  if (exportFormat.value === 'csv') {
    exportAsCSV(scents)
  } else {
    exportAsJSON(scents)
  }

  exportMessage.value = {
    type: 'success',
    message: `✅ Downloaded scent_library.${exportFormat.value}`
  }

  setTimeout(() => {
    exportMessage.value = null
  }, 3000)
}

const exportAsCSV = (scents) => {
  const headers = ['Name', 'Top Notes', 'Middle Notes', 'Base Notes', 'Created By', 'Date']
  const rows = scents.map(s => [
    s.name,
    s.topNotes,
    s.middleNotes,
    s.baseNotes,
    s.createdBy,
    s.createdAt
  ])

  const csv = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n')

  downloadFile(csv, 'scent_library.csv', 'text/csv')
}

const exportAsJSON = (scents) => {
  const json = JSON.stringify(scents, null, 2)
  downloadFile(json, 'scent_library.json', 'application/json')
}

const downloadFile = (content, filename, type) => {
  const blob = new Blob([content], { type })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}
</script>

<style scoped>
.import-export {
  padding: 30px;
}

.view-header {
  margin-bottom: 30px;
}

.view-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #333;
}

.view-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.sections {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 40px;
}

.section {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #333;
}

.instructions {
  background: #f9f9f9;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #666;
}

.instructions p {
  margin: 6px 0;
}

.instructions ul {
  margin: 8px 0;
  padding-left: 20px;
}

.instructions li {
  margin: 4px 0;
}

.example-table {
  width: 100%;
  margin-top: 8px;
  border-collapse: collapse;
  font-size: 12px;
}

.example-table th,
.example-table td {
  border: 1px solid #ddd;
  padding: 6px 8px;
  text-align: left;
}

.example-table th {
  background: #f0f0f0;
  font-weight: 600;
}

.upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 32px 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 16px;
  background: #fafafa;
}

.upload-area:hover {
  border-color: #667eea;
  background: #f0f3ff;
}

.upload-icon {
  font-size: 32px;
  display: block;
  margin-bottom: 8px;
}

.upload-content p {
  margin: 4px 0;
  color: #666;
}

.upload-content .small {
  font-size: 12px;
  color: #999;
}

.status {
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 16px;
  font-size: 14px;
}

.status-success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.status-error {
  background: #f8d7da;
  color: #842029;
  border: 1px solid #f5c6cb;
}

.export-options {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.export-options label {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5568d3;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.import-history {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.import-history h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #333;
}

.history-table {
  overflow-x: auto;
}

.history-table table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.history-table th,
.history-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.history-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.history-table tbody tr:hover {
  background: #f9f9f9;
}

.badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge-success {
  background: #d4edda;
  color: #155724;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: #999;
}

@media (max-width: 768px) {
  .sections {
    grid-template-columns: 1fr;
  }

  .section {
    padding: 16px;
  }

  .upload-area {
    padding: 20px 12px;
  }

  .btn {
    width: 100%;
  }
}
</style>
