<script setup lang="ts">
import CustomQuery from '@/components/CustomQuery.vue'
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-bold tracking-tight">Custom Query</h1>
      <p class="text-muted-foreground mt-2">
        Filter and analyze games based on specific players and roles
      </p>
    </div>

    <CustomQuery />
  </div>
</template>
