<template>
  <div class="login-container">
    <div class="login-card">
      <div class="logo-area">
        <img :src="'/logo.png'" alt="T4 Scents" class="logo-img" />
      </div>

      <div class="card-title">Welcome Back</div>
      <div class="card-sub">Sign in to your dashboard</div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="field">
          <label for="email">Email Address</label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="you@t4scents.com"
            required
          />
        </div>
        <div class="field">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="••••••••"
            required
          />
        </div>
        <button type="submit" :disabled="loading" class="login-btn">
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>

      <div v-if="error" class="error-msg">{{ error }}</div>

      <div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(email.value, password.value)
    router.push('/dashboard')
  } catch (err) {
    error.value = err.message || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: var(--cream);
  position: relative;
  overflow: hidden;
}

/* Soft radial gold glow in corners */
.login-container::before {
  content: '';
  position: absolute;
  width: 600px; height: 600px; border-radius: 50%;
  background: radial-gradient(circle, rgba(201,160,72,0.10) 0%, transparent 70%);
  top: -200px; right: -200px; pointer-events: none;
}
.login-container::after {
  content: '';
  position: absolute;
  width: 400px; height: 400px; border-radius: 50%;
  background: radial-gradient(circle, rgba(201,160,72,0.07) 0%, transparent 70%);
  bottom: -150px; left: -150px; pointer-events: none;
}

.login-card {
  background: var(--white);
  border-radius: 20px;
  padding: 48px 44px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 8px 60px rgba(44,24,16,0.10), 0 2px 12px rgba(201,160,72,0.06);
  border: 1px solid rgba(201,160,72,0.15);
  position: relative;
  z-index: 1;
}

/* Gold top accent */
.login-card::before {
  content: '';
  position: absolute;
  top: 0; left: 10%; right: 10%; height: 3px;
  background: linear-gradient(90deg, transparent, var(--gold-dk), var(--gold-lt), var(--gold-dk), transparent);
  border-radius: 0 0 4px 4px;
}

/* ── Logo ── */
.logo-area {
  text-align: center;
  margin-bottom: 28px;
}

.logo-img {
  width: 220px;
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0 auto 4px;
  /* fade edges to blend into the white card */
  -webkit-mask-image: radial-gradient(ellipse 85% 80% at 50% 50%, black 50%, transparent 100%);
  mask-image: radial-gradient(ellipse 85% 80% at 50% 50%, black 50%, transparent 100%);
  mix-blend-mode: multiply;
}

.logo-tagline {
  font-size: 10px;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  color: var(--gold-dk);
  font-weight: 600;
  margin-top: 4px;
}

.card-title {
  font-family: var(--font-serif);
  font-size: 22px;
  font-weight: 600;
  color: var(--brown);
  text-align: center;
  margin-bottom: 4px;
}
.card-sub {
  font-size: 12.5px;
  color: var(--brown-lt);
  text-align: center;
  margin-bottom: 28px;
}

/* ── Form ── */
.login-form { display: flex; flex-direction: column; gap: 18px; margin-bottom: 18px; }

.field { display: flex; flex-direction: column; }
.field label {
  font-size: 10px;
  font-weight: 700;
  color: var(--brown-md);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  margin-bottom: 7px;
}
.field input {
  padding: 12px 14px;
  border: 1.5px solid var(--cream-mid);
  border-radius: 10px;
  font-size: 13.5px;
  font-family: var(--font-sans);
  color: var(--brown);
  background: var(--cream);
  outline: none;
  transition: border-color .2s, box-shadow .2s, background .2s;
}
.field input::placeholder { color: var(--brown-lt); }
.field input:focus {
  border-color: var(--gold);
  box-shadow: 0 0 0 3px rgba(201,160,72,0.12);
  background: var(--white);
}

.login-btn {
  padding: 13px;
  background: linear-gradient(135deg, var(--gold-dk) 0%, var(--gold) 60%, #D4AA52 100%);
  color: var(--white);
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  font-family: var(--font-sans);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  cursor: pointer;
  margin-top: 4px;
  transition: transform .2s, box-shadow .2s;
  box-shadow: 0 4px 20px rgba(160,120,40,0.30);
}
.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px rgba(160,120,40,0.40);
}
.login-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.error-msg {
  background: #FEF2F2;
  color: var(--red);
  border: 1px solid #F3C0C0;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 12.5px;
  text-align: center;
  margin-bottom: 14px;
}

.divider {
  display: flex; align-items: center; gap: 10px;
  margin: 16px 0 14px;
}
.divider::before, .divider::after {
  content: ''; flex: 1; height: 1px; background: var(--cream-mid);
}
.divider span {
  font-size: 10px; color: var(--brown-lt);
  letter-spacing: 0.10em; text-transform: uppercase; white-space: nowrap;
}

.demo-box {
  background: var(--cream);
  border: 1px solid var(--cream-mid);
  border-radius: 8px;
  padding: 12px 14px;
  font-size: 12px;
  color: var(--brown-md);
  text-align: center;
  line-height: 1.6;
}
.demo-box strong {
  color: var(--gold-dk);
  font-size: 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
</style>
