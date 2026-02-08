# Divisão de Despesas Entre Usuários

Sistema completo para gerenciar divisões de despesas entre múltiplos usuários em um household.

## 📋 Índice

- [Conceitos](#conceitos)
- [Fluxo de Uso](#fluxo-de-uso)
- [Endpoints](#endpoints)
- [Exemplos Práticos](#exemplos-práticos)
- [Cálculo de Balanço](#cálculo-de-balanço)

---

## 🎯 Conceitos

### Tipos de Divisão

#### 1. **Equal** (Divisão Igual)
Cada usuário paga a mesma quantidade.

```
Total: R$ 100.00
Usuários: 2
Cada um paga: R$ 50.00
```

#### 2. **Custom** (Divisão Customizada)
Cada usuário paga um valor específico.

```
Total: R$ 100.00
João: R$ 60.00
Maria: R$ 40.00
```

#### 3. **Percentage** (Divisão por Percentual)
Cada usuário paga uma porcentagem.

```
Total: R$ 100.00
João: 60%  → R$ 60.00
Maria: 40% → R$ 40.00
```

---

## 🔄 Fluxo de Uso

```
1. Criar Household
   ↓
2. Criar Usuários no Household
   ↓
3. Criar Transação com split_type e split_users
   OU
3. Criar Divisão de Despesa manualmente
   ↓
4. Consultar balanço
   ↓
5. Marcar como resolvida quando quitada
```

---

## 📡 Endpoints

### 1. Gerenciar Usuários

#### Criar Usuário

**Endpoint**: `POST /users/`

**Request**:
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "email": "joao@example.com",
    "password": "senha123",
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  }'
```

**Response**:
```json
{
  "message": "Usuário criado com sucesso",
  "user_id": "65f3b4c1d2e5f7a8b9c0d1e5",
  "name": "João Silva",
  "email": "joao@example.com",
  "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
}
```

#### Listar Usuários do Household

```bash
curl "http://localhost:8000/users/household/65f3b4c1d2e5f7a8b9c0d1e4/members"
```

**Response**:
```json
[
  {
    "_id": "65f3b4c1d2e5f7a8b9c0d1e5",
    "name": "João Silva",
    "email": "joao@example.com",
    "role": "member",
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  },
  {
    "_id": "65f3b4c1d2e5f7a8b9c0d1e6",
    "name": "Maria Silva",
    "email": "maria@example.com",
    "role": "member",
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4"
  }
]
```

---

### 2. Criar Divisões de Despesas

#### Divisão Igual

**Endpoint**: `POST /expense-splits/`

```bash
curl -X POST "http://localhost:8000/expense-splits/" \
  -H "Content-Type: application/json" \
  -d '{
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4",
    "split_type": "equal",
    "description": "Pizza para dois",
    "split_users": [
      {
        "user_id": "65f3b4c1d2e5f7a8b9c0d1e5",
        "paid": true
      },
      {
        "user_id": "65f3b4c1d2e5f7a8b9c0d1e6",
        "paid": false
      }
    ]
  }'
```

#### Divisão Customizada

```bash
curl -X POST "http://localhost:8000/expense-splits/" \
  -H "Content-Type: application/json" \
  -d '{
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4",
    "split_type": "custom",
    "description": "Supermercado - diferentes quantidades",
    "split_users": [
      {
        "user_id": "65f3b4c1d2e5f7a8b9c0d1e5",
        "amount": 200.00,
        "paid": true
      },
      {
        "user_id": "65f3b4c1d2e5f7a8b9c0d1e6",
        "amount": 150.00,
        "paid": false
      }
    ]
  }'
```

#### Divisão por Percentual

```bash
curl -X POST "http://localhost:8000/expense-splits/" \
  -H "Content-Type: application/json" \
  -d '{
    "household_id": "65f3b4c1d2e5f7a8b9c0d1e4",
    "split_type": "percentage",
    "description": "Aluguel compartilhado",
    "split_users": [
      {
        "user_id": "65f3b4c1d2e5f7a8b9c0d1e5",
        "percentage": 60.0,
        "paid": true
      },
      {
        "user_id": "65f3b4c1d2e5f7a8b9c0d1e6",
        "percentage": 40.0,
        "paid": false
      }
    ]
  }'
```

---

### 3. Consultar Balanço

#### Balanço do Household

Mostra quanto cada usuário deve para cada outro.

```bash
curl "http://localhost:8000/expense-splits/household/65f3b4c1d2e5f7a8b9c0d1e4/balance"
```

**Response**:
```json
{
  "household_id": "65f3b4c1d2e5f7a8b9c0d1e4",
  "balances": {
    "65f3b4c1d2e5f7a8b9c0d1e5": {
      "user_name": "João Silva",
      "amount": -50.00,
      "status": "deve receber"
    },
    "65f3b4c1d2e5f7a8b9c0d1e6": {
      "user_name": "Maria Silva",
      "amount": 50.00,
      "status": "deve pagar"
    }
  },
  "total_pending": 1
}
```

#### Balanço do Usuário

Detalhes do que o usuário deve/deve receber.

```bash
curl "http://localhost:8000/expense-splits/user/65f3b4c1d2e5f7a8b9c0d1e6/balance?household_id=65f3b4c1d2e5f7a8b9c0d1e4"
```

**Response**:
```json
{
  "user_id": "65f3b4c1d2e5f7a8b9c0d1e6",
  "user_name": "Maria Silva",
  "household_id": "65f3b4c1d2e5f7a8b9c0d1e4",
  "total_balance": 50.00,
  "status": "deve pagar",
  "divisions_count": 1,
  "divisions": [
    {
      "split_id": "65f3b4c1d2e5f7a8b9c0d1e7",
      "description": "Pizza para dois",
      "amount": 50.00,
      "paid_by_user": false,
      "created_at": "2026-02-08T14:30:00"
    }
  ]
}
```

---

### 4. Marcar como Resolvida

Quando a divisão é quitada, marca como resolvida.

```bash
curl -X POST "http://localhost:8000/expense-splits/65f3b4c1d2e5f7a8b9c0d1e7/settle"
```

**Response**:
```json
{
  "message": "Divisão marcada como resolvida",
  "split_id": "65f3b4c1d2e5f7a8b9c0d1e7"
}
```

---

## 📊 Exemplos Práticos

### Cenário 1: Casal Dividindo Compras

#### Setup

```bash
# 1. Criar household
HOUSEHOLD="65f3b4c1d2e5f7a8b9c0d1e4"

# 2. Criar usuários
curl -X POST "http://localhost:8000/users/" \
  -d '{
    "name": "João",
    "email": "joao@example.com",
    "password": "pass",
    "household_id": "'$HOUSEHOLD'"
  }' > joao.json

