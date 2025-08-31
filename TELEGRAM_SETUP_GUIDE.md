# 🚀 Guia Completo de Configuração do Bot Telegram - Garimpeiro Geek

## 📋 **VISÃO GERAL**

Este guia explica como configurar e usar o bot do Telegram para postagem automática de ofertas no canal configurado.

## 🔧 **PASSO 1: CRIAR O BOT NO TELEGRAM**

### **1.1 Obter Token do Bot**
1. Abra o Telegram e procure por `@BotFather`
2. Envie o comando `/newbot`
3. Digite um nome para o bot (ex: "Garimpeiro Geek Bot")
4. Digite um username para o bot (ex: "garimpeiro_geek_bot")
5. **Guarde o token** que o BotFather enviar

### **1.2 Configurar Permissões do Bot**
1. Envie `/setprivacy` para o @BotFather
2. Selecione seu bot
3. Escolha `Disable` para permitir que o bot leia mensagens do canal

## 📢 **PASSO 2: CRIAR/OBTER CANAL**

### **2.1 Criar Canal (se necessário)**
1. No Telegram, clique em "Menu" → "Novo Canal"
2. Digite um nome (ex: "Garimpeiro Geek - Ofertas")
3. Adicione uma descrição
4. Escolha se será público ou privado

### **2.2 Obter ID do Canal**
1. Adicione o bot `@userinfobot` ao seu canal
2. Envie qualquer mensagem no canal
3. O bot responderá com o ID do canal (ex: `-1001234567890`)

## 👤 **PASSO 3: OBTER SEU USER ID**

### **3.1 Usar @userinfobot**
1. Procure por `@userinfobot` no Telegram
2. Envie `/start`
3. O bot responderá com seu User ID (ex: `123456789`)

## ⚙️ **PASSO 4: CONFIGURAR O SISTEMA**

### **4.1 Editar telegram_config.py**
Abra o arquivo `telegram_config.py` e configure:

```python
TELEGRAM_CONFIG = {
    # Token do seu bot (obtido do @BotFather)
    "BOT_TOKEN": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
    
    # ID do canal onde as mensagens serão postadas
    "CHANNEL_ID": "-1001234567890",
    
    # Seu User ID do Telegram (para comandos admin)
    "ADMIN_USER_ID": 123456789,
    
    # Modo de teste (False = postagem real)
    "DRY_RUN": False,
    
    # ... outras configurações ...
}
```

### **4.2 Verificar Configuração**
Execute:
```bash
python telegram_config.py
```

Deve mostrar:
```
✅ Configuração do Telegram válida
🚀 Modo produção ativo - mensagens serão enviadas para o canal
```

## 🧪 **PASSO 5: TESTAR O SISTEMA**

### **5.1 Teste Básico**
Execute:
```bash
python test_telegram_posting.py
```

### **5.2 Teste de Postagem Real**
Execute:
```bash
python test_real_posting.py
```

## 📱 **PASSO 6: VERIFICAR FUNCIONAMENTO**

### **6.1 Verificar Canal**
1. Acesse o canal configurado
2. Verifique se as mensagens de teste foram postadas
3. Confirme se os links de afiliado estão funcionando

### **6.2 Verificar Logs**
As mensagens de log aparecerão no terminal durante a execução.

## 🚀 **PASSO 7: ATIVAR POSTAGEM AUTOMÁTICA**

### **7.1 Iniciar Bot**
```bash
python -m src.telegram_bot.bot
```

### **7.2 Verificar Status**
O bot deve mostrar:
```
🤖 Bot do Telegram iniciado com sucesso
📢 Canal configurado: -1001234567890
✅ Postagem automática habilitada
```

## 📊 **MONITORAMENTO E CONTROLE**

### **Comandos Disponíveis**
- `/start` - Iniciar bot
- `/help` - Mostrar ajuda
- `/status` - Status do sistema
- `/ofertas` - Buscar ofertas
- `/config` - Configurações
- `/stats` - Estatísticas

### **Estatísticas do Bot**
- Total de posts
- Posts bem-sucedidos
- Posts que falharam
- Último post
- Uptime

## 🔒 **SEGURANÇA E MODERAÇÃO**

### **Validações Automáticas**
- ✅ URLs de afiliado válidas
- ✅ Categorias permitidas
- ✅ Rate limiting
- ✅ Moderação de conteúdo

### **Categorias Bloqueadas**
- Apostas
- Jogos de azar
- Conteúdo adulto
- Drogas
- Armas

## 🛠️ **SOLUÇÃO DE PROBLEMAS**

### **Erro: "Bot Token inválido"**
- Verifique se o token está correto
- Confirme se o bot foi criado corretamente

### **Erro: "Canal não encontrado"**
- Verifique se o ID do canal está correto
- Confirme se o bot foi adicionado ao canal

### **Erro: "Permissão negada"**
- Adicione o bot ao canal como administrador
- Configure permissões de postagem

### **Mensagens não aparecem**
- Verifique se `DRY_RUN=False`
- Confirme se o bot tem permissão para postar
- Verifique os logs de erro

## 📈 **OTIMIZAÇÃO**

### **Configurações Recomendadas**
```python
TELEGRAM_CONFIG = {
    "MAX_POSTS_PER_HOUR": 20,        # Máximo de posts por hora
    "AUTO_POSTING_ENABLED": True,     # Postagem automática
    "MODERATION_ENABLED": True,       # Moderação ativa
    "INCLUDE_EMOJIS": True,           # Emojis nas mensagens
    "SHOW_ORIGINAL_PRICE": True,      # Mostrar preço original
    "SHOW_DISCOUNT_PERCENTAGE": True, # Mostrar desconto
    "SHOW_CATEGORY": True,            # Mostrar categoria
    "SHOW_STORE": True,               # Mostrar loja
}
```

### **Rate Limiting**
- Máximo: 20 posts por hora
- Delay entre posts: 3 segundos
- Validação automática de URLs

## 🎯 **EXEMPLOS DE MENSAGENS**

### **Amazon**
```
🛒 **iPhone 15 Pro - 128GB**
💰 **R$ 5999.99**
🎯 **14% OFF**
🏪 Amazon
📂 Smartphones
🔗 [Ver oferta](https://amzn.to/iphone15pro)
```

### **Magazine Luiza**
```
🛍️ **Notebook Dell Inspiron 15**
💰 **R$ 2499.99**
🎯 **17% OFF**
🏪 Magazine Luiza
📂 Notebooks
🎫 Cupom: **GEEK15**
🔗 [Ver oferta](https://magazinevoce.com.br/notebook-dell)
```

## 📞 **SUPORTE**

### **Logs de Erro**
- Verifique o terminal durante a execução
- Logs são salvos em `logs/telegram_bot.log`

### **Debug Mode**
Para ativar modo debug, edite:
```python
"LOG_LEVEL": "DEBUG"
```

## 🎉 **CONCLUSÃO**

Após seguir todos os passos:
1. ✅ Bot configurado e funcionando
2. ✅ Canal configurado e acessível
3. ✅ Sistema de postagem ativo
4. ✅ Mensagens sendo enviadas automaticamente
5. ✅ Sistema monitorado e seguro

**O Garimpeiro Geek está pronto para postar ofertas automaticamente no seu canal do Telegram!** 🚀
