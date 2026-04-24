<template>
  <div class="pos-wrap">
    <!-- ── Receipt modal (shown after successful order) ── -->
    <div v-if="receipt" class="overlay" @click.self="receipt = null">
      <div class="receipt-modal">
        <div class="receipt-header">
          <div class="receipt-check">✓</div>
          <h2>Sale Complete</h2>
          <p class="receipt-sub">Order #{{ receipt.orderId }}</p>
        </div>
        <div class="receipt-row">
          <span>Total</span>
          <strong>${{ fmt(receipt.total) }}</strong>
        </div>
        <div class="receipt-row">
          <span>Payment</span>
          <strong>{{ receipt.paymentMethod }}</strong>
        </div>
        <template v-if="receipt.paymentMethod === 'cash'">
          <div class="receipt-row">
            <span>Cash Tendered</span>
            <strong>${{ fmt(receipt.cashTendered) }}</strong>
          </div>
          <div class="receipt-row change">
            <span>Change Due</span>
            <strong class="change-amt">${{ fmt(receipt.changeDue) }}</strong>
          </div>
        </template>
        <div v-if="receipt.eventName" class="receipt-row">
          <span>Event</span>
          <strong>{{ receipt.eventName }}</strong>
        </div>
        <button class="btn-primary btn-full" @click="receipt = null">New Sale</button>
      </div>
    </div>

    <!-- ── Checkout modal ── -->
    <div v-if="showCheckout" class="overlay" @click.self="showCheckout = false">
      <div class="checkout-modal">
        <h2>Checkout</h2>

        <div class="checkout-total">${{ fmt(posStore.cartTotal) }}</div>

        <div class="form-group">
          <label>Payment Method</label>
          <div class="method-grid">
            <button
              v-for="m in paymentMethods"
              :key="m.value"
              :class="['method-btn', { active: checkoutForm.paymentMethod === m.value }]"
              @click="checkoutForm.paymentMethod = m.value"
            >{{ m.label }}</button>
          </div>
        </div>

        <div v-if="checkoutForm.paymentMethod === 'cash'" class="form-group">
          <label>Cash Tendered</label>
          <input
            v-model="checkoutForm.cashTendered"
            type="number"
            step="0.01"
            min="0"
            class="cash-input"
            placeholder="0.00"
            @input="updateChange"
          />
          <div v-if="computedChange >= 0" class="change-display">
            Change Due: <span>${{ fmt(computedChange) }}</span>
          </div>
          <div v-else-if="checkoutForm.cashTendered" class="change-display insufficient">
            Amount too low by ${{ fmt(-computedChange) }}
          </div>
          <div class="quick-cash">
            <button v-for="amt in quickCashAmounts" :key="amt" class="quick-btn" @click="setQuickCash(amt)">
              ${{ amt }}
            </button>
          </div>
        </div>

        <div class="form-group">
          <label>Event Name <span class="optional">(optional)</span></label>
          <input v-model="checkoutForm.eventName" type="text" placeholder="e.g. Heights Farmers Market" class="text-input" />
        </div>

        <div class="form-group">
          <label>Event Date <span class="optional">(optional)</span></label>
          <input v-model="checkoutForm.eventDate" type="date" class="text-input" />
        </div>

        <p v-if="posStore.error" class="error-msg">{{ posStore.error }}</p>

        <div class="checkout-actions">
          <button class="btn-secondary" @click="showCheckout = false">Back</button>
          <button
            class="btn-primary"
            :disabled="!canSubmit || posStore.loading"
            @click="submitOrder"
          >{{ posStore.loading ? 'Processing…' : 'Complete Sale' }}</button>
        </div>
      </div>
    </div>

    <!-- ── Main POS layout ── -->
    <div class="pos-layout">
      <!-- Left: product grid -->
      <div class="product-panel">
        <div class="panel-header">
          <h1 class="panel-title">Point of Sale</h1>
          <input v-model="search" type="text" placeholder="Search products…" class="search-input" />
        </div>

        <div v-if="posStore.loading && !posStore.products.length" class="loading-state">
          Loading products…
        </div>
        <div v-else-if="!filteredProducts.length" class="empty-state">
          No products found.
        </div>

        <div v-else>
          <div
            v-for="(group, type) in groupedProducts"
            :key="type"
            class="product-group"
          >
            <p class="group-label">{{ type }}</p>
            <div class="product-grid">
              <button
                v-for="p in group"
                :key="p.id"
                class="product-card"
                @click="posStore.addToCart(p)"
              >
                <span class="product-name">{{ p.name }}</span>
                <span class="product-price">${{ fmt(p.price) }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: cart -->
      <div class="cart-panel">
        <div class="cart-header">
          <h2>Cart <span v-if="posStore.cartItemCount" class="cart-count">{{ posStore.cartItemCount }}</span></h2>
          <button v-if="posStore.cart.length" class="clear-btn" @click="posStore.clearCart()">Clear</button>
        </div>

        <div v-if="!posStore.cart.length" class="cart-empty">
          Tap a product to add it
        </div>

        <ul v-else class="cart-list">
          <li v-for="item in posStore.cart" :key="item.id" class="cart-item">
            <div class="cart-item-info">
              <span class="cart-item-name">{{ item.name }}</span>
              <span class="cart-item-price">${{ fmt(item.price * item.quantity) }}</span>
            </div>
            <div class="cart-item-controls">
              <button class="qty-btn" @click="posStore.updateQuantity(item.id, item.quantity - 1)">−</button>
              <span class="qty-val">{{ item.quantity }}</span>
              <button class="qty-btn" @click="posStore.updateQuantity(item.id, item.quantity + 1)">+</button>
              <button class="remove-btn" @click="posStore.removeFromCart(item.id)">✕</button>
            </div>
          </li>
        </ul>

        <div class="cart-footer">
          <div class="cart-total-row">
            <span>Total</span>
            <strong>${{ fmt(posStore.cartTotal) }}</strong>
          </div>
          <button
            class="btn-primary btn-full checkout-btn"
            :disabled="!posStore.cart.length"
            @click="openCheckout"
          >Checkout</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePOSStore } from '../stores/pos'

