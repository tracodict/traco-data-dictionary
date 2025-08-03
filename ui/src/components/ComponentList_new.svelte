<script lang="ts">
  import AgGrid from './AgGrid.svelte';
  import type { ComponentSummary } from '../lib/api-client';
  import type { GridApi, ColDef } from 'ag-grid-community';
  
  interface Props {
    components?: ComponentSummary[];
    selectedVersion: string;
    totalCount?: number;
    loading?: boolean;
    currentPage?: number;
    pageSize?: number;
    onPageChange?: (page: number) => void;
  }

  let { 
    components = [], 
    selectedVersion, 
    totalCount = 0, 
    loading = false,
    currentPage = 1,
    pageSize = 50,
    onPageChange
  }: Props = $props();

  let gridApi: GridApi;

  // Ensure components is always an array
  const displayComponents = $derived(Array.isArray(components) ? components : []);

  // Configure columns for AG Grid
  const columnDefs: ColDef[] = [
    {
      field: 'component_id',
      headerName: 'ID',
      width: 80,
      minWidth: 80,
      resizable: true,
      sortable: true,
      filter: true
    },
    {
      field: 'name',
      headerName: 'Component Name',
      width: 250,
      minWidth: 150,
      resizable: true,
      sortable: true,
      filter: true
    },
    {
      field: 'abbr_name',
      headerName: 'Abbreviation',
      width: 150,
      minWidth: 100,
      resizable: true,
      sortable: true,
      filter: true
    },
    {
      field: 'component_type',
      headerName: 'Type',
      width: 120,
      minWidth: 80,
      resizable: true,
      sortable: true,
      filter: true
    },
    {
      field: 'category_id',
      headerName: 'Category',
      width: 120,
      minWidth: 80,
      resizable: true,
      sortable: true,
      filter: true
    },
    {
      field: 'description',
      headerName: 'Description',
      width: 300,
      minWidth: 200,
      resizable: true,
      sortable: true,
      filter: true,
      wrapText: true,
      autoHeight: true
    }
  ];

  // Handle grid ready
  function handleGridReady(api: GridApi) {
    gridApi = api;
    // Auto-size columns to fit content
    api.sizeColumnsToFit();
  }

  // Handle row selection
  function handleRowSelection(event: any) {
    const selectedRows = gridApi.getSelectedRows();
    if (selectedRows.length > 0) {
      console.log('Selected component:', selectedRows[0]);
      // TODO: Implement component detail view or navigation
    }
  }

  // Handle pagination
  function handlePreviousPage() {
    if (currentPage > 1 && onPageChange) {
      onPageChange(currentPage - 1);
    }
  }

  function handleNextPage() {
    const totalPages = Math.ceil(totalCount / pageSize);
    if (currentPage < totalPages && onPageChange) {
      onPageChange(currentPage + 1);
    }
  }

  function handlePageInput(event: Event) {
    const target = event.target as HTMLInputElement;
    const page = parseInt(target.value);
    if (page >= 1 && page <= Math.ceil(totalCount / pageSize) && onPageChange) {
      onPageChange(page);
    }
  }

  // Calculate pagination info
  const totalPages = $derived(Math.ceil(totalCount / pageSize));
  const startRecord = $derived((currentPage - 1) * pageSize + 1);
  const endRecord = $derived(Math.min(currentPage * pageSize, totalCount));
</script>

<div class="component-list">
  <div class="list-header">
    <h3>Components</h3>
    <div class="count-info">
      Showing {displayComponents.length} of {totalCount} components (Page {currentPage})
      {#if loading}
        <span class="loading-indicator">Loading...</span>
      {/if}
    </div>
  </div>

  {#if displayComponents.length === 0 && !loading}
    <div class="empty-state">
      <p>No components found for the current search and version ({selectedVersion}).</p>
    </div>
  {:else}
    <div class="grid-container">
      <AgGrid 
        {columnDefs}
        rowData={displayComponents}
        height="500px"
        onGridReady={handleGridReady}
      />
    </div>
    
    {#if totalCount > pageSize}
      <div class="pagination-controls">
        <button 
          class="page-btn" 
          onclick={handlePreviousPage} 
          disabled={currentPage <= 1}
        >
          Previous
        </button>
        
        <div class="page-info">
          <span>Page</span>
          <input 
            type="number" 
            class="page-input" 
            value={currentPage} 
            min="1" 
            max={totalPages}
            onchange={handlePageInput}
          />
          <span>of {totalPages}</span>
          <span class="record-info">({startRecord}-{endRecord} of {totalCount})</span>
        </div>
        
        <button 
          class="page-btn" 
          onclick={handleNextPage} 
          disabled={currentPage >= totalPages}
        >
          Next
        </button>
      </div>
    {/if}
  {/if}
</div>

<style>
  .component-list {
    margin-bottom: 30px;
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding: 0 10px;
  }

  h3 {
    color: #ecf0f1;
    font-size: 1.25rem;
    margin: 0;
    border-bottom: 2px solid #34495e;
    padding-bottom: 10px;
  }

  .count-info {
    color: #95a5a6;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .loading-indicator {
    color: #3498db;
    font-style: italic;
  }

  .empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #95a5a6;
    background: #2c3e50;
    border-radius: 8px;
    border: 1px solid #34495e;
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .grid-container {
    flex: 1;
    background: #2c3e50;
    border-radius: 8px;
    border: 1px solid #34495e;
    overflow: hidden;
    min-height: 500px;
  }

  .pagination-controls {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    padding: 15px;
    background: #34495e;
    border-radius: 8px;
    margin-top: 15px;
  }

  .page-btn {
    background: #3498db;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: background-color 0.2s;
  }

  .page-btn:hover:not(:disabled) {
    background: #2980b9;
  }

  .page-btn:disabled {
    background: #7f8c8d;
    cursor: not-allowed;
  }

  .page-info {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #ecf0f1;
    font-size: 14px;
  }

  .page-input {
    width: 60px;
    padding: 4px 8px;
    border: 1px solid #7f8c8d;
    border-radius: 4px;
    background: #2c3e50;
    color: #ecf0f1;
    text-align: center;
  }

  .record-info {
    color: #95a5a6;
    font-size: 12px;
  }
</style>
