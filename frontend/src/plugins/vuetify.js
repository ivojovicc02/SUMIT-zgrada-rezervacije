import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import { aliases, mdi } from 'vuetify/iconsets/mdi'

const vuetify = createVuetify({
 
  components,
  directives,

  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },

  theme: {
    defaultTheme: 'sumitLight',

    themes: {
      sumitLight: {
        dark: false,

        colors: {
          primary: '#b51f2e',
          secondary: '#24364b',
          background: '#f7f8fa',
          surface: '#ffffff',
          success: '#26734d',
          error: '#b42318',
          info: '#2463a7',
          warning: '#b76e00',
        },
      },
    },
  },
})

export default vuetify