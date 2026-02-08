# 📋 Payloads de Exemplo para Transações

## 🎯 Transação Simples (Single)

### Despesa Individual

```json
{
  "description": "Supermercado Carrefour",
  "amount": 150.50,
  "flow_type": "expense",
  "transaction_type": "single",
  "payment_method": {
    "type": "debit"
  },
  "date": "2026-02-08",
  "account_id": "65c3a1234567890abcdef123",
  "category_id": "65c3b1234567890abcdef456",
  "household_id": "65c3c1234567890abcdef789"
}
```

### Receita Individual

```json
{
  "description": "Salário de fevereiro",
  "amount": 3500.00,
  "flow_type": "income",
  "transaction_type": "single",
  "payment_method": {
    "type": "pix"
  },
  "date": "2026-02-05",
  "account_id": "65c3a1234567890abcdef123",
  "category_id": "65c3d1234567890abcdef789",
  "household_id": "65c3c1234567890abcdef789"
}
```

---

## 💳 Transação com Cartão de Crédito

### Com Data de Fechamento e Vencimento

```json
{
  "description": "Compras no Mercado X",
  "amount": 287.99,
  "flow_type": "expense",
  "transaction_type": "single",
  "payment_method": {
    "type": "credit_card",
    "closing_day": 15,
    "due_day": 20
  },
  "date": "2026-02-08",
  "account_id": "65c3a1234567890abcdef123",
  "category_id": "65c3b1234567890abcdef456",
  "household_id": "65c3c1234567890abcdef789"
}
```

---

## 📅 Transação Parcelada (Installment)

### TV 65" em 12x

```json
{
  "description": "TV 65 polegadas - Samsung",
  "amount": 3500.00,
  "total_amount": 3500.00,
  "flow_type": "expense",
  "transaction_type": "installment",
  "payment_method": {
    "type": "credit_card",
    "closing_day": 15,
    "due_day": 20
  },
  "date": "2026-02-08",
  "installments": 12,
  "account_id": "65c3a1234567890abcdef123",
  "category_id": "65c3e1234567890abcdef321",
  "household_id": "65c3c1234567890abcdef789"
}
```

**Resultado**: 12 lançamentos de R$ 291,67 cada

### Notebook em 6x

```json
{
  "description": "Notebook Dell Inspiron",
  "amount": 2400.00,
  "total_amount": 2400.00,
  "flow_type": "expense",
  "transaction_type": "installment",
  "payment_method": {
    "type": "credit_card",
    "closing_day": 10,
    "due_day": 15
  },
  "date": "2026-02-08",
  "installments": 6,
  "account_id": "65c3a1234567890abcdef123",
  "category_id": "65c3f1234567890abcdef654",
  "household_id": "65c3c1234567890abcdef789"
}
```

**Resultado**: 6 lançamentos de R$ 400,00 cada

---

## 👫 Transação Compartilhada - CASAL

### Divisão Igualitária (Equal)

```json
{
  "description": "Supermercado Carrefour",
  "amount": 250.00,
  "flow_type": "expense",
  "transaction_type": "single",
  "payment_method": {
    "type": "debit"
  },
  "date": "2026-02-08",
  "account_id": "65c3a1234567890abcdef123",
  "category_id": "65c3b1234567890abcdef456",
  "household_id": "65c3c1234567890abcdef789",
  "paid_by_user_id": "65c3d1234567890abcdef101",
  "split_type": "equal",
  "split_users": [
    {
      "user_id": "65c3d1234567890abcdef101",
      "paid": true
    },
    {
      "user_id": "65c3e1234567890abcdef202",
      "paid": false
    }
  ]
}
```

**Resultado**: João (pagador) R$ 125 | Maria R$ 125

### Divisão Customizada (Custom)

```json
{
  "description": "Aluguel do apartamento",
  "amount": 2000.00,
  "flow_type": "expense",
  "transaction_type": "single",
  "payment_method": {
    "type": "pix"
  },
  "date": "2026-02-01",
  "account_id": "65c3a1234567890abcdef123",
  "category_id": "65c3g1234567890abcdef789",
  "household_id": "65c3c1234567890abcdef789",
  "paid_by_user_id": "65c3d1234567890abcdef101",
  "split_type": "custom",
  "split_users": [
    {
      "user_id": "65c3d1234567890abcdef101",
      "amount": 1200.00,
      "paid": true
    },
    {
      "user_id": "65c3e1234567890abcdef202",
      "amount": 800.00,
      "paid": false
    }
  ]
}
```

**Resultado**: João R$ 1.200 | Maria R$ 800

### Divisão por Percentual (Percentage)

