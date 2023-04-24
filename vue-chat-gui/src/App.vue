<template>
  <div id="myapp">
    <div class="chat-container" ref="chatContainer">
      
      <div class="chat-message" v-for="(message, index) in messages" :key="index" :class="message.type">
        <!-- 使用MarkdownViewer组件显示system类型的消息 -->
        <MarkdownViewer v-if="message.type === 'system'" :markdown="message.content" />
        <!-- 直接显示user类型的消息 -->
        <div v-else class="preserve-spaces">{{ message.content }}</div>
      </div>
    </div>
    <div class="bottom-container">
      <textarea class="input" @keydown.shift.enter="handleShiftEnter" v-model="input"
        @keydown.enter.exact.prevent="sendMessage" placeholder="Type your message..." rows="4"></textarea>
      <!-- make the input blue -->

    </div>
  </div>
</template>
<script>
import { ref, reactive, watch, nextTick } from "vue";
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
            nextTick(scrollToBottom);
          });
        } catch (error) {
          console.error("Error making API call:", error);
        }
      }
    }

    watch(messages, () => {
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
  height: 100vh;
  width: 100%;
  background-color: rgb(201, 252, 176);
  /* 设置 app 元素的宽度为 100% */
}

#myapp {
  display: flex;
  height: 100%;
  width: 95vw;
  /* 设置 app 元素的宽度为 100% */
  box-sizing: border-box;
  flex-direction: column;
  justify-content: space-between;
  padding: 20px 0px;
  background-color: #ffffff;
  max-width: 1200px;
  margin: 0 auto;
}

.chat-container {
  flex-grow: 1;
  overflow-y: auto;
  border-radius: 5px;
  padding-bottom: 110px;
  padding-left: 5px;
  padding-right: 5px;
}

.chat-message {
  margin-bottom: 10px;
  padding: 0px;
  border: 2px solid #ccc;
  border-radius: 5px;
  width: fit-content;
  max-width: 100%;
  box-sizing: border-box;
  padding: 5px 10px;
  /* 添加 box-sizing 属性 */
}

.system {
  background-color: #7a7676;
  box-sizing: border-box;
  background-color: #f1f1f1;
}

.user {
  box-sizing: border-box;
  background-color: #ffffff;
  margin-left:auto;
  /* text-align: right; */
}

.bottom-container {
  height: 100px;
  padding: 10px;
  width: inherit; 
  box-sizing: border-box;
  position: fixed;
  bottom: 0;
  left: 50%; /* Add left property */
  transform: translateX(-50%); /* Add transform property */
  max-width: inherit; 
}

.input {
  border-radius: 5px;
  outline: none;
  width: 100%;
  padding: 10px; /* Add some padding to textarea */
  box-sizing: border-box;
}

.preserve-spaces {
  white-space: pre-wrap;
}
</style>