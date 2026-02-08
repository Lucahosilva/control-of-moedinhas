# Control of Moedinhas 💰

Sistema de controle financeiro desenvolvido em **FastAPI** com integração ao **MongoDB** para gerenciar transações, categorias, contas e lançamentos de forma segura e eficiente.

## 📋 Índice

- [Características](#características)
- [Tecnologias](#tecnologias)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Como Usar](#como-usar)
- [Exemplos de API](#exemplos-de-api)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Testes](#testes)

---

## ✨ Características

- 🔐 **Transações Seguras**: Salva e gerencia transações financeiras
- 📊 **Múltiplos Tipos**: Suporta transações simples, parceladas e recorrentes
- 💳 **Métodos de Pagamento**: Cash, débito, crédito e PIX
- 📈 **Lançamentos Automáticos**: Gera automaticamente lançamentos para transações parceladas
- 👥 **Múltiplos Usuários**: Suporte para vários usuários por domicílio
- 💸 **Divisão de Despesas**: Divida despesas entre usuários (igual, customizado, percentual)
- 📊 **Balanço Automático**: Calcula automaticamente quem deve para quem
- 🏦 **Integração MongoDB**: Banco de dados NoSQL para flexibilidade
- 🔗 **API REST Completa**: Endpoints para criar, listar e filtrar transações
- ✅ **Validações Robustas**: Validação de dados com Pydantic v2

---

## 🛠️ Tecnologias

| Tecnologia | Versão | Descrição |
|-----------|--------|-----------|
| FastAPI | 0.128.4 | Framework web assíncrono |
| MongoDB | 4.16.0 | Banco de dados NoSQL |
| Motor | 3.7.1 | Driver async para MongoDB |
| Pydantic | 2.12.5 | Validação de dados |
| Python | 3.12+ | Linguagem de programação |

---

## 📦 Instalação

### Pré-requisitos

- Python 3.12+
- MongoDB (em execução)
- pip (gerenciador de pacotes)

### Passo 1: Clonar o repositório

```bash
git clone https://github.com/Lucahosilva/control-of-moedinhas.git
cd control-of-moedinhas
```

### Passo 2: Criar ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### Passo 3: Instalar dependências

```bash
pip install -r requirements.txt
```

### Passo 4: Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
MONGO_URI=mongodb+srv://usuario:senha@cluster.mongodb.net/?retryWrites=true&w=majority
```

**Nota**: Substitua `usuario`, `senha` e `cluster` pelas suas credenciais do MongoDB Atlas.

---

## ⚙️ Configuração

### Estrutura do Projeto

```
control-of-moedinhas/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicação principal FastAPI
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py           # Configurações (MongoDB URI)
│   ├── db/
│   │   ├── __init__.py
│   │   └── mongo.py            # Conexão MongoDB
│   ├── routes/
│   │   ├── __init__.py
│   │   └── transactions.py     # Rotas de transações
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── base.py             # Modelos base (PyObjectId, MongoBaseModel)
│   │   ├── transaction.py      # Schema de transação
│   │   ├── transaction_entry.py # Schema de lançamento
│   │   ├── account.py          # Schema de conta
│   │   ├── category.py         # Schema de categoria
│   │   ├── household.py        # Schema de domicílio
│   │   └── user.py             # Schema de usuário
│   └── services/
│       ├── __init__.py
│       ├── transaction_service.py  # Lógica de geração de lançamentos
│       └── date_utils.py           # Utilitários de data
├── .env                        # Variáveis de ambiente (não versionado)
├── requirements.txt            # Dependências Python
└── README.md                   # Este arquivo
```

---

## 🚀 Como Usar

### Iniciar o Servidor

```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

Saída esperada:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

Acesse a documentação interativa em: **http://localhost:8000/docs**

### Parar o Servidor

Pressione `CTRL+C` no terminal

---

## 📡 Exemplos de API

### 1. Criar Transação Simples (Single)

**Endpoint**: `POST /transactions/`

**Request**:
```bash
curl -X POST "http://localhost:8000/transactions/" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Compra no supermercado",
    "amount": 150.50,
    "flow_type": "expense",
    "transaction_type": "single",
    "payment_method": {
      "type": "cash"
    },
    "date": "2026-02-08",
    "account_id": "65f3b4c1d2e5f7a8b9c0d1e2",
    "category_id": "65f3b4c1d2e5f7a8b9c0d1e3",
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  }'
```

**Response** (201 Created):
```json
{
  "message": "Transação criada com sucesso",
  "transaction_id": "65f3b4c1d2e5f7a8b9c0d1e5",
  "entries_created": 1
}
```

---

### 2. Criar Transação Parcelada (Installment)

**Endpoint**: `POST /transactions/`

**Request**:
```bash
curl -X POST "http://localhost:8000/transactions/" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Compra parcelada no débito",
    "amount": 100.00,
    "flow_type": "expense",
    "transaction_type": "installment",
    "payment_method": {
      "type": "credit_card",
      "closing_day": 10,
      "due_day": 20
    },
    "date": "2026-02-08",
    "installments": 3,
    "total_amount": 300.00,
    "account_id": "65f3b4c1d2e5f7a8b9c0d1e2",
    "category_id": "65f3b4c1d2e5f7a8b9c0d1e3",
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  }'
```

**Response** (201 Created):
```json
{
  "message": "Transação criada com sucesso",
  "transaction_id": "65f3b4c1d2e5f7a8b9c0d1e5",
  "entries_created": 3
}
```

Nota: Gera automaticamente 3 lançamentos de R$ 100.00 cada

---

### 3. Listar Transações

**Endpoint**: `GET /transactions/?household_id=65f3b4c1d2e5f7a8b9c0d1e4`

**Request**:
```bash
curl "http://localhost:8000/transactions/?household_id=65f3b4c1d2e5f7a8b9c0d1e4"
```

**Response**:
```json
[
  {
    "_id": "65f3b4c1d2e5f7a8b9c0d1e5",
    "description": "Compra no supermercado",
    "amount": 150.50,
    "flow_type": "expense",
    "transaction_type": "single",
    "date": "2026-02-08T00:00:00",
    "account_id": "65f3b4c1d2e5f7a8b9c0d1e2"
  }
]
```

---

### 4. Listar Lançamentos do Mês

**Endpoint**: `GET /transactions/entries/month/{year}/{month}`

**Request**:
```bash
curl "http://localhost:8000/transactions/entries/month/2026/02?household_id=65f3b4c1d2e5f7a8b9c0d1e4"
```

**Response**:
```json
[
  {
    "_id": "65f3b4c1d2e5f7a8b9c0d1e6",
    "transaction_id": "65f3b4c1d2e5f7a8b9c0d1e5",
    "description": "Compra no supermercado",
    "amount": 150.50,
    "competence_month": "2026-02",
    "due_date": "2026-02-08T00:00:00",
    "status": "open",
    "payment_method": "cash"
  }
]
```

---

### 5. Extrato do Cartão de Crédito

**Endpoint**: `GET /transactions/entries/card/{account_id}/{year}/{month}`

**Request**:
```bash
curl "http://localhost:8000/transactions/entries/card/65f3b4c1d2e5f7a8b9c0d1e2/2026/02?household_id=65f3b4c1d2e5f7a8b9c0d1e4"
```

**Response**:
```json
{
  "competence_month": "2026-02",
  "total": 300.00,
  "entries": [
    {
      "_id": "65f3b4c1d2e5f7a8b9c0d1e7",
      "description": "Compra parcelada no débito 1/3",
      "amount": 100.00,
      "due_date": "2026-02-20T00:00:00"
    }
  ]
}
```

---

## 🏗️ Estrutura do Projeto

### Modelos de Dados

#### TransactionCreate (Schema de Entrada)
```python
{
  "description": str,           # Descrição da transação
  "amount": float,              # Valor (para single/recurring)
  "flow_type": "income|expense",# Tipo de fluxo
  "transaction_type": "single|installment|recurring",
  "payment_method": {
    "type": "cash|debit|credit_card|pix",
    "closing_day": int?,        # Para cartão de crédito
    "due_day": int?             # Para cartão de crédito
  },
  "date": date,                 # Data da transação
  "installments": int?,         # Número de parcelas (para installment)
  "total_amount": float?,       # Valor total (para installment)
  "account_id": str,            # ID da conta
  "category_id": str,           # ID da categoria
  "household_id": str           # ID do domicílio
}
```

#### TransactionEntryCreate (Schema de Lançamento)
```python
{
  "transaction_id": ObjectId,   # Referência à transação
  "description": str,           # Descrição do lançamento
  "amount": float,              # Valor do lançamento
  "competence_month": str,      # Mês de competência (YYYY-MM)
  "due_date": date,             # Data de vencimento
  "status": "open|paid",        # Status (padrão: open)
  "payment_method": str,        # Método de pagamento
  "account_id": ObjectId,       # Referência à conta
  "category_id": ObjectId,      # Referência à categoria
  "household_id": ObjectId      # Referência ao domicílio
}
```

### Tipos de Transações

| Tipo | Descrição | Parcelas | Lançamentos |
|------|-----------|----------|------------|
| **single** | Transação única | ❌ | 1 lançamento |
| **installment** | Parcelada | ✅ | N lançamentos (1 por parcela) |
| **recurring** | Recorrente | ❌ | 1 lançamento |

### Métodos de Pagamento

| Método | Requer closing_day? | Requer due_day? | Uso |
|--------|:-------------------:|:---------------:|-----|
| **cash** | ❌ | ❌ | Dinheiro |
| **debit** | ❌ | ❌ | Cartão de débito |
| **credit_card** | ✅ | ✅ | Cartão de crédito |
| **pix** | ❌ | ❌ | PIX |

---

## ✅ Testes

### Teste Rápido (Sem Servidor)

Execute diretamente um teste de integração:

```bash
source venv/bin/activate
python3 << 'EOF'
import asyncio
from datetime import date
from bson import ObjectId
from app.schemas.transaction import TransactionCreate, PaymentMethod, FlowType, TransactionType, PaymentMethodType
from app.services.transaction_service import TransactionService

async def test():
    # Teste de transação parcelada
    tx = TransactionCreate(
        description="Compra parcelada",
        amount=100.00,
        flow_type=FlowType.expense,
        transaction_type=TransactionType.installment,
        payment_method=PaymentMethod(
            type=PaymentMethodType.credit_card,
            closing_day=10,
            due_day=20
        ),
        date=date.today(),
        installments=3,
        total_amount=300.00,
        account_id=str(ObjectId()),
        category_id=str(ObjectId()),
        household_id=str(ObjectId())
    )
    
    entries = TransactionService.generate_entries(tx)
    print(f"✓ Transação gerou {len(entries)} lançamentos")
    for i, e in enumerate(entries, 1):
        print(f"  Parcela {i}: R$ {e.amount}")

asyncio.run(test())
EOF
```

### Teste com o Servidor Rodando

1. **Inicie o servidor**:
   ```bash
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. **Em outro terminal, crie uma transação**:
   ```bash
   curl -X POST "http://localhost:8000/transactions/" \
     -H "Content-Type: application/json" \
     -d '{
       "description": "Teste",
       "amount": 100,
       "flow_type": "expense",
       "transaction_type": "single",
       "payment_method": {"type": "cash"},
       "date": "2026-02-08",
       "household_id": "65f3b4c1d2e5f7a8b9c0d1e4",
       "category_id": "65f3b4c1d2e5f7a8b9c0d1e3",
       "account_id": "65f3b4c1d2e5f7a8b9c0d1e2"
     }'
   ```

3. **Verifique na documentação**:
   - Acesse http://localhost:8000/docs
   - Teste os endpoints interativamente
   - Visualize os schemas

---

## 🔧 Troubleshooting

### Erro: "Address already in use"

Outra instância está rodando na porta 8000:

```bash
# Matar processo na porta 8000
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Ou usar porta diferente
uvicorn app.main:app --reload --port 8001
```

### Erro: "MONGO_URI not found"

Verifique se o arquivo `.env` existe e contém:

```bash
cat .env
# Deve exibir:
# MONGO_URI=mongodb+srv://...
```

### Erro: "Connection refused" ao MongoDB

Verifique se:
- MongoDB está em execução
- A URI de conexão está correta
- Seu IP está autorizado no MongoDB Atlas (whitelist)

### Erro: "Invalid ObjectId"

ObjectIds devem ser:
- Strings válidas de 24 caracteres hexadecimais, OU
- Objetos ObjectId válidos

Exemplo válido: `65f3b4c1d2e5f7a8b9c0d1e2`

---

## 📝 Exemplos de Caso de Uso

### Cenário 1: Compra no Supermercado (Cash)

```json
{
  "description": "Supermercado Básico",
  "amount": 250.80,
  "flow_type": "expense",
  "transaction_type": "single",
  "payment_method": {
    "type": "cash"
  },
  "date": "2026-02-08",
  "account_id": "65f3b4c1d2e5f7a8b9c0d1e2",
  "category_id": "65f3b4c1d2e5f7a8b9c0d1e3",
  "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
}
```

✓ Cria 1 lançamento imediatamente

### Cenário 2: Compra Parcelada no Cartão

```json
{
  "description": "Geladeira LG",
  "amount": 500.00,
  "flow_type": "expense",
  "transaction_type": "installment",
  "payment_method": {
    "type": "credit_card",
    "closing_day": 10,
    "due_day": 20
  },
  "date": "2026-02-05",
  "installments": 12,
  "total_amount": 6000.00,
  "account_id": "65f3b4c1d2e5f7a8b9c0d1e2",
  "category_id": "65f3b4c1d2e5f7a8b9c0d1e3",
  "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
}
```

✓ Cria 12 lançamentos de R$ 500.00
✓ Distribui em 12 meses
✓ Calcula datas conforme closing_day e due_day

### Cenário 3: Renda Mensal (PIX)

```json
{
  "description": "Salário",
  "amount": 5000.00,
  "flow_type": "income",
  "transaction_type": "recurring",
  "payment_method": {
    "type": "pix"
  },
  "date": "2026-02-08",
  "account_id": "65f3b4c1d2e5f7a8b9c0d1e2",
  "category_id": "65f3b4c1d2e5f7a8b9c0d1e3",
  "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
}
```

✓ Cria 1 lançamento de renda
✓ Contabilizado como income

---

## 📚 Referências

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [MongoDB Documentation](https://docs.mongodb.com)
- [Motor Documentation](https://motor.readthedocs.io)
- [Pydantic Documentation](https://docs.pydantic.dev)

---

## 🤝 Contribuindo

Sinta-se à vontade para abrir issues e pull requests!

---

## 📄 Licença

Este projeto está sob licença MIT.

---

**Desenvolvido por**: Lucas Silva  
**Última atualização**: 8 de fevereiro de 2026