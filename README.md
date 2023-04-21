# Vue Chat GUI & FastAPI Backend

中文版 | [English](README-EN.md)

这是一个可以自行部署的类似chatGPT功能的BS架构工具，包含一个vue编写的前端和fastapi编写的后端。工具可以使用Azure OpenAI API或者OpenAI API进行对话。

## 项目介绍

**前端项目：vue-chat-gui**

这是一个基于Vue.js的类ChatGPT聊天程序，用户可以通过这个应用程序向chatGPT提问。

**后端项目：backend (FastAPI)**

这是一个基于FastAPI的后端项目，它为前端提供API接口。

## 安装与运行

### 使用docker启动
1. 修改backend/config.py中的配置

2. 在根目录 Build docker image
   ```
   docker build -t dfchat:0.1 -f deployment/Dockerfile-AllinOne .
   ```
3. 运行docker image（这里的80是你的本地端口）
   ```
   sudo docker run -d -p 80:8000 dfchat:0.1
   ```
4. 打开浏览器，输入http://localhost

### 前端项目

1. 进入前端项目目录：

   ```
   cd vue-chat-gui
   ```

2. 安装依赖：

   ```
   npm install
   ```

3. 运行项目：

   ```
   npm run dev
   ```

### 后端项目

1. 安装Python虚拟环境：

   ```
   python -m venv venv
   ```

2. 激活虚拟环境：

   - Windows:

     ```
     venv\Scripts\activate
     ```

   - Linux/Mac:

     ```
     source venv/bin/activate
     ```

3. 进入后端项目目录：

   ```
   cd backend
   ```

4. 安装依赖：

   ```
   pip install -r requirements.txt
   pip install uvicorn[standard]
   ```

5. 运行项目：

   ```
   uvicorn main:app --reload
   ```


## TODO 列表

- [ ] 实现用户注册和登录功能
- [ ] 对话记录功能
- [ ] 对话导出功能
- [ ] API费用统计功能

## 贡献

欢迎提交Pull Request来帮助改进这个项目。由于本人前端能力有限，急需前端大佬的帮助。

## 许可证

本项目采用MIT许可证，详情请参阅[LICENSE](LICENSE)文件。