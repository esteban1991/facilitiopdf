<template>
  <div class="flex h-screen bg-gray-100 overflow-hidden">
    <!-- ── SIDEBAR ── -->
    <aside class="w-64 bg-slate-900 flex flex-col flex-shrink-0 shadow-xl">
      <div class="p-5 border-b border-slate-700">
        <h1 class="text-white text-lg font-bold tracking-wide">FacilitioPDF</h1>
        <p class="text-slate-400 text-xs mt-0.5">Invoice Generator</p>
      </div>

      <div class="p-3">
        <button
          @click="createNew"
          class="w-full bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium py-2 px-3 rounded-lg transition-colors"
        >
          + New Invoice
        </button>
      </div>

      <nav class="flex-1 overflow-y-auto p-2">
        <div v-if="loadingList" class="text-slate-400 text-xs text-center py-6">
          Loading…
        </div>
        <div v-else-if="invoices.length === 0" class="text-slate-500 text-xs text-center py-6">
          No invoices yet
        </div>
        <button
          v-for="inv in invoices"
          :key="inv.id"
          @click="loadInvoice(inv.id)"
          class="w-full text-left rounded-lg px-3 py-2.5 mb-1 transition-colors"
          :class="
            currentId === inv.id
              ? 'bg-indigo-600 text-white'
              : 'text-slate-300 hover:bg-slate-800'
          "
        >
          <div class="flex justify-between items-center">
            <span class="text-xs font-semibold opacity-70">#{{ inv.invoice_number }}</span>
            <span class="text-xs opacity-70">{{ inv.currency }}{{ inv.total }}</span>
          </div>
          <div class="text-sm font-medium truncate mt-0.5">
            {{ inv.client_name || "No client" }}
          </div>
          <div class="text-xs opacity-50 mt-0.5">{{ inv.invoice_date }}</div>
        </button>
      </nav>

      <!-- Bottom links -->
      <div class="p-3 border-t border-slate-700 space-y-1">
        <button
          @click="showClients = true"
          class="w-full text-slate-400 hover:text-white text-xs py-1.5 transition-colors text-left px-1"
        >
          👥 Clients
        </button>
        <button
          @click="showSettings = true"
          class="w-full text-slate-400 hover:text-white text-xs py-1.5 transition-colors text-left px-1"
        >
          ⚙ Sender Profile
        </button>
      </div>
    </aside>

    <!-- ── MAIN AREA ── -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Top toolbar -->
      <header class="bg-white border-b border-gray-200 px-6 py-3 flex items-center gap-3 flex-shrink-0">
        <div class="flex-1">
          <span v-if="invoice" class="text-gray-700 font-medium text-sm">
            Invoice #{{ invoice.invoice_number }}
            <span class="text-gray-400 font-normal ml-2">{{ invoice.client_name }}</span>
          </span>
          <span v-else class="text-gray-400 text-sm">Select or create an invoice</span>
        </div>

        <template v-if="invoice">
          <span v-if="saveStatus === 'saving'" class="text-xs text-gray-400">Saving…</span>
          <span v-if="saveStatus === 'saved'" class="text-xs text-green-500">Saved ✓</span>
          <span v-if="saveStatus === 'error'" class="text-xs text-red-500">Save failed</span>

          <button
            @click="deleteInvoice"
            class="text-xs text-red-400 hover:text-red-600 px-3 py-1.5 rounded border border-red-200 hover:border-red-400 transition-colors"
          >
            Delete
          </button>
          <button
            v-if="invoice.id"
            @click="duplicateInvoice"
            class="text-xs text-gray-500 hover:text-gray-700 px-3 py-1.5 rounded border border-gray-200 hover:border-gray-400 transition-colors"
          >
            Duplicate
          </button>
          <button
            @click="saveInvoice"
            :disabled="saving"
            class="bg-slate-800 hover:bg-slate-700 text-white text-sm font-medium px-4 py-1.5 rounded-lg transition-colors disabled:opacity-50"
          >
            Save
          </button>
          <button
            @click="exportPdf"
            :disabled="exporting"
            class="bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium px-4 py-1.5 rounded-lg transition-colors disabled:opacity-50"
          >
            {{ exporting ? "Exporting…" : "Export PDF" }}
          </button>
        </template>
      </header>

      <!-- Editor + Preview -->
      <div v-if="invoice" class="flex flex-1 min-h-0">
        <!-- Editor panel -->
        <div class="w-96 flex-shrink-0 overflow-y-auto bg-white border-r border-gray-200">
          <InvoiceEditor v-model="invoice" :clients="clients" @logo-uploaded="handleLogoUploaded" />
        </div>

        <!-- Preview panel -->
        <div class="flex-1 overflow-auto bg-gray-100 p-6">
          <div class="mb-3 flex items-center justify-between">
            <span class="text-xs text-gray-500 font-medium uppercase tracking-wider">Live Preview</span>
          </div>
          <div class="flex justify-center">
            <div class="shadow-2xl">
              <InvoicePreview :invoice="invoice" />
            </div>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-else class="flex-1 flex items-center justify-center">
        <div class="text-center">
          <div class="text-6xl mb-4">📄</div>
          <h2 class="text-gray-500 text-lg font-medium mb-2">No invoice selected</h2>
          <p class="text-gray-400 text-sm mb-6">Create a new invoice or select one from the sidebar</p>
          <button
            @click="createNew"
            class="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2.5 rounded-lg text-sm font-medium transition-colors"
          >
            + New Invoice
          </button>
        </div>
      </div>
    </div>

    <!-- ── CLIENTS MODAL ── -->
    <ClientManager
      v-if="showClients"
      @close="showClients = false"
      @updated="fetchClients"
    />

    <!-- ── SETTINGS MODAL ── -->
    <div
      v-if="showSettings"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="showSettings = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center">
          <h2 class="font-semibold text-gray-800">Sender Profile</h2>
          <button @click="showSettings = false" class="text-gray-400 hover:text-gray-600 text-xl leading-none">×</button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="field-label">Your Name / Company</label>
            <input v-model="profile.name" class="field-input" placeholder="Esteban Peralta" />
          </div>
          <div>
            <label class="field-label">Address</label>
            <textarea v-model="profile.address" class="field-input" rows="3" placeholder="Street, City, Country" />
          </div>
          <div>
            <label class="field-label">Default Currency</label>
            <input v-model="profile.default_currency" class="field-input w-24" placeholder="$" />
          </div>
          <div>
            <label class="field-label">Default Terms</label>
            <textarea v-model="profile.default_terms" class="field-input" rows="2" placeholder="Payment due in 15 days" />
          </div>
          <div>
            <label class="field-label">Logo</label>
            <div class="flex items-center gap-3">
              <img v-if="profile.logo_url" :src="profile.logo_url" class="h-16 w-16 object-contain rounded border" />
              <input type="file" accept="image/*" @change="uploadProfileLogo" class="text-sm text-gray-600" />
            </div>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
          <button @click="showSettings = false" class="text-sm text-gray-500 hover:text-gray-700 px-4 py-2">Cancel</button>
          <button @click="saveProfile" class="bg-slate-800 hover:bg-slate-700 text-white text-sm font-medium px-5 py-2 rounded-lg transition-colors">
            Save Profile
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { invoicesApi, profileApi, clientsApi } from "./api/invoices.js";
import InvoiceEditor from "./components/InvoiceEditor.vue";
import InvoicePreview from "./components/InvoicePreview.vue";
import ClientManager from "./components/ClientManager.vue";

