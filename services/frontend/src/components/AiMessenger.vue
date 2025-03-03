<script setup lang="ts">
import { LANGUAGES } from '@/utils/constants'
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import { toast, type ToastOptions } from 'vue3-toastify'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import ChatMessage from './ChatMessage.vue'
import LanguageModal from './LanguageModal.vue'
import PromptModal from './PromptModal.vue'
import type { Language } from '@/types/Language'
import type { Message } from '@/types/Message'

const { t } = useI18n()

const TOAST_OPTIONS: ToastOptions = {
  position: toast.POSITION.TOP_RIGHT,
  autoClose: 2000,
}

const chatContainer = ref<HTMLDivElement | undefined>()
const userColor = ref<string | undefined>()
const isAiTyping = ref(false)
const isInitiated = ref(false)
const isLanguageSelected = ref<boolean>(false)
const isLocked = ref(true)
const isUserTyping = ref(false)
const messages = ref<Message[]>([])
const userInput = ref('')
const userTypingTimeout = ref<number | undefined>()
const ws = ref<WebSocket | undefined>()

const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const broadcast = (type: 'reset' | 'userMessage' | 'prompt', content?: string) => {
  if (ws.value && ws.value.readyState === WebSocket.OPEN) {
    ws.value.send(
      JSON.stringify({
        type,
        content,
        color: type === 'userMessage' ? userColor.value : undefined,
      }),
    )
    userInput.value = ''
  } else {
    switch (type) {
      case 'prompt':
        messages.value.push({
          role: 'system',
          content: content,
          error: true,
        })
        break
      case 'reset':
        toast.error(t('error.resetting'), TOAST_OPTIONS)
        break
      case 'userMessage':
        messages.value.push({
          role: 'user',
          content: content,
          color: userColor.value,
          error: true,
        })
        toast.error(t('error.sendingMessage'), TOAST_OPTIONS)
    }
  }
}

const getMessages = () => {
  axios
    .get('/messages')
    .then((res) => {
      messages.value = res.data
    })
    .catch((error) => {
      toast.error(t('error.fetchingMessages'), TOAST_OPTIONS)
      console.error(error)
    })
    .finally(() => {
      isInitiated.value = true
      nextTick(() => scrollToBottom())
    })
}

const createPrompt = (content: string) => {
  broadcast('prompt', content)
}

const createUserMessage = () => {
  if (!userInput.value || isLocked.value) return
  broadcast('userMessage', userInput.value)
  clearTimeout(userTypingTimeout.value)
  isUserTyping.value = false;
}

const clearMessages = () => {
  if (messages.value.length === 0 || isLocked.value) return
  broadcast('reset')
}

const resizeTextArea = (event: FocusEvent | KeyboardEvent) => {
  const textarea = event.target as HTMLTextAreaElement
  textarea.style.height = 'auto'
  textarea.style.height = `${textarea.scrollHeight}px`
  nextTick(() => scrollToBottom())
}

const handleUserTyping = () => {
  isUserTyping.value = true

  clearTimeout(userTypingTimeout.value)
  userTypingTimeout.value = setTimeout(() => {
    isUserTyping.value = false
    userTypingTimeout.value = undefined
  }, 3000)
}

onMounted(() => {
  getMessages()

  ws.value = new WebSocket(import.meta.env.VITE_WEBSOCKET_URL)

  ws.value.onopen = () => {
    toast.success(t('connected'), TOAST_OPTIONS)
    isLocked.value = false
  }

  ws.value.onmessage = (event) => {
    const data = JSON.parse(event.data)

    if (data.type === 'reset') messages.value = []
    else if (data.type === 'userMessage') {
      messages.value.push({
        role: 'user',
        content: data.content,
        color: data.color,
      })
      isAiTyping.value = true
      isLocked.value = true
    } else if (data.type === 'assistantMessageStart') {
      messages.value.push({
        role: 'assistant',
        content: '',
      })
      isAiTyping.value = false
    } else if (data.type === 'assistantChunk') {
      messages.value[messages.value.length - 1].content += data.content
    } else if (data.type === 'assistantMessageEnd') {
      isLocked.value = false
    } else if (data.type === 'prompt') {
      messages.value.push({
        role: 'system',
        content: data.content,
      })
    } else if (data.type === 'color') {
      userColor.value = data.content
    }

    nextTick(() => scrollToBottom())
  }

  ws.value.onclose = () => {
    toast.error(t('disconnected'), TOAST_OPTIONS)
    isLocked.value = true
  }

  ws.value.onerror = () => {
    toast.error(t('error.websocket'), TOAST_OPTIONS)
  }
})

