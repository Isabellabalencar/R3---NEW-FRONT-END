from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import os

# Carrega variáveis do .env
load_dotenv()
def generate_aereo_section(raw_data: str, tipo_viagem: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    MODEL_NAME = "gpt-4.1-mini"

    prompt = f"""
Você é um agente especialista em EXTRAÇÃO e ESTRUTURAÇÃO de COTAÇÕES AÉREAS CORPORATIVAS.

Sua tarefa é transformar o TEXTO BRUTO fornecido em uma COTAÇÃO AÉREA ESTRUTURADA,
em TEXTO PURO (SEM HTML, XML ou MARKDOWN), pronta para ser inserida em um e-mail corporativo.

==============================
REGRAS GERAIS (OBRIGATÓRIAS)
==============================

- O resultado final DEVE ser TEXTO FORMATADO.
- NÃO use HTML, XML ou Markdown.
- Linguagem formal, objetiva e profissional.
- NÃO inventar dados.
- NÃO omitir informações.
- NÃO criar cabeçalho institucional, rodapé ou mensagens comerciais.
- Trabalhe EXCLUSIVAMENTE com dados de AÉREO.
- Mostrar TODAS as opções encontradas no texto bruto.
- Repetições no texto bruto são intencionais e devem ser preservadas.

==============================
CONTEXTO DO SISTEMA
==============================

TIPO DE VIAGEM (INFORMADO PELO SISTEMA): {tipo_viagem}

- Utilize EXATAMENTE este valor.
- NÃO inferir tipo de viagem a partir de aeroportos.
- Exibir este valor na tabela.

==============================
CLASSIFICAÇÃO OBRIGATÓRIA DOS VOOS
==============================

- Antes de gerar as tabelas, classifique cada OCORRÊNCIA de voo como:
  - VOO DIRETO
  - VOO COM CONEXÃO

- Critério de classificação:
  - VOO DIRETO: trecho único entre origem e destino final.
  - VOO COM CONEXÃO: quando o texto bruto apresentar MAIS DE UMA OCORRÊNCIA
    necessária para atingir o destino final.

- A classificação é APENAS UMA ETIQUETA.
- A classificação NÃO autoriza unir, agrupar ou colapsar linhas.

==============================
REGRA ABSOLUTA – BLOQUEIO DE AGRUPAMENTO
==============================

- CADA NÚMERO DE VOO representa UMA LINHA INDEPENDENTE.
- É PROIBIDO unir dois ou mais voos em uma única linha,
  mesmo que façam parte de uma conexão.
- Exemplo PROIBIDO:
  "8072 / 583" → ❌
- Forma CORRETA:
  Linha 1: Voo nº 8072
  Linha 2: Voo nº 583

==============================
REGRAS CRÍTICAS – DATA E HORÁRIO
==============================

- Datas (DD/MM/AAAA) e horários (HH:MM) podem aparecer em linhas separadas.
- Sempre que um horário aparecer imediatamente após uma data:
  - Primeira combinação → Horário de Saída
  - Segunda combinação → Horário de Chegada
- Reconstrua corretamente mesmo sem rótulos explícitos.
- Só use "Não Contempla" se realmente não existir horário no texto.

==============================
REGRAS CRÍTICAS – DURAÇÃO
==============================

- A duração do voo DEVE ser sempre calculada.
- Calcule usando Horário de Saída e Horário de Chegada.
- Considere mudança de data (chegada no dia seguinte ou posterior).
- Exiba no formato: XhYY (ex.: 11h20).

==============================
REGRAS CRÍTICAS – VOO Nº
==============================

- O número do voo pode estar isolado ou colado a outros textos
  (ex.: "Econômic8085", "OW E8085").
- Extraia apenas o número (1 a 4 dígitos).
- Se não existir, use: "Não Contempla".

==============================
REGRAS CRÍTICAS – COMPANHIA
==============================

- Se o nome da companhia NÃO estiver explícito no texto bruto,
  preencher com: "Não Contempla".
- NÃO criar nomes genéricos ou placeholders.

==============================
REGRAS CRÍTICAS – CAMPO ENCONTRO
==============================

- O campo "Encontro" refere-se APENAS a instruções explícitas
  (ponto de encontro, observação operacional, orientação ao passageiro).
- NÃO usar para aeroportos intermediários.
- Se não houver texto explícito, usar: "Não Contempla".

==============================
REGRAS CRÍTICAS – OPERADO POR
==============================

- "Companhia Aérea": empresa que vende o bilhete.
- "Operado Por": empresa que executa o voo.
- Preencher SOMENTE se houver indicação explícita.
- Caso contrário, usar: "Não Contempla".
-verifque a coluna de voo e extraia a informação por onde é operado
==============================
REGRAS CRÍTICAS – CLASSE
==============================

- Padronizar sempre como:
  Econômica | Executiva | Primeira Classe
- Se não houver informação explícita, usar: "Não Contempla".

==============================
TABELAS OBRIGATÓRIAS – VOOS
==============================

Você DEVE gerar DUAS TABELAS SEPARADAS, nesta ordem:

--------------------------------
✈️ VOOS DIRETOS
--------------------------------

- Incluir APENAS voos classificados como VOO DIRETO.
- Se não houver, exibir:
  "Não há voos diretos disponíveis nesta cotação."

--------------------------------
🔁 VOOS COM CONEXÃO
--------------------------------

- Incluir APENAS voos classificados como VOO COM CONEXÃO.
- Cada linha representa UM VOO INDIVIDUAL, não um itinerário.

--------------------------------
FORMATO DAS TABELAS (OBRIGATÓRIO)
--------------------------------

As DUAS tabelas devem conter EXATAMENTE as colunas abaixo,
nesta ordem, sem renomear, remover ou adicionar colunas:

Data do Voo | Horário de Saída | Horário de Chegada | Encontro |
Companhia Aérea | Voo nº | Operado Por | Partem de | Chegar a |
Duração | Bagagem | Classe | Tipo | Total (Por Voo)

- Se algum campo não existir, usar: "Não Contempla".
- É PROIBIDO trocar a ordem das colunas.
- É PROIBIDO juntar colunas.
- É PROIBIDO deduplicar linhas.

==============================
REGRA ABSOLUTA – CONTAGEM FINAL
==============================

ETAPA 1 – CONTAGEM MECÂNICA
- Conte quantas vezes existe uma DATA DE SAÍDA (DD/MM/AAAA)
  associada a um horário no texto bruto.
- Cada ocorrência representa UMA LINHA DE VOO.

ETAPA 2 – VALIDAÇÃO
- A soma das linhas das DUAS tabelas
  DEVE ser IGUAL à contagem da ETAPA 1.

ETAPA 3 – BLOQUEIO
- Se houver divergência:
  NÃO resumir
  NÃO agrupar
  NÃO otimizar
  REFÇA a separação até igualar.

==============================
TEXTO BRUTO (ÚNICA FONTE)
==============================
{raw_data}



"""


    resposta = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Você é um agente especialista em extração e estruturação de dados de cotações aéreas corporativas."},
            {"role": "user", "content": prompt}
        ]
    )

    return resposta.choices[0].message.content