const posStore = usePOSStore()
const search = ref('')
const showCheckout = ref(false)
const receipt = ref(null)

const checkoutForm = ref({
  paymentMethod: 'cash',
  cashTendered: '',
  eventName: '',
  eventDate: new Date().toISOString().slice(0, 10)
})

const paymentMethods = [
  { value: 'cash',   label: 'Cash' },
  { value: 'card',   label: 'Card' },
  { value: 'venmo',  label: 'Venmo' },
  { value: 'zelle',  label: 'Zelle' }
]

const quickCashAmounts = [5, 10, 20, 50, 100]

const computedChange = computed(() => {
  const tendered = parseFloat(checkoutForm.value.cashTendered)
  if (isNaN(tendered)) return -posStore.cartTotal
  return Math.round((tendered - posStore.cartTotal) * 100) / 100
})

const canSubmit = computed(() => {
  if (checkoutForm.value.paymentMethod === 'cash') {
    const t = parseFloat(checkoutForm.value.cashTendered)
    return !isNaN(t) && t >= posStore.cartTotal
  }
  return true
})

const filteredProducts = computed(() =>
  posStore.products.filter(p =>
    p.name.toLowerCase().includes(search.value.toLowerCase()) ||
    p.type?.toLowerCase().includes(search.value.toLowerCase())
  )
)

const groupedProducts = computed(() => {
  return filteredProducts.value.reduce((acc, p) => {
    const key = p.type || 'Other'
    if (!acc[key]) acc[key] = []
    acc[key].push(p)
    return acc
  }, {})
})

function fmt(n) {
  return Number(n || 0).toFixed(2)
}

function updateChange() {}

function setQuickCash(amt) {
  const rounded = Math.ceil(posStore.cartTotal / amt) * amt
  checkoutForm.value.cashTendered = rounded >= posStore.cartTotal ? rounded : amt
}

function openCheckout() {
  checkoutForm.value.cashTendered = ''
  posStore.error = null
  showCheckout.value = true
}

async function submitOrder() {
  try {
    const result = await posStore.submitOrder({
      paymentMethod: checkoutForm.value.paymentMethod,
      cashTendered: checkoutForm.value.paymentMethod === 'cash' ? checkoutForm.value.cashTendered : null,
      eventName: checkoutForm.value.eventName,
      eventDate: checkoutForm.value.eventDate
    })
    showCheckout.value = false
    receipt.value = {
      ...result,
      cashTendered: checkoutForm.value.cashTendered
    }
  } catch {
    // error already set in store
  }
}

