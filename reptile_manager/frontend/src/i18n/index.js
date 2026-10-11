import { ref } from 'vue'
import de from './de'
import en from './en'

/*
 * Minimal built-in i18n — no external package needed.
 *
 * Adding a language:
 * 1. Create src/i18n/es.js (use en.js as the template)
 * 2. Import it here: import es from './es'
 * 3. Add it to 'messages' and 'languages'
 */

const messages = { en, de }

export const languages = {
  en: { name: 'English',  flag: '🇬🇧' },
  de: { name: 'Deutsch',  flag: '🇩🇪' },
}

// Locale used for date formatting per UI language
const dateLocales = { en: 'en-GB', de: 'de-DE' }

function storedLocale() {
  try {
    const l = localStorage.getItem('locale')
    return languages[l] ? l : 'en'
  } catch {
    return 'en'
  }
}

export const locale = ref(storedLocale())
document.documentElement.lang = locale.value

function get(obj, path) {
  return path.split('.').reduce((o, k) => o?.[k], obj)
}

export function setLocale(lang) {
  if (!languages[lang]) return
  locale.value = lang
  localStorage.setItem('locale', lang)
  document.documentElement.lang = lang
}

export function useI18n() {
  function t(key) {
    // Accessing locale.value makes Vue track reactivity automatically
    return get(messages[locale.value], key)
        ?? get(messages.en, key)
        ?? key
  }
  return { t, locale }
}

export function dateLocale() {
  return dateLocales[locale.value] ?? 'en-GB'
}

export function fmtDate(d) {
  return d ? new Date(d).toLocaleDateString(dateLocale(), { day: '2-digit', month: '2-digit', year: 'numeric' }) : '—'
}

export function fmtDateTime(d) {
  return d ? new Date(d).toLocaleString(dateLocale(), { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '—'
}

// Dummy Vue plugin — keeps import in main.js harmless
export default { install() {} }
