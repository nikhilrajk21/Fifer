<script setup>
import { SUPPORT_TEXT } from '../safety-content.js'
defineEmits(['close', 'stop'])
</script>

<template>
  <section class="dialog support-dialog" role="dialog" aria-modal="true" aria-labelledby="support-title">
    <p class="eyebrow">Available throughout</p>
    <h2 id="support-title" tabindex="-1" data-dialog-heading>Emergency Support</h2>
    <p class="support-copy">{{ SUPPORT_TEXT }}</p>
    <p class="prototype-note">Coursework prototype · Fictional scenarios only</p>
    <div class="dialog-actions">
      <button class="button primary" @click="$emit('close')">Return</button>
      <button class="button quiet" @click="$emit('stop')">Stop/Leave</button>
    </div>
  </section>
</template>

