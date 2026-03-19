<template>
  <div class="configuration-center">
    <div class="content-area">
      <router-view />
    </div>
  </div>
</template>

<script setup>
// No script logic needed for now
</script>

<style scoped>
.configuration-center {
  height: 100%;
  width: 100%;
}

.content-area {
  height: 100%;
  padding: 20px;
  overflow-y: auto;
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
}


</style>
