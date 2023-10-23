# Vue Chat GUI & FastAPI Backend

This is a self-deployable BS architecture tool similar to ChatGPT, including a front-end written in Vue and a back-end written in FastAPI. The tool can use Azure OpenAI API or OpenAI API for conversation.

## Project Introduction

**Front-end project: vue-chat-gui**

This is a ChatGPT-like chat program based on Vue.js. Users can ask questions to ChatGPT through this application.

**Back-end project: backend (FastAPI)**

This is a back-end project based on FastAPI, which provides API interface for the front-end.

## Installation and Running

### Front-end project

1. Enter the front-end project directory:

   ```
   cd vue-chat-gui
   ```

2. Install dependencies:

   ```
   npm install
   ```

3. Run the project:

   ```
   npm run dev
   ```

### Back-end project

1. Install Python virtual environment:

   ```
   python -m venv venv
   ```

2. Activate the virtual environment:

   - Windows:

     ```
     venv\Scripts\activate
     ```

   - Linux/Mac:

     ```
     source venv/bin/activate
     ```

3. Enter the back-end project directory:

   ```
   cd backend
   ```

4. Install dependencies:

   ```
   pip install -r requirements.txt
   pip install uvicorn[standard]
   ```

5. Run the project:

   ```
   uvicorn main:app --reload
   ```

## TODO List

- [x] Implement user registration and login function
- [x] Conversation record function
- [ ] Conversation export function
- [ ] API cost statistics function

## Contribution

Feel free to submit Pull Requests to help improve this project. Front-end talents are urgently needed as my front-end skills are limited.

## License

This project is licensed under the MIT License. For details, please see the [LICENSE](LICENSE) file.