```json
{
  "description": "Conta de internet e luz",
  "amount": 300.00,
  "flow_type": "expense",
  "transaction_type": "single",
  "payment_method": {
    "type": "pix"
  },
  "date": "2026-02-05",
  "account_id": "65c3a1234567890abcdef123",
  "category_id": "65c3h1234567890abcdef123",
  "household_id": "65c3c1234567890abcdef789",
  "paid_by_user_id": "65c3d1234567890abcdef101",
  "split_type": "percentage",
  "split_users": [
    {
      "user_id": "65c3d1234567890abcdef101",
      "percentage": 60,
      "paid": true
    },
    {
      "user_id": "65c3e1234567890abcdef202",
      "percentage": 40,
      "paid": false
    }
  ]
}
```

**Resultado**: João R$ 180 (60%) | Maria R$ 120 (40%)

---

## 👥 Transação com 3+ Pessoas

### 3 Roommates Dividindo Aluguel

```json
{
  "description": "Aluguel da casa - fevereiro",
  "amount": 3000.00,
  "flow_type": "expense",
  "transaction_type": "single",
  "payment_method": {
    "type": "pix"
  },
  "date": "2026-02-01",
  "account_id": "65c3a1234567890abcdef123",
  "category_id": "65c3g1234567890abcdef789",
  "household_id": "65c3c1234567890abcdef789",
  "paid_by_user_id": "65c3d1234567890abcdef101",
  "split_type": "equal",
  "split_users": [
    {
      "user_id": "65c3d1234567890abcdef101",
      "paid": true
    },
    {
      "user_id": "65c3e1234567890abcdef202",
      "paid": false
    },
    {
      "user_id": "65c3f1234567890abcdef303",
      "paid": false
    }
  ]
}
```

**Resultado**: Cada um R$ 1.000

### 4 Amigos Dividindo Refeita (Custom)

```json
{
  "description": "Churrascaria - almoço dos amigos",
  "amount": 400.00,
  "flow_type": "expense",
  "transaction_type": "single",
  "payment_method": {
    "type": "credit_card"
  },
  "date": "2026-02-08",
  "account_id": "65c3a1234567890abcdef123",
  "category_id": "65c3i1234567890abcdef456",
  "household_id": "65c3c1234567890abcdef789",
  "paid_by_user_id": "65c3d1234567890abcdef101",
  "split_type": "custom",
  "split_users": [
    {
      "user_id": "65c3d1234567890abcdef101",
      "amount": 120.00,
      "paid": true
    },
    {
      "user_id": "65c3e1234567890abcdef202",
      "amount": 100.00,
      "paid": false
    },
    {
      "user_id": "65c3f1234567890abcdef303",
      "amount": 90.00,
      "paid": false
    },
    {
      "user_id": "65c3g1234567890abcdef404",
      "amount": 90.00,
      "paid": false
    }
  ]
}
```

**Resultado**: Cada um paga o valor customizado

---

## 🚗 Transação Parcelada Compartilhada

### Carro em 48x com Divisão

```json
{
  "description": "Toyota Corolla 2024",
  "amount": 120000.00,
  "total_amount": 120000.00,
  "flow_type": "expense",
  "transaction_type": "installment",
  "payment_method": {
    "type": "credit_card",
    "closing_day": 10,
    "due_day": 15
  },
  "date": "2026-02-08",
  "installments": 48,
  "account_id": "65c3a1234567890abcdef123",
  "category_id": "65c3j1234567890abcdef789",
  "household_id": "65c3c1234567890abcdef789",
  "paid_by_user_id": "65c3d1234567890abcdef101",
  "split_type": "equal",
  "split_users": [
    {
      "user_id": "65c3d1234567890abcdef101",
      "paid": true
    },
    {
      "user_id": "65c3e1234567890abcdef202",
      "paid": false
    }
  ]
}
```

**Resultado**: 
- 48 lançamentos de R$ 2.500 cada
- Cada pessoa paga R$ 1.250 por mês

---

## 🧪 Testando com cURL

### Criar Transação Simples

```bash
curl -X POST http://localhost:8000/transactions/ \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Supermercado Carrefour",
    "amount": 150.50,
    "flow_type": "expense",
    "transaction_type": "single",
    "payment_method": {
      "type": "debit"
    },
    "date": "2026-02-08",
    "account_id": "65c3a1234567890abcdef123",
    "category_id": "65c3b1234567890abcdef456",
    "household_id": "65c3c1234567890abcdef789"
  }'
```

### Criar Transação Parcelada

