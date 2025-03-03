<script setup lang="ts">
import type { Message } from '@/types/Message'

defineProps<{
  message: Message
}>()
</script>

<template>
  <div class="flex mb-3">
    <div v-if="message.role === 'user'" class="grow min-w-[20%]"></div>
    <div
      class="relative"
      :class="{
        'pb-5': message.error,
        'mx-auto': message.role === 'system',
        'max-w-[80%]': message.role !== 'system',
      }"
    >
      <div
        class="relative rounded-md py-2 px-4"
        :class="{
          'border border-gray-300 bg-white-100 px-6 text-center': message.role === 'system',
          'userMessage bg-blue-500 text-white mr-2': message.role === 'user',
          'aiMessage bg-gray-100 ml-2': message.role === 'assistant',
        }"
        :style="{ backgroundColor: message.color }"
      >
        <pre
          v-if="message.content"
          class="overflow-x-auto whitespace-pre-wrap break-words text-sm hyphens-auto"
          :class="{ 'text-xs': message.role === 'system' }"
        >{{ message.content }}</pre>
        <div v-else>
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
        <div class="triangle" :style="{ borderLeftColor: message.color }"></div>
      </div>
      <div
        v-if="message.error"
        class="mx-2 text-xs absolute bottom-0 text-nowrap"
        :class="{
          'left-1/2 transform -translate-x-1/2': message.role === 'system',
          'right-0': message.role === 'user',
          'left-0': message.role === 'assistant',
        }"
      >
        {{ $t('error.sendingMessage') }}
      </div>
    </div>
    <div v-if="message.role === 'assistant'" class="grow min-w-[20%]"></div>
  </div>
</template>

<style scoped>
.userMessage,
.aiMessage {
  .triangle {
    content: '';
    position: absolute;
    bottom: 0;
    border-top: 15px solid transparent;
  }

  .dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    animation: dot 1.5s infinite;

    &:not(:last-child) {
      margin-right: 3px;
    }

    &:nth-child(1) {
      animation-delay: 0s;
    }

    &:nth-child(2) {
      animation-delay: 0.2s;
    }

    &:nth-child(3) {
      animation-delay: 0.4s;
    }
  }
}

.userMessage .triangle {
  right: -6px;
  border-left: 13px solid;
}

.aiMessage .triangle {
  left: -6px;
  border-right: 13px solid rgb(243 244 246);
}

.aiMessage .dot {
  background-color: #2c3e50;
}

.userMessage .dot {
  background-color: white;
}

@keyframes dot {
  0%,
  40% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
  60%,
  100% {
    transform: translateY(0);
  }
}
</style>
