<script setup lang="ts">
import { LANGUAGES, TOAST_OPTIONS } from '@/utils/constants'
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import { toast } from 'vue3-toastify'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import ChatMessage from './ChatMessage.vue'
import LanguageModal from './LanguageModal.vue'
import PromptModal from './PromptModal.vue'
import type { Language } from '@/types/Language'
import type { Message } from '@/types/Message'

/** Initiate I18n composable */
const { t } = useI18n()

/** String literal representing the types of messages that can be sent */
type SentDataType = 'reset' | 'userMessage' | 'prompt' | 'typing'
/** String literal representing the types of messages that can be received */
type ReceivedDataType = SentDataType | 'aiStart' | 'aiChunk' | 'aiEnd' | 'color'

/** HTMLDivElement that contains the chat, used for scroll-to-bottom functionality */
const chatContainer = ref<HTMLDivElement | undefined>()
/** Array that holds all messages in the current chatbot session (ai, prompt, and from all users) */
const chatMessages = ref<Message[]>([])
/** Whether the AI Assistant is typing up a message (in a processing state) */
const isAiTyping = ref(false)
/** Whether the chatbot UI is initiated (e.g. if the current state has been gathered from the server) */
const isInitiated = ref(false)
/** Whether a language has been explicitly selected */
const isLanguageSelected = ref<boolean>(false)
/** Whether the app is currently locked. Defaults to true until the state of the app is fetched */
const isLocked = ref(true)
/** HTMLTextAreaElement that holds the user input. Ref used for resizing the field on change events, and for focusing. */
const textArea = ref<HTMLTextAreaElement | undefined>()
/** Accent color assigned by the server to the current user in session */
const userColor = ref<string | undefined>()
/** Input content that the user currently has inside {@link textArea} */
const userInput = ref('')
/** Dictionary linking the color hash of each user that is currently typing to the respective timeout code */
const userTypingTimeouts = ref<{ [color: string]: number | undefined }>({})
/** Object that manages the connection to the WebSocket endpoint on our backend service */
const webSocket = ref<WebSocket | undefined>()

/** Scrolls the {@link chatContainer} to the bottom (e.g. when a new message is submitted by a user) */
const scrollToBottom = () => {
  const elm = chatContainer.value
  if (elm) elm.scrollTop = elm.scrollHeight
}

/**
 * Returns true if {@link chatContainer} is currently scrolled to the bottom
 * Used to avoid screen jumps while the AI is streaming.
 */
const isScrolledToBottom = () => {
  const elm = chatContainer.value
  return elm &&
    Math.abs(elm.scrollHeight - elm.scrollTop - elm.clientHeight) < 1
}

/** Streams data to the WebSocket endpoint */
const sendData = (type: SentDataType, content?: string) => {
  if (webSocket.value && webSocket.value.readyState === WebSocket.OPEN) {
    /** If connection is open, send the stringified data. Clean up the input field if needed. */
    webSocket.value.send(
      JSON.stringify({
        type,
        content,
        color: ['typing', 'userMessage'].includes(type) ? userColor.value : undefined,
      }),
    )
    if (type === 'userMessage') userInput.value = ''
  } else {
    /** Otherwise, handle error recovery (e.g. display a toast, show message with error flag) */
    switch (type) {
      case 'prompt':
        chatMessages.value.push({
          role: 'system',
          content: content,
          error: true,
        })
        break
      case 'reset':
        toast.error(t('error.resetting'), TOAST_OPTIONS)
        break
      case 'userMessage':
        chatMessages.value.push({
          role: 'user',
          content: content,
          color: userColor.value,
          error: true,
        })
        toast.error(t('error.sendingMessage'), TOAST_OPTIONS)
    }

    nextTick(() => scrollToBottom())
  }

  /** Focus on the textArea */
  focusTextArea()
}

/**
 * Fetches the current state of the app, this is used to synchronize
 * the client state with the server state when the app is first opened */
