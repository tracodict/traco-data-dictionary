import { mount as svelteMount, unmount as svelteUnmount } from 'svelte'
import App from './App.svelte'

// Type declaration for single-spa
declare global {
  interface Window {
    singleSpaNavigate?: any;
    bootstrap?: any;
    mount?: any;
    unmount?: any;
  }
}

let app: any = null

// Single-spa lifecycle functions
export async function bootstrap() {
  console.log('FIX Dictionary app bootstrapping...')
  return Promise.resolve()
}

export async function mount(props: { domElement: any; container: any; } | undefined) {
  console.log('FIX Dictionary app mounting...')
  
  // Try to find the best container: immediate parent first, then specific ID, then body
  let container = document.currentScript?.parentElement  ||
    props?.domElement || 
    props?.container || 
    document.getElementById('mfe-chat-container') || 
    document.body;
  
  // Create a new div for our Svelte app
  const target = document.createElement('div');
  target.id = 'mfe-data-dictionary-app';
  target.style.overflow = 'auto'; // Prevent scrollbars
  target.className = 'w-full h-full'; // Ensure it takes full width and height';
  container.appendChild(target);
  
  app = svelteMount(App, {
    target,
    props: {
      ...props,
      name: 'fix-dictionary',
      singleSpa: true
    }
  })
  
  return Promise.resolve()
}

export async function unmount() {
  console.log('FIX Dictionary app unmounting...')
  
  if (app) {
    svelteUnmount(app)
    app = null
  }
  
  return Promise.resolve()
}

// Expose functions globally for UMD access
if (typeof window !== 'undefined') {
  window.bootstrap = bootstrap
  window.mount = mount
  window.unmount = unmount
}

// For development mode (non single-spa)
if (!window.singleSpaNavigate) {
  // Create a container element for development
  const devContainer = document.createElement('div')
  devContainer.id = 'fix-dictionary-app'
  document.body.appendChild(devContainer)
  
  // Auto-mount in development mode
  mount().catch(console.error)
}