JOAO=$(jq -r '.user_id' joao.json)

curl -X POST "http://localhost:8000/users/" \
  -d '{
    "name": "Maria",
    "email": "maria@example.com",
    "password": "pass",
    "household_id": "'$HOUSEHOLD'"
  }' > maria.json

MARIA=$(jq -r '.user_id' maria.json)
```

#### Compra no Supermercado

João compra coisas para dois, paga R$ 100.00

```bash
curl -X POST "http://localhost:8000/expense-splits/" \
  -H "Content-Type: application/json" \
  -d '{
    "household_id": "'$HOUSEHOLD'",
    "split_type": "equal",
    "description": "Supermercado - compras compartilhadas",
    "split_users": [
      {
        "user_id": "'$JOAO'",
        "paid": true
      },
      {
        "user_id": "'$MARIA'",
        "paid": false
      }
    ]
  }'
```

**Resultado**: Maria deve R$ 50.00 para João

#### Verificar Balanço

```bash
curl "http://localhost:8000/expense-splits/user/$MARIA/balance?household_id=$HOUSEHOLD"
```

#### Maria Paga

```bash
curl -X POST "http://localhost:8000/expense-splits/{split_id}/settle"
```

---

### Cenário 2: Aluguel em 3 Pessoas

```bash
# Setup
CASA="65f3b4c1d2e5f7a8b9c0d1e4"
JOAO="65f3b4c1d2e5f7a8b9c0d1e5"
MARIA="65f3b4c1d2e5f7a8b9c0d1e6"
PEDRO="65f3b4c1d2e5f7a8b9c0d1e7"

# Aluguel: R$ 3000
# João paga tudo no cartão
# Maria paga 40% (R$ 1200)
# Pedro paga 60% (R$ 1800)

curl -X POST "http://localhost:8000/expense-splits/" \
  -H "Content-Type: application/json" \
  -d '{
    "household_id": "'$CASA'",
    "split_type": "percentage",
    "description": "Aluguel - Fevereiro 2026",
    "split_users": [
      {
        "user_id": "'$JOAO'",
        "percentage": 0,
        "paid": true
      },
      {
        "user_id": "'$MARIA'",
        "percentage": 40.0,
        "paid": false
      },
      {
        "user_id": "'$PEDRO'",
        "percentage": 60.0,
        "paid": false
      }
    ]
  }'
```

#### Ver quem deve o quê

```bash
curl "http://localhost:8000/expense-splits/household/$CASA/balance"
```

Resultado esperado:
- João: -R$ 3000 (deve receber)
- Maria: R$ 1200 (deve pagar)
- Pedro: R$ 1800 (deve pagar)

---

## 💰 Cálculo de Balanço

### Como Funciona

1. Para cada divisão não resolvida:
   - Identifica quem pagou
   - Calcula quanto cada um deve pagar
   
2. Para cada usuário:
   - Soma quanto deve em todas as divisões onde não pagou
   - Subtrai quanto outros devem para ele

### Exemplo

```
Divisão 1: Pizza R$ 100
- João pagou
- Maria deve R$ 50

Divisão 2: Aluguel R$ 3000
- João pagou
- Maria deve R$ 1200

Balanço de Maria:
Total devido = R$ 50 + R$ 1200 = R$ 1250
Status: deve pagar R$ 1250 para João
```

---

## 🔍 Validações

✅ **Household deve existir**

✅ **Todos os usuários devem estar no mesmo household**

✅ **Para percentage split: percentuais devem somar 100%**

✅ **Para custom split: valores devem somar ao total**

✅ **Pelo menos 2 usuários na divisão**

---

## 📝 Notas Importantes

1. **Quem Pagou**: Marque `paid: true` para quem pagou a despesa original
2. **Divisões Resolvidas**: Após pagar, use `{split_id}/settle` para marcar como resolvida
3. **Balanço Negativo**: Significa que o usuário deve receber dinheiro
4. **Balanço Positivo**: Significa que o usuário deve pagar dinheiro

---

**Sistema de divisão de despesas pronto para usar!** 🎉
