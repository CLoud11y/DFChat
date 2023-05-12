<template>
  <div id="main-window">
    <div id="history-container">
      <div class="history-message" v-for="(history, index) in histories" :key="'history-' + index">
        {{ history.content }}
      </div>
    </div>
    <div class="chat-container" ref="chatContainer">
      <div id="chat-window">
        <div class="chat-message" v-for="(message, index) in messages" :key="index" :class="message.type">
          <!-- 使用MarkdownViewer组件显示assistant类型的消息 -->
          <MarkdownViewer v-if="message.type === 'assistant'" :markdown="message.content" />
          <!-- 直接显示user类型的消息 -->
          <div v-else class="preserve-spaces">{{ message.content }}</div>
        </div>
      </div>
      <div class="bottom-container">
        <textarea class="input" @keydown.shift.enter="handleShiftEnter" v-model="input"
          @keydown.enter.exact.prevent="sendMessage" placeholder="Type your message..." rows="4"></textarea>

      </div>
    </div>
  </div>
</template>
<script>
import { ref, reactive, watch, nextTick } from "vue";
import axios from 'axios'
import MarkdownViewer from './MarkdownViewer.vue';

export default {
  setup() {
    const input = ref("");
    const dialogId = ""
    const messages = reactive([
      // { type: "assistant", content: "Welcome to the chat!" },
    ]);
    const chatContainer = ref(null);
    function scrollToBottom() {
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
      }
    };
    watch(messages, () => {
      scrollToBottom();
    });
    const gpt4SSEAPI = axios.create({
      baseURL: '', // 替换成你的API服务器的URL
      headers: { Accept: 'text/event-stream' },
    });

    const histories = [{ type: "assistant", content: "We111!" },
    { type: "assistant", content: "We222 chat!" },
    { type: "assistant", content: "Wel3333chat!" }]

    return { input, messages, gpt4SSEAPI, chatContainer, scrollToBottom, dialogId, histories };
  },
  methods: {
    async sendMessage() {
      if (this.input.trim() !== "") {
        const user_content = this.input.trim();
        this.messages.push({ type: "user", content: user_content });
        this.input = "";

        try {
          const messagesList = this.messages.map(message => {
            return {
              type: message.type,
              content: message.content
            };
          });

          let msg = reactive({ type: "assistant", content: "" })
          this.messages.push(msg);
          nextTick(() => {
            this.scrollToBottom();
          });
          let token = localStorage.getItem('jwtToken');
          const response = await this.gpt4SSEAPI.post("/api/gpt4/sse", { "query": messagesList, "dialogId": this.dialogId }, {
            headers: { Authorization: `Bearer ${token}` },
            onDownloadProgress: (progressEvent) => {
              let resText = progressEvent.event.target.responseText
              let lines = resText.substr(6).split("\r\ndata: ") // 去掉前面的"data: "，然后按照"\r\ndata: "分割
              let m = ""
              let ignoreNextLine = false
              for (let i = 0; i < lines.length; i++) {
                if (ignoreNextLine) {
                  ignoreNextLine = false
                  continue
                }
                let line_str = lines[i]
                if (line_str.startsWith("dialogIdComplexSubfix82jjivmpq90doqjwdoiwq:")) {
                  this.dialogId = line_str.substr(43).trim()
                  console.log("dialogId:", this.dialogId)
                  continue
                }


                if (line_str.endsWith("\r\nevent: ping")) {   //这是为了解决返回中包含ping的event
                  line_str = line_str.substr(0, line_str.length - 13)
                  ignoreNextLine = true
                }

                if (line_str.length >= 2 && line_str.substr(-2) == "\r\n") {  // openai的返回有时会包含一组\r\n，有时会包含两组\r\n，这里会去除掉第二组\r\n
                  line_str = line_str.substr(0, line_str.length - 2)
                }
                if (line_str != "") {
                  m += line_str
                } else {
                  m += "\n" // 对于内容为空的行，应该为原文加一个回车符号
                }
              }
              msg.content = m
              nextTick(() => {
                this.scrollToBottom();
              });
            }
          });
          console.log(response);
        } catch (error) {
          console.error("Error making API call:", error);
        }
      }
    },
    handleShiftEnter(event) {
      event.preventDefault(); // 阻止默认换行行为

      const textarea = event.target;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      this.input = this.input.slice(0, start) + '\n' + this.input.slice(end);
      nextTick(() => {
        event.target.selectionStart = event.target.selectionEnd = start + 1; // 将光标移动到新的行
      });
    }
  },
  components: {
    MarkdownViewer
  }
}
</script>
<style>
#main-window {
  display: flex;
  height: 100%;
  width: 100%;
  max-width: 1200px;
  box-sizing: border-box;
  padding: 10px 5px;
}

#history-container {
  width: 200px;
  background-color: #0a8c5a;
  box-sizing:border-box;
  padding: 5px;
  /* overflow-y: scroll; */
  height: 100%;
}

#chat-window {
  /* 设置 app 元素的宽度为 100% */
  min-height: 100%;
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

.assistant {
  background-color: #7a7676;
  box-sizing: border-box;
  background-color: #f1f1f1;
}

.user {
  box-sizing: border-box;
  background-color: #ffffff;
  margin-left: auto;
  /* text-align: right; */
}

.bottom-container {
  height: 100px;
  padding: 0 10px;
  width: calc(100% - 220px); ;
  box-sizing: border-box;
  position: absolute;
  bottom: 0;
  /* left: 50%; */
  /* Add left property */
  /* transform: translateX(0); */
  /* Add transform property */
  max-width: inherit;
}

.input {
  border-radius: 5px;
  outline: none;
  width: 100%;
  padding: 10px;
  /* Add some padding to textarea */
  box-sizing: border-box;
}

.preserve-spaces {
  white-space: pre-wrap;
}
</style>