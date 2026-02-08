# Estrutura de Rotas Independentes

## 📋 Resumo

O projeto agora possui **4 rotas independentes** para gerenciar diferentes entidades:

```
/households    → Domicílios
/categories    → Categorias
/accounts      → Contas
/transactions  → Transações
```

---

## 🏗️ Arquitetura

### Rotas Independentes

```
app/routes/
├── households.py    (3 endpoints)
├── categories.py    (3 endpoints)
├── accounts.py      (3 endpoints)
└── transactions.py  (4 endpoints)
```

Cada arquivo é **completamente independente** e gerencia sua própria entidade.

---

## 📍 Endpoints Disponíveis

### Households (`/households`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/` | Criar domicílio |
| GET | `/` | Listar domicílios |
| GET | `/{household_id}` | Obter detalhes |

**Exemplo:**
```bash
curl -X POST http://localhost:8000/households/ \
  -d '{"name": "Minha Casa"}'
```

---

### Categories (`/categories`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/` | Criar categoria |
| GET | `/` | Listar categorias |
| GET | `/{category_id}` | Obter detalhes |

**Filtros disponíveis:**
- `?household_id=...` para listar de um domicílio específico

**Exemplo:**
```bash
curl -X POST http://localhost:8000/categories/ \
  -d '{"name": "Supermercado", "type": "expense", "household_id": "..."}'
```

---

### Accounts (`/accounts`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/` | Criar conta |
| GET | `/` | Listar contas |
| GET | `/{account_id}` | Obter detalhes |

**Filtros disponíveis:**
- `?household_id=...` para listar de um domicílio específico

**Exemplo:**
```bash
curl -X POST http://localhost:8000/accounts/ \
  -d '{"name": "Bradesco", "type": "checking", "initial_balance": 5000, "household_id": "..."}'
```

---

### Transactions (`/transactions`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/` | Criar transação |
| GET | `/` | Listar transações |
| GET | `/entries/month/{year}/{month}` | Lançamentos do mês |
| GET | `/entries/card/{account_id}/{year}/{month}` | Extrato do cartão |

**Exemplo:**
```bash
curl -X POST http://localhost:8000/transactions/ \
  -d '{"description": "Compra", "amount": 150, ...}'
```

---

## 🔄 Fluxo de Uso

### 1️⃣ Criar Domicílio
```bash
POST /households/
{
  "name": "Casa Silva"
}
→ Retorna: household_id
```

### 2️⃣ Criar Categorias
```bash
POST /categories/
{
  "name": "Supermercado",
  "type": "expense",
  "household_id": "..."
}
→ Retorna: category_id
```

### 3️⃣ Criar Contas
```bash
POST /accounts/
{
  "name": "Bradesco",
  "type": "checking",
  "initial_balance": 5000,
  "household_id": "..."
}
→ Retorna: account_id
```

### 4️⃣ Criar Transações
```bash
POST /transactions/
{
  "description": "Supermercado",
  "amount": 150.50,
  "flow_type": "expense",
  "transaction_type": "single",
  "payment_method": {"type": "cash"},
  "date": "2026-02-08",
  "household_id": "...",
  "category_id": "...",
  "account_id": "..."
}
→ Retorna: transaction_id
```

---

## 💡 Vantagens da Estrutura Independente

✅ **Cada rota é independente** - Pode ser modificada sem afetar as outras

✅ **Reutilização** - Categorias e Accounts podem ser compartilhados entre transações

✅ **Flexibilidade** - Listar/filtrar dados de forma independente

✅ **Manutenibilidade** - Código organizado e fácil de entender

✅ **Escalabilidade** - Fácil adicionar novas rotas sem quebrar as existentes

---

## 🔍 Validações em Cada Rota

### Households
- ✅ Nome obrigatório

### Categories
- ✅ Nome obrigatório
- ✅ Type deve ser "income" ou "expense"
- ✅ Household deve existir

### Accounts
- ✅ Nome obrigatório
- ✅ Type deve ser "checking", "savings" ou "credit_card"
- ✅ Para credit_card: closing_day e due_day obrigatórios
- ✅ Household deve existir

### Transactions
- ✅ Amount deve ser > 0
- ✅ Para installment: installments e total_amount obrigatórios
- ✅ Category e Account devem existir
- ✅ Household deve existir

---

## 📖 Documentação Completa

Para exemplos detalhados, consulte:

- **README.md** - Visão geral do projeto e exemplos de transações
- **CADASTRO.md** - Guia completo de como usar cada rota
- **Swagger UI** - http://localhost:8000/docs

---

**Sistema pronto para ser usado!** 🎉
