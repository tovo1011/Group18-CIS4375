import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

export const usePOSStore = defineStore('pos', () => {
  const products = ref([])
  const cart = ref([])
  const recentOrders = ref([])
  const loading = ref(false)
  const error = ref(null)

  const cartTotal = computed(() =>
    cart.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
  )

  const cartItemCount = computed(() =>
    cart.value.reduce((sum, item) => sum + item.quantity, 0)
  )

  async function fetchProducts() {
    loading.value = true
    error.value = null
    try {
      const res = await axios.get(`${API_URL}/pos/products`)
      products.value = res.data
    } catch (e) {
      error.value = e.response?.data?.message || 'Failed to load products'
    } finally {
      loading.value = false
    }
  }

  function addToCart(product) {
    const existing = cart.value.find(i => i.id === product.id)
    if (existing) {
      existing.quantity++
    } else {
      cart.value.push({ ...product, quantity: 1 })
    }
  }

  function removeFromCart(productId) {
    cart.value = cart.value.filter(i => i.id !== productId)
  }

  function updateQuantity(productId, quantity) {
    const item = cart.value.find(i => i.id === productId)
    if (item) {
      if (quantity <= 0) {
        removeFromCart(productId)
      } else {
        item.quantity = quantity
      }
    }
  }

  function clearCart() {
    cart.value = []
  }

  async function submitOrder({ paymentMethod, cashTendered, customerName, eventName, eventDate }) {
    loading.value = true
    error.value = null
    try {
      const res = await axios.post(`${API_URL}/pos/orders`, {
        items: cart.value.map(i => ({ product_id: i.id, quantity: i.quantity })),
        payment_method: paymentMethod,
        cash_tendered: cashTendered ? parseFloat(cashTendered) : null,
        customer_name: customerName || null,
        event_name: eventName || '',
        event_date: eventDate || null
      })
      clearCart()
      return res.data
    } catch (e) {
      error.value = e.response?.data?.message || 'Order failed'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchRecentOrders() {
    try {
      const res = await axios.get(`${API_URL}/pos/orders`)
      recentOrders.value = res.data
    } catch (e) {
      error.value = e.response?.data?.message || 'Failed to load orders'
    }
  }

  return {
    products, cart, recentOrders, loading, error,
    cartTotal, cartItemCount,
    fetchProducts, addToCart, removeFromCart, updateQuantity, clearCart,
    submitOrder, fetchRecentOrders
  }
})
