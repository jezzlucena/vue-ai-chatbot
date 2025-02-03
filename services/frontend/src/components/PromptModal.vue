<script setup lang="ts">
import { ref, defineProps, onMounted, onUnmounted } from 'vue';

const textarea = ref<HTMLTextAreaElement | null>(null);

const PROMPT_MESSAGES = [
  "You are a helpful assistant.",
  "You are a friendly waiter at a busy restaurant.",
  "You are a pirate with a heavy Irish accent.",
  "You are a cognitive-behavioural therapist."
];

const props = defineProps<{
  onChoose: (content: string) => void
}>();

const content = ref("");

const resizeTextArea = () => {
  if (!!textarea.value) {
    textarea.value.style.height = "auto";
    textarea.value.style.height = `${textarea.value.scrollHeight}px`;
  }
}

const handleChoose = () => {
  props.onChoose?.(content.value);
}

onMounted(() => {
  window.addEventListener('resize', resizeTextArea);
});

onUnmounted(() => {
  window.removeEventListener('resize', resizeTextArea);
});
</script>

<template>
  <div class="fixed top-0 left-0 right-0 bottom-0">
    <div class="absolute top-0 left-0 right-0 bottom-0 bg-black bg-opacity-50"></div>
    <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white p-4 rounded-lg shadow-lg w-[90%] max-w-[600px]">
      <p class="text-gray-700 mb-4 text-2xl">Give the AI assistant an "instruction." How should they behave during this conversation?</p>
      <hr/>
      <div v-for="msg in PROMPT_MESSAGES" :key="msg" class="flex items-center justify-between p-2 mt-4 bg-gray-100 rounded-lg cursor-pointer" @click="content = msg">
        <div>{{ msg }}</div>
        <div class="text-xs text-gray-500 ml-2">Choose</div>
      </div>
      <div class="mt-4">
        <form @submit.prevent="handleChoose">
          <textarea
            class="p-[10px] w-[100%] h-auto overflow-y-hidden text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500"
            rows="1"
            v-model="content"
            ref="textarea"
            @keydown.enter.prevent="handleChoose"
            @keyup="resizeTextArea"
            @focus="resizeTextArea"
          ></textarea>
          <div class="flex">
            <button
              class="mt-1 r-0 bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-4 rounded"
              type="submit">Send</button>
        </div>
        </form>
      </div>
    </div>
  </div>
</template>