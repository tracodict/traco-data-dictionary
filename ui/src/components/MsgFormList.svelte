<script lang="ts">
  import AgGrid from './AgGrid.svelte';
  import type { IServerSideGetRowsRequest, LoadSuccessParams } from '../lib/api-client';
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
  let hasAttemptedLoad = $state(false);

  // React to version and search changes
  $effect(() => {
    console.log('MsgFormList: effect triggered', { gridApi: !!gridApi, selectedVersion, searchQuery });
    if (gridApi && (selectedVersion || searchQuery)) {
      console.log('MsgFormList: refreshing server side');
      gridApi.refreshServerSide({ purge: true });
    }
  });

  // Configure columns for AG Grid
  const columnDefs: ColDef[] = [
    {
      field: 'component_id',
      headerName: 'Component ID',
      width: 120,
      minWidth: 100,
      resizable: true,
      sortable: true,
      filter: 'agTextColumnFilter'
    },
    {
      field: 'msgType',
      headerName: 'Msg Type',
      width: 100,
      minWidth: 80,
      resizable: true,
      sortable: true,
      filter: 'agTextColumnFilter'
    },
    {
      field: 'componentName',
      headerName: 'Component Name',
      width: 180,
      minWidth: 150,
      resizable: true,
      sortable: true,
      filter: 'agTextColumnFilter'
    },
    {
      field: 'tag',
      headerName: 'Tag',
      width: 80,
      minWidth: 60,
      resizable: true,
      sortable: true,
      filter: 'agTextColumnFilter',
      cellRenderer: (params: any) => params.value ? `[${params.value}]` : ''
    },
    {
      field: 'name',
      headerName: 'Name',
      width: 200,
      minWidth: 150,
      resizable: true,
      sortable: true,
      filter: 'agTextColumnFilter'
    },
    {
      field: 'abbr_name',
      headerName: 'Abbr Name',
      width: 120,
      minWidth: 100,
      resizable: true,
      sortable: true,
      filter: 'agTextColumnFilter'
    },
    {
      field: 'type',
      headerName: 'Type',
      width: 100,
      minWidth: 80,
      resizable: true,
      sortable: true,
      filter: 'agTextColumnFilter'
    },
    {
      field: 'reqd',
      headerName: 'Required',
      width: 100,
      minWidth: 80,
      resizable: true,
      sortable: true,
      filter: 'agTextColumnFilter',
      cellRenderer: (params: any) => params.value ? 'Yes' : 'No'
    },
    {
      field: 'indent',
      headerName: 'Indent',
      width: 80,
      minWidth: 60,
      resizable: true,
      sortable: true,
      filter: 'agTextColumnFilter'
    },
    {
      field: 'position',
      headerName: 'Position',
      width: 100,
      minWidth: 80,
      resizable: true,
      sortable: true,
      filter: 'agTextColumnFilter'
    },
    {
      field: 'comments',
      headerName: 'Comments',
      width: 300,
      minWidth: 200,
      resizable: true,
      sortable: true,
      filter: 'agTextColumnFilter',
      tooltipField: 'comments',
      cellRenderer: (params: any) => {
        const value = params.value || '';
        if (value.length > 100) {
          return `<span title="${value}">${value.substring(0, 100)}...</span>`;
        }
        return value;
      }
    },
    {
      field: 'field_or_component',
      headerName: 'Source Type',
      width: 120,
      minWidth: 100,
      resizable: true,
      sortable: true,
      filter: 'agTextColumnFilter'
    }
  ];

  // Handle grid ready and setup server-side datasource
  function handleGridReady(api: GridApi) {
    console.log('MsgFormList: handleGridReady called', api);
    gridApi = api;
    
    serverSideDatasource = {
      getRows: async (params) => {
        console.log('MsgFormList: getRows called', params);
        const startRow = params.request.startRow || 0;
        const endRow = params.request.endRow || 100;
        const groupKeys = params.request.groupKeys || [];
        
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
            groupKeys: groupKeys,
            filterModel: params.request.filterModel || undefined,
            sortModel: params.request.sortModel || []
          };
          
          console.log('MsgFormList: calling SSRM API', {
            datasource: 'msgform',
            request: ssrmRequest,
            version: selectedVersion,
            searchQuery,
            groupKeys
          });
          
          const response: LoadSuccessParams = await apiClient.getSSRMData(
            'msgform', 
            ssrmRequest, 
            selectedVersion,
            searchQuery
          );
          
          console.log('MsgFormList: SSRM response', response);
          
          if (response.rowCount !== undefined) {
            totalCount = response.rowCount;
          }
          
          params.success({
            rowData: response.rowData,
            rowCount: response.rowCount
          });
          
        } catch (error) {
          console.error('MsgFormList SSRM error:', error);
          params.fail();
        } finally {
          loading = false;
        }
      }
    };
    
    console.log('MsgFormList: setting datasource', serverSideDatasource);
    api.setGridOption('serverSideDatasource', serverSideDatasource);
  }
</script>

<div class="msgform-list">
  <div class="list-header">
    <h2>Message Form Structure ({selectedVersion})</h2>
    {#if totalCount > 0}
      <span class="count-badge">{totalCount.toLocaleString()} items</span>
    {/if}
  </div>
  
  <div class="grid-container">
    <AgGrid
      {columnDefs}
      height="500px"
      onGridReady={handleGridReady}
      rowModelType="serverSide"
      cacheBlockSize={100}
      maxBlocksInCache={10}
      treeData={true}
      isServerSideGroup={(dataItem) => !dataItem.tag || dataItem.tag === ''}
      getServerSideGroupKey={(dataItem) => dataItem.name}
    />
  </div>
</div>

<style>
  .msgform-list {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #34495e;
  }

  .list-header h2 {
    margin: 0;
    color: #ecf0f1;
    font-size: 1.5rem;
  }

  .count-badge {
    background: #3498db;
    color: white;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 0.875rem;
    font-weight: 500;
  }

  .grid-container {
    flex: 1;
    min-height: 500px;
    width: 100%;
  }
</style>