const getState = () => {
  axios.get<{ messages: Message[], isLocked: boolean }>('/state')
    .then((res) => {
      chatMessages.value = res.data['messages']
      isLocked.value = res.data['isLocked']
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

/** Submit prompt message */
const createPrompt = (content: string) => {
  sendData('prompt', content)
}

/** Submit user message */
const createUserMessage = () => {
  if (!userInput.value || isLocked.value) return
  sendData('userMessage', userInput.value)
}

/** Empty the chat messages array, synchronizing with all clients */
const clearMessages = () => {
  if (chatMessages.value.length === 0 || isLocked.value) return
  sendData('reset')
}

/** Submit signal to add a typing indicator on all clients' screens */
const handleUserTyping = () => {
  sendData('typing')
}

/**
 * Resize text area (e.g. when the user types a message that takes
 * up more than one line.)
 */
const resizeTextArea = () => {
  if (textArea.value) {
    const wasAtBottom = isScrolledToBottom()

    textArea.value.style.height = 'auto'
    textArea.value.style.height = `${textArea.value.scrollHeight}px`

    if (wasAtBottom) nextTick(() => scrollToBottom())
  }
}

/** 
 * Handle explicit language selection (e.g. user either selected
 * a language or closed the language selection modal on purpose).
 */
const handleSelectLanguage = () => {
  isLanguageSelected.value = true

  /** 
   * Only focus on the textArea if there are chatMessages (e.g.
   * to avoid focusing on a field behind the {@link PromptModal}).
   */
  if (chatMessages.value.length > 0) focusTextArea()
}

/** Focus on the user textArea input field */
const focusTextArea = () => {
  textArea.value?.focus()
}

/** Function that runs when the component is successfully mounted */
onMounted(() => {
  /** Fetch and synchronize with the server state */
  getState()

  /** Connect with the WebSocket endpoint */
  webSocket.value = new WebSocket(import.meta.env.VITE_WEBSOCKET_URL)

  /** Show success toast and unlock the app once WebSocket connects */
  webSocket.value.onopen = () => {
    toast.success(t('connected'), TOAST_OPTIONS)
    isLocked.value = false
  }

  /** Process data received from the server */
  webSocket.value.onmessage = (event: MessageEvent<string>) => {
    const data: { 
      type: ReceivedDataType,
      content?: string,
      color?: string
    } = JSON.parse(event.data)
    /** 
     * Only scroll to bottom in the end of this function if
     * the chat was already scrolled to the bottom to begin with.
     * This is done to avoid screen jumps.
     */
    const wasAtBottom = isScrolledToBottom()

    switch (data.type) {
      case 'reset':
        /** Empty chatMessages */
        chatMessages.value = []
        break
      case 'userMessage':
        /**
         * 1 - Push user message to chatMessages with the respective color
         * 2 - Clear timeouts and delete keys from the timeouts dictionary,
         * that way no more typing indicators are displayed.
         * 3 - Add AI Typing indicator.
         */
        chatMessages.value.push({
          role: 'user',
          content: data.content,
          color: data.color,
        })
        clearTimeout(userTypingTimeouts.value[data.color as string])
        delete userTypingTimeouts.value[data.color as string]
        isAiTyping.value = true
        break
      case 'aiStart':
        /**
         * Create a new AI message, hide AI typing indicator, and lock
         * the app. Prepare for a stream of chunks.
         */
        chatMessages.value.push({
          role: 'assistant',
          content: '',
        })
        isAiTyping.value = false
        isLocked.value = true
        break
      case 'aiChunk':
        /** Add a chunk of stream to the last message on the chat */
        chatMessages.value[chatMessages.value.length - 1].content += data.content as string
        isLocked.value = true
        break
      case 'aiEnd':
        /** Unlock the app */
        isLocked.value = false
        break
      case 'prompt':
        /**
         * Add a system prompt to the messages array (usually
         * done when the session first starts, or when messages
         * are reset)
         */
        chatMessages.value.push({
          role: 'system',
          content: data.content,
        })
        break
      case 'color':
        /**
         * Take note of the color that the server assigned to
         * the current user.
         */
        userColor.value = data.content
        break
      case 'typing':
        /**
         * Display typing indicator for the respective color,
         * clear and set timeouts accordingly 
         */
        clearTimeout(userTypingTimeouts.value[data.color as string])
        userTypingTimeouts.value[data.color as string] = setTimeout(() => {
          delete userTypingTimeouts.value[data.color as string]
        }, 5000)
    }

    if (wasAtBottom) nextTick(() => scrollToBottom())
  }

  /** Display error toast if connection to WebSocket endpoint is closed */
  webSocket.value.onclose = () => {
    toast.error(t('disconnected'), TOAST_OPTIONS)
    isLocked.value = true
  }

  /** Display error toast if error happens on WebSocket endpoint */
  webSocket.value.onerror = () => {
    toast.error(t('error.websocket'), TOAST_OPTIONS)
  }

  /** Add event listener for window resizes */
  window.addEventListener('resize', resizeTextArea)
})

/** Gracefully close the WebSocket connection when unmounting */
onUnmounted(() => {
  if (webSocket.value) {
    webSocket.value.close()
  }
  window.removeEventListener('resize', resizeTextArea)
})
</script>

<template>
  <div class="absolute flex flex-col top-0 left-[50%] bottom-0 w-[100%] -translate-x-[50%] pb-5 pr-5 pl-5 max-w-lg mx-auto my-0 overflow-hidden">
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
      <ChatMessage
        v-for="(message, index) in chatMessages"
        :message="message"
        :key="index"
      />
      <ChatMessage v-if="isAiTyping" :message="{ role: 'assistant' }" />
      <ChatMessage
        v-for="color of Object.keys(userTypingTimeouts)"
        :key="color"
        :message="{ role: 'user', color }"
      />
    </div>
    <div>
      <form @submit.prevent="createUserMessage">
        <textarea
          class="p-[10px] w-[100%] h-auto overflow-y-hidden text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500"
          rows="1"
          v-model="userInput"
          ref="textArea"
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
    v-if="isLanguageSelected && isInitiated && chatMessages.length === 0"
    @choose="createPrompt"
    :userColor="userColor"
    style="z-index: 2"
  />
  <LanguageModal
    v-if="!isLanguageSelected"
    @choose="(language: Language) => {
      $i18n.locale = language
      handleSelectLanguage()
    }"
    @close="handleSelectLanguage"
    style="z-index: 2"
  />
</template>

<style scoped>
.chatContainer::-webkit-scrollbar {
  display: none;
}
</style>
