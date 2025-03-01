<script setup lang="ts">
import type { Message } from '@/types/Message';
import axios from 'axios';
import { nextTick, onMounted, onUnmounted, ref } from 'vue';
import PromptModal from './PromptModal.vue';
import LanguageModal from './LanguageModal.vue';
import { toast, type ToastOptions } from 'vue3-toastify';
import 'vue3-toastify/dist/index.css';
import type { Language } from '@/types/Language';
import { useI18n } from 'vue-i18n';
import { LANGUAGES } from '@/utils/constants'

const { t } = useI18n();

const TOAST_OPTIONS: ToastOptions = { position: toast.POSITION.BOTTOM_RIGHT };

const chatContainer = ref<HTMLDivElement | null>(null);
const message = ref("");
const messages = ref<Message[]>([]);
const isLocked = ref(true);
const isTyping = ref(false);
const isInitiated = ref(false);
const language = ref<Language | null>(null);
const ws = ref<WebSocket | null>(null);
const color = ref<string | null>(null);

const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

const sendMessage = (type: 'reset' | 'userMessage' | 'prompt', content?: string) => {
  if (ws.value && ws.value.readyState === WebSocket.OPEN) {
    ws.value.send(JSON.stringify({ type, content, color: type === 'userMessage' ? color.value : undefined }));
    message.value = '';
  } else {
    switch (type) {
      case 'prompt':
        messages.value.push({ role: 'system', content: content || '', error: true })
        break;
      case 'reset':
        toast.error(t("error.resetting"), TOAST_OPTIONS)
        break;
      case 'userMessage':
        messages.value.push({ role: 'user', content: content || '', color: color.value || '', error: true });
        toast.error(t("error.sendingMessage"), TOAST_OPTIONS)
    }
  }
}

const getMessages = () => {
  axios.get('/messages')
    .then((res) => {
      messages.value = res.data;
    })
    .catch((error) => {
      toast.error(t("error.fetchingMessages"), { position: toast.POSITION.BOTTOM_RIGHT });
      console.error(error);
    })
    .finally(() => {
      isInitiated.value = true;
      nextTick(() => scrollToBottom());
    });
}

const createPrompt = (content: string) => {
  sendMessage('prompt', content);
}

const createUserMessage = () => {
  if (!message.value || isLocked.value) return;
  sendMessage('userMessage', message.value);
}

const clearMessages = () => {
  if (messages.value.length === 0 || isLocked.value) return;
  sendMessage('reset');
}

const resizeTextArea = (event: FocusEvent | KeyboardEvent) => {
  const textarea = event.target as HTMLTextAreaElement;
  textarea.style.height = "auto";
  textarea.style.height = `${textarea.scrollHeight}px`;
  nextTick(() => scrollToBottom());
}

onMounted(() => {
  getMessages();

  ws.value = new WebSocket(import.meta.env.VITE_WEBSOCKET_URL);

  ws.value.onopen = () => {
    toast.success(t("connected"), TOAST_OPTIONS);
    isLocked.value = false;
  };

  ws.value.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === 'reset') messages.value = [];
    else if (data.type === 'userMessage') {
      messages.value.push({
        role: 'user',
        content: data.content,
        color: data.color
      });
      isTyping.value = true;
      isLocked.value = true;
    } else if (data.type === 'assistantMessageStart') {
      messages.value.push({
        role: 'assistant',
        content: ''
      });
      isTyping.value = false;
    } else if (data.type === 'assistantChunk') {
      messages.value[messages.value.length-1].content += data.content;
    } else if (data.type === 'assistantMessageEnd') {
      isLocked.value = false;
    } else if (data.type === 'prompt') {
      messages.value.push({
        role: 'system',
        content: data.content
      });
    } else if (data.type === 'color') {
      color.value = data.content;
    }

    nextTick(() => scrollToBottom());
  };

  ws.value.onclose = () => {
    toast.error(t("disconnected"), TOAST_OPTIONS);
    isLocked.value = true;
  };

  ws.value.onerror = () => {
    toast.error(t("error.websocket"), TOAST_OPTIONS);
  };
});

onUnmounted(() => {
  if (ws.value) {
    ws.value.close();
  }
});
</script>

