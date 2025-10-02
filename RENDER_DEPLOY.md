# Deploy no Render.com

Este projeto está configurado para deploy apenas do **frontend** no Render.com.

## Configuração Automática

### Arquivos de Deploy:

- `render.yaml` - Configuração principal do Render
- `build.sh` - Script de build (instala deps + build React)
- `start.sh` - Script de inicialização (serve arquivos estáticos)

### Configurações:

- **Tipo**: Web Service
- **Ambiente**: Node.js
- **Comando Build**: `chmod +x build.sh && ./build.sh`
- **Comando Start**: `chmod +x start.sh && ./start.sh`
- **Porta**: 10000 (padrão do Render)
- **Plano**: Free

### Arquivos Ignorados:

- `backend/` - Backend Python não incluído
- `venv/` - Ambiente virtual Python
- `*.py` - Arquivos Python
- `requirements.txt` - Dependências Python

## Deploy Manual

Se preferir configurar manualmente no Render:

1. Conecte seu repositório GitHub
2. Configure como **Web Service**
3. **Build Command**: `npm install && npm run build`
4. **Start Command**: `npm start`
5. **Environment**: Node.js
6. **Port**: 10000

## Recursos

- **Memória**: Frontend usa ~50-100MB (dentro do limite free)
- **Backend**: Para funcionalidade completa, deploy separadamente o backend Python em serviço dedicado
- **API**: Configure variáveis de ambiente para apontar para backend externo