// ── State ──────────────────────────────────────────────────
const invoices = ref([]);
const invoice = ref(null);
const currentId = ref(null);
const loadingList = ref(false);
const saving = ref(false);
const saveStatus = ref("");
const exporting = ref(false);
const showSettings = ref(false);
const showClients = ref(false);
const profile = ref({ name: "", address: "", default_currency: "$", default_terms: "", logo_url: "" });
const clients = ref([]);

// ── Init ───────────────────────────────────────────────────
onMounted(async () => {
  await Promise.all([fetchList(), fetchProfile(), fetchClients()]);
});

async function fetchClients() {
  const res = await clientsApi.list();
  clients.value = res.data;
}

async function fetchList() {
  loadingList.value = true;
  try {
    const res = await invoicesApi.list();
    invoices.value = res.data;
  } finally {
    loadingList.value = false;
  }
}

async function fetchProfile() {
  const res = await profileApi.get();
  profile.value = res.data;
}

// ── Invoice CRUD ───────────────────────────────────────────
async function createNew() {
  const numRes = await invoicesApi.nextNumber();
  invoice.value = {
    id: null,
    sender_name: profile.value.name,
    sender_address: profile.value.address,
    sender_logo: null,
    sender_logo_url: profile.value.logo_url,
    client_name: "",
    client_phone: "",
    client_email: "",
    client_address: "",
    invoice_number: numRes.data.next_number,
    invoice_date: new Date().toISOString().split("T")[0],
    currency: profile.value.default_currency || "$",
    terms: profile.value.default_terms || "",
    items: [{ id: null, description: "", hours: null, rate: null, amount: 0, order: 0 }],
    total: 0,
  };
  currentId.value = null;
}

async function loadInvoice(id) {
  const res = await invoicesApi.get(id);
  invoice.value = res.data;
  currentId.value = id;
}

