<script lang="ts">
  import type { Message } from '../lib/api-client';
  
  interface Props {
    messages: Message[];
    selectedVersion: string;
  }

  let { messages, selectedVersion }: Props = $props();

  function getCategoryColor(category: string): string {
    const colors: Record<string, string> = {
      'Session': '#28a745',
      'UserRequest': '#007bff',
      'Advertisement': '#ffc107',
      'Indication': '#17a2b8',
      'Order': '#6f42c1',
      'Execution': '#dc3545',
      'Trade': '#fd7e14',
      'Confirmation': '#20c997',
      'Allocation': '#6c757d',
      'Settlement': '#e83e8c',
      'News': '#343a40'
    };
    return colors[category] || '#6c757d';
  }
</script>

<div class="message-list">
  <h3>Messages ({messages.length})</h3>
  
  {#if messages.length === 0}
    <div class="empty-state">
      <p>No messages found for the current search and version.</p>
    </div>
  {:else}
    <div class="messages-grid">
      {#each messages as message}
        <div class="message-card">
          <div class="message-header">
            <div class="message-name">{message.name}</div>
            <div class="message-type" style="background-color: {getCategoryColor(message.category_id || 'Unknown')}">
              {message.category_id || 'Unknown'}
            </div>
          </div>
          
          <div class="message-details">
            <div class="detail-row">
              <span class="label">Message Type:</span>
              <span class="value">{message.msg_type}</span>
            </div>
            
            <div class="detail-row">
              <span class="label">Component ID:</span>
              <span class="value">{message.component_id}</span>
            </div>
            
            {#if message.description}
              <div class="detail-row description">
                <span class="label">Description:</span>
                <span class="value">{message.description}</span>
              </div>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .message-list {
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

  .messages-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
  }

  .message-card {
    background: #2c3e50;
    border: 1px solid #34495e;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }

  .message-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    border-color: #3498db;
  }

  .message-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 15px;
  }

  .message-name {
    font-weight: 600;
    font-size: 1.1rem;
    color: #ecf0f1;
    flex: 1;
    margin-right: 10px;
  }

  .message-type {
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 500;
    text-align: center;
    white-space: nowrap;
    background: #3498db;
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
    min-width: 120px;
    margin-right: 10px;
  }

  .value {
    color: #ecf0f1;
    flex: 1;
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
  }

  .description .value {
    margin-top: 5px;
    font-family: inherit;
    font-size: 0.9rem;
    line-height: 1.4;
  }
</style>
