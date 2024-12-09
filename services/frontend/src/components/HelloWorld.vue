<template>
  <div v-for="msg in messages">
    <div class="mb-3">
      <div>{{ msg.role }}: </div>
      <pre style="overflow-x: auto; white-space: pre-wrap; word-wrap: break-word;">{{ msg.content }}</pre>
    </div>
  </div>
  <div>
    <form @submit.prevent="createMessage">
      <textarea
        class="block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
        v-model="message"
        rows="1"
        cols="35"
        @keyup.enter="createMessage"
      ></textarea>
      <button
        class="mt-3 mb-3 r-0 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        type="submit"
      >Send</button>
    </form>
    <form @submit.prevent="clearMessages">
      <button
        class="mt-3 mb-3 r-0 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        type="submit"
      >Reset</button>
    </form>
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