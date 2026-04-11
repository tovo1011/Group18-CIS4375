<template>
  <div class="audit-logs">
    <div class="view-header">
      <h2>📋 Audit Logs</h2>
      <p>Track all changes made to scents, ingredients, and suppliers</p>
    </div>

    <div class="filters-section">
      <div class="filter-group">
        <label for="actionFilter">Action:</label>
        <select id="actionFilter" v-model="actionFilter" @change="auditStore.setFilterAction(actionFilter)">
          <option value="">All Actions</option>
          <option value="CREATE">Create</option>
          <option value="UPDATE">Update</option>
          <option value="DELETE">Delete</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="tableFilter">Table:</label>
        <select id="tableFilter" v-model="tableFilter" @change="auditStore.setFilterTable(tableFilter)">
          <option value="">All Tables</option>
          <option value="Scents">Scents</option>
          <option value="Essential_oil">Essential Oils</option>
          <option value="Suppliers">Suppliers</option>
          <option value="import">Imports</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="userFilter">User:</label>
        <input
          id="userFilter"
          v-model="userFilter"
          type="text"
          placeholder="Filter by user email"
          @input="auditStore.setFilterUser(userFilter)"
        />
      </div>
    </div>

    <div class="table-container">
      <table class="logs-table">
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>User</th>
            <th>Action</th>
            <th>Entity</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in auditStore.filteredAuditLogs" :key="log.id" :class="`action-${log.action.toLowerCase()}`">
            <td class="timestamp">{{ new Date(log.timestamp).toLocaleString() }}</td>
            <td class="user">{{ log.userName }}</td>
            <td class="action">
              <span :class="`badge badge-${log.action.toLowerCase()}`">
                {{ log.action }}
              </span>
            </td>
            <td class="table-name">{{ log.tableName }} (ID: {{ log.recordId }})</td>
          </tr>
        </tbody>
      </table>

      <div v-if="auditStore.filteredAuditLogs.length === 0" class="empty-state">
        <p>No audit logs found.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuditStore } from '../stores/audit'

const auditStore = useAuditStore()

const actionFilter = ref('')
const tableFilter = ref('')
const userFilter = ref('')

onMounted(() => {
  auditStore.fetchAuditLogs()
})
</script>

<style scoped>
.audit-logs {
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

.filters-section {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
  background: #f9f9f9;
  padding: 16px;
  border-radius: 8px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-weight: 600;
  color: #333;
  white-space: nowrap;
}

.filter-group input,
.filter-group select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
}

.filter-group input:focus,
.filter-group select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.table-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.logs-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.logs-table thead {
  background: #f8f9fa;
  border-bottom: 1px solid #ddd;
}

.logs-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #333;
}

.logs-table tbody tr {
  border-bottom: 1px solid #eee;
  transition: background 0.2s ease;
}

.logs-table tbody tr:hover {
  background: #f9f9f9;
}

.logs-table td {
  padding: 12px 16px;
}

.timestamp {
  font-family: 'Monaco', 'Courier New', monospace;
  color: #999;
  white-space: nowrap;
}

.user {
  color: #667eea;
  font-weight: 600;
}

.action {
  text-align: center;
}

.badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge-create {
  background: #d4edda;
  color: #155724;
}

.badge-update {
  background: #cfe2ff;
  color: #084298;
}

.badge-delete {
  background: #f8d7da;
  color: #842029;
}

.table-name {
  color: #999;
  text-transform: capitalize;
}

.record-name {
  font-weight: 600;
  color: #333;
}

.details {
  color: #666;
  font-size: 12px;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
  color: #999;
}

@media (max-width: 768px) {
  .filters-section {
    flex-direction: column;
  }

  .filter-group {
    flex-direction: column;
    width: 100%;
  }

  .filter-group label {
    width: 100%;
  }

  .filter-group input,
  .filter-group select {
    width: 100%;
  }

  .logs-table {
    font-size: 11px;
  }

  .logs-table th,
  .logs-table td {
    padding: 8px 10px;
  }

  .timestamp {
    font-size: 10px;
  }
}
</style>
