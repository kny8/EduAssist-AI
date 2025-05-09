import {createApp} from 'vue'
import App from './App.vue'
import router from './router'

// Import Material Design Icons
import {aliases, mdi} from 'vuetify/iconsets/mdi-svg'

// Import Bootstrap
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'

// Vuetify
import 'vuetify/styles'
import {createVuetify} from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

const vuetify = createVuetify({
    components,
    directives,
    icons: {
        defaultSet: 'mdi',
        aliases,
        sets: {
            mdi,
        },
    }
})

createApp(App)
    .use(vuetify)
    .use(router)
    // .use(store)
    .mount('#app')
