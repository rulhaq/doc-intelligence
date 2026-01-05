# Adding Jais LLM to the System

## Overview
This guide explains how to add the Jais (Arabic-focused) LLM to your Ollama instance.

## Prerequisites
- Jais model file (e.g., `jais-13b.gguf` or similar)
- Docker container running with enough storage
- At least 16GB RAM for Jais-13b

## Option 1: If You Have a Jais GGUF File

### Step 1: Create Modelfile
Create a file named `Modelfile` in your project root:

```dockerfile
FROM ./jais-13b.gguf

TEMPLATE """{{ if .System }}<|system|>
{{ .System }}<|end|>
{{ end }}{{ if .Prompt }}<|user|>
{{ .Prompt }}<|end|>
{{ end }}<|assistant|>
{{ .Response }}<|end|>
"""

PARAMETER stop "<|system|>"
PARAMETER stop "<|user|>"
PARAMETER stop "<|assistant|>"
PARAMETER stop "<|end|>"

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40

SYSTEM """أنت جايس، مساعد ذكي متخصص في اللغة العربية. قدم إجابات مفيدة ودقيقة."""
```

### Step 2: Copy Model File to Ollama Container
```powershell
# Copy your Jais model file to the container
docker cp ./jais-13b.gguf customerllm-ollama:/root/jais-13b.gguf

# Copy the Modelfile
docker cp ./Modelfile customerllm-ollama:/root/Modelfile
```

### Step 3: Create the Model in Ollama
```powershell
# Enter the Ollama container
docker exec -it customerllm-ollama sh

# Create the model
ollama create jais:13b -f /root/Modelfile

# Test the model
ollama run jais:13b "مرحبا، كيف حالك؟"

# Exit container
exit
```

### Step 4: Update Environment Variables
Update `.env` file:
```bash
OLLAMA_MODEL=jais:13b
```

### Step 5: Restart Backend
```powershell
docker compose restart backend
```

## Option 2: Pull from Ollama Registry (If Available)

If Jais is available in Ollama's model library:

```powershell
# Pull the model
docker exec -it customerllm-ollama ollama pull jais:13b

# Update .env
# OLLAMA_MODEL=jais:13b

# Restart backend
docker compose restart backend
```

## Option 3: Convert from Hugging Face

If you have a Hugging Face Jais model:

### Step 1: Install llama.cpp Tools
```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Convert to GGUF
```bash
# Convert Hugging Face model to GGUF
python convert.py /path/to/jais-hf-model --outtype f16 --outfile jais-13b-f16.gguf

# Quantize (optional, for smaller size)
./quantize jais-13b-f16.gguf jais-13b-q4_0.gguf q4_0
```

### Step 3: Follow Option 1 above with your new GGUF file

## Verification

Test the model through the admin console:
1. Navigate to **Admin Console** → **System Settings**
2. Check if `jais:13b` appears in the **Generation Model** dropdown
3. Select it and save
4. Go to chat and test with Arabic text: "مرحبا"

## Performance Notes

### Model Sizes
- **Jais 13B Full (F16)**: ~26GB
- **Jais 13B Q4_0**: ~7GB (recommended)
- **Jais 13B Q5_K_M**: ~9GB (better quality)

### Resource Requirements
- **Minimum RAM**: 16GB
- **Recommended RAM**: 32GB for smooth performance
- **Storage**: 10-30GB depending on quantization

## Troubleshooting

### Model Not Showing in Admin Console
```powershell
# List all models
docker exec -it customerllm-ollama ollama list

# If model is missing, recreate it
docker exec -it customerllm-ollama ollama create jais:13b -f /root/Modelfile
```

### Out of Memory Errors
```bash
# Use a more quantized version (q4_0 instead of f16)
# Or increase Docker memory limit in Docker Desktop Settings
```

### Slow Response Times
```bash
# Consider using smaller quantization
# Or use llama3.2:latest for faster responses with Arabic support
```

## Alternative: Use llama3.2 with Arabic

The current setup uses `llama3.2:latest` which has **excellent Arabic support**:
- Understands Arabic queries
- Responds in Arabic when detected
- Faster than Jais-13b
- Already downloaded and working

To test Arabic with current setup:
1. Go to chat
2. Type: "ما هي مميزات هذا النظام؟"
3. Get Arabic response with proper RTL formatting

## Production Recommendation

For MVP/Demo:
- ✅ Use **llama3.2:latest** (already working, good Arabic support)

For Production with Arabic Focus:
- 🚀 Add **Jais-13b-q4_0** (better Arabic, larger model)
- Or use **RHELAI** with vLLM as originally planned

## Next Steps

1. **Current Models Working**:
   - ✅ llama3.2:latest (1.88 GB) - Generation
   - ✅ llama3.2:1b (1.23 GB) - Fast generation
   - ✅ nomic-embed-text:latest (0.26 GB) - Embeddings

2. **To Add Jais**:
   - Place your Jais GGUF file in the project root
   - Follow Option 1 above
   - Update environment variables
   - Test through admin console

3. **Monitor Performance**:
   - Check Grafana dashboard
   - Monitor response times in Admin Console → Monitoring
   - Adjust model based on performance needs


