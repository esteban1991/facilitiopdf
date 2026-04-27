<template>
  <div
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    @click.self="$emit('close')"
  >
    <div
      class="bg-white rounded-2xl shadow-2xl w-full max-w-3xl mx-4 flex flex-col"
      style="max-height: 90vh"
    >
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between flex-shrink-0">
        <div>
          <h2 class="font-semibold text-gray-800">Earnings Overview</h2>
          <p v-if="grandTotal > 0" class="text-xs text-gray-400 mt-0.5">
            Total: <span class="font-semibold text-gray-600">{{ fmt(grandTotal * rate) }}</span>
          </p>
        </div>
        <div class="flex items-center gap-4">
          <!-- Currency selector -->
          <div class="flex items-center gap-2">
            <span class="text-xs text-gray-400 font-semibold uppercase tracking-wider">View in</span>
            <div class="flex rounded-lg border border-gray-200 overflow-hidden text-sm">
              <button
                v-for="c in CURRENCIES"
                :key="c.code"
                @click="setCurrency(c.code)"
                class="px-3 py-1.5 transition-colors font-medium"
                :class="
                  selectedCurrency === c.code
                    ? 'bg-indigo-600 text-white'
                    : 'text-gray-500 hover:bg-gray-50'
                "
              >
                {{ c.label }}
              </button>
            </div>
            <span v-if="loadingRate" class="text-xs text-gray-400">...</span>
          </div>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 text-xl leading-none">×</button>
        </div>
      </div>

      <!-- Body -->
      <div class="p-6 overflow-y-auto flex-1 space-y-8">
        <div v-if="loading" class="flex items-center justify-center py-16 text-gray-300 text-sm">
          Loading…
        </div>

        <template v-else-if="grandTotal === 0">
          <div class="flex flex-col items-center justify-center py-16 text-gray-300">
            <div class="text-5xl mb-3">📊</div>
            <p class="text-sm">No invoice data yet</p>
          </div>
        </template>

        <template v-else>
          <!-- Earnings by Year -->
          <section>
            <h3 class="section-label">Earnings by Year</h3>
            <div class="space-y-2.5 mt-3">
              <div
                v-for="row in byYear"
                :key="row.year"
                class="flex items-center gap-3 group"
              >
                <span class="text-sm text-gray-400 font-mono w-10 flex-shrink-0">{{ row.year }}</span>
                <div class="flex-1 bg-gray-100 rounded-full h-7 overflow-hidden relative">
                  <div
                    class="h-full bg-indigo-500 rounded-full flex items-center justify-end pr-2 transition-all duration-700"
                    :style="{ width: pct(row.converted, maxYear) }"
                  >
                    <span
                      v-if="row.converted / maxYear > 0.15"
                      class="text-xs font-semibold text-white/90 whitespace-nowrap"
                    >{{ fmt(row.converted) }}</span>
                  </div>
                </div>
                <span class="text-sm font-semibold text-gray-700 w-28 text-right flex-shrink-0 tabular-nums">
                  {{ fmt(row.converted) }}
                </span>
              </div>
            </div>
          </section>

          <!-- Earnings by Client -->
          <section>
            <h3 class="section-label">Earnings by Client</h3>
            <div class="space-y-2.5 mt-3">
              <div
                v-for="row in byClient"
                :key="row.client_name"
                class="flex items-center gap-3"
              >
                <span
                  class="text-sm text-gray-500 w-36 flex-shrink-0 truncate"
                  :title="row.client_name"
                >{{ row.client_name || '(no name)' }}</span>
                <div class="flex-1 bg-gray-100 rounded-full h-7 overflow-hidden relative">
                  <div
                    class="h-full bg-emerald-500 rounded-full flex items-center justify-end pr-2 transition-all duration-700"
                    :style="{ width: pct(row.converted, maxClient) }"
                  >
                    <span
                      v-if="row.converted / maxClient > 0.2"
                      class="text-xs font-semibold text-white/90 whitespace-nowrap"
                    >{{ fmt(row.converted) }}</span>
                  </div>
                </div>
                <span class="text-sm font-semibold text-gray-700 w-28 text-right flex-shrink-0 tabular-nums">
                  {{ fmt(row.converted) }}
                </span>
              </div>
            </div>
          </section>

          <!-- Rate note -->
          <p v-if="selectedCurrency !== 'USD'" class="text-xs text-gray-300">
            Rate: 1 USD = {{ rate.toLocaleString('en-US', { maximumFractionDigits: 4 }) }} {{ selectedCurrency }} · source: open.er-api.com
          </p>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { statsApi } from "../api/invoices.js";

defineEmits(["close"]);

const CURRENCIES = [
  { code: "USD", label: "USD $", symbol: "$", decimals: 2 },
  { code: "EUR", label: "EUR €", symbol: "€", decimals: 2 },
  { code: "JPY", label: "JPY ¥", symbol: "¥", decimals: 0 },
  { code: "CLP", label: "CLP $", symbol: "$", decimals: 0 },
];

const loading = ref(true);
const loadingRate = ref(false);
const rawByYear = ref([]);
const rawByClient = ref([]);
const grandTotal = ref(0);
const selectedCurrency = ref("USD");
const rate = ref(1);
const ratesCache = {};

onMounted(async () => {
  const res = await statsApi.get();
  rawByYear.value = res.data.by_year;
  rawByClient.value = res.data.by_client;
  grandTotal.value = Number(res.data.grand_total) || 0;
  loading.value = false;
});

async function setCurrency(code) {
  if (code === selectedCurrency.value) return;
  selectedCurrency.value = code;
  if (code === "USD") { rate.value = 1; return; }
  if (ratesCache[code]) { rate.value = ratesCache[code]; return; }
  loadingRate.value = true;
  try {
    const res = await fetch("https://open.er-api.com/v6/latest/USD");
    const data = await res.json();
    Object.assign(ratesCache, data.rates);
    rate.value = data.rates[code] ?? 1;
  } catch {
    rate.value = 1;
  } finally {
    loadingRate.value = false;
  }
}

const byYear = computed(() =>
  rawByYear.value.map((r) => ({ ...r, converted: Number(r.total) * rate.value }))
);

const byClient = computed(() =>
  rawByClient.value.map((r) => ({ ...r, converted: Number(r.total) * rate.value }))
);

const maxYear = computed(() => Math.max(...byYear.value.map((r) => r.converted), 1));
const maxClient = computed(() => Math.max(...byClient.value.map((r) => r.converted), 1));

function pct(value, max) {
  const p = Math.max(4, Math.round((value / max) * 100));
  return `${p}%`;
}

function fmt(value) {
  const cur = CURRENCIES.find((c) => c.code === selectedCurrency.value);
  return `${cur.symbol}${value.toLocaleString("en-US", {
    minimumFractionDigits: cur.decimals,
    maximumFractionDigits: cur.decimals,
  })}`;
}
</script>

<style scoped>
.section-label {
  @apply text-xs font-bold text-gray-400 uppercase tracking-widest;
}
</style>
