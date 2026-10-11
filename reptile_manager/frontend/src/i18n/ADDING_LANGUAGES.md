# Adding a new language

## Step 1 – Create the translation file

Create `src/i18n/es.js`, using `en.js` as the template:

```js
export default {
  nav: {
    dashboard: 'Inicio',
    animals: 'Animales',
    // ...
  },
  // add all other keys from en.js
}
```

Missing keys automatically fall back to English.

## Step 2 – Register it in index.js

```js
import es from './es'

const messages = { en, de, es }  // <-- add here

export const languages = {
  en: { name: 'English',  flag: '🇬🇧' },
  de: { name: 'Deutsch',  flag: '🇩🇪' },
  es: { name: 'Español',  flag: '🇪🇸' },  // <-- and here
}

const dateLocales = { en: 'en-GB', de: 'de-DE', es: 'es-ES' }  // <-- date format
```

## Done

The new language appears automatically in the language picker.
