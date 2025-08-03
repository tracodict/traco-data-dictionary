<script lang="ts">
  import type { Field } from '../lib/api-client';
  
  interface Props {
    fields: Field[];
    selectedVersion: string;
  }

  let { fields, selectedVersion }: Props = $props();

  function getDatatypeColor(datatype: string): string {
    const colors: Record<string, string> = {
      'String': '#3498db',
      'char': '#2ecc71',
      'int': '#e74c3c',
      'Length': '#f39c12',
      'NumInGroup': '#9b59b6',
      'SeqNum': '#1abc9c',
      'TagNum': '#e67e22',
      'float': '#16a085',
      'Qty': '#e91e63',
      'Price': '#95a5a6',
      'PriceOffset': '#34495e',
      'Amt': '#ecf0f1',
      'Boolean': '#27ae60',
      'data': '#7f8c8d'
    };
    return colors[datatype] || '#7f8c8d';
  }
</script>

<div class="field-list">
  <h3>Fields ({fields.length})</h3>
  
  {#if fields.length === 0}
    <div class="empty-state">
      <p>No fields found for the current search and version.</p>
    </div>
  {:else}
    <div class="fields-grid">
      {#each fields as field}
        <div class="field-card">
          <div class="field-header">
            <div class="field-info">
              <div class="field-name">{field.name}</div>
              <div class="field-tag">Tag: {field.tag}</div>
            </div>
            <div class="field-datatype" style="background-color: {getDatatypeColor(field.datatype)}">
              {field.datatype}
            </div>
          </div>
          
          <div class="field-details">
            {#if field.abbr_name}
              <div class="detail-row">
                <span class="label">Abbreviated:</span>
                <span class="value">{field.abbr_name}</span>
              </div>
            {/if}
            
            {#if field.union_datatype}
              <div class="detail-row">
                <span class="label">Union Type:</span>
                <span class="value">{field.union_datatype}</span>
              </div>
            {/if}
            
            {#if field.description}
              <div class="detail-row description">
                <span class="label">Description:</span>
                <span class="value">{field.description}</span>
              </div>
            {/if}
            
            <div class="detail-row">
              <span class="label">Pedigree:</span>
              <span class="value pedigree">{field.pedigree}</span>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .field-list {
    margin-bottom: 30px;
  }

  h3 {
    color: #ecf0f1;
    font-size: 1.25rem;
    margin-bottom: 15px;
    border-bottom: 2px solid #34495e;
    padding-bottom: 10px;
  }

  .empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #95a5a6;
    background: #2c3e50;
    border-radius: 8px;
    border: 1px solid #34495e;
  }

  .fields-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
  }

  .field-card {
    background: #2c3e50;
    border: 1px solid #34495e;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }

  .field-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    border-color: #3498db;
  }

  .field-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 15px;
  }

  .field-info {
    flex: 1;
    margin-right: 10px;
  }

  .field-name {
    font-weight: 600;
    font-size: 1.1rem;
    color: #ecf0f1;
    margin-bottom: 4px;
  }

  .field-tag {
    color: #95a5a6;
    font-size: 0.9rem;
    font-family: 'Courier New', monospace;
  }

  .field-datatype {
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 500;
    text-align: center;
    white-space: nowrap;
  }

  .detail-row {
    display: flex;
    margin-bottom: 8px;
  }

  .detail-row.description {
    flex-direction: column;
  }

  .label {
    font-weight: 500;
    color: #95a5a6;
    min-width: 100px;
    margin-right: 10px;
  }

  .value {
    color: #ecf0f1;
    flex: 1;
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
  }

  .value.pedigree {
    font-style: italic;
    color: #95a5a6;
  }

  .description .value {
    margin-top: 5px;
    font-family: inherit;
    font-size: 0.9rem;
    line-height: 1.4;
  }
</style>
