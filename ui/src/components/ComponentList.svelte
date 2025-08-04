<script lang="ts">
  import AgGrid from './AgGrid.svelte';
  import type { ComponentSummary, IServerSideGetRowsRequest, LoadSuccessParams } from '../lib/api-client';
  import { getApiClient } from '../lib/api-client-instance';
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

  const apiClient = getApiClient();
  let gridApi: GridApi;
  let serverSideDatasource: IServerSideDatasource;
  let totalCount = $state(0);
  let loading = $state(false);
  let hasAttemptedLoad = $state(false); // Track if we've attempted to load data

  // React to version and search changes
  $effect(() => {
    if (gridApi && (selectedVersion || searchQuery)) {
      // Refresh the grid when version or search changes
      gridApi.refreshServerSide({ purge: true });
    }
  });

  // Configure columns for AG Grid
  const columnDefs: ColDef[] = [
    {
      field: 'component_id',
      headerName: 'ID',
      width: 80,
      minWidth: 80,
      resizable: true,
      sortable: true,
      filter: 'agTextColumnFilter'
    },
    {
      field: 'name',
      headerName: 'Component Name',
      width: 250,
      minWidth: 150,
      resizable: true,
      sortable: true,
      filter: 'agTextColumnFilter'
    },
    {
      field: 'abbr_name',
      headerName: 'Abbreviation',
      width: 150,
      minWidth: 100,
      resizable: true,
      sortable: true,
      filter: 'agTextColumnFilter'
    },
    {
      field: 'component_type',
      headerName: 'Type',
      width: 120,
      minWidth: 80,
      resizable: true,
      sortable: true,
      filter: 'agTextColumnFilter'
    },
    {
      field: 'category_id',
      headerName: 'Category',
      width: 120,
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
    
    // Create server-side datasource
    serverSideDatasource = {
      getRows: async (params) => {
        const startRow = params.request.startRow || 0;
        const endRow = params.request.endRow || 100;
        
        try {
          loading = true;
          hasAttemptedLoad = true;
          
          // Create the SSRM request
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
          
          // Call the new SSRM API with search query
          const response: LoadSuccessParams = await apiClient.getSSRMData(
            'components', 
            ssrmRequest, 
            selectedVersion,
            searchQuery
          );
          
          // Update total count
          if (response.rowCount !== undefined) {
            totalCount = response.rowCount;
          }
          
          // Call success with the response data
          params.success({
            rowData: response.rowData,
            rowCount: response.rowCount
          });
          
        } catch (error) {
          console.error('ComponentList SSRM error:', error);
          params.fail();
        } finally {
          loading = false;
        }
      }
    };
    
    // Set the datasource
    api.setGridOption('serverSideDatasource', serverSideDatasource);
  }

  // Handle row selection
  function handleRowSelection(event: any) {
    const selectedRows = gridApi.getSelectedRows();
    if (selectedRows.length > 0) {
      console.log('Selected component:', selectedRows[0]);
      // TODO: Implement component detail view or navigation
    }
  }
</script>

<div class="component-list">
  <div class="list-header">
    <h3>Components</h3>
    <div class="count-info">
      Total: {totalCount} components
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
</style>
