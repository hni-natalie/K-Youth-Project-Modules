# Week 3 - System Integration & Application

## 📌 Project Overview
This project is a **full-stack AI-powered chat application** built using FastAPI, a modern web frontend, and large language model (LLM) integration. It allows users to chat with an AI assistant, upload PDF documents, and perform skill extraction and gap analysis.

The system supports both:
- 🌐 Cloud LLMs (Google Gemini)
- 🏠 Local LLMs (Ollama / Llama models)

It is fully containerized using Docker and orchestrated with Docker Compose for easy deployment and portability.

---

---

## ⚙️ Setup Instructions

### 📋 Prerequisites

Before running this project, ensure you have installed:

- Docker (latest stable version)
- Docker Compose v2+
> Docker Desktop for Windows/macOS includes Docker Compose by default. [Official Docker](https://docs.docker.com/get-docker/)

- Python 3.14+ (only required for manual setup)
- uv 0.8* (Python package manager)
- ruff 0.15* (Python linting)

Check installation:

```bash
docker --version
docker compose version
python --version
```

---

### 📁 Clone the Repository

```bash
git clone <your-repository-url>
cd <project-folder>
cd week_3
```

---

### 🛠️ Create Virtual Environment

Create and activate a virtual environment:

```bash
uv venv
```

Activate the environment:

#### macOS / Linux
```bash
source .venv/bin/activate
```

#### Windows
```bash
.venv\Scripts\activate
```

---

### 🔐 Configure Environment File

#### Copy the example env file to local env file:
```bash
cp .env.example .env
```
⚠️ **Edit `.env` to fill in your custom configurations. Do not commit `.env` to version control.**

---

## 📦 Usage Guide

### Docker command 

Start services:

```bash
docker compose up -d --build
```

Check running status:

```bash
docker compose ps
```

Stop services:

```bash
docker compose down
```

---

### 🌍 Access the Application

#### Once running:

- 💬 Frontend: http://localhost:8000
- ⚙️ Backend API Chat: http://localhost:3000/chat

---

### Chat Interface Features

You can:

#### 💬 Send Messages
- Type a message in the input box
- Press Enter to send
- Press Shift + Enter to create a new line

#### 📎 Upload Files
- Click the plus (+) button
- Upload PDF files
- The system will extract text automatically

---

### ✅ Expected Behavior
Example Input:
```text
I want to become a data analyst. What skills do I need?
```
Example Output:
- AI-generated response explaining required skills
- If PDF is uploaded:
    - Skills will be extracted from the document
    - AI will perform skill gap analysis

---

## 📡 API / Function Reference

This section documents the key backend API endpoints and frontend functions used in the application, as well as how both services communicate within the Docker environment.

---

## 🖥️ Backend API

The backend is built using **FastAPI** and exposes a REST API that handles chat requests, file uploads, and AI model integration.

---

### 📍 POST `/chat`

This is the main endpoint used by the frontend to interact with the AI system.

#### 📥 Request Format

The endpoint accepts **form-data** (not raw JSON), supporting both text and file uploads:

| Field   | Type        | Description |
|----------|------------|-------------|
| message  | string     | User's chat message |
| files    | file[]     | Optional PDF files uploaded by the user |

---

#### 📤 Example Request

```bash
POST /chat
Content-Type: multipart/form-data
```

Example form-data payload:
```bash
message: "I want to become a data analyst. What skills do I need?"
files: resume.pdf (optional)
```

--- 

#### 📤 Response Format

✅ Success Response (200 OK)
```bash
{
  "success": true,
  "response": "AI-generated reply based on user message and/or PDF analysis"
}
```

❌ Error Response (500 Internal Server Error)
```bash
{
  "success": false,
  "message": "LLM service temporarily unavailable. Please try again."
}
```
--- 

## 🌐 Frontend Functions
The frontend is built using vanilla JavaScript and is responsible for UI rendering and API communication.

---

### 📌 sendMessage()

This is the core function that handles sending user input to the backend.

#### Responsibilities:
- Collects user message and uploaded files
- Sends POST request to /chat
- Displays user message in chat UI immediately
- Shows loading indicator while waiting for response
- Renders AI response when received

#### Flow:
```text
User Input → FormData → Fetch API → Backend /chat → Response → UI Update
```

---

### 📌 addMessage(text, sender)

Responsible for rendering chat bubbles in the UI.

#### Features:
- Displays user messages (right-aligned)
- Displays AI messages (left-aligned)
- Automatically scrolls chat to bottom

--- 

### 📌 addLoadingMessage() / removeLoadingMessage()

Handles loading state UI.
- Shows spinner while waiting for AI response
- Removes spinner once response is received

--- 

### 📌 addFileBubbles(fileList)

Displays uploaded files inside the chat UI.

- Shows file name
- Displays PDF icon
- Helps users confirm uploaded content

--- 

### 📌 File Handling Functions

| Function	| Purpose |
|---|---|
| renderFiles()	| Shows selected files before sending |
| removeFile(index)	| Removes a specific file |
| clearFiles()	| Clears all uploaded files |

--- 

## 🔗 Frontend ↔ Backend Communication (Docker Network)

When running via Docker Compose:

- Frontend and backend run as separate containers
- They communicate through a shared Docker network

---

## 📊 Data / Assumptions

This section describes the data structures used in the system, key assumptions made during development, and how data flows through the application from frontend to backend and AI models.

---

## 📦 Data Structure

### 📤 Frontend → Backend Request

The frontend sends data to the backend using `multipart/form-data` (not JSON), allowing support for both text and file uploads.

#### Fields:

| Field   | Type        | Description |
|----------|------------|-------------|
| message  | string     | User’s chat input message |
| files    | file[]     | Optional uploaded PDF documents |

---

### 📥 Backend → Frontend Response

The backend returns a JSON object in the following format:

#### ✅ Success Response

```json
{
  "success": true,
  "response": "AI-generated response text"
}
```

#### ❌ Error Response

```json
{
  "success": false,
  "message": "Error description (e.g., LLM failure)"
}
```

---

## 📌 Assumptions

### 1. Input Format Assumptions
- User messages are assumed to be plain text
- Uploaded files are assumed to be valid PDF documents
- PDF files are expected to contain readable text (not scanned images unless OCR is added)

### 2. File Constraints
- Only PDF files are supported for upload
- Large files may impact processing time
- Files are temporarily stored on the backend and deleted after processing

### 3. AI Model Integration Assumptions
- The system assumes at least one AI provider is available:
    - Gemini (cloud-based API), OR
    - Ollama (local model via Docker/host machine)
- The model is treated as a black box that returns generated text
- Week 2 skill extraction logic is assumed to be deterministic and independent of the LLM

### 4. System Design Simplifications
- No persistent database is used for chat history (stateless design)
- Files are not permanently stored (temporary processing only)
- AI responses are not cached
- Error handling is simplified to a single structured response format

--- 

## 🧪 Testing

This project was tested at both the **frontend** and **backend** levels to ensure correct functionality of the chat system, file handling, and AI integration inside a Dockerized environment.

---

### 🖥️ Frontend Testing

#### Test Cases

- Sending a plain text message in the chat input
- Sending a message with `Enter` key (Shift + Enter for newline)
- Uploading single and multiple PDF files
- Removing uploaded files before sending
- Ensuring chat messages render correctly (user vs bot styling)
- Checking loading indicator appears while waiting for backend response
- Verifying chat scrolls automatically to latest message

#### How to Test

1. Run the system using Docker Compose:
   ```bash
   docker compose up --build
   ```

2. Open the frontend in browser:
    ``` bash
    http://localhost:3000
    ```

3. Interact with the chat interface:
    - Type messages
    - Upload PDFs
    - Send messages and observe responses

---

### 🔧 Backend Testing

#### Test Cases
- Sending a simple text message (no file upload)
- Sending a message with one or multiple PDF files
- Testing invalid or empty inputs
- Verifying correct JSON response format
- Ensuring error handling returns proper HTTP status codes

--- 

#### 📮 Postman Testing

Endpoint:
``` bash
POST http://localhost:3000/chat

```
Body Type:
```
form-data
```

Fields:
- message → string (user input text)
- files → file (optional PDF upload, can be multiple)

--- 

#### Example Request
|Key	|Value	|Type | 
|---|---|---|
|message	|"Find my skill gaps"	|Text |
|files	| resume.pdf	| File |

--- 

#### Expected Success Response
``` json
{
  "success": true,
  "response": "AI-generated answer here..."
}
```

--- 

#### Expected Error Response
```json
{
  "success": false,
  "message": "LLM service temporarily unavailable. Please try again."
}
```

---

### 🐳 Docker Integration Testing

To ensure frontend and backend communication works inside Docker:

- Verified frontend correctly calls backend using environment variable:
    ```
    BACKEND_URL=http://backend:3000
    ```
- Confirmed backend is reachable from frontend container via Docker network
- Tested full flow:
    1. Frontend sends request
    2. Backend processes request
    3. AI model returns response
    4. Frontend renders response in chat UI

---

## ⚠️ Limitations

This project demonstrates a full-stack AI chat system, but it has several known limitations.

---

### 🤖 AI Model
- Response quality depends on the underlying LLM (Gemini or Ollama).
- Outputs may be inconsistent or sensitive to prompt changes.
- No fine-tuning or advanced guardrails are implemented.

---

### 📄 PDF Processing
- Basic text extraction only (no OCR support for scanned PDFs).
- Complex layouts (tables, multi-column formats) may not parse correctly.
- Large files may slow down processing or fail due to limits.

---

### ⚙️ System Design
- No persistent chat history (messages reset on refresh).
- Uploaded files are temporary and deleted after processing.
- No authentication or multi-user support.

---

### 🚀 Performance
- Response time depends on model availability and hardware.
- Ollama requires a local running service.
- No caching or optimization for repeated queries.

---

## 🏗️ Architecture Reflection

### 🧩 Design Choices

The frontend handles the UI, while the backend manages file processing and AI model integration. Docker Compose connects both services, making the system easy to run with a single command.

This design improves modularity and makes each part of the system easier to develop and maintain independently.

---

### ⚖️ Trade-offs

To keep the project simple and easy to run:
- Used vanilla HTML/JS instead of a frontend framework
- Avoided adding a database or authentication system
- Focused on Docker Compose instead of cloud deployment

These choices reduce complexity but limit scalability and production readiness.

---

### 🚀 Possible Improvements

If extended, the system could include:
- Persistent storage for chat history
- A modern frontend framework (React/Vue)
- Better PDF processing with OCR support
- Cloud deployment and scaling support
