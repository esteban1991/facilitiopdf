<template>
  <div
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    @click.self="$emit('close')"
  >
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl mx-4 overflow-hidden flex flex-col" style="max-height: 80vh">
      <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center flex-shrink-0">
        <h2 class="font-semibold text-gray-800">Clients</h2>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 text-xl leading-none">×</button>
      </div>

      <div class="flex flex-1 min-h-0">
        <!-- List -->
        <div class="w-64 border-r border-gray-100 flex flex-col flex-shrink-0">
          <div class="p-3 flex-shrink-0">
            <button
              @click="startNew"
              class="w-full bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium py-2 px-3 rounded-lg transition-colors"
            >
              + New Client
            </button>
          </div>
          <div class="overflow-y-auto flex-1">
            <div v-if="clients.length === 0" class="text-gray-400 text-xs text-center py-6">No clients yet</div>
            <button
              v-for="c in clients"
              :key="c.id"
              @click="editClient(c)"
              class="w-full text-left px-4 py-3 border-b border-gray-50 hover:bg-gray-50 transition-colors"
              :class="editing?.id === c.id ? 'bg-indigo-50 border-l-2 border-l-indigo-500' : ''"
            >
              <div class="text-sm font-medium text-gray-800 truncate">{{ c.name }}</div>
              <div class="text-xs text-gray-400 mt-0.5 truncate">{{ c.email || c.phone || '—' }}</div>
            </button>
          </div>
        </div>

        <!-- Form -->
        <div class="flex-1 p-6 overflow-y-auto">
          <div v-if="!editing" class="flex items-center justify-center h-full text-gray-300 text-sm select-none">
            Select a client to edit or create a new one
          </div>
          <div v-else class="space-y-4">
            <h3 class="text-xs font-bold text-gray-400 uppercase tracking-widest">
              {{ editing.id ? 'Edit Client' : 'New Client' }}
            </h3>
            <div>
              <label class="field-label">Name *</label>
              <input v-model="editing.name" class="field-input" placeholder="ACME Corp" />
            </div>
            <div>
              <label class="field-label">Email</label>
              <input v-model="editing.email" type="email" class="field-input" placeholder="contact@acme.com" />
            </div>
            <div>
              <label class="field-label">Phone</label>
              <input v-model="editing.phone" class="field-input" placeholder="+56 2 2234 5678" />
            </div>
            <div>
              <label class="field-label">Address</label>
              <textarea v-model="editing.address" class="field-input" rows="3" placeholder="Street, City, Country" />
            </div>
            <div v-if="error" class="text-xs text-red-500">{{ error }}</div>
            <div class="flex justify-between pt-2">
              <button
                v-if="editing.id"
                @click="deleteClient"
                class="text-xs text-red-400 hover:text-red-600 px-3 py-1.5 rounded border border-red-200 hover:border-red-400 transition-colors"
              >
                Delete
              </button>
              <div v-else></div>
              <div class="flex gap-2">
                <button @click="editing = null; error = ''" class="text-sm text-gray-500 hover:text-gray-700 px-4 py-2">
                  Cancel
                </button>
                <button
                  @click="saveClient"
                  class="bg-slate-800 hover:bg-slate-700 text-white text-sm font-medium px-5 py-2 rounded-lg transition-colors"
                >
                  Save
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { clientsApi } from "../api/invoices.js";

const emit = defineEmits(["close", "updated"]);

const clients = ref([]);
const editing = ref(null);
const error = ref("");

onMounted(fetchClients);

async function fetchClients() {
  const res = await clientsApi.list();
  clients.value = res.data;
}

function startNew() {
  editing.value = { id: null, name: "", email: "", phone: "", address: "" };
  error.value = "";
}

function editClient(c) {
  editing.value = { ...c };
  error.value = "";
}

async function saveClient() {
  if (!editing.value.name.trim()) {
    error.value = "Name is required.";
    return;
  }
  if (editing.value.id) {
    await clientsApi.update(editing.value.id, editing.value);
  } else {
    await clientsApi.create(editing.value);
  }
  editing.value = null;
  error.value = "";
  await fetchClients();
  emit("updated");
}

async function deleteClient() {
  if (!confirm(`Delete client "${editing.value.name}"?`)) return;
  await clientsApi.delete(editing.value.id);
  editing.value = null;
  await fetchClients();
  emit("updated");
}
</script>

<style scoped>
.field-label {
  @apply block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1;
}
.field-input {
  @apply w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400 transition-colors;
}
</style>
