<script lang="ts">
    import { onMount } from 'svelte';
    import {
        createGrid,
        ModuleRegistry,
        ClientSideRowModelModule,
        TextFilterModule,
        type GridOptions,
        type GridApi,
        type IServerSideDatasource,
        themeQuartz,
        colorSchemeDarkBlue,
        TooltipModule,
    } from 'ag-grid-community';
    
    // Import enterprise features and modules
    import { 
        ServerSideRowModelModule,
        ColumnsToolPanelModule,
        FiltersToolPanelModule,
        MenuModule,
        MultiFilterModule,
        StatusBarModule,
        SideBarModule,
        RowGroupingModule,
        ValidationModule
    } from 'ag-grid-enterprise';

    // Register AG Grid Modules including enterprise features
    // Note: SetFilterModule is excluded for SSRM compatibility
    ModuleRegistry.registerModules([
        ClientSideRowModelModule,
        TextFilterModule,
        ServerSideRowModelModule,
        ColumnsToolPanelModule,
        FiltersToolPanelModule,
        MenuModule,
        MultiFilterModule,
        StatusBarModule,
        SideBarModule,
        RowGroupingModule,
        ValidationModule,
        TooltipModule
    ]);

    interface Props {
        columnDefs?: Array<any>;
        rowData?: Array<any>;
        height?: string;
        onGridReady?: (api: GridApi) => void;
        rowModelType?: 'clientSide' | 'serverSide';
        serverSideDatasource?: IServerSideDatasource;
        cacheBlockSize?: number;
        maxBlocksInCache?: number;
        treeData?: boolean;
        isServerSideGroup?: (dataItem: any) => boolean;
        getServerSideGroupKey?: (dataItem: any) => string;
    }

    let { 
        columnDefs = [], 
        rowData = [], 
        height = '400px',
        onGridReady,
        rowModelType = 'clientSide',
        serverSideDatasource,
        cacheBlockSize = 50,
        maxBlocksInCache = 10,
        treeData = false,
        isServerSideGroup,
        getServerSideGroupKey
    }: Props = $props();

    // Create a custom dark theme using Theming API
    const darkTheme = themeQuartz.withPart(colorSchemeDarkBlue).withParams({
        backgroundColor: '#2c3e50',
        foregroundColor: '#ecf0f1',
        headerBackgroundColor: '#1a252f',
        headerTextColor: '#ecf0f1',
        oddRowBackgroundColor: '#34495e',
        rowHoverColor: '#3e566d',
        borderColor: '#34495e'
    });

    let gridDiv: HTMLDivElement;
    let gridApi: GridApi;

    onMount(() => {
        try {
            const gridOptions: GridOptions = {
            columnDefs,
            rowData: rowModelType === 'clientSide' ? rowData : undefined,
            rowModelType,
            theme: darkTheme,
            rowHeight: rowModelType === 'serverSide' ? 40 : undefined,
            treeData,
            isServerSideGroup,
            getServerSideGroupKey,
            defaultColDef: {
                resizable: true,
                sortable: true,
                filter: rowModelType === 'serverSide' ? 'agTextColumnFilter' : true,
                filterParams: rowModelType === 'serverSide' ? {
                    filterOptions: ['equals', 'contains'],
                    defaultOption: 'contains',
                    suppressAndOrCondition: true,
                    textMatcher: ({ filterOption, value, filterText }: any) => {
                        if (filterOption === 'equals') {
                            return value === filterText;
                        } else if (filterOption === 'contains') {
                            return value != null && value.toString().toLowerCase().includes(filterText.toLowerCase());
                        }
                        return false;
                    }
                } : undefined,
            },
            cacheBlockSize,
            maxBlocksInCache,
            // Note: serverSideDatasource will be set in the onGridReady callback
            onGridReady: (params) => {
                gridApi = params.api;
                if (onGridReady) {
                    onGridReady(params.api);
                }
            }
        };

        gridApi = createGrid(gridDiv, gridOptions);
    } catch (error) {
        console.error('AgGrid: Error creating grid:', error);
    }
    });

    // Reactive updates when data changes
    $effect(() => {
        if (gridApi && rowData && rowModelType === 'clientSide') {
            gridApi.setGridOption('rowData', rowData);
        }
    });

    $effect(() => {
        if (gridApi && columnDefs) {
            gridApi.setGridOption('columnDefs', columnDefs);
        }
    });

    // Note: serverSideDatasource is managed by the parent component via onGridReady callback
</script>

<!-- Grid Container -->
<div bind:this={gridDiv} style="height: {height}; width: 100%;"></div>

<style>
  /* Hide filter and menu icons by default */
  :global(.ag-header-cell .ag-header-cell-menu-button),
  :global(.ag-header-cell .ag-floating-filter-button) {
    opacity: 0;
    transition: opacity 0.2s ease-in-out;
    pointer-events: none;
  }

  /* Show filter and menu icons on column header hover */
  :global(.ag-header-cell:hover .ag-header-cell-menu-button),
  :global(.ag-header-cell:hover .ag-floating-filter-button) {
    opacity: 1;
    pointer-events: auto;
  }

  /* Also handle the filter icon specifically */
  :global(.ag-header-cell .ag-icon-filter) {
    opacity: 0;
    transition: opacity 0.2s ease-in-out;
  }

  :global(.ag-header-cell:hover .ag-icon-filter) {
    opacity: 1;
  }

  /* Dynamic width adjustment for header text */
  :global(.ag-header-cell-text) {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    transition: margin-right 0.2s ease-in-out;
    margin-right: 2px; /* Small margin when icons are hidden */
  }

  /* Reduce header text width when hovering to make space for icons */
  :global(.ag-header-cell:hover .ag-header-cell-text) {
    margin-right: 2px; /* Space for menu + filter icons when visible */
  }

  /* Ensure proper positioning of the header content */
  :global(.ag-header-cell-comp-wrapper) {
    position: relative;
    width: 100%;
    display: flex;
    align-items: center;
  }

  /* Position icons at the right edge */
  :global(.ag-header-cell .ag-header-cell-menu-button) {
    position: absolute;
    right: 24px;
    top: 50%;
    transform: translateY(-50%);
    z-index: 1;
  }

  :global(.ag-header-cell .ag-floating-filter-button) {
    position: absolute;
    right: 4px;
    top: 50%;
    transform: translateY(-50%);
    z-index: 1;
  }
</style>