<template>
  <div class="absolute flex flex-col top-0 left-[50%] bottom-0 w-[100%] -translate-x-[50%] pb-5 pr-5 pl-5 max-w-lg mx-auto my-0 overflow-hidden">
    <div class="absolute left-0 top-0 w-[100%] py-5 text-center text-3xl backdrop-blur-sm bg-white bg-opacity-90 pointer-events-none whitespace-nowrap border-b border-gray border-solid" style="z-index: 1;">{{ $t("title") }} <span class="text-sm">{{ $t("byJezzLucena") }}</span></div>
    <div ref="chatContainer" class="chatContainer grow overflow-y-scroll pt-[90px]">
      <div class="flex mb-3" v-for="(msg, index) in messages" :key="index">
        <div v-if="msg.role === 'user'" class="grow min-w-[20%]"></div>
        <div class="relative" :class="{ 'pb-5': msg.error, 'mx-auto': msg.role === 'system', 'max-w-[80%]': msg.role !== 'system' }">
          <div
            class="relative rounded-md py-2 px-4"
            :class="{
              'border border-gray-300 bg-white-100 px-6 text-center': msg.role === 'system',
              'userMessage text-white mr-2': msg.role === 'user',
              'aiMessage bg-gray-100 ml-2': msg.role === 'assistant'
            }"
            :style="{ backgroundColor: msg.color }"
          >
            <pre
              class="overflow-x-auto whitespace-pre-wrap break-words text-sm hyphens-auto"
              :class="{ 'text-xs': msg.role === 'system' }"
            >{{ msg.content }}</pre>
            <div class="triangle" :style="{ borderLeftColor: msg.color }"></div>
          </div>
          <div
            v-if="msg.error"
            class="mx-2 text-xs absolute bottom-0 text-nowrap"
            :class="{
              'left-1/2 transform -translate-x-1/2': msg.role === 'system',
              'right-0': msg.role === 'user',
              'left-0': msg.role === 'assistant'
            }"
          >{{ $t("error.sendingMessage") }}</div>
        </div>
        <div v-if="msg.role === 'assistant'" class="grow min-w-[20%]"></div>
      </div>
      <div class="flex">
        <div v-if="isTyping" class="aiMessage relative ml-2 mb-3 rounded py-2 px-4 bg-gray-100">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
        <div class="grow min-w-[20%]"></div>
      </div>
    </div>
    <div>
      <form @submit.prevent="createUserMessage">
        <textarea
          class="p-[10px] w-[100%] h-auto overflow-y-hidden text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500"
          rows="1"
          v-model="message"
          ref="textarea"
          @keydown.enter.prevent="createUserMessage"
          @keyup="resizeTextArea"
          @focus="resizeTextArea"
        ></textarea>
        <div class="flex font-bold text-xs">
          <div class="grow">powered by<a class="underline" href="https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct" target="_blank">Qwen 2.5</a></div>
          <button
            v-if="language"
            class="ml-2 mt-1 bg-gray-100 hover:bg-gray-200 text-black py-1 px-2 rounded"
            @click.prevent="() => language = null"
          >{{ LANGUAGES[language] }}</button>
          <button
            class="ml-2 mt-1 bg-gray-100 hover:bg-gray-200 text-black py-1 px-2 rounded"
            @click.prevent="clearMessages"
            :class="{ 'opacity-50 cursor-not-allowed': isLocked }"
          >{{ $t("reset") }}</button>
          <button
            class="ml-2 mt-1 bg-blue-500 hover:opacity-70 text-white py-1 px-2 rounded"
            type="submit"
            :class="{ 'opacity-50 cursor-not-allowed': isLocked }"
            :style="{ backgroundColor: color || '' }"
          >{{ $t("send") }}</button>
        </div>
      </form>
    </div>
  </div>

  <PromptModal v-if="language && isInitiated && messages.length === 0" @choose="createPrompt" style="z-index: 2;"/>
  <LanguageModal v-if="!language"
    @choose="(lang: Language) => {
      language = lang;
      $i18n.locale = language;
    }"
    style="z-index: 2;"
  />
</template>

<style scoped>
.chatContainer::-webkit-scrollbar {
    display: none;
}

.userMessage, .aiMessage {
  .triangle {
    content: '';
    position: absolute;
    bottom: 0;
    border-top: 15px solid transparent;
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

.dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: #2c3e50;
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

@keyframes dot {
  0%, 40% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
  60%, 100% {
    transform: translateY(0);
  }
}
</style>
