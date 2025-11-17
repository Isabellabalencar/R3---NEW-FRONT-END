# Portal R3 – Nova Versão  
### Estrutura de Diretórios e Boas Práticas

Este documento descreve a **arquitetura padrão** do projeto **Portal R3**, com separação entre **frontend (HTML/CSS/JS)** e **backend (Python)**.  
O objetivo é garantir uma estrutura **organizada, semântica e escalável**, seguindo boas práticas de desenvolvimento web moderno.

---

## Estrutura Geral do Projeto

```
R3-Portal/
│
├── app.py                               # Servidor Flask principal
│
├── database/                            # Banco de dados e scripts relacionados
│   ├── create_db.py                     # Script para criação/inicialização do banco
│   └── Users.db                         # Banco SQLite com a tabela 'user'
│
├── static/                              # Arquivos estáticos (CSS, imagens, ícones, etc.)
│   └── assets/
│       ├── icone.png                    # Favicon do site
│       ├── login_bg.jpg                 # Imagem de fundo da tela de login
│       ├── logo_r3.png                  # Logo principal da R3 Viagens
│       └── (outros arquivos futuros)   
│
├── templates/                           # Templates HTML usados com Flask
│   ├── index.html                       # Tela de login
│   ├── lost_password.html               # Tela "Esqueci minha senha"
│   ├── home.html                        # Dashboard inicial (versão nova)
│   ├── profile.html                     # Tela de perfil do usuário
│   └── users.html                       # Tela de listagem e gestão de usuários
│
└── README_PortalR3.md                   # Documentação do projeto



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
