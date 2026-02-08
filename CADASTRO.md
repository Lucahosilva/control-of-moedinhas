# Guia de Cadastro: Households, Categories e Accounts

Este documento explica como cadastrar **Domicílios (Households)**, **Categorias (Categories)** e **Contas (Accounts)** de forma independente.

## 📋 Estrutura de Rotas

As rotas estão organizadas em 3 módulos independentes:

```
/households    → Gerenciar domicílios
/categories    → Gerenciar categorias
/accounts      → Gerenciar contas
/transactions  → Criar transações
```

## 📋 Ordem de Criação Recomendada

```
1. Criar Household (Domicílio)
   ↓
2. Criar Categories (Categorias) para o Household
   ↓
3. Criar Accounts (Contas) para o Household
   ↓
4. Criar Transactions (Transações) usando IDs de Category e Account
```

---

## 1️⃣ Criar Domicílio (Household)

Um domicílio representa um grupo/família que compartilha recursos financeiros.

### Endpoint
```
POST /households/
```

### Request
```bash
curl -X POST "http://localhost:8000/households/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Casa da Família Silva"
  }'
```

### Response (201 Created)
```json
{
  "message": "Domicílio criado com sucesso",
  "household_id": "65f3b4c1d2e5f7a8b9c0d1e4",
  "name": "Casa da Família Silva"
}
```

**Guarde o `household_id` para usar nos próximos passos!**

---

### Listar Domicílios

```bash
curl "http://localhost:8000/households/"
```

**Response**:
```json
[
  {
    "_id": "65f3b4c1d2e5f7a8b9c0d1e4",
    "name": "Casa da Família Silva",
    "members": []
  }
]
```

---

### Obter Detalhes de um Domicílio

```bash
curl "http://localhost:8000/households/65f3b4c1d2e5f7a8b9c0d1e4"
```

**Response**:
```json
{
  "_id": "65f3b4c1d2e5f7a8b9c0d1e4",
  "name": "Casa da Família Silva",
  "members": []
}
```

---

## 2️⃣ Criar Categoria (Category)

Categorias são usadas para classificar transações como renda ou despesa.

### Endpoint
```
POST /categories/
```

### Request - Categoria de Despesa

```bash
curl -X POST "http://localhost:8000/categories/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Supermercado",
    "type": "expense",
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  }'
```

### Response (201 Created)
```json
{
  "message": "Categoria criada com sucesso",
  "category_id": "65f3b4c1d2e5f7a8b9c0d1e3",
  "name": "Supermercado",
  "type": "expense",
  "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
}
```

---

### Request - Categoria de Renda

```bash
curl -X POST "http://localhost:8000/categories/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Salário",
    "type": "income",
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  }'
```

---

### Criar Várias Categorias (Exemplo Completo)

Para um domicílio completo, crie estas categorias:

**Despesas:**
```bash
# Supermercado
curl -X POST "http://localhost:8000/categories/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Supermercado", "type": "expense", "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"}'

# Transporte
curl -X POST "http://localhost:8000/categories/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Transporte", "type": "expense", "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"}'

# Saúde
curl -X POST "http://localhost:8000/categories/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Saúde", "type": "expense", "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"}'

# Moradia
curl -X POST "http://localhost:8000/categories/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Moradia", "type": "expense", "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"}'
```

**Rendas:**
```bash
# Salário
curl -X POST "http://localhost:8000/categories/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Salário", "type": "income", "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"}'

# Freelance
curl -X POST "http://localhost:8000/categories/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Freelance", "type": "income", "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"}'
```

---

### Listar Categorias

**Listar todas:**
```bash
curl "http://localhost:8000/categories/"
```

**Listar de um domicílio específico:**
```bash
curl "http://localhost:8000/categories/?household_id=65f3b4c1d2e5f7a8b9c0d1e4"
```

