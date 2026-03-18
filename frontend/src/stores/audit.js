import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuditStore = defineStore('audit', () => {
  const auditLogs = ref([
    {
      id: 1,
      userId: 1,
      userName: 'admin@t4scents.com',
      action: 'CREATE',
      tableName: 'scents',
      recordId: 1,
      recordName: 'Rose Elegance',
      details: 'Created new scent formula',
      timestamp: '2025-01-15 10:30:00'
    },
    {
      id: 2,
      userId: 2,
      userName: 'manager@t4scents.com',
      action: 'UPDATE',
      tableName: 'ingredients',
      recordId: 1,
      recordName: 'Rose Oil',
      details: 'Updated cost and storage location',
      timestamp: '2025-01-20 14:15:00'
    },
    {
      id: 3,
      userId: 1,
      userName: 'admin@t4scents.com',
      action: 'CREATE',
      tableName: 'suppliers',
      recordId: 1,
      recordName: 'Global Florals Inc',
      details: 'Added new supplier partner',
      timestamp: '2025-01-22 09:45:00'
    },
    {
      id: 4,
      userId: 2,
      userName: 'manager@t4scents.com',
      action: 'DELETE',
      tableName: 'scents',
      recordId: 2,
      recordName: 'Old Formula',
      details: 'Archived outdated scent',
      timestamp: '2025-02-05 16:20:00'
    }
  ])

  const filterAction = ref('')
  const filterTable = ref('')
  const filterUser = ref('')

  const filteredAuditLogs = computed(() => {
    return auditLogs.value.filter(log => {
      const matchesAction = !filterAction.value || log.action === filterAction.value
      const matchesTable = !filterTable.value || log.tableName === filterTable.value
      const matchesUser = !filterUser.value || log.userName.includes(filterUser.value)
      return matchesAction && matchesTable && matchesUser
    })
  })

  const addAuditLog = (log) => {
    const newLog = {
      id: Math.max(...auditLogs.value.map(l => l.id), 0) + 1,
      ...log,
      timestamp: new Date().toLocaleString()
    }
    auditLogs.value.unshift(newLog) // Add to front
    return newLog
  }

  const setFilterAction = (action) => {
    filterAction.value = action
  }

  const setFilterTable = (table) => {
    filterTable.value = table
  }

  const setFilterUser = (user) => {
    filterUser.value = user
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
    addAuditLog,
    setFilterAction,
    setFilterTable,
    setFilterUser,
    getUniqueTables,
    getUniqueUsers,
    getUniqueActions
  }
})