onUnmounted(() => {
  if (ws.value) {
    ws.value.close()
  }
})
</script>

<template>
  <div
    class="absolute flex flex-col top-0 left-[50%] bottom-0 w-[100%] -translate-x-[50%] pb-5 pr-5 pl-5 max-w-lg mx-auto my-0 overflow-hidden"
  >
    <div
      class="absolute left-0 top-0 w-[100%] py-5 text-center backdrop-blur-sm bg-white bg-opacity-70 pointer-events-none whitespace-nowrap border-b border-gray border-solid"
      style="z-index: 1"
    >
      <span class="text-3xl">
        {{ $t('title') }}
      </span>
      {{ ' ' }}
      <span class="text-sm">
        {{ $t('byJezzLucena') }}
      </span>
    </div>
    <div ref="chatContainer" class="chatContainer grow overflow-y-scroll pt-[90px]">
      <ChatMessage v-for="(message, index) in messages" :message="message" :key="index" />
      <ChatMessage v-if="isAiTyping" :message="{ role: 'assistant' }" />
      <ChatMessage v-if="isUserTyping" :message="{ role: 'user', color: userColor }" />
    </div>
    <div>
      <form @submit.prevent="createUserMessage">
        <textarea
          class="p-[10px] w-[100%] h-auto overflow-y-hidden text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500"
          rows="1"
          v-model="userInput"
          ref="textarea"
          @keydown="handleUserTyping"
          @keydown.enter.prevent="createUserMessage"
          @keyup="resizeTextArea"
          @focus="resizeTextArea"
        ></textarea>
        <div class="flex font-bold text-xs">
          <div class="grow">
            {{ $t('poweredBy') }}
            <a
              class="underline p-0"
              href="https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct"
              target="_blank"
              >Qwen 2.5</a
            >
          </div>
          <button
            class="ml-2 bg-gray-100 hover:bg-gray-200 text-black py-1 px-2 rounded"
            @click.prevent="() => (isLanguageSelected = false)"
          >
            {{ LANGUAGES[$i18n.locale as Language].short }}
          </button>
          <button
            class="ml-2 bg-gray-100 hover:bg-gray-200 text-black py-1 px-2 rounded"
            @click.prevent="clearMessages"
            :class="{ 'opacity-50 cursor-not-allowed': isLocked }"
          >
            {{ $t('reset') }}
          </button>
          <button
            class="ml-2 bg-blue-500 hover:opacity-70 text-white py-1 px-2 rounded"
            type="submit"
            :class="{ 'opacity-50 cursor-not-allowed': isLocked }"
            :style="{ backgroundColor: userColor }"
          >
            {{ $t('send') }}
          </button>
        </div>
      </form>
    </div>
  </div>

  <PromptModal
    v-if="isLanguageSelected && isInitiated && messages.length === 0"
    @choose="createPrompt"
    :userColor="userColor"
    style="z-index: 2"
  />
  <LanguageModal
    v-if="!isLanguageSelected"
    @choose="(language: Language) => {
      $i18n.locale = language
      isLanguageSelected = true
    }"
    @close="() => {
      isLanguageSelected = true
    }"
    style="z-index: 2"
  />
</template>

<style scoped>
.chatContainer::-webkit-scrollbar {
  display: none;
}
</style>