**Response**:
```json
[
  {
    "_id": "65f3b4c1d2e5f7a8b9c0d1e3",
    "name": "Supermercado",
    "type": "expense",
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  },
  {
    "_id": "65f3b4c1d2e5f7a8b9c0d1e2",
    "name": "Salário",
    "type": "income",
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  }
]
```

---

### Obter Detalhes de uma Categoria

```bash
curl "http://localhost:8000/categories/65f3b4c1d2e5f7a8b9c0d1e3"
```

---

## 3️⃣ Criar Conta (Account)

Contas representam suas fontes de dinheiro (conta bancária, cartão, etc).

### Endpoint
```
POST /accounts/
```

### Request - Conta Corrente

```bash
curl -X POST "http://localhost:8000/accounts/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Conta Corrente Bradesco",
    "type": "checking",
    "initial_balance": 5000.00,
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  }'
```

### Response (201 Created)
```json
{
  "message": "Conta criada com sucesso",
  "account_id": "65f3b4c1d2e5f7a8b9c0d1e1",
  "name": "Conta Corrente Bradesco",
  "type": "checking",
  "initial_balance": 5000.00,
  "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
}
```

---

### Request - Conta Poupança

```bash
curl -X POST "http://localhost:8000/accounts/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Poupança Caixa",
    "type": "savings",
    "initial_balance": 2000.00,
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  }'
```

---

### Request - Cartão de Crédito

⚠️ **Obrigatório**: `closing_day` e `due_day`

```bash
curl -X POST "http://localhost:8000/accounts/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cartão Itaú",
    "type": "credit_card",
    "initial_balance": 0,
    "closing_day": 10,
    "due_day": 20,
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  }'
```

**Significado:**
- `closing_day`: Dia do mês em que a fatura fecha (ex: 10)
- `due_day`: Dia do mês em que o pagamento vence (ex: 20)

---

### Listar Contas

**Listar todas:**
```bash
curl "http://localhost:8000/accounts/"
```

**Listar de um domicílio específico:**
```bash
curl "http://localhost:8000/accounts/?household_id=65f3b4c1d2e5f7a8b9c0d1e4"
```

**Response**:
```json
[
  {
    "_id": "65f3b4c1d2e5f7a8b9c0d1e1",
    "name": "Conta Corrente Bradesco",
    "type": "checking",
    "initial_balance": 5000.00,
    "current_balance": 5000.00,
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  },
  {
    "_id": "65f3b4c1d2e5f7a8b9c0d1e0",
    "name": "Cartão Itaú",
    "type": "credit_card",
    "initial_balance": 0,
    "current_balance": 0,
    "closing_day": 10,
    "due_day": 20,
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  }
]
```

---

### Obter Detalhes de uma Conta

```bash
curl "http://localhost:8000/accounts/65f3b4c1d2e5f7a8b9c0d1e1"
```

---

## 4️⃣ Agora Crie Transações!

Com os IDs em mãos, você pode criar transações:

```bash
curl -X POST "http://localhost:8000/transactions/" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Supermercado Básico",
    "amount": 250.80,
    "flow_type": "expense",
    "transaction_type": "single",
    "payment_method": {"type": "cash"},
    "date": "2026-02-08",
    "account_id": "65f3b4c1d2e5f7a8b9c0d1e1",
    "category_id": "65f3b4c1d2e5f7a8b9c0d1e3",
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  }'
```

---

## 📊 Exemplo Completo - Do Zero ao Herói

### Passo 1: Criar Domicílio

```bash
HOUSEHOLD=$(curl -s -X POST "http://localhost:8000/households/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Minha Casa"}' | grep -o '"household_id":"[^"]*' | cut -d'"' -f4)

echo "Household ID: $HOUSEHOLD"
```

### Passo 2: Criar Categorias