def corporate_quote_template(
    client_name,
    consultant_name,
    raw_data,
    selected_services,
    aereo_texto_formatado
):
    """
    Monta o e-mail corporativo final da R3 Viagens
    (HTML final gerado por agente – SEM alterar dados)
    """

    quote_date = datetime.now().strftime("%d/%m/%Y")
    servicos = [s.strip().lower() for s in selected_services.split(",")] if selected_services else []

    # ===============================
    # 1) AGREGAÇÃO DOS CONTEÚDOS (SEM IA)
    # ===============================

    processed_quote_text = ""

    # ✈️ COTAÇÃO AÉREA (JÁ ESTRUTURADA)
    if "aéreo" in servicos or "aereo" in servicos:
        processed_quote_text += f"""✈️ COTAÇÃO AÉREA

{aereo_texto_formatado}

────────────────────────────
"""

    # (Futuro: hotel, locação, seguro, etc.)

    # ===============================
    # 2) AGENTE FINAL – HTML INSTITUCIONAL
    # ===============================

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


    prompt_html_final = f"""
Você é um agente especialista em CRIAÇÃO DE E-MAILS HTML CORPORATIVOS.

Sua tarefa é TRANSFORMAR o conteúdo fornecido em um E-MAIL HTML PROFISSIONAL,
institucional e compatível com clientes de e-mail.

==============================
REGRAS OBRIGATÓRIAS
==============================

- O RESULTADO FINAL DEVE SER APENAS HTML.
- NÃO usar Markdown.
- NÃO usar XML.
- Usar HTML simples e compatível com e-mail (table, tr, td, inline style).
- Layout limpo, corporativo e profissional.
- NÃO inventar informações.
- NÃO remover conteúdo.
- NÃO alterar valores.
- NÃO recalcular dados.
- NÃO reinterpretar informações.
- Renderizar EXATAMENTE os dados recebidos.
- Preservar TODAS as linhas e tabelas recebidas.
- NÃO repetir instruções, apenas o HTML final.

✅ ÍCONES OBRIGATÓRIOS (NÃO REMOVER):
- Preservar os ícones conforme fornecidos no conteúdo base:
  ✈️ voos | 🏨 hotel | 🚗 locação | 🛡️ seguro viagem | 🎟️ passeios | 🚐 transfers | 🚆 trens | 📦 outros
- Cada seção deve manter o ícone no título.

==============================
ESTRUTURA OBRIGATÓRIA DO E-MAIL
==============================

1. Cabeçalho institucional R3 Viagens
2. Saudação personalizada
3. Dados da cotação (data e consultor)
4. Aviso importante destacado
5. Conteúdo das cotações (converter texto em tabelas HTML, SEM ALTERAR DADOS)
6. Dicas do consultor
7. Contato
8. Rodapé institucional com endereço e links

==============================
CONTEÚDO BASE (NÃO ALTERAR)
==============================

Cliente: {client_name}
Consultor: {consultant_name}
Data da Cotação: {quote_date}

------------------------------
COTAÇÕES E SERVIÇOS
------------------------------
{processed_quote_text}

------------------------------
📌 DICAS DO CONSULTOR
------------------------------
- Verifique se seu documento de identificação está válido.
- Chegue ao aeroporto com pelo menos 2h de antecedência.
- Realize o check-in online para agilizar seu embarque.

------------------------------
📞 CONTATO
------------------------------
E-mail: atendimento@r3viagens.com.br
Telefone: (11) 3871.1959

------------------------------
RODAPÉ
------------------------------
Av. Francisco Matarazzo, 1500 - 18º andar  
Barra Funda, São Paulo - SP, 05001-100

Links:
Blog: https://r3viagens.com.br/blog/
Instagram: https://www.instagram.com/r3viagens
LinkedIn: https://www.linkedin.com/company/r3-viagens
YouTube: https://www.youtube.com/@r3viagens573
"""

    resposta_html = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Você gera e-mails HTML institucionais para envio corporativo."},
            {"role": "user", "content": prompt_html_final}
        ]
    )

    return resposta_html.choices[0].message.content
