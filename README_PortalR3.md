# Portal R3 – Nova Versão  
### Estrutura de Diretórios e Boas Práticas

Este documento descreve a **arquitetura padrão** do projeto **Portal R3**, com separação entre **frontend (HTML/CSS/JS)** e **backend (Python)**.  
O objetivo é garantir uma estrutura **organizada, semântica e escalável**, seguindo boas práticas de desenvolvimento web moderno.

---

## Estrutura Geral do Projeto

```
R3 - NEW FRONT-END/
│
├── app.py                  # Servidor Flask principal com rotas e lógica de envio de e-mail
│
├── static/                 # Arquivos estáticos (imagens, ícones, estilos, etc.)
│   ├── assets/
│   │   ├── aviso.png       # Ícone de aviso
│   │   ├── icone.png       # Favicon do sistema
│   │   ├── logo_r3.png     # Logo institucional da R3 Viagens
│   │   └── outros arquivos de mídia
│   ├── css/
│   │   └── style.css       # Estilos customizados (se houver)
│   └── js/
│       └── main.js         # Scripts JavaScript principais (se houver)
│
├── templates/              # Templates HTML utilizados pelo Flask
│   ├── template.html       # Template base (herdado pelas outras páginas)
│   ├── login.html          # Tela de login
│   ├── home.html           # Dashboard inicial
│   ├── cotacoes.html       # Tela de cotações (ex: lazer ou corporativa)
│   ├── corporativo.html    # Tela específica para cotação corporativa
│   ├── perfil.html         # Tela de perfil do usuário
│   └── outras páginas HTML
│
├── .git/                   # Dados de versionamento Git
│   └── (arquivos ocultos do Git)
│
├── README_PortalR3.md      # Documentação do projeto
└── requirements.txt        # Lista de dependências do projeto Flask (sugestão: incluir)





```

---


## Execução Local (Exemplo Flask)

```bash
# 1. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # (ou venv\Scripts\activate no Windows)

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Rodar o servidor Flask
python app.py

# 4. Acessar no navegador
http://127.0.0.1:5000

```

---


**Autor:** Isabella Alencar  
**Data:** Novembro/2025  
**Organização:** Grupo EBG / R3 Online  
