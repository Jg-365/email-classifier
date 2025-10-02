# AI Email Sorter - Backend Setup

## Ambiente Virtual Python Configurado

O projeto agora está configurado com um ambiente virtual Python isolado com todas as dependências necessárias.

### Dependências Instaladas:

- **Flask 3.1.2** - Framework web
- **Flask-CORS 6.0.1** - Suporte CORS
- **PyTorch 2.8.0+cpu** - Framework de Machine Learning
- **Transformers 4.56.2** - Modelos de IA da Hugging Face
- **PyPDF2 3.0.1** - Processamento de PDFs
- **Python-dotenv 1.1.1** - Variáveis de ambiente

### Como usar:

#### Opção 1: Script Automático

```batch
start-backend.bat
```

#### Opção 2: Manual

```batch
# Ativar ambiente virtual
venv\Scripts\activate

# Ir para pasta backend
cd backend

# Executar aplicação
python app.py
```

### Modelos AI Carregados:

- ✅ **DistilBERT** - Análise de sentimento
- ✅ **BART** - Classificação zero-shot

### Status do Servidor:

- 🌐 URL Local: http://127.0.0.1:5000
- 🔗 Health Check: http://127.0.0.1:5000/api/health
- 📊 Análise: http://127.0.0.1:5000/api/analyze (POST)

### Próximos Passos:

1. ✅ Ambiente virtual configurado
2. ✅ Dependências instaladas
3. ✅ Modelos AI carregados
4. 🔄 Deploy para Render (quando necessário)
5. 🔄 CORS fix para produção
