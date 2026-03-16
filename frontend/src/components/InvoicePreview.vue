<template>
  <!-- A4 paper, scaled to fit the preview area -->
  <div class="invoice-preview-page" :style="pageStyle">

    <!-- HEADER -->
    <div class="inv-header">
      <div>
        <div class="inv-sender-name">{{ invoice.sender_name || "Your Name" }}</div>
        <div class="inv-sender-address">{{ invoice.sender_address }}</div>
      </div>
      <div class="inv-header-right">
        <div class="inv-title">INVOICE</div>
        <img
          v-if="invoice.sender_logo_url"
          :src="invoice.sender_logo_url"
          class="inv-logo"
          alt="Logo"
        />
      </div>
    </div>

    <!-- BILLING + META -->
    <div class="inv-billing">
      <div>
        <div class="inv-section-label">Bill To</div>
        <div class="inv-client-name">{{ invoice.client_name || "—" }}</div>
        <div class="inv-client-detail">
          <template v-if="invoice.client_phone">TELF: {{ invoice.client_phone }}<br /></template>
          <template v-if="invoice.client_email">EMAIL: {{ invoice.client_email }}<br /></template>
          <template v-if="invoice.client_address">{{ invoice.client_address }}</template>
        </div>
      </div>
      <div class="inv-meta">
        <div class="inv-meta-row">
          <span class="inv-meta-label">Invoice&nbsp;#</span>
          <span class="inv-meta-value">{{ invoice.invoice_number }}</span>
        </div>
        <div class="inv-meta-row">
          <span class="inv-meta-label">Invoice&nbsp;Date</span>
          <span class="inv-meta-value">{{ invoice.invoice_date }}</span>
        </div>
      </div>
    </div>

    <!-- TABLE -->
    <table class="inv-table">
      <thead>
        <tr>
          <th class="inv-th">Description</th>
          <th class="inv-th inv-th-right">Hours</th>
          <th class="inv-th inv-th-right">Rate</th>
          <th class="inv-th inv-th-right">Amount</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(item, idx) in invoice.items" :key="idx">
          <td class="inv-td" style="white-space: pre-line;">
            {{ item.description || "—" }}
          </td>
          <td class="inv-td inv-td-right">
            {{ item.hours != null && item.hours !== '' ? item.hours : '—' }}
          </td>
          <td class="inv-td inv-td-right">
            {{ item.rate != null && item.rate !== '' ? (invoice.currency || '$') + formatAmount(item.rate) : '—' }}
          </td>
          <td class="inv-td inv-td-right">
            {{ formatAmount(item.amount) }}
          </td>
        </tr>
        <tr v-if="!invoice.items || invoice.items.length === 0">
          <td class="inv-td" colspan="4" style="text-align:center; color:#aaa;">
            No items
          </td>
        </tr>
      </tbody>
      <tfoot>
        <tr>
          <td class="inv-total-label" colspan="3">Total</td>
          <td class="inv-total-value">
            {{ invoice.currency || "$" }}{{ formatAmount(computedTotal) }}
          </td>
        </tr>
      </tfoot>
    </table>

    <!-- TERMS -->
    <div v-if="invoice.terms" class="inv-terms">
      <div class="inv-section-label">Terms &amp; Conditions</div>
      <div class="inv-terms-text">{{ invoice.terms }}</div>
    </div>

  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  invoice: { type: Object, required: true },
  scale: { type: Number, default: 0.72 },
});

// A4 dimensions in px at 96dpi: 794 × 1123
const A4_W = 794;
const A4_H = 1123;

const pageStyle = computed(() => ({
  width: A4_W + "px",
  minHeight: A4_H + "px",
  transform: `scale(${props.scale})`,
  transformOrigin: "top center",
}));

const computedTotal = computed(() =>
  (props.invoice.items || []).reduce((s, i) => s + (Number(i.amount) || 0), 0)
);

function formatAmount(val) {
  const n = Number(val) || 0;
  return n.toFixed(2);
}
</script>

<style scoped>
/* ── Page ── */
.invoice-preview-page {
  background: #fff;
  padding: 52px 58px;
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 13px;
  color: #2d2d2d;
  line-height: 1.4;
}

/* ── Header ── */
.inv-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 44px;
  padding-bottom: 22px;
  border-bottom: 2px solid #e8e8e8;
}

.inv-sender-name {
  font-size: 22px;
  font-weight: 700;
  color: #111;
  letter-spacing: -0.3px;
}

.inv-sender-address {
  margin-top: 8px;
  font-size: 11px;
  color: #777;
  line-height: 1.65;
  max-width: 280px;
  white-space: pre-line;
}

.inv-header-right {
  text-align: right;
}

.inv-title {
  font-size: 22px;
  font-weight: 700;
  color: #111;
  letter-spacing: 3px;
  text-transform: uppercase;
}

.inv-logo {
  margin-top: 10px;
  max-height: 72px;
  max-width: 108px;
  display: block;
  margin-left: auto;
  object-fit: contain;
}

/* ── Billing ── */
.inv-billing {
  display: flex;
  justify-content: space-between;
  margin-bottom: 36px;
}

.inv-section-label {
  font-weight: 700;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #888;
  margin-bottom: 9px;
}

.inv-client-name {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 5px;
  color: #111;
}

.inv-client-detail {
  font-size: 12px;
  color: #555;
  line-height: 1.75;
}

.inv-meta {
  text-align: right;
}

.inv-meta-row {
  display: flex;
  justify-content: flex-end;
  gap: 24px;
  margin-bottom: 7px;
  font-size: 13px;
}

.inv-meta-label {
  font-weight: 600;
  color: #555;
}

.inv-meta-value {
  min-width: 110px;
  color: #111;
}

/* ── Table ── */
.inv-table {
  width: 100%;
  border-collapse: collapse;
}

.inv-th {
  background: #f5f5f5;
  padding: 11px 16px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.7px;
  color: #666;
  border: 1px solid #ddd;
  text-align: left;
}

.inv-th-right {
  text-align: right;
  width: 80px;
}

.inv-td {
  padding: 14px 16px;
  border: 1px solid #ddd;
  vertical-align: top;
  line-height: 1.65;
  color: #333;
}

.inv-td-right {
  text-align: right;
  font-weight: 500;
  white-space: nowrap;
  color: #111;
}

.inv-total-label {
  border: 1px solid #ddd;
  padding: 13px 16px;
  background: #f5f5f5;
  text-align: right;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: #111;
}

.inv-total-value {
  border: 1px solid #ddd;
  padding: 13px 16px;
  background: #f5f5f5;
  text-align: right;
  font-size: 16px;
  font-weight: 700;
  color: #111;
  white-space: nowrap;
  width: 80px;
}

/* ── Terms ── */
.inv-terms {
  margin-top: 44px;
  padding-top: 18px;
  border-top: 1px solid #e8e8e8;
}

.inv-terms-text {
  font-size: 12px;
  color: #555;
  line-height: 1.65;
  margin-top: 6px;
}
</style>
