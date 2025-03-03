<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'

/** Initiate I18n composable */
const { t } = useI18n()

/** Initiate PROMPT_MESSAGES with options the user can pick, localized */
const PROMPT_MESSAGES = [
  t('prompt.helpfulAssistant'),
  t('prompt.friendlyWaiter'),
  t('prompt.irishPirate'),
  t('prompt.therapist')
]

/** Define the props this component can receive */
const { onChoose, userColor } = defineProps<{
  /** Function that handles user prompt choice */
  onChoose: (content: string) => void
  /** (Optional) Color of the current user, assigned by the server */
  userColor?: string
}>()

/** HTMLTextAreaElement that holds the user input. Ref used for resizing the field on change events, and for focusing. */
const textArea = ref<HTMLTextAreaElement | undefined>()
/** Input content that the user currently has inside {@link textArea} */
const userInput = ref('')

/**
 * Resize text area (e.g. when the user types a message that takes
 * up more than one line.)
 */
const resizeTextArea = () => {
  if (textArea.value) {
    textArea.value.style.height = 'auto'
    textArea.value.style.height = `${textArea.value.scrollHeight}px`
  }
}

/** Focus on the user textArea input field */
const focusTextArea = () => {
  textArea.value?.focus()
}

/** Handles user selection of the prompt */
const handleChoose = () => {
  onChoose(userInput.value)
}

/** Focus on the textArea and add window resize event listener */
onMounted(() => {
  focusTextArea()
  window.addEventListener('resize', resizeTextArea)
})

/** Remove window resize event */
onUnmounted(() => {
  window.removeEventListener('resize', resizeTextArea)
})
</script>

<template>
  <div
    class="fixed top-0 left-0 right-0 bottom-0"
    @click="focusTextArea"
  >
    <div class="absolute top-0 left-0 right-0 bottom-0 bg-black bg-opacity-50"></div>
    <div
      class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white p-4 rounded-lg shadow-lg w-[90%] max-w-[500px]"
    >
      <div class="text-gray-700 mb-1 text-2xl">
        {{ $t('prompt.giveInstruction') }}
      </div>
      <div class="text-gray-700 mb-4 text-md">
        {{ $t('prompt.howShouldBehave') }}
      </div>
      <hr />
      <div class="mt-2">
        <div
          v-for="msg in PROMPT_MESSAGES"
          :key="msg"
          class="flex items-center justify-between p-2 mt-2 bg-gray-100 rounded-lg cursor-pointer"
          :class="{ 'bg-gray-300': userInput === msg }"
          @click="userInput = msg"
        >
          <div>{{ msg }}</div>
          <div class="text-xs text-gray-500 ml-2">
            {{ $t('choose') }}
          </div>
        </div>
      </div>
      <div class="mt-4">
        <form @submit.prevent="handleChoose">
          <textarea
            class="p-[10px] w-[100%] h-auto overflow-y-hidden text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500"
            rows="1"
            v-model="userInput"
            ref="textArea"
            @keydown.enter.prevent="handleChoose"
            @keyup="resizeTextArea"
            @focus="resizeTextArea"
          ></textarea>
          <div class="flex">
            <div class="grow"></div>
            <button
              class="mt-1 r-0 bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-4 rounded"
              type="submit"
              :style="{ backgroundColor: userColor }"
            >
              {{ $t('send') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
