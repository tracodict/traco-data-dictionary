<script lang="ts">
  import AgGrid from './AgGrid.svelte';
  import type { IServerSideGetRowsRequest, LoadSuccessParams } from '../lib/api-client';
  import ApiClient from '../lib/api-client';
  import type { GridApi, ColDef } from 'ag-grid-community';
  import type { IServerSideDatasource } from 'ag-grid-community';
  
  interface Props {
    selectedVersion: string;
    onPageChange?: (page: number) => void;
    searchQuery?: string;
  }

  let { 
    selectedVersion,
    onPageChange,
    searchQuery = ''
  }: Props = $props();

  const apiClient = new ApiClient();
  let gridApi: GridApi;
  let serverSideDatasource: IServerSideDatasource;
  let totalCount = $state(0);
  let loading = $state(false);
  let hasAttemptedLoad = $state(false);

  // React to version and search changes
  $effect(() => {
    if (gridApi && (selectedVersion || searchQuery)) {
      gridApi.refreshServerSide({ purge: true });
    }
  });

  // Configure columns for AG Grid
  const columnDefs: ColDef[] = [
    {
      field: 'category_id',
      headerName: 'Category ID',
      width: 120,
      minWidth: 100,
      resizable: true,
      sortable: true,
      filter: 'agTextColumnFilter'
    },
    {
      field: 'fixml_filename',
      headerName: 'FIXML File',
      width: 150,
      minWidth: 120,
      resizable: true,
      sortable: true,
      filter: 'agTextColumnFilter'
    },
    {
      field: 'component_type',
      headerName: 'Component Type',
      width: 150,
      minWidth: 120,
      resizable: true,
      sortable: true,
      filter: 'agTextColumnFilter'
    },
    {
      field: 'section_id',
      headerName: 'Section',
      width: 120,
      minWidth: 80,
      resizable: true,
      sortable: true,
      filter: 'agTextColumnFilter'
    },
    {
      field: 'volume',
      headerName: 'Volume',
      width: 100,
      minWidth: 80,
      resizable: true,
      sortable: true,
      filter: 'agTextColumnFilter'
    },
    {
      field: 'description',
      headerName: 'Description',
      width: 300,
      minWidth: 200,
      resizable: true,
      sortable: true,
      filter: 'agTextColumnFilter',
      wrapText: true
    }
  ];

  // Handle grid ready and setup server-side datasource
  function handleGridReady(api: GridApi) {
    gridApi = api;
    
    serverSideDatasource = {
      getRows: async (params) => {
        const startRow = params.request.startRow || 0;
        const endRow = params.request.endRow || 100;
        
        try {
          loading = true;
          hasAttemptedLoad = true;
          
          const ssrmRequest: IServerSideGetRowsRequest = {
            startRow,
            endRow,
            rowGroupCols: params.request.rowGroupCols || [],
            valueCols: params.request.valueCols || [],
            pivotCols: params.request.pivotCols || [],
            pivotMode: params.request.pivotMode || false,
            groupKeys: params.request.groupKeys || [],
            filterModel: params.request.filterModel || undefined,
            sortModel: params.request.sortModel || []
          };
          
          const response: LoadSuccessParams = await apiClient.getSSRMData(
            'categories', 
            ssrmRequest, 
            selectedVersion,
            searchQuery
          );
          
          if (response.rowCount !== undefined) {
            totalCount = response.rowCount;
          }
          
          params.success({
            rowData: response.rowData,
            rowCount: response.rowCount
          });
          
        } catch (error) {
          console.error('CategoryList SSRM error:', error);
          params.fail();
        } finally {
          loading = false;
        }
      }
    };
    
    api.setGridOption('serverSideDatasource', serverSideDatasource);
  }
</script>

<div class="category-list">
  <div class="list-header">
    <h3>Categories</h3>
    <div class="count-info">
      Total: {totalCount} categories
      {#if loading}
        <span class="loading-indicator">Loading...</span>
      {/if}
    </div>
  </div>

  <div class="grid-container">
      <AgGrid 
        {columnDefs}
        height="500px"
        onGridReady={handleGridReady}
        rowModelType="serverSide"
        cacheBlockSize={100}
        maxBlocksInCache={10}
      />
    </div>
</div>

<style>
  .category-list {
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

  .grid-container {
    flex: 1;
    background: #2c3e50;
    border-radius: 8px;
    border: 1px solid #34495e;
    overflow: hidden;
    min-height: 500px;
  }
</style>
