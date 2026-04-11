<template>
  <div class="import-export">
    <div class="breadcrumb">
      <router-link to="/dashboard" class="bc-back">← Dashboard</router-link>
      <span class="bc-sep">/</span>
      <span class="bc-current">Import / Export</span>
    </div>
    <div class="view-header">
      <div class="view-header-left">
        <h2>Import / Export</h2>
        <p>Upload scent data from Excel or download your library as CSV</p>
      </div>
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
.import-export { font-family: var(--font-sans); }

.sections { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
@media (max-width: 768px) { .sections { grid-template-columns: 1fr; } }

.section {
  background: var(--white); border-radius: 12px; padding: 22px 24px;
  border: 1px solid var(--cream-mid);
}
.section h3 {
  font-size: 13px; font-weight: 700; color: var(--brown);
  letter-spacing: 0.06em; text-transform: uppercase; margin: 0 0 16px;
}

.instructions { margin-bottom: 16px; font-size: 12.5px; color: var(--brown-md); line-height: 1.7; }
.instructions strong { color: var(--brown); }

.example-table { width: 100%; border-collapse: collapse; font-size: 11px; margin-top: 8px; }
.example-table th {
  background: var(--cream); padding: 6px 10px; text-align: left;
  font-size: 10px; font-weight: 700; color: var(--brown-lt);
  letter-spacing: 0.1em; text-transform: uppercase;
  border: 1px solid var(--cream-mid);
}
.example-table td { padding: 6px 10px; border: 1px solid var(--cream-mid); color: var(--brown-md); }

.upload-area {
  border: 2px dashed var(--cream-dk); border-radius: 12px;
  padding: 32px 20px; text-align: center; cursor: pointer;
  transition: all .2s; background: var(--cream); margin-bottom: 14px;
}
.upload-area:hover { border-color: var(--gold); background: rgba(201,160,72,0.04); }
.upload-icon { font-size: 32px; display: block; margin-bottom: 10px; }
.upload-content p { margin: 4px 0; font-size: 13px; color: var(--brown-md); }
.upload-content .small { font-size: 11px; color: var(--brown-lt); }

.status { padding: 10px 14px; border-radius: 8px; font-size: 12.5px; margin-bottom: 12px; }
.status-success { background: rgba(74,124,89,0.1); color: var(--green); border: 1px solid rgba(74,124,89,0.2); }
.status-error   { background: rgba(155,58,58,0.1); color: var(--red);   border: 1px solid rgba(155,58,58,0.2); }
.status-warning { background: rgba(201,160,72,0.1); color: var(--gold-dk); border: 1px solid rgba(201,160,72,0.2); }

.export-options { display: flex; flex-direction: column; gap: 10px; margin-bottom: 16px; }
.export-option {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 14px; border-radius: 10px;
  border: 1.5px solid var(--cream-mid); background: var(--cream); cursor: pointer;
  transition: all .15s;
}
.export-option:hover { border-color: var(--gold); background: rgba(201,160,72,0.05); }
.export-option.selected { border-color: var(--gold); background: rgba(201,160,72,0.08); }
.option-label { font-size: 13px; font-weight: 600; color: var(--brown); }
.option-desc  { font-size: 11px; color: var(--brown-lt); margin-top: 2px; }
.option-radio { width: 16px; height: 16px; accent-color: var(--gold-dk); }

.import-results { margin-top: 14px; }
.result-item {
  display: flex; justify-content: space-between; padding: 8px 0;
  border-bottom: 1px solid var(--cream-mid); font-size: 12.5px;
}
.result-item:last-child { border-bottom: none; }
.result-key { color: var(--brown-md); }
.result-val { font-weight: 600; color: var(--brown); }
</style>