onMounted(() => posStore.fetchProducts())
</script>

<style scoped>
.pos-wrap { height: 100%; display: flex; flex-direction: column; }

/* ── Layout ── */
.pos-layout { display: flex; gap: 20px; flex: 1; min-height: 0; }
.product-panel { flex: 1; overflow-y: auto; }
.cart-panel {
  width: 320px; flex-shrink: 0;
  background: var(--white); border: 1px solid var(--cream-mid); border-radius: 12px;
  display: flex; flex-direction: column; max-height: calc(100vh - 120px);
}

/* ── Panel header ── */
.panel-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; gap: 12px; }
.panel-title { font-size: 20px; font-weight: 700; color: var(--brown); margin: 0; }
.search-input {
  flex: 1; max-width: 260px;
  padding: 8px 12px; border: 1px solid var(--cream-mid);
  border-radius: 8px; font-size: 13px; background: var(--white);
  color: var(--brown);
}

/* ── Product groups ── */
.group-label {
  font-size: 9px; font-weight: 700; color: var(--brown-lt);
  letter-spacing: 0.18em; text-transform: uppercase; margin: 0 0 8px;
}
.product-group { margin-bottom: 20px; }
.product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 8px; }
.product-card {
  background: var(--white); border: 1px solid var(--cream-mid); border-radius: 10px;
  padding: 14px 12px; cursor: pointer; text-align: left;
  display: flex; flex-direction: column; gap: 4px;
  transition: all .15s; font-family: var(--font-sans);
}
.product-card:hover { border-color: var(--gold); background: var(--cream); }
.product-card:active { transform: scale(0.97); }
.product-name { font-size: 13px; font-weight: 600; color: var(--brown); }
.product-price { font-size: 12px; color: var(--brown-lt); }