```bash
# Despesa - Supermercado
CATEGORY_FOOD=$(curl -s -X POST "http://localhost:8000/categories/" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Supermercado\", \"type\": \"expense\", \"household_id\": \"$HOUSEHOLD\"}" | grep -o '"category_id":"[^"]*' | cut -d'"' -f4)

# Renda - Salário
CATEGORY_INCOME=$(curl -s -X POST "http://localhost:8000/categories/" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Salário\", \"type\": \"income\", \"household_id\": \"$HOUSEHOLD\"}" | grep -o '"category_id":"[^"]*' | cut -d'"' -f4)

echo "Category Food ID: $CATEGORY_FOOD"
echo "Category Income ID: $CATEGORY_INCOME"
```

### Passo 3: Criar Contas

```bash
# Conta Corrente
ACCOUNT=$(curl -s -X POST "http://localhost:8000/accounts/" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Bradesco\", \"type\": \"checking\", \"initial_balance\": 5000, \"household_id\": \"$HOUSEHOLD\"}" | grep -o '"account_id":"[^"]*' | cut -d'"' -f4)

echo "Account ID: $ACCOUNT"
```

### Passo 4: Criar Transações

```bash
# Transação de Despesa
curl -X POST "http://localhost:8000/transactions/" \
  -H "Content-Type: application/json" \
  -d "{
    \"description\": \"Supermercado\",
    \"amount\": 150.50,
    \"flow_type\": \"expense\",
    \"transaction_type\": \"single\",
    \"payment_method\": {\"type\": \"cash\"},
    \"date\": \"2026-02-08\",
    \"account_id\": \"$ACCOUNT\",
    \"category_id\": \"$CATEGORY_FOOD\",
    \"household_id\": \"$HOUSEHOLD\"
  }"

# Transação de Renda
curl -X POST "http://localhost:8000/transactions/" \
  -H "Content-Type: application/json" \
  -d "{
    \"description\": \"Salário\",
    \"amount\": 5000.00,
    \"flow_type\": \"income\",
    \"transaction_type\": \"single\",
    \"payment_method\": {\"type\": \"pix\"},
    \"date\": \"2026-02-08\",
    \"account_id\": \"$ACCOUNT\",
    \"category_id\": \"$CATEGORY_INCOME\",
    \"household_id\": \"$HOUSEHOLD\"
  }"
```

---

## 🔍 Validações Importantes

### Type de Category
- ✅ `"income"` - Renda
- ✅ `"expense"` - Despesa
- ❌ Qualquer outro valor resulta em erro

### Type de Account
- ✅ `"checking"` - Conta Corrente
- ✅ `"savings"` - Poupança
- ✅ `"credit_card"` - Cartão de Crédito
- ❌ Qualquer outro valor resulta em erro

### Cartão de Crédito (credit_card)
- `closing_day` e `due_day` são **obrigatórios**
- Valores de 1 a 31
- Exemplo: closing_day=10, due_day=20

---

## 💡 Dicas Úteis

1. **Guarde os IDs**: Após criar, salve os IDs em um arquivo de texto
2. **Use a documentação**: Acesse http://localhost:8000/docs para testar interativamente
3. **Teste antes**: Use a Swagger UI para validar payloads
4. **Nomeação clara**: Use nomes descritivos para categorias e contas

---

## 🆘 Erros Comuns

| Erro | Causa | Solução |
|------|-------|---------|
| `Domicílio não encontrado` | household_id inválido | Use um household_id válido |
| `type deve ser 'income' ou 'expense'` | Tipo de categoria errado | Use exatamente `"income"` ou `"expense"` |
| `closing_day e due_day são obrigatórios` | Cartão sem dias | Adicione `closing_day` e `due_day` |
| `Invalid ObjectId` | ID em formato inválido | IDs devem ter 24 caracteres hexadecimais |

---

**Pronto! Agora você pode gerenciar suas finanças!** 🎉

```
1. Criar Household (Domicílio)
   ↓
2. Criar Categories (Categorias) para o Household
   ↓
3. Criar Accounts (Contas) para o Household
   ↓
4. Criar Transactions (Transações) usando IDs de Category e Account
```

