# Portal R3 – Nova Versão  
### Estrutura de Diretórios e Boas Práticas

Este documento descreve a **arquitetura padrão** do projeto **Portal R3**, com separação entre **frontend (HTML/CSS/JS)** e **backend (Python)**.  
O objetivo é garantir uma estrutura **organizada, semântica e escalável**, seguindo boas práticas de desenvolvimento web moderno.

---

## Estrutura Geral do Projeto

```
R3 - NEW FRONT-END/
│
├── backend/                           # Backend em Python (Flask + SQLite)
│   │
│   ├── app.py                         # Servidor Flask principal
│   │
│   └── database/                      # Banco de dados e scripts relacionados
│       ├── create_db.py               # Script para criação/inicialização do banco
│       └── Users.db                   # Banco SQLite com a tabela 'user'
│
│
├── frontend/                          # Parte visual do sistema
│   ├── index.html                     # Tela de login
│   │
│   └── assets/                        # Recursos visuais utilizados no frontend
│       ├── login_bg.jpg               # Imagem de fundo da tela de login
│       └── logo_r3.png                # Logo principal da R3 Viagens
│
│
└── README_PortalR3.md                 # Documentação do projeto


```

---


## Execução Local (Exemplo Flask)

```bash
# 1. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # (ou venv\Scripts\activate no Windows)

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Rodar servidor backend
cd backend
python app.py

# 4. Abrir frontend
Abra o arquivo frontend/index.html no navegador
```

---


**Autor:** Isabella Alencar  
**Versão:** 1.0  
**Data:** Novembro/2025  
**Organização:** Grupo EBG / R3 Online  
