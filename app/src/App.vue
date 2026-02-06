<template>
  <Suspense>
    <template #default>
      <EscrowScreen />
    </template>
    <template #fallback>
      <div class="flex items-center justify-center h-screen">
        <div class="text-gray-400">Loading...</div>
      </div>
    </template>
  </Suspense>
</template>

<script setup>
import EscrowScreen from "./components/EscrowScreen.vue";
</script>