---

## 1️⃣ Criar Domicílio (Household)

Um domicílio representa um grupo/família que compartilha recursos financeiros.

### Endpoint
```
POST /households/
```

### Request
```bash
curl -X POST "http://localhost:8000/households/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Casa da Família Silva"
  }'
```

### Response (201 Created)
```json
{
  "message": "Domicílio criado com sucesso",
  "household_id": "65f3b4c1d2e5f7a8b9c0d1e4",
  "name": "Casa da Família Silva"
}
```

**Guarde o `household_id` para usar nos próximos passos!**

---

### Listar Domicílios

```bash
curl "http://localhost:8000/households/"
```

**Response**:
```json
[
  {
    "_id": "65f3b4c1d2e5f7a8b9c0d1e4",
    "name": "Casa da Família Silva",
    "members": []
  }
]
```

---

### Obter Detalhes de um Domicílio

```bash
curl "http://localhost:8000/households/65f3b4c1d2e5f7a8b9c0d1e4"
```

**Response**:
```json
{
  "_id": "65f3b4c1d2e5f7a8b9c0d1e4",
  "name": "Casa da Família Silva",
  "members": []
}
```

---

## 2️⃣ Criar Categoria (Category)

Categorias são usadas para classificar transações como renda ou despesa.

### Endpoint
```
POST /households/{household_id}/categories
```

### Request - Categoria de Despesa

```bash
curl -X POST "http://localhost:8000/households/65f3b4c1d2e5f7a8b9c0d1e4/categories" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Supermercado",
    "type": "expense",
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  }'
```

### Response (201 Created)
```json
{
  "message": "Categoria criada com sucesso",
  "category_id": "65f3b4c1d2e5f7a8b9c0d1e3",
  "name": "Supermercado",
  "type": "expense",
  "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
}
```

---

### Exemplo - Categoria de Renda

```bash
curl -X POST "http://localhost:8000/households/65f3b4c1d2e5f7a8b9c0d1e4/categories" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Salário",
    "type": "income",
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  }'
```

---

### Criar Várias Categorias (Exemplo Completo)

Para um domicílio completo, crie estas categorias:

**Despesas:**
```bash
# Supermercado
curl -X POST "http://localhost:8000/households/65f3b4c1d2e5f7a8b9c0d1e4/categories" \
  -H "Content-Type: application/json" \
  -d '{"name": "Supermercado", "type": "expense", "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"}'

# Transporte
curl -X POST "http://localhost:8000/households/65f3b4c1d2e5f7a8b9c0d1e4/categories" \
  -H "Content-Type: application/json" \
  -d '{"name": "Transporte", "type": "expense", "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"}'

# Saúde
curl -X POST "http://localhost:8000/households/65f3b4c1d2e5f7a8b9c0d1e4/categories" \
  -H "Content-Type: application/json" \
  -d '{"name": "Saúde", "type": "expense", "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"}'

# Moradia
curl -X POST "http://localhost:8000/households/65f3b4c1d2e5f7a8b9c0d1e4/categories" \
  -H "Content-Type: application/json" \
  -d '{"name": "Moradia", "type": "expense", "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"}'
```

**Rendas:**
```bash
# Salário
curl -X POST "http://localhost:8000/households/65f3b4c1d2e5f7a8b9c0d1e4/categories" \
  -H "Content-Type: application/json" \
  -d '{"name": "Salário", "type": "income", "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"}'

# Freelance
curl -X POST "http://localhost:8000/households/65f3b4c1d2e5f7a8b9c0d1e4/categories" \
  -H "Content-Type: application/json" \
  -d '{"name": "Freelance", "type": "income", "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"}'
```

---

### Listar Categorias

```bash
curl "http://localhost:8000/households/65f3b4c1d2e5f7a8b9c0d1e4/categories"
```