/* ── Cart ── */
.cart-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 16px; border-bottom: 1px solid var(--cream-mid);
}
.cart-header h2 { margin: 0; font-size: 15px; font-weight: 700; color: var(--brown); }
.cart-count {
  display: inline-flex; align-items: center; justify-content: center;
  width: 20px; height: 20px; border-radius: 50%; background: var(--brown);
  color: var(--gold-lt); font-size: 10px; font-weight: 700; margin-left: 6px;
}
.clear-btn { font-size: 11px; color: var(--brown-lt); background: none; border: none; cursor: pointer; }
.clear-btn:hover { color: #c0392b; }

.cart-empty { padding: 32px 16px; text-align: center; font-size: 13px; color: var(--brown-lt); }
.cart-list { list-style: none; margin: 0; padding: 0; flex: 1; overflow-y: auto; }
.cart-item {
  padding: 10px 16px; border-bottom: 1px solid var(--cream-mid);
  display: flex; flex-direction: column; gap: 6px;
}
.cart-item-info { display: flex; justify-content: space-between; align-items: baseline; }
.cart-item-name { font-size: 13px; font-weight: 500; color: var(--brown); }
.cart-item-price { font-size: 13px; font-weight: 600; color: var(--brown); }
.cart-item-controls { display: flex; align-items: center; gap: 6px; }
.qty-btn {
  width: 24px; height: 24px; border-radius: 6px; border: 1px solid var(--cream-mid);
  background: var(--cream); font-size: 14px; font-weight: 600; color: var(--brown);
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all .12s;
}
.qty-btn:hover { background: var(--brown); color: var(--gold-lt); border-color: var(--brown); }
.qty-val { font-size: 13px; font-weight: 600; color: var(--brown); min-width: 20px; text-align: center; }
.remove-btn {
  margin-left: auto; background: none; border: none; font-size: 11px;
  color: var(--brown-lt); cursor: pointer; padding: 2px 4px;
}
.remove-btn:hover { color: #c0392b; }

.cart-footer { padding: 14px 16px; border-top: 1px solid var(--cream-mid); margin-top: auto; }
.cart-total-row {
  display: flex; justify-content: space-between; font-size: 16px;
  font-weight: 700; color: var(--brown); margin-bottom: 12px;
}

/* ── Buttons ── */
.btn-primary {
  background: var(--brown); color: var(--gold-lt);
  border: none; border-radius: 8px; padding: 11px 20px;
  font-size: 13px; font-weight: 600; cursor: pointer;
  font-family: var(--font-sans); transition: all .15s;
}
.btn-primary:hover:not(:disabled) { background: var(--brown-md); }
.btn-primary:disabled { opacity: 0.45; cursor: not-allowed; }
.btn-secondary {
  background: var(--cream); color: var(--brown);
  border: 1px solid var(--cream-mid); border-radius: 8px; padding: 11px 20px;
  font-size: 13px; font-weight: 600; cursor: pointer;
  font-family: var(--font-sans); transition: all .15s;
}
.btn-secondary:hover { background: var(--cream-mid); }
.btn-full { width: 100%; }
.checkout-btn { margin-top: 4px; }

/* ── Overlays ── */
.overlay {
  position: fixed; inset: 0; background: rgba(44,24,16,0.45);
  display: flex; align-items: center; justify-content: center; z-index: 1000;
}
.checkout-modal, .receipt-modal {
  background: var(--white); border-radius: 16px; padding: 28px;
  width: 380px; max-width: 95vw; max-height: 90vh; overflow-y: auto;
  box-shadow: 0 20px 60px rgba(44,24,16,0.3);
}
.checkout-modal h2, .receipt-modal h2 {
  margin: 0 0 4px; font-size: 20px; color: var(--brown);
}
.checkout-total {
  font-size: 36px; font-weight: 800; color: var(--brown);
  text-align: center; margin: 12px 0 20px;
}

/* ── Checkout form ── */
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 11px; font-weight: 700; color: var(--brown-lt); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 6px; }
.optional { font-weight: 400; text-transform: none; letter-spacing: 0; color: var(--brown-lt); opacity: 0.7; }
.text-input, .cash-input {
  width: 100%; box-sizing: border-box; padding: 10px 12px;
  border: 1px solid var(--cream-mid); border-radius: 8px;
  font-size: 15px; color: var(--brown); background: var(--cream);
  font-family: var(--font-sans);
}
.cash-input { font-size: 22px; font-weight: 700; text-align: center; }
.method-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.method-btn {
  padding: 10px; border: 1px solid var(--cream-mid); border-radius: 8px;
  background: var(--cream); font-size: 13px; font-weight: 600; color: var(--brown);
  cursor: pointer; font-family: var(--font-sans); transition: all .12s;
}
.method-btn.active { background: var(--brown); color: var(--gold-lt); border-color: var(--brown); }
.change-display {
  text-align: center; margin-top: 8px; font-size: 18px; font-weight: 700; color: var(--brown);
}
.change-display.insufficient { color: #c0392b; font-size: 13px; }
.change-display span { color: #27ae60; }
.quick-cash { display: flex; gap: 6px; margin-top: 10px; }
.quick-btn {
  flex: 1; padding: 8px 4px; border: 1px solid var(--cream-mid); border-radius: 6px;
  background: var(--cream); font-size: 12px; font-weight: 600; color: var(--brown);
  cursor: pointer; font-family: var(--font-sans); transition: all .12s;
}
.quick-btn:hover { background: var(--brown); color: var(--gold-lt); border-color: var(--brown); }
.checkout-actions { display: flex; gap: 10px; margin-top: 20px; }
.checkout-actions .btn-primary, .checkout-actions .btn-secondary { flex: 1; }
.error-msg { color: #c0392b; font-size: 12px; margin: 8px 0 0; }

/* ── Receipt ── */
.receipt-header { text-align: center; margin-bottom: 20px; }
.receipt-check {
  width: 52px; height: 52px; border-radius: 50%; background: #27ae60;
  color: white; font-size: 24px; display: flex; align-items: center; justify-content: center;
  margin: 0 auto 12px;
}
.receipt-sub { font-size: 12px; color: var(--brown-lt); margin: 4px 0 0; }
.receipt-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 0; border-bottom: 1px solid var(--cream-mid); font-size: 14px; color: var(--brown);
}
.receipt-row.change { border-bottom: none; margin-bottom: 20px; }
.change-amt { font-size: 22px; color: #27ae60; }

/* ── States ── */
.loading-state, .empty-state {
  text-align: center; padding: 48px 24px; font-size: 14px; color: var(--brown-lt);
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .pos-layout { flex-direction: column; }
  .cart-panel { width: 100%; max-height: none; }
  .panel-header { flex-direction: column; align-items: flex-start; }
  .search-input { max-width: 100%; width: 100%; }
}
</style>
