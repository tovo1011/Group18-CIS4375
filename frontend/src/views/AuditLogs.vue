<template>
  <div class="audit-logs">
    <div class="breadcrumb">
      <router-link to="/dashboard" class="bc-back">← Dashboard</router-link>
      <span class="bc-sep">/</span>
      <span class="bc-current">Audit Logs</span>
    </div>
    <div class="view-header">
      <div class="view-header-left">
        <h2>Audit Logs</h2>
        <p>Track all changes made to scents, ingredients, and suppliers</p>
      </div>
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
          <option value="scents">Scents</option>
          <option value="oils">Essential Oils</option>
          <option value="suppliers">Suppliers</option>
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
            <th>Record</th>
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in auditStore.filteredAuditLogs" :key="log.id" :class="`action-${log.action.toLowerCase()}`">
            <td class="timestamp">{{ log.timestamp }}</td>
            <td class="user">{{ log.userName }}</td>
            <td class="action">
              <span :class="`badge badge-${log.action.toLowerCase()}`">
                {{ log.action }}
              </span>
            </td>
            <td class="table-name">{{ log.tableName }}</td>
            <td class="record-name">{{ log.recordName }}</td>
            <td class="details">{{ log.details }}</td>
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
import { ref } from 'vue'
import { useAuditStore } from '../stores/audit'

const auditStore = useAuditStore()

const actionFilter = ref('')
const tableFilter = ref('')
const userFilter = ref('')
</script>

<style scoped>
.audit-logs { font-family: var(--font-sans); }

.filters-section {
  display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end; margin-bottom: 16px;
}
.filter-group { display: flex; flex-direction: column; gap: 5px; }
.filter-group label {
  font-size: 10px; font-weight: 700; color: var(--brown-md);
  letter-spacing: 0.12em; text-transform: uppercase;
}
.filter-group select,
.filter-group input {
  padding: 8px 12px;
  border: 1.5px solid var(--cream-mid);
  border-radius: 8px;
  font-size: 12.5px;
  color: var(--brown);
  background: var(--white);
  font-family: var(--font-sans);
  outline: none;
}
.filter-group select:focus,
.filter-group input:focus {
  border-color: var(--gold);
  box-shadow: 0 0 0 3px rgba(201,160,72,0.12);
}

.timestamp { font-size: 11px; color: var(--brown-lt); white-space: nowrap; }
.user { font-size: 12px; color: var(--brown-md); }
.record-name { font-weight: 600; color: var(--brown); }
.details { font-size: 11.5px; color: var(--brown-lt); max-width: 240px; }
</style>
