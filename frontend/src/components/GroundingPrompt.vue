<script setup>
defineProps({ step: Object, selected: Array, response: String })
defineEmits(['select', 'write'])
</script>

<template>
  <div class="grounding-prompt">
    <p class="intro-copy">{{ step.hint }}</p>
    <p class="sense-boundary" :id="step.id + '-boundary'">Fifer does not sense your surroundings. These are optional prompts, not detected observations.</p>
    <figure v-if="step.image" class="scene">
      <img :src="step.image.src" :alt="step.image.alt" width="800" height="440" />
      <figcaption>{{ step.image.credit }}</figcaption>
    </figure>
    <label class="response-label" :for="step.id + '-response'">Your {{ step.name.toLowerCase() }} observations (optional)</label>
    <textarea :id="step.id + '-response'" :key="step.id" :value="response" rows="3" maxlength="500"
      :aria-describedby="step.id + '-boundary ' + step.id + '-privacy'" autocomplete="off" spellcheck="false"
      @input="$emit('write', $event.target.value)"></textarea>
    <p class="response-note" :id="step.id + '-privacy'">Optional sensory words only; do not enter personal details. Text stays in this tab and is not saved or sent. Skip, Stop, Finish, or reload clears it. No answer or total is required.</p>
    <p class="examples-label" :id="step.id + '-examples'">{{ step.image ? 'Optional examples visible in the picture' : 'Optional examples or no answer' }}</p>
    <div class="choices" role="group" :aria-labelledby="step.id + '-examples'">
      <button v-for="choice in step.choices" :key="choice" class="sensory-choice"
        :aria-pressed="selected.includes(choice)" @click="$emit('select', choice)">
        <span class="selection-mark" aria-hidden="true">{{ selected.includes(choice) ? '✓' : '' }}</span>{{ choice }}
      </button>
    </div>
    <p class="gentle-note">Choose any examples, type, continue without answering, or Skip this step. Nothing is scored.</p>
  </div>
</template>

<style scoped>
.sense-boundary,.response-note,.scene figcaption{font-size:.78rem;line-height:1.65;color:#506277;margin-top:12px}
.scene{margin:22px 0}.scene img{display:block;width:100%;height:auto;border:1px solid #b8c6d3;border-radius:12px}
.scene figcaption{margin-top:8px}.response-label,.examples-label{display:block;font-size:.87rem;font-weight:600;color:#35495e;margin-top:24px}
textarea{display:block;width:100%;max-width:100%;min-height:90px;margin-top:9px;padding:12px;border:1px solid #9aaabd;border-radius:10px;background:#fbfcff;color:#25374a;font:inherit;resize:vertical;scroll-margin-top:240px}
textarea:focus-visible{outline:3px solid #524579;outline-offset:4px}.choices{margin-top:12px}
</style>
