<template>
  <!-- Outer shell handles scaling without breaking layout -->
  <div class="preview-outer" :style="outerStyle">
    <div class="invoice-preview-page" :style="innerStyle">

      <!-- HEADER -->
      <div class="inv-header">
        <div>
          <div class="inv-sender-name">{{ invoice.sender_name || "Your Name" }}</div>
          <div class="inv-sender-address">{{ invoice.sender_address }}</div>
        </div>
        <div class="inv-header-right">
          <div class="inv-title">INVOICE</div>
          <img v-if="invoice.sender_logo_url" :src="invoice.sender_logo_url" class="inv-logo" alt="Logo" />
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
            <td class="inv-td" style="white-space: pre-line;">{{ item.description || "—" }}</td>
            <td class="inv-td inv-td-right">{{ item.hours != null && item.hours !== "" ? item.hours : "—" }}</td>
            <td class="inv-td inv-td-right">{{ item.rate != null && item.rate !== "" ? (invoice.currency || "$") + formatAmount(item.rate) : "—" }}</td>
            <td class="inv-td inv-td-right">{{ formatAmount(item.amount) }}</td>
          </tr>
          <tr v-if="!invoice.items || invoice.items.length === 0">
            <td class="inv-td" colspan="4" style="text-align:center;color:#aaa;">No items</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td class="inv-total-label" colspan="3">Total</td>
            <td class="inv-total-value">{{ invoice.currency || "$" }}{{ formatAmount(computedTotal) }}</td>
          </tr>
        </tfoot>
      </table>

      <!-- TERMS -->
      <div v-if="invoice.terms" class="inv-terms">
        <div class="inv-section-label">Terms &amp; Conditions</div>
        <div class="inv-terms-text">{{ invoice.terms }}</div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  invoice: { type: Object, required: true },
  scale: { type: Number, default: 0.75 },
});

// A4 at 96 dpi
const A4_W = 794;
const A4_H = 1123;

const outerStyle = computed(() => ({
  width: Math.round(A4_W * props.scale) + "px",
  height: Math.round(A4_H * props.scale) + "px",
  overflow: "hidden",
  position: "relative",
}));

const innerStyle = computed(() => ({
  width: A4_W + "px",
  minHeight: A4_H + "px",
  transform: `scale(${props.scale})`,
  transformOrigin: "top left",
  position: "absolute",
  top: 0,
  left: 0,
}));

const computedTotal = computed(() =>
  (props.invoice.items || []).reduce((s, i) => s + (Number(i.amount) || 0), 0)
);

function formatAmount(val) {
  return (Number(val) || 0).toFixed(2);
}
</script>

<style scoped>
.invoice-preview-page {
  background: #fff;
  padding: 53px 68px;
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 14.7px;
  color: #2d2d2d;
  line-height: 1.4;
}

/* ── Header ── */
.inv-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 38px;
  padding-bottom: 22px;
  border-bottom: 2px solid #e8e8e8;
}

.inv-sender-name {
  font-size: 29px;
  font-weight: 700;
  color: #111;
}

.inv-sender-address {
  margin-top: 10px;
  font-size: 12px;
  color: #777;
  line-height: 1.75;
  white-space: pre-line;
}

.inv-header-right { text-align: right; }

.inv-title {
  font-size: 29px;
  font-weight: 700;
  color: #111;
  letter-spacing: 3px;
}

.inv-logo {
  margin-top: 10px;
  max-height: 84px;
  max-width: 122px;
  display: block;
  margin-left: auto;
  object-fit: contain;
}

/* ── Billing ── */
.inv-billing {
  display: flex;
  justify-content: space-between;
  margin-bottom: 38px;
}

.inv-section-label {
  font-weight: 700;
  font-size: 10.5px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #888;
  margin-bottom: 10px;
}

.inv-client-name {
  font-weight: 600;
  font-size: 17px;
  margin-bottom: 7px;
  color: #111;
}

.inv-client-detail {
  font-size: 13px;
  color: #555;
  line-height: 1.85;
}

.inv-meta { text-align: right; }

.inv-meta-row {
  display: flex;
  justify-content: flex-end;
  gap: 28px;
  margin-bottom: 8px;
  font-size: 14px;
}

.inv-meta-label { font-weight: 600; color: #555; }
.inv-meta-value { min-width: 110px; color: #111; }

/* ── Table ── */
.inv-table { width: 100%; border-collapse: collapse; }

.inv-th {
  background: #f5f5f5;
  padding: 13px 17px;
  font-size: 10.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.7px;
  color: #666;
  border: 1px solid #ddd;
  text-align: left;
}

.inv-th-right { text-align: right; width: 90px; }

.inv-td {
  padding: 17px 17px;
  border: 1px solid #ddd;
  vertical-align: top;
  line-height: 1.75;
  color: #333;
  font-size: 14px;
}

.inv-td-right {
  text-align: right;
  font-weight: 500;
  white-space: nowrap;
  color: #111;
}

.inv-total-label {
  border: 1px solid #ddd;
  padding: 15px 17px;
  background: #f5f5f5;
  text-align: right;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: #111;
}

.inv-total-value {
  border: 1px solid #ddd;
  padding: 15px 17px;
  background: #f5f5f5;
  text-align: right;
  font-size: 19px;
  font-weight: 700;
  color: #111;
  white-space: nowrap;
  width: 90px;
}

/* ── Terms ── */
.inv-terms {
  margin-top: 38px;
  padding-top: 20px;
  border-top: 1px solid #e8e8e8;
}

.inv-terms-text {
  font-size: 13px;
  color: #555;
  line-height: 1.75;
  margin-top: 7px;
}
</style>
