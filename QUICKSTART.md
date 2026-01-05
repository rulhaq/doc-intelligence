# CustomerLLM - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Docker Desktop installed and running
- At least 16GB RAM
- 20GB free disk space

### Start the Application
```powershell
# Start all services
docker compose up -d

# Wait ~30 seconds for all services to initialize
# Check status
docker compose ps
```

## 🔑 Access the Application

### Main Application
**URL**: http://localhost:3000

**Admin Credentials**:
- Email: `admin@scalovate.com`
- Password: `scalovate123`

**Regular User** (for testing):
- Email: `scalovate@scalovate.com`
- Password: `scalovate123`

### Service Dashboards
| Service | URL | Credentials |
|---------|-----|-------------|
| API Docs | http://localhost:8000/docs | - |
| Qdrant | http://localhost:6333/dashboard | - |
| MinIO | http://localhost:9001 | minioadmin / minioadmin |
| Grafana | http://localhost:3001 | admin / admin |
| Prometheus | http://localhost:9090 | - |

## 📋 Step-by-Step Workflow

### 1. Upload Documents (Admin Only)

1. **Login** as admin at http://localhost:3000
2. Click **"Documents"** in the header
3. **Drag & Drop** a PDF, DOCX, or TXT file
4. Wait for automatic processing (~5-10 seconds)
5. **Click the document** to preview

### 2. Review & Edit Document

1. Document appears with **split-screen view**:
   - **Left**: Original document preview (PDF/image)
   - **Right**: Editable extracted text
2. **Edit text** if needed to correct OCR errors
3. Click **"Save Corrections"**
4. Click **"Commit to Vector DB"** to make it searchable

### 3. Chat with Documents

1. Click **"Chat"** in the header
2. Click **"+ New Chat"** button
3. **Ask questions** about your documents:
   - English: "What is the main topic of the documents?"
   - Arabic: "ما هو الموضوع الرئيسي للمستندات؟"
4. **View sources**: Click on document references to see where information came from

### 4. Manage Users (Admin Only)

1. Go to **"Admin Console"** → **"User Management"**
2. Click **"Add User"**
3. Fill in details and assign role:
   - **ADMIN**: Full access
   - **EDITOR**: Can upload documents
   - **VIEWER**: Can only chat
4. Search, edit, or delete users as needed

### 5. Monitor System

1. Go to **"Admin Console"** → **"Monitoring"**
2. View real-time stats:
   - Total users, documents, vectors
   - Service health (Ollama, Qdrant)
3. Switch between dashboards:
   - **Grafana**: Metrics & alerts
   - **Qdrant**: Vector database
   - **MinIO**: File storage
   - **Prometheus**: Raw metrics

## ✨ Key Features

### Document Processing
- ✅ **Supported formats**: PDF, DOCX, TXT
- ✅ **Auto-processing**: Starts immediately after upload
- ✅ **Multi-language**: Arabic, English, French, Spanish, Chinese, etc.
- ✅ **Editable text**: Fix OCR errors before vectorization
- ✅ **Preview mode**: See original + extracted text side-by-side

### Chat Interface
- ✅ **RAG Search**: Answers based on your documents
- ✅ **Source Attribution**: See which documents were used
- ✅ **Multi-language**: Detects language and responds accordingly
- ✅ **Typing Animation**: Natural conversation feel
- ✅ **Suggested Questions**: Context-aware prompts
- ✅ **RTL Support**: Proper Arabic/Hebrew rendering

### Admin Features
- ✅ **User Management**: Create, edit, delete users
- ✅ **Role-Based Access**: ADMIN, EDITOR, VIEWER
- ✅ **System Settings**: Configure LLM models and RAG parameters
- ✅ **Monitoring**: Real-time stats and embedded dashboards
- ✅ **Document Control**: Manage uploaded documents
- ✅ **Chat Deletion**: Admins can delete any conversation

## 🔍 Testing the System

### Test RAG Search
```bash
# 1. Upload a document with specific information
# 2. In chat, ask: "What does the document say about [topic]?"
# 3. Verify the response includes relevant information
# 4. Check that sources are shown at the bottom
# 5. Click "View Doc" to verify the source
```

### Test Arabic Support
```bash
# In chat, type:
مرحبا، ما هي المعلومات المتوفرة في المستندات؟

# Expected: Arabic response with RTL formatting
```

### Test User Roles
```bash
# 1. As admin, create a VIEWER user
# 2. Logout and login as that user
# 3. Verify: Can chat but cannot access Documents or Admin Console
# 4. As admin, create an EDITOR user
# 5. Verify: Can upload documents but cannot access Admin Console
```

## 📊 Verify System Health

```powershell
# Check all containers are running
docker compose ps

# All should show "running" or "healthy"
# Expected output:
# customerllm-postgres   (healthy)
# customerllm-redis      (healthy)
# customerllm-minio      (healthy)
# customerllm-qdrant     (running)
# customerllm-ollama     (running)
# customerllm-backend    (running)
# customerllm-frontend   (running)
# customerllm-prometheus (running)
# customerllm-grafana    (running)

# Check Qdrant vectors
Invoke-RestMethod -Uri "http://localhost:6333/collections/documents"
# Should show: points_count > 0 (after uploading documents)

# Check Ollama models
docker exec -it customerllm-ollama ollama list
# Should show:
# - llama3.2:latest
# - nomic-embed-text:latest
# - llama3.2:1b (optional)
```

## 🐛 Troubleshooting

