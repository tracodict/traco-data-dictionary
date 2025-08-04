import { defineConfig, loadEnv } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig(({ command, mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, process.cwd(), '')
  const isProduction = command === 'build'
  
  if (isProduction) {
    // Production build for single-spa
    return {
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
        'process.env.NODE_ENV': JSON.stringify('production'),
        '__DEV__': false
      }
    }
  } else {
    // Development mode - standard SPA
    return {
      plugins: [svelte()],
      server: {
        port: 5173,
        host: true
      },
      define: {
        'process.env.NODE_ENV': JSON.stringify('development'),
        '__DEV__': true
      }
    }
  }
})
