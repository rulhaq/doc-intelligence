# Jais LLM Integration Guide

## Overview

This guide explains how to integrate the Jais Arabic language model into your CustomerLLM application using Ollama.

Jais is a bilingual (Arabic-English) large language model specifically designed for Arabic language understanding and generation. It's perfect for enterprise applications requiring robust Arabic support.

## Prerequisites

- Docker and Docker Compose installed and running
- Jais model file (you mentioned you have this file)
- Ollama container running
- At least 16GB RAM recommended
- 20GB+ free disk space for the model

## Step 1: Prepare the Jais Model File

You have the Jais model file. You'll need to convert it to Ollama format or use it with Ollama's model import feature.

### Option A: Using Ollama's Model Import (Recommended)

1. First, ensure your Jais model file is in a format compatible with Ollama (GGUF format is preferred)

2. Access the Ollama container:
```bash
docker exec -it customerllm-ollama bash
```

3. Create a Modelfile for Jais:
```bash
cat > /tmp/Jais-Modelfile << 'EOF'
FROM /path/to/your/jais-model-file.gguf

TEMPLATE """{{ .System }}
{{ .Prompt }}"""

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_ctx 4096

SYSTEM """أنت نموذج لغوي ذكاء اصطناعي متقدم يتحدث العربية والإنجليزية. You are an advanced AI language model that speaks both Arabic and English."""
EOF
```

4. Import the model into Ollama:
```bash
ollama create jais:13b -f /tmp/Jais-Modelfile
```

### Option B: Direct File Copy

If you have the Jais model in GGUF format:

1. Copy your Jais model file into the Ollama container:
```powershell
docker cp path/to/your/jais-13b.gguf customerllm-ollama:/root/.ollama/models/
```

2. Create and import the model:
```bash
docker exec -it customerllm-ollama ollama create jais:13b -f /tmp/Jais-Modelfile
```

## Step 2: Verify the Model Installation

Check that Jais is available in Ollama:

```bash
docker exec customerllm-ollama ollama list
```

You should see `jais:13b` in the list.

## Step 3: Test the Model

Test Jais directly in Ollama:

```bash
docker exec -it customerllm-ollama ollama run jais:13b "مرحبا، كيف حالك؟"
```

You should receive a response in Arabic.

## Step 4: Update Application Configuration

Update the `.env` file to use Jais as the default model:

```bash
# Change this line:
OLLAMA_MODEL=llama3.2:latest

# To:
OLLAMA_MODEL=jais:13b
```

## Step 5: Restart the Backend

Restart the backend service to pick up the new configuration:

```powershell
docker compose restart backend
```

## Step 6: Configure via Admin Console

Alternatively, you can configure Jais through the Admin Console UI:

1. Log in as admin
2. Navigate to **Console → System Settings**
3. Under "LLM Configuration", select `jais:13b` from the dropdown
4. Click "Save Settings"

## Step 7: Test in the Application

1. Go to the Chat page
2. Type a message in Arabic: "ما هو الذكاء الاصطناعي؟"
3. Verify that Jais responds appropriately in Arabic

## Model Specifications

### Jais 13B Model

- **Size**: ~13 billion parameters
- **Languages**: Arabic (primary), English (secondary)
- **Context Window**: 4096 tokens (configurable)
- **Quantization**: Recommend Q4_K_M or Q5_K_M for balance of quality/speed
- **RAM Requirements**: 
  - Q4_K_M: ~8GB
  - Q5_K_M: ~10GB
  - Q8_0: ~14GB

## Performance Optimization

### For Better Arabic Text Generation:

Update the Modelfile with optimized parameters:

```modelfile
FROM /path/to/jais-model.gguf

PARAMETER temperature 0.8
PARAMETER top_p 0.95
PARAMETER top_k 50
PARAMETER repeat_penalty 1.1
PARAMETER num_ctx 8192

SYSTEM """أنت مساعد ذكي متخصص في اللغة العربية. تجيب بدقة وبشكل مفصل. 
You are an intelligent Arabic language assistant. You answer accurately and in detail."""
```

### For GPU Acceleration:

If you have GPU available, enable it in `docker-compose.yml`:

```yaml
services:
  ollama:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              capabilities: [gpu]
```

## Troubleshooting

### Issue: Model file not found

**Solution**: Verify the path to your Jais model file is correct. Use absolute paths.

### Issue: Out of memory errors

**Solution**: 
1. Use a smaller quantization (Q4 instead of Q8)
2. Reduce `num_ctx` parameter
3. Ensure Docker has enough memory allocated (Settings → Resources)

### Issue: Slow inference

**Solution**:
1. Enable GPU if available
2. Use Q4_K_M quantization for faster inference
3. Reduce context window size

### Issue: Model gives generic responses

**Solution**: Fine-tune the system prompt in the Modelfile to be more specific to your use case.

## Arabic-Specific Configuration

### RTL (Right-to-Left) Text Support

The frontend already supports RTL text detection and rendering. No additional configuration needed.

### Proper Arabic Tokenization

Jais is pre-trained with Arabic tokenization, so no special configuration is needed.

## Switching Between Models

You can easily switch between Jais and other models:

### Via Environment Variable:

```bash
# .env file
OLLAMA_MODEL=jais:13b          # For Arabic-heavy workloads
OLLAMA_MODEL=llama3.2:latest   # For English workloads
```

### Via Admin Console:

Navigate to **Console → System Settings → Generation Model** and select from the dropdown.

## Model File Formats

Jais can be in several formats. Here's how to handle each:

### GGUF Format (Recommended)
- Ready to use with Ollama
- Just copy and create model

### HuggingFace Format
- Convert using llama.cpp tools:
  ```bash
  python convert-hf-to-gguf.py /path/to/jais-hf-model
  ```

### PyTorch Format
- Convert to GGUF first using conversion scripts

## Advanced Configuration

### Multi-Model Setup

Run both Jais and other models simultaneously:

```yaml
# docker-compose.yml
services:
  ollama:
    environment:
      - OLLAMA_KEEP_ALIVE=24h
      - OLLAMA_MAX_LOADED_MODELS=2
```

Then pull/create both models:
```bash
docker exec customerllm-ollama ollama pull llama3.2:latest
docker exec customerllm-ollama ollama create jais:13b -f /tmp/Jais-Modelfile
```

Users can select their preferred model in the admin console.

## Production Considerations

1. **Model Versioning**: Tag your Jais model with version numbers (`jais:13b-v1.0`)
2. **Backup**: Keep backup of your Jais model file
3. **Monitoring**: Monitor response quality and adjust parameters
4. **Load Testing**: Test with concurrent Arabic queries
5. **Caching**: Enable response caching for common queries

## Resources

- Jais Model Card: https://huggingface.co/core42/jais-13b
- Ollama Documentation: https://ollama.ai/docs
- GGUF Format: https://github.com/ggerganov/llama.cpp

## Support

For issues specific to:
- **Jais Model**: Check Core42 AI documentation
- **Ollama Integration**: Check Ollama GitHub issues
- **Application**: Check the backend logs: `docker logs customerllm-backend`

---

**Note**: Jais requires significant computational resources. For production deployments, consider using GPU acceleration or deploying on servers with adequate RAM (32GB+ recommended for optimal performance).

