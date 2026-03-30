import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

export const useAuditStore = defineStore('audit', () => {
  const auditLogs = ref([])
  const filterAction = ref('')
  const filterTable = ref('')
  const filterUser = ref('')
  const loading = ref(false)
  const error = ref(null)

  const filteredAuditLogs = computed(() => {
    return auditLogs.value.filter(log => {
      const matchesAction = !filterAction.value || log.action === filterAction.value
      const matchesTable = !filterTable.value || log.tableName === filterTable.value
      const matchesUser = !filterUser.value || log.userName.includes(filterUser.value)
      return matchesAction && matchesTable && matchesUser
    })
  })

  const fetchAuditLogs = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await axios.get(`${API_URL}/audit-logs`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      })
      auditLogs.value = response.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to fetch audit logs'
      console.error('Fetch audit logs error:', err)
    } finally {
      loading.value = false
    }
  }

  const filterAuditLogs = async () => {
    try {
      loading.value = true
      error.value = null
      const params = new URLSearchParams()
      if (filterAction.value) params.append('action', filterAction.value)
      if (filterTable.value) params.append('table', filterTable.value)
      if (filterUser.value) params.append('user', filterUser.value)
      
      const response = await axios.get(`${API_URL}/audit-logs/filter?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      })
      auditLogs.value = response.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to filter audit logs'
      console.error('Filter audit logs error:', err)
    } finally {
      loading.value = false
    }
  }

  const setFilterAction = (action) => {
    filterAction.value = action
    filterAuditLogs()
  }

  const setFilterTable = (table) => {
    filterTable.value = table
    filterAuditLogs()
  }

  const setFilterUser = (user) => {
    filterUser.value = user
    filterAuditLogs()
  }

  const getUniqueTables = () => {
    return [...new Set(auditLogs.value.map(log => log.tableName))]
  }

  const getUniqueUsers = () => {
    return [...new Set(auditLogs.value.map(log => log.userName))]
  }

  const getUniqueActions = () => {
    return [...new Set(auditLogs.value.map(log => log.action))]
  }

  return {
    auditLogs,
    filteredAuditLogs,
    filterAction,
    filterTable,
    filterUser,
    loading,
    error,
    fetchAuditLogs,
    filterAuditLogs,
    setFilterAction,
    setFilterTable,
    setFilterUser,
    getUniqueTables,
    getUniqueUsers,
    getUniqueActions
  }
})
