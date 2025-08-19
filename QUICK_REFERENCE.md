# Invoice Processing System - Quick Reference

## 🚀 Service Status Check
```bash
# Check all services
docker compose ps

# Verify service health
curl https://ocr.fivi.eu/health
curl http://localhost:11434/api/tags  # (from server)
curl https://frappe.fivi.eu/api/resource/Supplier \
  -H "Authorization: token API_KEY:API_SECRET"
```

## 🔧 Service Management
```bash
# Start all services
docker compose up -d

# Restart specific service
docker compose restart n8n
docker compose restart ollama

# View logs
docker compose logs n8n --tail 20
docker compose logs ollama --tail 20
```

## 📊 Current System Status
- ✅ **ERPNext**: https://frappe.fivi.eu (v15.72.2, Production Ready)
- ✅ **OCR Service**: https://ocr.fivi.eu (Hybrid Tesseract + Layout Analysis)
- ✅ **Ollama LLM**: Running with llama3.2:1b model (1.3GB, optimized for 2.9GB RAM)
- ⚠️ **N8N**: Container startup issue (command config needs fix)

## 🎯 Next Session Priorities
1. Fix N8N container: Update command in `compose.n8n.yaml`
2. Configure HTTPS for N8N and Ollama via Traefik
3. Import context-aware parser into N8N workflow
4. Test complete pipeline with sample invoices

## 📁 Key Files
- Context Parser: `/opt/frappe_docker/n8n-context-aware-invoice-parser.js`
- Complete Manual: `/opt/frappe_docker/INVOICE_PROCESSING_MANUAL.md`
- Ollama Setup: `/opt/frappe_docker/setup-ollama-docker.sh`
- Compose Configs: `/opt/frappe_docker/overrides/*.yaml`

## 🧪 Test Commands
```bash
# Test OCR Service
curl -X POST https://ocr.fivi.eu/process_invoice -F "file=@invoice.pdf"

# Test Ollama Model
curl http://localhost:11434/api/generate \
  -d '{"model":"llama3.2:1b","prompt":"Extract: INVOICE #123 €100","stream":false}'

# Test ERPNext API
curl https://frappe.fivi.eu/api/resource/Supplier?limit_page_length=5 \
  -H "Authorization: token API_KEY:API_SECRET"
```

## 💡 Memory-Optimized Configuration
- **Available RAM**: 2.9GB (detected automatically)
- **Selected Model**: llama3.2:1b (1.3GB) 
- **Architecture**: Hybrid OCR + Context-Aware LLM
- **Performance**: Optimized for VPS constraints

---
**Status**: Ready for N8N workflow implementation! 🎉
