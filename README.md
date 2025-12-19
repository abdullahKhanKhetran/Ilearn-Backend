# Student Performance Chatbot - Complete Guide

## 🚀 Setup Instructions

### 1. Installation

```bash
# Create project directory
mkdir student-performance-chatbot
cd student-performance-chatbot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Project Structure Setup

Create all folders and files according to the folder structure artifact. Make sure to:
- Create the `data/` folder and add `student_data.json`
- Create the `src/` folder with all Python modules
- Create the `api/` folder with `main.py`
- Create the `streamlit_ui/` folder with `app.py`
- Add the `.env` file in the root directory

### 3. Running the Application

#### Start FastAPI Backend
```bash
# From project root
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

#### Start Streamlit UI (for testing)
```bash
# In a new terminal
cd streamlit_ui
streamlit run app.py
```

## 📡 Frontend Integration Guide for .NET Developers

### API Endpoints

#### 1. Health Check
```
GET http://localhost:8000/health
Response: {"status": "healthy", "message": "All systems operational"}
```

#### 2. Get Student List
```
GET http://localhost:8000/students
Response: {
  "students": [
    {"student_id": "S001", "name": "Ahmed Khan"},
    ...
  ]
}
```

#### 3. Chat Endpoint (Main)
```
POST http://localhost:8000/chat
Content-Type: application/json

Request Body:
{
  "student_id": "S001",
  "question": "How is this student performing in studies?"
}

Response:
{
  "student_id": "S001",
  "question": "How is this student performing in studies?",
  "answer": "Ahmed Khan is performing well overall...",
  "performance_category": "Average",
  "retrieved_context": "Student data..."
}
```

### .NET Integration Example (C#)

```csharp
using System.Net.Http;
using System.Text.Json;

public class StudentChatService
{
    private readonly HttpClient _httpClient;
    private const string ApiBaseUrl = "http://localhost:8000";

    public StudentChatService()
    {
        _httpClient = new HttpClient();
    }

    public async Task<ChatResponse> GetStudentPerformanceAsync(
        string studentId, 
        string question)
    {
        var request = new ChatRequest
        {
            StudentId = studentId,
            Question = question
        };

        var jsonContent = JsonSerializer.Serialize(request);
        var content = new StringContent(
            jsonContent, 
            System.Text.Encoding.UTF8, 
            "application/json"
        );

        var response = await _httpClient.PostAsync(
            $"{ApiBaseUrl}/chat", 
            content
        );

        response.EnsureSuccessStatusCode();
        
        var responseJson = await response.Content.ReadAsStringAsync();
        return JsonSerializer.Deserialize<ChatResponse>(responseJson);
    }
}

// Models
public class ChatRequest
{
    [JsonPropertyName("student_id")]
    public string StudentId { get; set; }
    
    [JsonPropertyName("question")]
    public string Question { get; set; }
}

public class ChatResponse
{
    [JsonPropertyName("student_id")]
    public string StudentId { get; set; }
    
    [JsonPropertyName("question")]
    public string Question { get; set; }
    
    [JsonPropertyName("answer")]
    public string Answer { get; set; }
    
    [JsonPropertyName("performance_category")]
    public string PerformanceCategory { get; set; }
    
    [JsonPropertyName("retrieved_context")]
    public string RetrievedContext { get; set; }
}
```

### Testing with Postman/curl

```bash
# Health check
curl http://localhost:8000/health

# Get students
curl http://localhost:8000/students

# Chat query
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "S001",
    "question": "How is this student performing?"
  }'
```

## 📊 How the RAG System Works

### 1. Data Flow

```
Student Data (JSON) 
    → Text Formatting 
    → Embedding Generation 
    → Vector Database (FAISS)
    → Query Search 
    → Context Retrieval 
    → LLM Generation 
    → Response
```

### 2. Adding New Student Data

To add more students, simply update `data/student_data.json`:

```json
{
  "student_id": "S005",
  "name": "New Student",
  "semester": 3,
  "subjects": {
    "Mathematics": {"marks": 75, "total": 100},
    "Physics": {"marks": 80, "total": 100}
  },
  "attendance": 85,
  "assignments_submitted": 18,
  "total_assignments": 20,
  "performance_notes": "Description of student performance..."
}
```

Then restart the API - it will automatically rebuild the vector database.

### 3. How the Chatbot Answers Questions

1. **User asks**: "How is student S001 performing?"
2. **System retrieves**: Relevant student data from vector database
3. **System analyzes**: Calculates average marks, checks attendance
4. **System categorizes**: Fantastic/Average/Below Average
5. **LLM generates**: Natural language response with recommendations
6. **System returns**: Complete answer with performance category

### 4. Performance Categories

- **Fantastic**: Average marks ≥ 85% AND attendance ≥ 80%
- **Average**: Average marks between 60-85%
- **Below Average**: Average marks < 60%

You can adjust these thresholds in `src/config.py`.

## 🔧 Customization

### Change LLM Model
Edit `.env`:
```
LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2
```

### Change Embedding Model
Edit `.env`:
```
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
```

### Modify Performance Thresholds
Edit `src/config.py`:
```python
FANTASTIC_THRESHOLD = 90  # Change from 85
AVERAGE_THRESHOLD = 70    # Change from 60
```

## 🐛 Troubleshooting

### "Model not found"
- Ensure you have internet connection for first-time model download
- Models are cached in `~/.cache/huggingface/`

### "Out of memory"
- Use smaller models or CPU-only mode
- Reduce `max_new_tokens` in `src/llm_handler.py`

### "CORS error from frontend"
- Ensure CORS is configured in `api/main.py`
- Add your frontend domain to `allow_origins`

## 📝 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🎯 Production Deployment

For production:
1. Set specific CORS origins in `api/main.py`
2. Use environment variables for sensitive config
3. Deploy on cloud (AWS, Azure, Google Cloud)
4. Use gunicorn/uvicorn workers for scalability
5. Add authentication/rate limiting
6. Use managed vector databases (Pinecone, Weaviate)

## 💡 Tips for .NET Frontend

1. **Handle Loading States**: API calls may take 3-10 seconds
2. **Show Progress**: Display "Analyzing student data..." message
3. **Error Handling**: Handle connection errors gracefully
4. **Caching**: Cache student list to reduce API calls
5. **Retry Logic**: Implement retry for failed requests