# 📧 Lightweight Email Classifier

**Solução empresarial de classificação automática de emails com algoritmos leves e eficientes**

Uma aplicação web completa que utiliza análise de texto inteligente para classificar emails automaticamente como **Produtivos** ou **Não Produtivos** e gerar respostas automáticas contextualizadas. Otimizada para performance e baixo consumo de memória.

> 📱 **Demo ao vivo:** [https://email-classifier.vercel.app](https://email-classifier.vercel.app)  
> 🔗 **API Backend:** [https://email-classifier-backend.onrender.com](https://email-classifier-backend.onrender.com)

---

## 🚀 Features

- Upload `.txt` or `.pdf` email files, or paste text directly.
- Classifies emails into:
  - **Productive** → requires an action or response.
  - **Non-Productive** → no immediate action required.
- Generates polite, context-aware automatic replies.
- Clean, responsive web interface.

---

## 🛠️ Tech Stack

- **Frontend:** React + Vite + TypeScript
- **UI/UX:** Tailwind CSS + shadcn-ui
- **State Management:** TanStack React Query
- **Form Handling:** React Hook Form + Zod
- **Package Management:** Node.js & npm

### 📦 Dependencies

#### Main Dependencies

- React 18.3.1 + React DOM
- React Router DOM (routing)
- Radix UI components (@radix-ui/\*)
- TanStack React Query (state management)
- React Hook Form + Hookform Resolvers (forms)
- Zod (validation)
- Lucide React (icons)
- Tailwind CSS + utilities
- Class Variance Authority (styling)
- Date-fns (date utilities)
- Recharts (charts)
- Sonner (notifications)

#### Development Dependencies

- Vite (build tool)
- TypeScript + ESLint
- Tailwind CSS + plugins
- Autoprefixer + PostCSS

---

## 📂 Project Structure

```
📦 ai-email-sorter-main
┣ 📂 src/
┃ ┣ 📂 components/
┃ ┃ ┣ email-analyzer.tsx
┃ ┃ ┗ 📂 ui/ # shadcn-ui components
┃ ┣ 📂 hooks/
┃ ┣ 📂 lib/
┃ ┣ 📂 pages/
┃ ┣ App.tsx
┃ ┣ main.tsx
┃ ┗ index.css
┣ 📂 public/
┣ index.html
┣ vite.config.ts
┣ tailwind.config.ts
┣ package.json
┗ README.md
```

---

## 🚀 Execução Local

### **Pré-requisitos**

- [Node.js](https://nodejs.org/) (>= 18)
- [Python](https://python.org/) (>= 3.9)
- [Git](https://git-scm.com/)

### **1. Clone o Repositório**

```bash
git clone https://github.com/Jg-365/email-classifier.git
cd email-classifier
```

### **2. Configure o Backend (Python)**

```bash
cd backend
pip install -r requirements.txt
python app.py
```

**Backend estará rodando em:** `http://localhost:5000`

### **3. Configure o Frontend (React)**

```bash
# Em outro terminal, volte para a raiz do projeto
cd ..
npm install
npm run dev
```

**Frontend estará rodando em:** `http://localhost:5173`

### **4. Teste a Integração**

1. Acesse `http://localhost:5173`
2. Verifique se aparece "Online" no header (conexão com backend)
3. Teste com os exemplos disponíveis na aba "Exemplos"

---

## 🌐 Deploy em Produção

### **Links da Aplicação Deployada**

- **🌍 Aplicação Frontend:** [https://email-classifier.vercel.app](https://email-classifier.vercel.app)
- **⚙️ API Backend:** [https://email-classifier-backend.onrender.com](https://email-classifier-backend.onrender.com)
- **📊 Health Check:** [https://email-classifier-backend.onrender.com/api/health](https://email-classifier-backend.onrender.com/api/health)

### **Backend Deploy (Render.com)**

1. Conecte o repositório no [Render](https://render.com)
2. Configure como Web Service
3. **Root Directory:** `backend`
4. **Build Command:** `pip install -r requirements.txt`
5. **Start Command:** `gunicorn --bind 0.0.0.0:$PORT app:app`

### **Frontend Deploy (Vercel)**

1. Conecte o repositório no [Vercel](https://vercel.com)
2. **Framework:** Vite
3. **Build Command:** `npm run build`
4. **Environment Variables:**
   - `VITE_API_URL`: URL do backend no Render

---

## 📋 Como Usar a Aplicação

### **Classificação por Texto**

1. Acesse a aba "Texto"
2. Cole o conteúdo do email no campo de texto
3. Clique em "Analisar com IA"
4. Veja o resultado da classificação e resposta sugerida

### **Upload de Arquivos**

1. Acesse a aba "Arquivo"
2. Faça upload de arquivo `.txt` ou `.pdf` (máx. 16MB)
3. Clique em "Analisar com IA"
4. Visualize os resultados detalhados

### **Exemplos de Teste**

1. Acesse a aba "Exemplos"
2. Clique em qualquer exemplo para carregá-lo
3. Observe as diferenças entre emails produtivos e não produtivos

---

## 🔬 Algoritmo de Classificação Leve

### **Processamento de Texto Otimizado**

1. **Normalização:** Limpeza e padronização do texto
2. **Análise de Padrões:** Regex para detecção de estruturas específicas
3. **Contagem de Palavras-chave:** Sistema de scoring inteligente
4. **Análise Estrutural:** Métricas de texto (perguntas, exclamações, etc.)

### **Classificação Híbrida Leve**

1. **🔤 Análise de Palavras-chave:** 30+ termos produtivos/não-produtivos
2. **📊 TextBlob Sentiment:** Análise de sentimento (quando disponível)
3. **🎯 Pattern Matching:** Regex para padrões específicos (códigos de erro, etc.)
4. **⚖️ Score Inteligente:** Combinação ponderada de múltiplas fontes
5. **🚀 Performance:** Classificação em < 100ms, < 50MB RAM

### **Palavras-chave Produtivas**

`urgent`, `request`, `help`, `support`, `question`, `issue`, `problem`, `deadline`, `meeting`, `status`, `update`, `technical`, `assistance`

### **Palavras-chave Não Produtivas**

`congratulations`, `thank you`, `appreciate`, `birthday`, `holiday`, `greeting`, `newsletter`, `social`, `celebration`

---

## 🛠️ Stack Tecnológico Completo

### **Backend (Lightweight)**

- **🐍 Python 3.9+** - Linguagem principal
- **🌶️ Flask 3.1.2** - Framework web minimalista
- **📊 TextBlob** - Análise de sentimento leve (opcional)
- **📄 PyPDF2 3.0.1** - Extração de texto de PDFs
- **🔀 Flask-CORS 6.0.1** - Configuração de CORS
- **🧠 Rule-based AI** - Classificação inteligente sem modelos pesados
- **🚀 Gunicorn** - Servidor WSGI para produção
- **💾 Memory Usage:** < 50MB (vs 2GB+ com PyTorch)

### **Frontend**

- **⚛️ React 18** - Library de interface
- **📘 TypeScript** - Tipagem estática
- **⚡ Vite** - Build tool ultrarrápido
- **🎨 Tailwind CSS** - Framework de styling
- **🧩 shadcn/ui** - Componentes de alta qualidade
- **📊 Radix UI** - Componentes acessíveis
- **🔥 Lucide React** - Ícones modernos

---

## 📊 Exemplos de Classificação

### ✅ **Email Produtivo** (Score: 87%)

```
"Hi, I'm having trouble accessing my account. Can you please help me reset my password? This is urgent as I need to complete a transaction by end of day."
```

**Resposta sugerida:** "Thank you for your email. We have received your request and will prioritize it accordingly. Our team will get back to you within 24 hours with a detailed response."

### ❌ **Email Não Produtivo** (Score: 92%)

```
"Thank you so much for the excellent service last month. I really appreciate the help your team provided during the setup process."
```

**Resposta sugerida:** "Thank you for your kind message. We truly appreciate you taking the time to reach out to us."

---

## 🤝 Contribuições

Contribuições são bem-vindas! Para contribuir:

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## � Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 👥 Autor

**Desenvolvido para o Case Técnico AutoU**

- 🌐 **GitHub:** [@Jg-365](https://github.com/Jg-365)
- 📧 **Repositório:** [email-classifier](https://github.com/Jg-365/email-classifier)

---

_⭐ Se este projeto te ajudou, considere dar uma estrela no repositório!_

_⭐ Se este projeto te ajudou, considere dar uma estrela no repositório!_