**Response**:
```json
[
  {
    "_id": "65f3b4c1d2e5f7a8b9c0d1e3",
    "name": "Supermercado",
    "type": "expense",
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  },
  {
    "_id": "65f3b4c1d2e5f7a8b9c0d1e2",
    "name": "Salário",
    "type": "income",
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  }
]
```

---

## 3️⃣ Criar Conta (Account)

Contas representam suas fontes de dinheiro (conta bancária, cartão, etc).

### Endpoint
```
POST /households/{household_id}/accounts
```

### Request - Conta Corrente

```bash
curl -X POST "http://localhost:8000/households/65f3b4c1d2e5f7a8b9c0d1e4/accounts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Conta Corrente Bradesco",
    "type": "checking",
    "initial_balance": 5000.00,
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  }'
```

### Response (201 Created)
```json
{
  "message": "Conta criada com sucesso",
  "account_id": "65f3b4c1d2e5f7a8b9c0d1e1",
  "name": "Conta Corrente Bradesco",
  "type": "checking",
  "initial_balance": 5000.00,
  "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
}
```

---

### Request - Conta Poupança

```bash
curl -X POST "http://localhost:8000/households/65f3b4c1d2e5f7a8b9c0d1e4/accounts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Poupança Caixa",
    "type": "savings",
    "initial_balance": 2000.00,
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  }'
```

---

### Request - Cartão de Crédito

⚠️ **Obrigatório**: `closing_day` e `due_day`

```bash
curl -X POST "http://localhost:8000/households/65f3b4c1d2e5f7a8b9c0d1e4/accounts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cartão Itaú",
    "type": "credit_card",
    "initial_balance": 0,
    "closing_day": 10,
    "due_day": 20,
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  }'
```

**Significado:**
- `closing_day`: Dia do mês em que a fatura fecha (ex: 10)
- `due_day`: Dia do mês em que o pagamento vence (ex: 20)

---

### Listar Contas

```bash
curl "http://localhost:8000/households/65f3b4c1d2e5f7a8b9c0d1e4/accounts"
```

**Response**:
```json
[
  {
    "_id": "65f3b4c1d2e5f7a8b9c0d1e1",
    "name": "Conta Corrente Bradesco",
    "type": "checking",
    "initial_balance": 5000.00,
    "current_balance": 5000.00,
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  },
  {
    "_id": "65f3b4c1d2e5f7a8b9c0d1e0",
    "name": "Cartão Itaú",
    "type": "credit_card",
    "initial_balance": 0,
    "current_balance": 0,
    "closing_day": 10,
    "due_day": 20,
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  }
]
```

---

### Obter Detalhes de uma Conta

```bash
curl "http://localhost:8000/households/65f3b4c1d2e5f7a8b9c0d1e4/accounts/65f3b4c1d2e5f7a8b9c0d1e1"
```

---

## 4️⃣ Agora Crie Transações!

Com os IDs em mãos, você pode criar transações:

```bash
curl -X POST "http://localhost:8000/transactions/" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Supermercado Básico",
    "amount": 250.80,
    "flow_type": "expense",
    "transaction_type": "single",
    "payment_method": {"type": "cash"},
    "date": "2026-02-08",
    "account_id": "65f3b4c1d2e5f7a8b9c0d1e1",
    "category_id": "65f3b4c1d2e5f7a8b9c0d1e3",
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  }'
```

---

## 📊 Exemplo Completo - Do Zero ao Herói

### Passo 1: Criar Domicílio

```bash
HOUSEHOLD=$(curl -s -X POST "http://localhost:8000/households/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Minha Casa"}' | grep -o '"household_id":"[^"]*' | cut -d'"' -f4)

echo "Household ID: $HOUSEHOLD"
```

### Passo 2: Criar Categorias

