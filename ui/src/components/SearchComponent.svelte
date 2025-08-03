<script lang="ts">
  interface Props {
    searchQuery: string;
    onSearch: (query: string) => void;
    isSearching?: boolean;
  }

  let { searchQuery, onSearch, isSearching = false }: Props = $props();

  let inputValue = $state(searchQuery);

  function handleSubmit(event: Event) {
    event.preventDefault();
    onSearch(inputValue);
  }

  function handleInput(event: Event) {
    const target = event.target as HTMLInputElement;
    inputValue = target.value;
  }
</script>

<form onsubmit={handleSubmit} class="search-form">
  <div class="search-container">
    <input 
      type="text" 
      placeholder="Search FIX dictionary..." 
      value={inputValue}
      oninput={handleInput}
      class="search-input"
      disabled={isSearching}
    />
    <button 
      type="submit" 
      class="search-button" 
      disabled={isSearching || !inputValue.trim()}
    >
      {#if isSearching}
        <span class="loading-spinner"></span>
        Searching...
      {:else}
        Search
      {/if}
    </button>
  </div>
</form>

<style>
  .search-form {
    width: 100%;
    margin-bottom: 20px;
  }

  .search-container {
    display: flex;
    gap: 10px;
  }

  .search-input {
    flex: 1;
    padding: 12px 16px;
    border: 2px solid #34495e;
    border-radius: 6px;
    font-size: 1rem;
    background: #2c3e50;
    color: #ecf0f1;
    transition: border-color 0.2s ease;
  }

  .search-input:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.25);
  }

  .search-input:disabled {
    background-color: #1a1a1a;
    cursor: not-allowed;
    opacity: 0.6;
  }

  .search-input::placeholder {
    color: #95a5a6;
  }

  .search-button {
    padding: 12px 24px;
    background: #3498db;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s ease;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .search-button:hover:not(:disabled) {
    background: #2980b9;
  }

  .search-button:disabled {
    background: #5d6d7e;
    cursor: not-allowed;
  }

  .loading-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid transparent;
    border-top: 2px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
</style>
