<script lang="ts">
import type { Message } from '@/types/Message';
import axios from 'axios';
import { nextTick, onMounted, onUnmounted, ref } from 'vue';
import PromptModal from './PromptModal.vue';
import { toast } from 'vue3-toastify';
import 'vue3-toastify/dist/index.css';

/** Example of how to use the Options API */
export default {
  name: 'AiMessenger',
  setup() {
    const chatContainer = ref<HTMLDivElement | null>(null);
    const message = ref("");
    const messages = ref<Message[]>([]);
    const isProcessing = ref(false);
    const isTyping = ref(false);
    const isInitiated = ref(false);
    const isTestMode = ref(false);
    const ws = ref<WebSocket | null>(null);

    const scrollToBottom = () => {
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
      }
    };

    onMounted(() => {
      ws.value = new WebSocket(import.meta.env.VITE_WEBSOCKET_URL);

      ws.value.onopen = () => {
        console.log('Connected to WebSocket server');
      };

      ws.value.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'reset') messages.value = [];
        else if (data.type === 'userMessage') {
          messages.value.push({
            role: 'user',
            content: data.content
          });
          isTyping.value = true;
          isProcessing.value = true;
        } else if (data.type === 'assistantMessageStart') {
          messages.value.push({
            role: 'assistant',
            content: ''
          });
          isTyping.value = false;
        } else if (data.type === 'assistantChunk') {
          messages.value[messages.value.length-1].content += data.content;
        } else if (data.type === 'assistantMessageEnd') {
          isProcessing.value = false;
        } else if (data.type === 'prompt') {
          messages.value.push({
            role: 'system',
            content: data.content
          });
        }

        nextTick(() => scrollToBottom());
      };

      ws.value.onclose = () => {
        console.log('Disconnected from WebSocket server');
      };

      ws.value.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    });

    onUnmounted(() => {
      if (ws.value) {
        ws.value.close();
      }
    });

    const sendMessage = (type: 'reset' | 'userMessage' | 'prompt', content?: string) => {
      if (ws.value && ws.value.readyState === WebSocket.OPEN) {
        ws.value.send(JSON.stringify({ type, content }));
        message.value = '';
      }
    }

    return {
      chatContainer,
      sendMessage,
      scrollToBottom,
      message,
      messages,
      isProcessing,
      isTyping,
      isInitiated,
      isTestMode,
    };
  },
  methods: {
    getMessages() {
      axios.get('/messages')
        .then((res) => {
          this.messages = res.data;
        })
        .catch((error) => {
          toast.error("Failed to fetch messages.", { position: toast.POSITION.BOTTOM_RIGHT });
          console.error(error);
        })
        .finally(() => {
          this.isInitiated = true;
          nextTick(() => this.scrollToBottom());
        });
    },
    createPrompt(content: string) {
      this.sendMessage('prompt', content);
    },
    createUserMessage() {
      if (!this.message || this.isProcessing) return;
      this.sendMessage('userMessage', this.message);
    },
    clearMessages() {
      this.sendMessage('reset');
    },
    resizeTextArea(event: FocusEvent | KeyboardEvent) {
      const textarea = event.target as HTMLTextAreaElement;
      textarea.style.height = "auto";
      textarea.style.height = `${textarea.scrollHeight}px`;
      nextTick(() => this.scrollToBottom());
    },
  },
  created() {
    this.getMessages();
  },
  components: {
    PromptModal,
  },
};
</script>

<template>
  <div class="relative flex flex-col h-[100vh] w-[100%] pb-5 pr-5 pl-5 max-w-lg mx-auto my-0">
    <div class="absolute left-0 top-0 w-[100%] py-5 text-center text-3xl backdrop-blur-sm bg-white bg-opacity-90 pointer-events-none whitespace-nowrap border-b border-gray border-solid" style="z-index: 1;">AI Chatbot <span class="text-sm">by Jezz Lucena</span></div>
    <div ref="chatContainer" class="chatContainer grow overflow-y-scroll pt-[90px]">
      <div class="flex mb-3" v-for="(msg, index) in messages" :key="index">
        <div v-if="msg.role === 'user'" class="grow min-w-[20%]"></div>
        <div class="relative" :class="{ 'pb-5': msg.error, 'mx-auto': msg.role === 'system', 'max-w-[80%]': msg.role !== 'system' }">
          <div
            class="relative rounded-md py-2 px-4"
            :class="{
              'border border-gray-300 bg-white-100 px-6 text-center text-sm': msg.role === 'system',
              'userMessage bg-blue-500 text-white mr-2': msg.role === 'user',
              'aiMessage bg-gray-100 ml-2': msg.role === 'assistant'
            }"
          >
            <pre class="overflow-x-auto whitespace-pre-wrap break-words text-sm hyphens-auto">{{ msg.content }}</pre>
          </div>
          <div
            v-if="msg.error"
            class="mx-2 text-xs absolute bottom-0 text-nowrap"
            :class="{
              'left-1/2 transform -translate-x-1/2': msg.role === 'system',
              'right-0': msg.role === 'user',
              'left-0': msg.role === 'assistant'
            }"
          >Error sending message</div>
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
        <div class="flex">
          <button
            class="mt-1 r-0 bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-4 rounded"
            type="submit"
            :class="{ 'bg-blue-300 pointer-events-none': isProcessing }">Send</button>
          <button
            class="mt-1 ml-3 bg-gray-100 hover:bg-gray-200 text-black font-bold py-1 px-4 rounded"
            @click.prevent="clearMessages">Reset</button>
          <div class="grow text-right text-xs">powered by<a class="underline" href="https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct" target="_blank">Qwen 2.5</a></div>
        </div>
      </form>
    </div>
  </div>

  <PromptModal v-if="isInitiated && messages.length === 0" @choose="createPrompt" style="z-index: 2;"/>
</template>

<style scoped>
.chatContainer::-webkit-scrollbar {
    display: none;
}

.userMessage, .aiMessage {
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    border-top: 15px solid transparent;
  }
}

.userMessage::after {
  right: -6px;
  border-left: 13px solid rgb(59 130 246);
}

.aiMessage::after {
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
