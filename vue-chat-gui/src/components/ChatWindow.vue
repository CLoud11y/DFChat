<template>
  <div id="main-window">
    <div id="history-container">
      <div class="history-item"  @click=createNewDialog() >
        New dialog
      </div>
      <div class="history-item" v-for="(history, index) in histories" :key="index" @click.self=handleHistoryClick(history) @click.right.native="showContextMenu($event,index)" >
        <context-menu :ref="'contextmenu'+index">
          <button @click="deleteDialog(history.dialog_id)">删除</button>
          <button @click="updateRecordName(history.dialog_id)">改名</button>
          <button @click="doNothing">取消</button>
          <!-- Add more menu items here -->
        </context-menu>
        {{ history.record_name }}...
      </div>
    </div>


    
    <div class="chat-container" ref="chatContainer">
      <div id="chat-window">
        <div class="chat-message" v-for="(message, index) in messages" :key="index" :class="message.role">
          <!-- 使用MarkdownViewer组件显示assistant类型的消息 -->
          <MarkdownViewer v-if="message.role === 'assistant'" :markdown="message.content" />
          <!-- 直接显示user类型的消息 -->
          <div v-else class="preserve-spaces">{{ message.content }}</div>
        </div>
      </div>
      <div class="bottom-container">
        <textarea class="input" @keydown.shift.enter="handleShiftEnter" v-model="input"
          @keydown.enter.exact.prevent="sendMessage" placeholder="Type your message..." rows="4">
        </textarea>
         
        <div v-if="is_uploaded.state == false" class="file">     
          <label>选择文件</label>    
          <input type="file" multiple @change="handleFileUpload($event)"/>
          <button v-on:click="submitFiles()">上传</button>
        </div>
        <div v-else class="file">该对话已有文件上传</div>
      </div>
    </div>
  </div>
</template>
<script>
import { ref, reactive, watch, nextTick } from "vue";
import axios from 'axios'
import MarkdownViewer from './MarkdownViewer.vue';
import ContextMenu from "./ContextMenu.vue";

