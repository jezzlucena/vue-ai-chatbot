<template>
  <div class="flex flex-col h-[100vh] w-[100%] p-5 max-w-lg mx-auto my-0">
    <div class="mb-4 text-center text-3xl">VueJS AI Chatbot <span class="text-sm">by Jezz Lucena</span></div>
    <div ref="chatContainer" class="grow shrink overflow-scroll">
      <div class="flex mb-3" v-for="msg in messages">
        <div v-if="msg.role === 'user'" class="grow min-w-[20%]"></div>
        <div class="relative" :class="{ 'pb-5': msg.error }">
          <div
            class="rounded py-2 px-4"
            :class="{
              'border border-gray-300': msg.role === 'system',
              'userMessage bg-blue-500 text-white mr-2': msg.role === 'user',
              'aiMessage bg-gray-100 ml-2': msg.role === 'assistant'
            }"
          >
            <div v-if="msg.role === 'system'" class="text-xs">System Prompt:</div>
            <pre style="overflow-x: auto; white-space: pre-wrap; word-wrap: break-word;">{{ msg.content }}</pre>
          </div>
          <div v-if="msg.error" class="text-sm absolute right-0 bottom-0 text-nowrap">Error sending message</div>
        </div>
        <div v-if="msg.role === 'assistant'" class="grow min-w-[20%]"></div>
      </div>
      <div class="flex">
        <div v-if="isTyping" class="mb-3 rounded py-2 px-4 bg-gray-100">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
        <div class="grow min-w-[20%]"></div>
      </div>
    </div>
    <div>
      <form @submit.prevent="createMessage">
        <textarea
          class="p-[10px] text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500"
          style="width: 100%; height: auto; overflow-y: hidden;"
          rows="1"
          v-model="message"
          ref="textarea"
          @keydown.enter.prevent="createMessage"
          @keyup="resizeTextarea"
          @focus="resizeTextarea"
        ></textarea>
        <div class="flex">
          <button
            class="mt-1 r-0 bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-4 rounded"
            type="submit"
            :class="{ 'bg-blue-300 pointer-events-none': isProcessing }">Send</button>
          <button
            class="mt-1 ml-3 bg-gray-100 hover:bg-gray-200 text-black font-bold py-1 px-4 rounded"
            @click.prevent="clearMessages">Reset</button>
          <div class="grow text-right text-xs">powered by<a href="https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct" target="_blank">Qwen2.5-1.5B-Instruct</a></div>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.userMessage, .aiMessage {
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    border-top: 13px solid transparent;
  }
}

.userMessage::after {
  right: 0;
  border-left: 10px solid rgb(59 130 246);
}

.aiMessage::after {
  left: 0;
  border-right: 10px solid rgb(243 244 246);
}

.dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: black;
  animation: dot 1.5s infinite;

  &:not(:last-child) {
    margin-right: 5px;
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

<script>
import axios from 'axios';
import { nextTick, onMounted, ref } from 'vue';

export default {
  name: 'Messages',
  setup() {
    const chatContainer = ref(null);

    const scrollToBottom = () => {
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
      }
    };

    onMounted(() => {
      scrollToBottom(); // Scroll to bottom on initial load
    });

    return { chatContainer, scrollToBottom };
  },
  data() {
    return {
      messages: [],
      isProcessing: false,
      isTyping: false,
    };
  },
  methods: {
    getMessages() {
      axios.get('/messages')
        .then((res) => {
          this.messages = res.data;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    createMessage() {
      if (!this.message || this.isProcessing) return;

      // Test mode
      // Change this to true to simulate a chatbot response
      const isTestMode = false;

      this.isProcessing = true;

      const typingTimeout = setTimeout(() => {
        this.isTyping = true;
      }, 500);
      
      const userMessage = { role: "user", content: this.message };
      this.messages.push(userMessage);
      
      nextTick(() => this.scrollToBottom());

      if (isTestMode) {
        setTimeout(() => {
          const aiMessage = { role: "assistant", content: "I'm sorry, I'm just a demo chatbot. I can't respond to your message." };
          this.messages.push(aiMessage);
          this.isProcessing = false;
          this.isTyping = false;

          nextTick(() => this.scrollToBottom());
        }, 2000);
      } else {
        axios.post('/messages', userMessage)
          .then((res) => {
            this.messages.push(res.data);
            nextTick(() => this.scrollToBottom());
          })
          .catch((error) => {
            userMessage.error = true;
            console.error(error);
          })
          .finally(() => {
            this.isProcessing = false;
            this.isTyping = false;
            clearTimeout(typingTimeout);
          });
      }

      this.message = "";
    },
    clearMessages() {
      axios.delete('/messages')
        .then((res) => {
          this.messages = res.data;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    resizeTextarea(event) {
      const textarea = event.target;
      textarea.style.height = "auto";
      textarea.style.height = `${textarea.scrollHeight}px`;
      nextTick(() => this.scrollToBottom());
    },
  },
  created() {
    this.getMessages();
  },
};
</script>