```bash
# Despesa - Supermercado
CATEGORY_FOOD=$(curl -s -X POST "http://localhost:8000/households/$HOUSEHOLD/categories" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Supermercado\", \"type\": \"expense\", \"household_id\": \"$HOUSEHOLD\"}" | grep -o '"category_id":"[^"]*' | cut -d'"' -f4)

# Renda - Salário
CATEGORY_INCOME=$(curl -s -X POST "http://localhost:8000/households/$HOUSEHOLD/categories" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Salário\", \"type\": \"income\", \"household_id\": \"$HOUSEHOLD\"}" | grep -o '"category_id":"[^"]*' | cut -d'"' -f4)

echo "Category Food ID: $CATEGORY_FOOD"
echo "Category Income ID: $CATEGORY_INCOME"
```

### Passo 3: Criar Contas

```bash
# Conta Corrente
ACCOUNT=$(curl -s -X POST "http://localhost:8000/households/$HOUSEHOLD/accounts" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Bradesco\", \"type\": \"checking\", \"initial_balance\": 5000, \"household_id\": \"$HOUSEHOLD\"}" | grep -o '"account_id":"[^"]*' | cut -d'"' -f4)

echo "Account ID: $ACCOUNT"
```

### Passo 4: Criar Transações

```bash
# Transação de Despesa
curl -X POST "http://localhost:8000/transactions/" \
  -H "Content-Type: application/json" \
  -d "{
    \"description\": \"Supermercado\",
    \"amount\": 150.50,
    \"flow_type\": \"expense\",
    \"transaction_type\": \"single\",
    \"payment_method\": {\"type\": \"cash\"},
    \"date\": \"2026-02-08\",
    \"account_id\": \"$ACCOUNT\",
    \"category_id\": \"$CATEGORY_FOOD\",
    \"household_id\": \"$HOUSEHOLD\"
  }"

# Transação de Renda
curl -X POST "http://localhost:8000/transactions/" \
  -H "Content-Type: application/json" \
  -d "{
    \"description\": \"Salário\",
    \"amount\": 5000.00,
    \"flow_type\": \"income\",
    \"transaction_type\": \"single\",
    \"payment_method\": {\"type\": \"pix\"},
    \"date\": \"2026-02-08\",
    \"account_id\": \"$ACCOUNT\",
    \"category_id\": \"$CATEGORY_INCOME\",
    \"household_id\": \"$HOUSEHOLD\"
  }"
```

---

## 🔍 Validações Importantes

### Type de Category
- ✅ `"income"` - Renda
- ✅ `"expense"` - Despesa
- ❌ Qualquer outro valor resulta em erro

### Type de Account
- ✅ `"checking"` - Conta Corrente
- ✅ `"savings"` - Poupança
- ✅ `"credit_card"` - Cartão de Crédito
- ❌ Qualquer outro valor resulta em erro

### Cartão de Crédito (credit_card)
- `closing_day` e `due_day` são **obrigatórios**
- Valores de 1 a 31
- Exemplo: closing_day=10, due_day=20

---

## 💡 Dicas Úteis

1. **Guarde os IDs**: Após criar, salve os IDs em um arquivo de texto
2. **Use a documentação**: Acesse http://localhost:8000/docs para testar interativamente
3. **Teste antes**: Use a Swagger UI para validar payloads
4. **Nomeação clara**: Use nomes descritivos para categorias e contas

---

## 🆘 Erros Comuns

| Erro | Causa | Solução |
|------|-------|---------|
| `Domicílio não encontrado` | household_id inválido | Use um household_id válido |
| `type deve ser 'income' ou 'expense'` | Tipo de categoria errado | Use exatamente `"income"` ou `"expense"` |
| `closing_day e due_day são obrigatórios` | Cartão sem dias | Adicione `closing_day` e `due_day` |
| `Invalid ObjectId` | ID em formato inválido | IDs devem ter 24 caracteres hexadecimais |

---

**Pronto! Agora você pode gerenciar suas finanças!** 🎉
