<template>
  <div class="p-5 space-y-5">

    <!-- ── SECTION: Sender ── -->
    <section>
      <h3 class="section-title">From</h3>
      <div class="space-y-3">
        <div>
          <label class="field-label">Your Name</label>
          <input v-model="inv.sender_name" class="field-input" placeholder="Esteban Peralta" />
        </div>
        <div>
          <label class="field-label">Your Address</label>
          <textarea v-model="inv.sender_address" class="field-input" rows="3"
            placeholder="Street, City, Country" />
        </div>
        <div>
          <label class="field-label">Logo</label>
          <div class="flex items-center gap-3">
            <img v-if="inv.sender_logo_url" :src="inv.sender_logo_url"
              class="h-14 w-14 object-contain rounded border border-gray-200" />
            <div v-else
              class="h-14 w-14 rounded border-2 border-dashed border-gray-200 flex items-center justify-center text-gray-300 text-xs">
              logo
            </div>
            <label
              class="cursor-pointer text-xs text-indigo-600 hover:text-indigo-800 font-medium transition-colors">
              Upload
              <input type="file" accept="image/*" class="hidden" @change="onLogoChange" />
            </label>
          </div>
        </div>
      </div>
    </section>

    <hr class="border-gray-100" />

    <!-- ── SECTION: Client ── -->
    <section>
      <h3 class="section-title">Bill To</h3>
      <div class="space-y-3">
        <div>
          <label class="field-label">Client Name</label>
          <input v-model="inv.client_name" class="field-input" placeholder="ACME Corp" />
        </div>
        <div>
          <label class="field-label">Phone</label>
          <input v-model="inv.client_phone" class="field-input" placeholder="+56 2 2234 5678" />
        </div>
        <div>
          <label class="field-label">Email</label>
          <input v-model="inv.client_email" class="field-input" type="email" placeholder="client@example.com" />
        </div>
        <div>
          <label class="field-label">Address</label>
          <textarea v-model="inv.client_address" class="field-input" rows="3"
            placeholder="Street, City, Country" />
        </div>
      </div>
    </section>

    <hr class="border-gray-100" />

    <!-- ── SECTION: Invoice Meta ── -->
    <section>
      <h3 class="section-title">Invoice Details</h3>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="field-label">Invoice #</label>
          <input v-model.number="inv.invoice_number" class="field-input" type="number" min="1" />
        </div>
        <div>
          <label class="field-label">Currency</label>
          <input v-model="inv.currency" class="field-input" placeholder="$" />
        </div>
        <div class="col-span-2">
          <label class="field-label">Invoice Date</label>
          <input v-model="inv.invoice_date" class="field-input" type="date" />
        </div>
      </div>
    </section>

    <hr class="border-gray-100" />

    <!-- ── SECTION: Line Items ── -->
    <section>
      <div class="flex items-center justify-between mb-3">
        <h3 class="section-title mb-0">Line Items</h3>
        <button @click="addItem"
          class="text-xs text-indigo-600 hover:text-indigo-800 font-medium transition-colors">
          + Add Item
        </button>
      </div>

      <div v-for="(item, idx) in inv.items" :key="idx"
        class="bg-gray-50 rounded-xl p-3 mb-2 space-y-2 border border-gray-100">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-gray-400">Item {{ idx + 1 }}</span>
          <button v-if="inv.items.length > 1" @click="removeItem(idx)"
            class="text-red-400 hover:text-red-600 text-xs transition-colors">
            Remove
          </button>
        </div>

        <div>
          <label class="field-label">Description</label>
          <textarea v-model="item.description" class="field-input" rows="4"
            placeholder="Describe the work done…" />
        </div>

        <div class="grid grid-cols-3 gap-2">
          <div>
            <label class="field-label">Hours</label>
            <input v-model.number="item.hours" @input="calcAmount(item)" class="field-input"
              type="number" min="0" step="0.5" placeholder="0" />
          </div>
          <div>
            <label class="field-label">Rate</label>
            <input v-model.number="item.rate" @input="calcAmount(item)" class="field-input"
              type="number" min="0" step="0.01" placeholder="0.00" />
          </div>
          <div>
            <label class="field-label">Amount</label>
            <input v-model.number="item.amount" class="field-input" type="number" min="0"
              step="0.01" placeholder="0.00" />
          </div>
        </div>
      </div>

      <!-- Totals display -->
      <div class="mt-3 flex justify-end">
        <div class="text-sm font-semibold text-gray-700">
          Total: {{ inv.currency }}{{ computedTotal.toFixed(2) }}
        </div>
      </div>
    </section>

    <hr class="border-gray-100" />

    <!-- ── SECTION: Terms ── -->
    <section>
      <h3 class="section-title">Terms &amp; Conditions</h3>
      <textarea v-model="inv.terms" class="field-input" rows="3"
        placeholder="Payment due within 15 days…" />
    </section>

  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({ modelValue: { type: Object, required: true } });
const emit = defineEmits(["update:modelValue", "logo-uploaded"]);

const inv = computed({
  get: () => props.modelValue,
  set: (val) => emit("update:modelValue", val),
});

const computedTotal = computed(() =>
  (inv.value.items || []).reduce((sum, item) => sum + (Number(item.amount) || 0), 0)
);

function addItem() {
  inv.value.items.push({ id: null, description: "", hours: null, rate: null, amount: 0, order: inv.value.items.length });
}

function removeItem(idx) {
  inv.value.items.splice(idx, 1);
}

function calcAmount(item) {
  if (item.hours != null && item.rate != null) {
    item.amount = parseFloat((item.hours * item.rate).toFixed(2));
  }
}

function onLogoChange(e) {
  const file = e.target.files[0];
  if (!file) return;
  // Show local preview immediately
  const reader = new FileReader();
  reader.onload = (ev) => {
    inv.value.sender_logo_url = ev.target.result;
  };
  reader.readAsDataURL(file);
  emit("logo-uploaded", file);
}
</script>

<style scoped>
.section-title {
  @apply text-xs font-bold text-gray-400 uppercase tracking-widest mb-3;
}
.field-label {
  @apply block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1;
}
.field-input {
  @apply w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400 transition-colors bg-white;
}
</style>
