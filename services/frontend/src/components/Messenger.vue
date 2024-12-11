<template>
  <div style="width: 100%; max-width: 400px; margin: 0 auto;">
    <div class="mb-3 text-center">VueJS AI Chatbot <span class="text-xs">by Jezz Lucena</span></div>
    <div v-for="msg in messages">
      <div
        class="mb-3 rounded py-2 px-4"
        :class="{
          'border border-gray-300': msg.role === 'system',
          'bg-blue-500 text-white w-[80%] ml-[20%]': msg.role === 'user',
          'bg-gray-100 w-[80%]': msg.role === 'assistant'
        }"
      >
        <div v-if="msg.role === 'system'" class="text-xs">System Prompt:</div>
        <pre style="overflow-x: auto; white-space: pre-wrap; word-wrap: break-word;">{{ msg.content }}</pre>
      </div>
    </div>
    <div>
      <form @submit.prevent="createMessage">
        <textarea
          class="block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
          style="width: 100%;"
          v-model="message"
          @keyup.enter="createMessage"
        ></textarea>
        <button
          class="mt-3 mb-3 r-0 bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-4 rounded"
          type="submit"
        >Send</button>
        <button
          class="mt-3 mb-3 ml-3 bg-gray-100 hover:bg-gray-200 text-black font-bold py-1 px-4 rounded"
          @click.prevent="clearMessages"
        >Reset</button>
      </form>
    </div>
    <div class="mt-3 text-right text-xs">powered by<a href="https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct" target="_blank">Qwen2.5-1.5B-Instruct</a></div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Messages',
  data() {
    return {
      messages: [],
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
      const newMsg = { role: "user", content: this.message };
      this.messages.push(newMsg);

      axios.post('/messages', newMsg)
        .then((res) => {
          this.messages.push(res.data);
        })
        .catch((error) => {
          console.error(error);
        });

      this.message = '';
    },
    clearMessages() {
      axios.get('/clear_messages')
        .then((res) => {
          this.messages = res.data;
        })
        .catch((error) => {
          console.error(error);
        });
    },
  },
  created() {
    this.getMessages();
  },
};
</script>