### Frontend Issues

**Problem**: "Can't connect to backend" or 404 errors
```powershell
# Solution 1: Clear browser cache
# Press Ctrl+Shift+Delete, clear cache, or hard refresh (Ctrl+Shift+R)

# Solution 2: Rebuild frontend
docker compose build frontend --no-cache
docker compose up -d frontend
```

**Problem**: UI not updating
```powershell
# Force restart
docker compose down frontend
docker compose up -d frontend
```

### Backend Issues

**Problem**: API errors or slow responses
```powershell
# Check logs
docker logs customerllm-backend --tail 50

# Restart backend
docker compose restart backend
```

**Problem**: "Ollama connection failed"
```powershell
# Check Ollama status
docker exec -it customerllm-ollama ollama list

# Pull models if missing
docker exec -it customerllm-ollama ollama pull llama3.2:latest
docker exec -it customerllm-ollama ollama pull nomic-embed-text:latest
```

### Document Processing Issues

**Problem**: "Failed to process document"
```powershell
# Check backend logs
docker logs customerllm-backend --tail 100

# Common causes:
# - File too large (>50MB)
# - Unsupported format
# - Corrupted file

# Solution: Try a different file or reduce size
```

**Problem**: "Failed to commit to vector DB"
```powershell
# Check Qdrant status
Invoke-RestMethod -Uri "http://localhost:6333/collections/documents"

# Restart Qdrant if needed
docker compose restart qdrant
```

### Chat Not Working

**Problem**: No response or error in chat
```powershell
# Check if documents are uploaded
# Go to Admin Console -> Monitoring -> Check "Total Vectors"

# Check Ollama status
docker exec -it customerllm-ollama ollama list

# Check backend logs
docker logs customerllm-backend --follow

# Then try chatting again
```

**Problem**: "Random" or irrelevant responses
```bash
# This means:
# 1. Documents not properly vectorized
#    -> Re-upload and commit documents
# 2. Query too vague
#    -> Be more specific in your question
# 3. No relevant documents
#    -> Upload documents related to your query
```

### Database Issues

**Problem**: Login not working or users missing
```powershell
# Reset database
docker compose down
docker volume rm cisco-thegroup_postgres-data
docker compose up -d

# Wait 30 seconds for initialization
# Default admin user will be recreated
```

## 🎯 Best Practices

### Document Upload
1. **Use clear, text-based documents** (not scanned images for now)
2. **Keep files under 20MB** for faster processing
3. **Always review extracted text** before committing to vector DB
4. **Use descriptive filenames** for easier organization

### Chat Queries
1. **Be specific**: "What are the payment terms in contract X?" vs "Tell me about payments"
2. **Reference documents**: "According to the uploaded contract, what is..."
3. **Use natural language**: System understands conversational queries
4. **Try different languages**: System auto-detects and responds appropriately

### User Management
1. **Use VIEWER role** for most users (read-only access)
2. **Limit ADMIN users** to 1-2 trusted administrators
3. **Use strong passwords** (system enforces minimum requirements)
4. **Regularly review users** in Admin Console

### Monitoring
1. **Check stats daily** in Admin Console → Monitoring
2. **Watch for errors** in Grafana dashboard
3. **Monitor storage** via MinIO console
4. **Review conversation quality** periodically

## 📈 Performance Tips

### For Better Speed
- Use **llama3.2:1b** model (faster, slightly lower quality)
- Reduce **chunk_size** in System Settings
- Limit **document size** to < 10MB

### For Better Quality
- Use **llama3.2:latest** or **Jais** (when added)
- Increase **chunk_overlap** in System Settings
- Review and correct **extracted text** before committing

### For Better Search
- Use **specific queries** with keywords
- Upload **related documents** together
- **Tag documents** with descriptive titles
- **Test searches** after uploading new documents

## 🚀 Next Steps

1. **Upload sample documents** to test the system
2. **Create test users** with different roles
3. **Try Arabic queries** to test multi-language support
4. **Explore admin dashboards** to understand monitoring
5. **Read JAIS_INTEGRATION.md** if you want to add the Jais model
6. **Review SYSTEM_STATUS.md** for detailed feature list

## 📞 Support

### Logs Location
```powershell
# Backend logs
docker logs customerllm-backend --tail 100 --follow

# All services
docker compose logs --follow

# Specific service
docker logs customerllm-[service-name]
```

### Health Checks
```powershell
# API health
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Qdrant health
Invoke-RestMethod -Uri "http://localhost:6333/readyz"

# Ollama health
Invoke-RestMethod -Uri "http://localhost:11434/api/tags"
```

### Reset Everything
```powershell
# Nuclear option: start fresh
docker compose down -v
docker compose up -d

# Wait ~30 seconds
# Login with default admin credentials
```

---

## ✅ Success Checklist

- [ ] All containers running (`docker compose ps`)
- [ ] Can login at http://localhost:3000
- [ ] Uploaded at least one document
- [ ] Document appears in Documents tab
- [ ] Can preview document with split-screen
- [ ] Committed document to vector DB
- [ ] Can create new chat conversation
- [ ] Chat responds with relevant information
- [ ] Sources shown at bottom of responses
- [ ] Can view source documents from chat
- [ ] Admin Console shows real statistics
- [ ] Can create/edit/delete users
- [ ] Grafana dashboard accessible
- [ ] Arabic text displays correctly (RTL)

If all items are checked, your system is fully operational! 🎉

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Status**: ✅ Production-Ready MVP
