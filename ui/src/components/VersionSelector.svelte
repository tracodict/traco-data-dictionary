<script lang="ts">
  interface Props {
    selectedVersion: string;
    onVersionChange: (version: string) => void;
  }

  let { selectedVersion, onVersionChange }: Props = $props();

  const versions = ['FIX.4.4', 'FIX.5.0SP2', 'FIX.Z'];

  function handleChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    onVersionChange(target.value);
  }
</script>

<div class="version-selector">
  <label for="version-select">FIX Version:</label>
  <select 
    id="version-select" 
    value={selectedVersion} 
    onchange={handleChange}
    class="version-select"
  >
    {#each versions as version}
      <option value={version}>{version}</option>
    {/each}
  </select>
</div>

<style>
  .version-selector {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  label {
    font-weight: 500;
    color: #ecf0f1;
  }

  .version-select {
    padding: 8px 12px;
    border: 2px solid #34495e;
    border-radius: 6px;
    font-size: 1rem;
    background: #2c3e50;
    color: #ecf0f1;
    cursor: pointer;
    transition: border-color 0.2s ease;
  }

  .version-select:hover {
    border-color: #3498db;
  }

  .version-select:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.25);
  }

  .version-select option {
    background: #2c3e50;
    color: #ecf0f1;
  }
</style>
