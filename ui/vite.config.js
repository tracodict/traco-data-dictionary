import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
  plugins: [svelte({emitCss: false})],
  build: {
    lib: {
      entry: 'src/main.ts',
      name: 'fixDictionary',
      fileName: () => 'single-spa-entry.js',
      formats: ['es']
    },
    rollupOptions: {
      external: ['single-spa'],
      output: {
        globals: {
          'single-spa': 'singleSpa'
        },
        // Inline CSS into JS bundle
        inlineDynamicImports: true,
        assetFileNames: () => {
          return 'assets/[name].[ext]';
        }
      }
    },
    outDir: '../api/static',
    emptyOutDir: false,
    // Ensure CSS is inlined
    cssCodeSplit: false
  },
  define: {
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'development')
  }
})
