<script lang="ts">
  import { onMount } from 'svelte'
  import SearchComponent from './components/SearchComponent.svelte'
  import VersionSelector from './components/VersionSelector.svelte'
  import MessageList from './components/MessageList.svelte'
  import FieldList from './components/FieldList.svelte'
  import ComponentList from './components/ComponentList.svelte'
  import type { Message, Field, Component } from './lib/api-client'
  import { ApiClient, type SearchResponseData } from './lib/api-client'

  interface Props {
    name?: string;
    singleSpa?: boolean;
  }

  let { name = 'fix-dictionary', singleSpa = false }: Props = $props()

  let activeTab = $state('search')
  let selectedVersion = $state('FIX.5.0SP2')
  let apiClient: ApiClient

  let searchResults: SearchResponseData | null = $state(null)
  let loading = $state(false)
  let searchQuery = $state('')

  onMount(() => {
    // Initialize API client with base URL
    const baseUrl = singleSpa ? window.location.origin : 'http://localhost:8000'
    apiClient = new ApiClient(baseUrl)
    // Note: List components now handle their own data loading via SSRM
  })

  async function handleSearch(query: string) {
    if (!apiClient) return
    
    loading = true
    searchQuery = query
    try {
      searchResults = await apiClient.search(query, selectedVersion)
    } catch (error) {
      console.error('Search failed:', error)
      searchResults = { messages: [], fields: [], components: [] }
    } finally {
      loading = false
    }
  }

  function handleVersionChange(version: string) {
    selectedVersion = version
    // Note: Individual list components will handle their own data reloading
    // when selectedVersion changes through their SSRM implementation
  }

  function handleTabChange(tab: string) {
    activeTab = tab
    // Note: Each list component now handles its own data loading via SSRM
  }
</script>

<div class="fix-dictionary-app">
  <header class="app-header">
    <h1>FIX Dictionary Browser</h1>
    <VersionSelector 
      {selectedVersion} 
      onVersionChange={handleVersionChange} 
    />
  </header>

  <nav class="tab-navigation">
    <button 
      class="tab-button" 
      class:active={activeTab === 'search'}
      onclick={() => handleTabChange('search')}
    >
      Search
    </button>
    <button 
      class="tab-button" 
      class:active={activeTab === 'messages'}
      onclick={() => handleTabChange('messages')}
    >
      Messages
    </button>
    <button 
      class="tab-button" 
      class:active={activeTab === 'fields'}
      onclick={() => handleTabChange('fields')}
    >
      Fields
    </button>
    <button 
      class="tab-button" 
      class:active={activeTab === 'components'}
      onclick={() => handleTabChange('components')}
    >
      Components
    </button>
  </nav>

  <main class="app-content">
    {#if loading}
      <div class="loading">Loading...</div>
    {/if}

    {#if activeTab === 'search'}
      <div class="search-tab">
        <SearchComponent 
          searchQuery={searchQuery}
          isSearching={loading}
          onSearch={handleSearch}
        />
        
        {#if searchResults}
          <div class="search-results">
            <h2>Search Results for "{searchQuery}" ({selectedVersion})</h2>
            
            {#if searchResults.messages.length > 0}
              <MessageList {selectedVersion} searchQuery={searchQuery} />
            {/if}
            
            {#if searchResults.fields.length > 0}
              <FieldList {selectedVersion} searchQuery={searchQuery} />
            {/if}
            
            {#if searchResults.components.length > 0}
              <ComponentList {selectedVersion} searchQuery={searchQuery} />
            {/if}
            
            {#if searchResults.messages.length === 0 && searchResults.fields.length === 0 && searchResults.components.length === 0}
              <div class="no-results">
                <p>No results found for "{searchQuery}" in {selectedVersion}</p>
              </div>
            {/if}
          </div>
        {/if}
      </div>
    {:else if activeTab === 'messages'}
      <MessageList 
        {selectedVersion}
      />
    {:else if activeTab === 'fields'}
      <FieldList 
        {selectedVersion}
      />
    {:else if activeTab === 'components'}
      <ComponentList 
        {selectedVersion}
      />
    {/if}
  </main>
</div>

<style>
  .fix-dictionary-app {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    margin: 0 auto;
    padding: 20px;
    background: #1a1a1a;
    color: #e1e5e9;
  }

  .app-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 2px solid #34495e;
  }

  .app-header h1 {
    color: #ecf0f1;
    margin: 0;
    font-size: 2.5rem;
    font-weight: 600;
    background: linear-gradient(45deg, #3498db, #2ecc71);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .tab-navigation {
    display: flex;
    gap: 2px;
    margin-bottom: 30px;
    border-bottom: 2px solid #34495e;
  }

  .tab-button {
    padding: 12px 24px;
    background: #2c3e50;
    border: none;
    border-bottom: 3px solid transparent;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 500;
    color: #bdc3c7;
    transition: all 0.2s ease;
  }

  .tab-button:hover {
    background: #34495e;
    color: #ecf0f1;
  }

  .tab-button.active {
    background: #3498db;
    color: #ffffff;
    border-bottom-color: #2ecc71;
  }

  .app-content {
    min-height: 500px;
  }

  .loading {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
    font-size: 1.2rem;
    color: #95a5a6;
  }

  .search-tab {
    max-width: 100%;
  }

  .search-results {
    margin-top: 30px;
    padding-top: 30px;
    border-top: 2px solid #34495e;
  }

  .search-results h2 {
    color: #ecf0f1;
    margin-bottom: 20px;
    font-size: 1.5rem;
  }

  .no-results {
    text-align: center;
    padding: 40px 20px;
    color: #95a5a6;
    background: #2c3e50;
    border-radius: 8px;
    margin-top: 20px;
    border: 1px solid #34495e;
  }

  @media (max-width: 768px) {
    .fix-dictionary-app {
      padding: 10px;
    }

    .app-header {
      flex-direction: column;
      gap: 15px;
      align-items: flex-start;
    }

    .app-header h1 {
      font-size: 2rem;
    }

    .tab-navigation {
      flex-wrap: wrap;
    }

    .tab-button {
      flex: 1;
      min-width: 120px;
    }
  }
</style>