export default {
  setup() {
    const input = ref("");
    const dialogId = "";
    const files = [];
    const is_uploaded = reactive({state: false})
    const messages = reactive([
      // { role: "assistant", content: "Welcome to the chat!" },
    ]);
    const histories = reactive([
    ]);
    const chatContainer = ref(null);

    function scrollToBottom() {
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
        console.log('消息拉到底')
      }
    };

    function getDialogs() {
      let token = localStorage.getItem('jwtToken');
      axios.get("/api/dialog/list", {
        headers: { Authorization: `Bearer ${token}` },
      }).then((response) => {
        console.log(response.data)
        for (let i = 0; i < response.data.length; i++) {
          histories.unshift( response.data[i] );
        }
      });
    };
    getDialogs();
  
    
    const gpt4SSEAPI = axios.create({
      baseURL: '', // 替换成你的API服务器的URL
      headers: { Accept: 'text/event-stream' },
    });

    return { input, messages, gpt4SSEAPI, chatContainer, scrollToBottom, dialogId, histories, files, is_uploaded};
  },
  methods: {
    async sendMessage() {
      if (this.input.trim() !== "") {
        const user_content = this.input.trim();
        this.messages.push({ role: "user", content: user_content });
        this.input = "";
        let isNewDialog = this.dialogId == ""

        try {
          const messagesList = this.messages.map(message => {
            return {
              role: message.role,
              content: message.content
            };
          });

          let msg = reactive({ role: "assistant", content: "" })
          this.messages.push(msg);
          nextTick(() => {
            this.scrollToBottom();
          });
          let token = localStorage.getItem('jwtToken');
          const response = await this.gpt4SSEAPI.post("/api/gpt4/sse", { "query": messagesList, "dialogId": this.dialogId }, {
            headers: { Authorization: `Bearer ${token}` },
            onDownloadProgress: (progressEvent) => {
              let resText = progressEvent.event.target.responseText
              if(resText.includes("Invalid authentication credentials")){
                localStorage.removeItem('jwtToken')
                localStorage.removeItem('username')
                localStorage.removeItem('expirationDate')
                this.$router.push({ path: '/' })
              }

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

                if(line_str.startsWith(" ping")){ // 处理起始行的"event: ping",但是前面有一个substr(6),所以
                  ignoreNextLine = true
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
          if(isNewDialog){
            let d_content = JSON.parse(JSON.stringify(this.messages));
            this.histories.unshift({
              dialog_id: this.dialogId, 
              dialog_content: d_content, 
              file_path: null,
              record_name: d_content[0].content.slice(0, 40)
            })
          }
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
    },
    handleHistoryClick(history) {
      let token = localStorage.getItem('jwtToken');
      this.scrollToBottom();
      this.messages.splice(0, this.messages.length);
      this.dialogId = history.dialog_id;
      axios.get(`/api/dialog/by_id/${this.dialogId}`, {
        headers: { Authorization: `Bearer ${token}` }
      }).then((response) => {
        console.log(response.data);
        history.dialog_content = response.data["dialog_content"];
        history.file_path = response.data["file_path"];
        for (let i = 0; i < history.dialog_content.length; i++) {
          this.messages.push(history.dialog_content[i]);
        }
        this.is_uploaded.state = history.file_path ? true : false;
        console.log(this.is_uploaded.state)
      }); 
      
     },
    createNewDialog() {
      this.messages.splice(0, this.messages.length);
      this.dialogId = "";
      this.is_uploaded.state = false;
    },
    showContextMenu(event, index) {
      console.log(event);
      let contextMenuRef = `contextmenu${index}`;
      console.log(this.$refs[contextMenuRef].length);
      this.$refs[contextMenuRef][0].showContextMenu(event);
    },
    deleteDialog(id){
      console.log(id)
      let token = localStorage.getItem('jwtToken');
      this.messages.splice(0, this.messages.length);
      this.dialogId = "";
      axios.delete(`/api/dialog/id/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      }).then((response) => {
        console.log(response.data)
        for (let i = 0; i < this.histories.length; i++) {
          if(this.histories[i].dialog_id == id){
            this.histories.splice(i, 1);
            break;
          }
        }
      });
    },
    updateRecordName(id) {
      console.log(id)
      let token = localStorage.getItem('jwtToken');
      let update_name = prompt("Enter the name for this dialog", "new name");
      axios.post(`/api/dialog/update_record_name`, {dialogId: id, record_name: update_name}, {
        headers: { Authorization: `Bearer ${token}` }
      }).then((response) => {
        console.log(response.data)
        for (let i = 0; i < this.histories.length; i++) {
          if(this.histories[i].dialog_id == id){
            this.histories[i].record_name = update_name;
            break;
          }
        }
      });
    },
    doNothing(event) {
      event.preventDefault();
    },
    handleFileUpload(event) {
      this.files = event.target.files;
      console.log(this.files)
    },
    async submitFiles() {
      let token = localStorage.getItem('jwtToken');
      let formData = new FormData();
      for (let i = 0; i < this.files.length; i++) {
        formData.append("files", this.files[i]); 
      }
      console.log(formData.getAll("files"))
      axios.post(`/api/upload/upload_files/${this.dialogId ? this.dialogId : 0}`, 
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data' ,
          Authorization: `Bearer ${token}`
        }
      }
      )
      .then((response) => {
        let isNewDialog = this.dialogId == "";
        this.dialogId = response.data["dialogId"];
        let path = response.data["file_path"];
        let name = response.data["record_name"];
        console.log(response.data); // 处理成功的响应
        alert("上传文件成功");
        this.is_uploaded.state = true;
        console.log(this.is_uploaded.state);
        this.messages.push({role: "assistant", content: "All files have been uploaded successfully! Ask questions about them"});
        if(isNewDialog){
          this.histories.unshift({
            dialog_id: this.dialogId, 
            dialog_content: JSON.parse(JSON.stringify(this.messages)), 
            file_path: path,
            record_name: name
          });
        }
      })
      .catch((error) => {
        console.log(error); // 处理失败的错误
      });

    }
  },
  components: {
    MarkdownViewer,
    ContextMenu
  },
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
  overflow-y: auto;
  height: 100%;
}

.history-item{
  border: rgb(236, 122, 140) 1px double;
  margin: 2px 0px;
}

#chat-window {
  /* 设置 app 元素的宽度为 100% */
  min-height: 100%;
  box-sizing: border-box;
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
  height: 130px;
  width: calc(100% - 240px);
  max-width: 980px;

  box-sizing: border-box;
  position: absolute;
  bottom: 0px;
  /* left: 50%; */
  /* Add left property */
  /* transform: translateX(0); */
  /* Add transform property */
}

.input {
  border-radius: 5px;
  outline: none;
  width: 99%;
  padding: 10px;
  position: absolute;
  top: 5px;
  /* Add some padding to textarea */
  box-sizing: border-box;
  resize: none;
}
.file{
   position:absolute;
   bottom: 10px;
}

.preserve-spaces {
  white-space: pre-wrap;
}
</style>