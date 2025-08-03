<script lang="ts">
  // Simple test with minimal imports
  let testData = [
    { id: 1, name: 'Test Message 1', type: 'D' },
    { id: 2, name: 'Test Message 2', type: 'A' }
  ];

  let testColumns = [
    { id: 'name', header: 'Name', width: 200 },
    { id: 'type', header: 'Type', width: 100 }
  ];

  console.log('Test data:', testData);
  console.log('Test columns:', testColumns);
</script>

<div class="test-container">
  <h3>Grid Test</h3>
  <p>Data items: {testData.length}</p>
  <div class="data-preview">
    {#each testData as item}
      <div>ID: {item.id}, Name: {item.name}, Type: {item.type}</div>
    {/each}
  </div>
</div>

<style>
  .test-container {
    padding: 20px;
    background: #2c3e50;
    color: #ecf0f1;
  }
  
  .data-preview {
    margin: 10px 0;
    padding: 10px;
    background: #34495e;
    border-radius: 4px;
  }
</style>
