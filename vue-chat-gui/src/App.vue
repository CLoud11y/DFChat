<template>
  <div id="myapp">
    <div class="chat-container" ref="chatContainer">
      
      <div class="chat-message" v-for="(message, index) in messages" :key="index" :class="message.type">
          <MarkdownViewer :markdown=message.content />
      </div>
    </div>
    <div class="input-container">
      <textarea class="input" @keydown.shift.enter="handleShiftEnter" v-model="input"
        @keydown.enter.exact.prevent="sendMessage" placeholder="Type your message..." rows="4"></textarea>
      <!-- make the input blue -->

    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick } from "vue";
import axios from 'axios'
import MarkdownViewer from './components/MarkdownViewer.vue';

export default {
  setup() {
    const input = ref("");
    const messages = reactive([
      // { type: "system", content: "Welcome to the chat!" },
    ]);
    const chatContainer = ref(null);
    function scrollToBottom() {
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
      }
    };

    function sendMessage() {
      if (input.value.trim() !== "") {
        const user_content = input.value.trim();
        messages.push({ type: "user", content: user_content });
        input.value = "";

        try {
          const headers = {
            'Content-Type': 'application/json',
          };
          // Replace below URL with the actual API URL you want to call
          const messagesList = messages.map(message => {
            return {
              type: message.type,
              content: message.content
            };
          });
          const response = axios.post("/api/gpt4", { "query": messagesList }, { headers: headers }).then((response) => {
            console.log(response.data);
            messages.push({ type: "system", content: response.data });
          });
          // console.log(response.data);
          // messages.push({ type: "system", content: response });
        } catch (error) {
          console.error("Error making API call:", error);
        }


        nextTick(() => {
          scrollToBottom(); // 新增此行
        });
      }
    }

    onMounted(() => {
      scrollToBottom();
    });

    return { input, messages, sendMessage, chatContainer };
  },
  methods: {
    handleShiftEnter(event) {
      event.preventDefault(); // 阻止默认事件行为
      this.input += '\n'; // 在当前文本中插入换行符
    },
  },
  components: {
    MarkdownViewer
  }
}
</script>

<style>
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  font-size: large;
  display: flex;
  height: 100vh;
  width: 100%;
  background-color: rgb(255, 255, 255);
  /* 设置 app 元素的宽度为 100% */
}

#myapp {
  height: 100%;
  width: 95vw;
  /* 设置 app 元素的宽度为 100% */
  align-items: center;
  box-sizing: border-box;
  flex-direction: column;
  justify-content: space-between;
  padding: 20px;
  /* background-color: #f5f5f5; */
  max-width: 100%;
}

.chat-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow-y: auto;
  width: 100%;
  /* 设置 chat-container 元素的宽度为 100% */
  border-radius: 5px;
}

.chat-message {
  margin-bottom: 10px;
  padding: 10px;
  border-radius: 5px;
  width: fit-content;
  /* 设置 chat-message 元素的宽度为 100% */
  box-sizing: border-box;
  /* 添加 box-sizing 属性 */
}

.system {
  background-color: #7a7676;
  padding: 4px;
  box-sizing: border-box;
  background-color: #f1f1f1;
  border: 1px solid #ccc;
}

.user {
  padding: 4px;
  box-sizing: border-box;
  background-color: #ffffff;
  border: 1px solid #ccc;
  margin-left:auto;
  text-align: right;
}

.input-container {
  width: 100%;
  max-width: 600px;
  padding: 10px;
  box-sizing: border-box;
}

.input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  outline: none;
  position: fixed;
  bottom: 0;
  width: 100%;
  left: 0;
}
</style>