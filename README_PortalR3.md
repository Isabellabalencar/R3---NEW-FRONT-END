# Portal R3 – Nova Versão  
## Estrutura de Diretórios, Arquitetura e Boas Práticas

Este documento descreve a **arquitetura oficial** do projeto **Portal R3**, contemplando a separação clara entre **frontend (HTML/CSS/JS)** e **backend (Python/Flask)**.  

O objetivo é garantir uma base **organizada, semântica, escalável e preparada para evolução**, seguindo boas práticas de desenvolvimento web e integração com Inteligência Artificial.

---

## 📁 Estrutura Geral do Projeto

```
R3 - NEW FRONT-END/
│
├── app.py                         # Servidor Flask principal com rotas e lógica do backend
│
├── backend/                       # Módulos responsáveis pela lógica de negócio e templates de e-mail
│   ├── templates_corporate.py     # Template e regras de e-mails para cotações corporativas
│   └── templates_leisure.py       # Template e regras de e-mails para cotações de lazer
│
├── database/                      # Banco de dados e scripts auxiliares
│   ├── create_db.py               # Script de criação do banco de usuários
│   └── Users.db                   # Banco SQLite com dados dos usuários
│
├── static/                        # Arquivos estáticos
│   ├── assets/                    # Logos, ícones e imagens do sistema
│   │   ├── aviso.png
│   │   ├── icone.png
│   │   ├── login_bg.jpg
│   │   ├── logo_r3.png
│   │   └── outros arquivos visuais
│   │
│   └── profile_pics/              # Imagens de perfil dos usuários
│       ├── admin_teste.png
│       ├── icon_user.png
│       ├── icon_user.svg
│       ├── julio22.png
│       └── teste100.jpeg
│
├── templates/                     # Templates HTML renderizados pelo Flask
│   ├── template.html              # Template base (layout, navbar, estrutura comum)
│   ├── index.html                 # Tela de login
│   ├── home.html                  # Dashboard inicial
│   ├── leisure.html               # Tela de cotações de lazer
│   ├── corporate.html             # Tela de cotações corporativas
│   ├── profile.html               # Perfil do usuário
│   ├── users.html                 # Gestão de usuários (admin)
│   ├── lost_password.html         # Recuperação de senha
│   ├── powerbi.html               # Integração com dashboards Power BI
│   ├── teste.html                 # Página de testes
│   └── outras páginas HTML
│
├── .env                           # Variáveis de ambiente (API keys, credenciais)
├── .gitignore                     # Arquivos ignorados pelo Git
├── README_PortalR3.md             # Documentação técnica do projeto
└── requirements.txt               # Dependências do projeto
```

---

## ▶️ Execução Local (Flask)

```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt
python app.py
```

Acesse: http://127.0.0.1:5000

---

## 🚀 Sugestões de Melhoria e Evolução

### Fine-tuning de Modelo de IA
- Criação de modelo treinado especificamente para cotações de viagens.
- Maior consistência, menor dependência de prompts longos.
- Melhor performance e redução de custos a médio prazo.

---

## 🌐 Próximos Passos – Infraestrutura

### Domínio e Deploy
- Compra de domínio (sugestão: Hostinger)
- Configuração de DNS e SSL
- Deploy com Gunicorn + Nginx
- Separação de ambientes

---

**Autora:** Isabella Alencar  
**Data:** Novembro/2025  
**Organização:** Grupo EBG / R3 Online