```bash
curl -X POST http://localhost:8000/transactions/ \
  -H "Content-Type: application/json" \
  -d '{
    "description": "TV 65 polegadas - Samsung",
    "amount": 3500.00,
    "total_amount": 3500.00,
    "flow_type": "expense",
    "transaction_type": "installment",
    "payment_method": {
      "type": "credit_card",
      "closing_day": 15,
      "due_day": 20
    },
    "date": "2026-02-08",
    "installments": 12,
    "account_id": "65c3a1234567890abcdef123",
    "category_id": "65c3e1234567890abcdef321",
    "household_id": "65c3c1234567890abcdef789"
  }'
```

### Criar Transação Compartilhada (Casal)

```bash
curl -X POST http://localhost:8000/transactions/ \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Supermercado Carrefour",
    "amount": 250.00,
    "flow_type": "expense",
    "transaction_type": "single",
    "payment_method": {
      "type": "debit"
    },
    "date": "2026-02-08",
    "account_id": "65c3a1234567890abcdef123",
    "category_id": "65c3b1234567890abcdef456",
    "household_id": "65c3c1234567890abcdef789",
    "paid_by_user_id": "65c3d1234567890abcdef101",
    "split_type": "equal",
    "split_users": [
      {
        "user_id": "65c3d1234567890abcdef101",
        "paid": true
      },
      {
        "user_id": "65c3e1234567890abcdef202",
        "paid": false
      }
    ]
  }'
```

---

## ✅ Validações

### ❌ Erro: Amount negativo

```json
{
  "description": "Teste inválido",
  "amount": -100,
  ...
}
```

**Resposta**: `"amount deve ser maior que 0"`

### ❌ Erro: Parcelamento incompleto

```json
{
  "transaction_type": "installment",
  "installments": null,
  "total_amount": null
  ...
}
```

**Resposta**: `"installments e total_amount são obrigatórios"`

### ❌ Erro: Divisão com 1 usuário

```json
{
  "split_type": "equal",
  "split_users": [
    { "user_id": "joao" }
  ]
}
```

**Resposta**: `"split_users deve conter pelo menos 2 usuários"`

### ❌ Erro: Percentuais não somam 100%

```json
{
  "split_type": "percentage",
  "split_users": [
    { "user_id": "joao", "percentage": 60 },
    { "user_id": "maria", "percentage": 30 }
  ]
}
```

**Resposta**: `"percentuais devem somar 100%"`

### ❌ Erro: Valores não batem

```json
{
  "amount": 100,
  "split_type": "custom",
  "split_users": [
    { "user_id": "joao", "amount": 50 },
    { "user_id": "maria", "amount": 60 }
  ]
}
```

**Resposta**: `"valores customizados devem somar ao amount total"`

---

## 📚 Campos Opcionais vs Obrigatórios

| Campo | Obrigatório | Tipo | Exemplo |
|-------|------------|------|---------|
| `description` | ✅ | string | "Supermercado" |
| `amount` | ✅ | float | 150.50 |
| `flow_type` | ✅ | enum | "expense" \| "income" |
| `transaction_type` | ✅ | enum | "single" \| "installment" \| "recurring" |
| `payment_method` | ✅ | object | `{"type": "debit"}` |
| `date` | ✅ | date | "2026-02-08" |
| `account_id` | ❌ | string | ObjectId |
| `category_id` | ❌ | string | ObjectId |
| `household_id` | ❌ | string | ObjectId |
| `installments` | ⚠️ | int | 12 (obrigatório se installment) |
| `total_amount` | ⚠️ | float | 3500.00 (obrigatório se installment) |
| `split_type` | ❌ | string | "equal" \| "custom" \| "percentage" |
| `split_users` | ⚠️ | array | (obrigatório se split_type) |
| `paid_by_user_id` | ❌ | string | ObjectId |

---

## 💡 Dicas Importantes

1. **Datas**: Use formato ISO `YYYY-MM-DD` (ex: "2026-02-08")
2. **ObjectIds**: Use strings com 24 caracteres hexadecimais
3. **Split com parcelamento**: O sistema gera lançamentos para cada parcela
4. **Percentuais**: Devem somar exatamente 100%
5. **Valores custom**: Devem somar exatamente ao amount
6. **Mínimo de usuários**: Split requer no mínimo 2 usuários

---

## 🔗 Endpoints Relacionados

- `POST /transactions/` - Criar transação
- `GET /transactions/` - Listar transações (requer household_id)
- `GET /transaction-entries/month/{year}/{month}` - Lançamentos do mês
- `POST /expense-splits/` - Registrar divisão
- `GET /expense-splits/household/{household_id}/balance` - Balanço domicílio
- `GET /expense-splits/user/{user_id}/balance` - Balanço individual