async function saveInvoice() {
  if (!invoice.value) return;
  saving.value = true;
  saveStatus.value = "saving";
  try {
    const payload = buildPayload();
    let res;
    if (invoice.value.id) {
      res = await invoicesApi.update(invoice.value.id, payload);
    } else {
      res = await invoicesApi.create(payload);
    }
    invoice.value = { ...invoice.value, ...res.data };
    currentId.value = res.data.id;
    saveStatus.value = "saved";
    await Promise.all([fetchList(), autoCreateClient()]);
    setTimeout(() => (saveStatus.value = ""), 2500);
  } catch {
    saveStatus.value = "error";
  } finally {
    saving.value = false;
  }
}

async function autoCreateClient() {
  const name = invoice.value?.client_name?.trim();
  if (!name) return;
  const exists = clients.value.some(
    (c) => c.name.toLowerCase() === name.toLowerCase()
  );
  if (!exists) {
    await clientsApi.create({
      name,
      phone: invoice.value.client_phone || "",
      email: invoice.value.client_email || "",
      address: invoice.value.client_address || "",
    });
    await fetchClients();
  }
}

async function duplicateInvoice() {
  if (!invoice.value?.id) return;
  const res = await invoicesApi.duplicate(invoice.value.id);
  invoice.value = res.data;
  currentId.value = res.data.id;
  await fetchList();
}

async function deleteInvoice() {
  if (!invoice.value?.id) {
    invoice.value = null;
    return;
  }
  if (!confirm(`Delete Invoice #${invoice.value.invoice_number}?`)) return;
  await invoicesApi.delete(invoice.value.id);
  invoice.value = null;
  currentId.value = null;
  await fetchList();
}

function buildPayload() {
  const { id, total, created_at, updated_at, sender_logo, sender_logo_url, ...rest } = invoice.value;
  return rest;
}

// ── Logo upload ────────────────────────────────────────────
async function handleLogoUploaded(file) {
  // Auto-save first if invoice not yet persisted
  if (!invoice.value?.id) {
    await saveInvoice();
  }
  if (!invoice.value?.id) return; // save failed
  const res = await invoicesApi.uploadLogo(invoice.value.id, file);
  invoice.value.sender_logo_url = res.data.sender_logo_url;
}

// ── PDF Export ─────────────────────────────────────────────
async function exportPdf() {
  exporting.value = true;
  try {
    if (!invoice.value?.id) {
      await saveInvoice();
    }
    // Use backend PDF (WeasyPrint)
    const res = await invoicesApi.downloadPdf(invoice.value.id);
    const url = URL.createObjectURL(res.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = `invoice-${invoice.value.invoice_number}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  } catch (err) {
    console.warn("Backend PDF failed, using client-side fallback:", err);
    await clientSidePdf();
  } finally {
    exporting.value = false;
  }
}

async function clientSidePdf() {
  const { default: html2pdf } = await import("html2pdf.js");
  const el = document.querySelector(".invoice-preview-page");
  if (!el) return;

  // Wrap clone in an off-screen container so overflow:hidden parent doesn't clip it
  const offscreen = document.createElement("div");
  offscreen.style.cssText =
    "position:absolute;left:-9999px;top:0;width:794px;background:white;overflow:visible;";

  const clone = el.cloneNode(true);
  // Reset all inline positioning/scaling so html2canvas sees full content
  clone.style.transform = "none";
  clone.style.position = "static";
  clone.style.top = "auto";
  clone.style.left = "auto";
  clone.style.width = "794px";
  clone.style.minHeight = "1123px";

  offscreen.appendChild(clone);
  document.body.appendChild(offscreen);

  try {
    await html2pdf()
      .set({
        margin: 0,
        filename: `invoice-${invoice.value.invoice_number}.pdf`,
        image: { type: "jpeg", quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { unit: "px", format: [794, 1123], orientation: "portrait" },
      })
      .from(offscreen)
      .save();
  } finally {
    document.body.removeChild(offscreen);
  }
}

// ── Profile ────────────────────────────────────────────────
async function saveProfile() {
  const fd = new FormData();
  fd.append("name", profile.value.name);
  fd.append("address", profile.value.address);
  fd.append("default_currency", profile.value.default_currency);
  fd.append("default_terms", profile.value.default_terms);
  const res = await profileApi.update(fd);
  profile.value = res.data;
  showSettings.value = false;
}

async function uploadProfileLogo(e) {
  const file = e.target.files[0];
  if (!file) return;
  const fd = new FormData();
  fd.append("logo", file);
  const res = await profileApi.update(fd);
  profile.value = res.data;
}
</script>

<style>
.field-label {
  @apply block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1;
}
.field-input {
  @apply w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400 transition-colors;
}
</style>
