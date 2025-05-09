import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'url'
import path from 'path'

// Convert import.meta.url to a directory path for ESM support
const __dirname = path.dirname(fileURLToPath(import.meta.url));

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: [
            { find: '@', replacement: fileURLToPath(new URL('./src', import.meta.url)) },
            { find: '@services', replacement: fileURLToPath(new URL('./src/services', import.meta.url)) }
        ]
    },
    optimizeDeps: {
        include: [
            'monaco-editor/esm/vs/language/json/json.worker',
            'monaco-editor/esm/vs/language/css/css.worker',
            'monaco-editor/esm/vs/language/html/html.worker',
            'monaco-editor/esm/vs/language/typescript/ts.worker',
            'monaco-editor/esm/vs/editor/editor.worker',
            'marked'
        ]
    }
})
