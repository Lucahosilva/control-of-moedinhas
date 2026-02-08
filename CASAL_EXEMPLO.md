# 👫 Exemplo: Casal Dividindo Despesas

Este documento mostra um exemplo prático e completo de como usar o sistema para um casal dividir despesas e acompanhar quem deve para quem.

## 📋 Cenário

**João e Maria Silva** moram juntos e compartilham despesas:
- Supermercado: R$ 250 (pago por João)
- Cinema: R$ 80 (pago por Maria)  
- Luz: R$ 180 (pago por João)

**Total**: R$ 510 → **Por pessoa**: R$ 255

**Resultado**: Maria deve R$ 175 para João

---

## 🚀 Como Rodar o Exemplo

### 1. Certifique-se que o MongoDB está rodando

```bash
# Se usar Docker
docker run -d -p 27017:27017 mongo:latest

# Ou localmente
mongod
```

### 2. Configure o ambiente Python

```bash
cd /home/lucas/projects/control-of-moedinhas
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Execute o script de exemplo

```bash
python test_couple_expenses.py
```

**Saída esperada:**
```
============================================================
🏠 EXEMPLO: CASAL DIVIDINDO DESPESAS
============================================================

1️⃣  Criando domicílio...
   ✓ Domicílio criado: 65c3a...

2️⃣  Criando usuários...
   ✓ João criado: 65c3b...
   ✓ Maria criada: 65c3c...

...

💰 CÁLCULO DE QUEM DEVE PARA QUEM:
------------------------------------------------------------
João pagou: R$ 430.00
Maria pagou: R$ 80.00
Total de despesas: R$ 510.00
Por pessoa: R$ 255.00

📊 RESULTADO FINAL:
   João deve RECEBER: R$ 175.00
   Maria deve PAGAR: R$ 175.00

✅ CONCLUSÃO:
   Maria faz uma transferência PIX de R$ 175.00 para João
   E as contas ficam ZERADAS! 🎉
```

---

## 🔍 Testando via API

### 1. Inicie o servidor

```bash
uvicorn app.main:app --reload
```

### 2. Consulte o balanço do domicílio

Substitua `{household_id}` pelo ID do domicílio:

```bash
curl http://localhost:8000/expense-splits/household/{household_id}/balance
```

**Resposta esperada:**
```json
{
  "household_id": "65c3a...",
  "users": [
    {
      "user_id": "65c3b...",
      "name": "João Silva",
      "balance": 175.00,
      "meaning": "Deve receber"
    },
    {
      "user_id": "65c3c...",
      "name": "Maria Silva",
      "balance": -175.00,
      "meaning": "Deve pagar"
    }
  ]
}
```

### 3. Consulte o balanço individual

```bash
curl http://localhost:8000/expense-splits/user/{joao_id}/balance
```

**Resposta:**
```json
{
  "user_id": "65c3b...",
  "name": "João Silva",
  "total_balance": 175.00,
  "meaning": "Deve receber",
  "transactions": [
    {
      "transaction_id": "65c3d...",
      "description": "Supermercado Carrefour",
      "amount": 250.0,
      "your_share": 125.0,
      "you_paid": 250.0,
      "difference": 125.0
    },
    {
      "transaction_id": "65c3e...",
      "description": "Cinema e pipoca",
      "amount": 80.0,
      "your_share": 40.0,
      "you_paid": 0.0,
      "difference": -40.0
    },
    {
      "transaction_id": "65c3f...",
      "description": "Conta de luz",
      "amount": 180.0,
      "your_share": 90.0,
      "you_paid": 180.0,
      "difference": 90.0
    }
  ]
}
```

---

## 📱 API Endpoints para Dividir Despesas

### Criar uma Transação Compartilhada

```http
POST /transactions/
Content-Type: application/json

{
  "description": "Supermercado",
  "amount": 250.0,
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
  "split_users": [
    {
      "user_id": "65c3d1234567890abcdef101",
      "paid": true
    },
    {
      "user_id": "65c3e1234567890abcdef202",
      "paid": false
    }
  ],
  "split_type": "equal"
}
```

### Registrar a Divisão de Despesa

```http
POST /expense-splits/
Content-Type: application/json

{
  "transaction_id": "65c3f1234567890abcdef303",
  "household_id": "65c3c1234567890abcdef789",
  "split_type": "equal",
  "split_users": [
    {
      "user_id": "65c3d1234567890abcdef101",
      "paid_by_user": true
    },
    {
      "user_id": "65c3e1234567890abcdef202",
      "paid_by_user": false
    }
  ],
  "description": "Supermercado dividido entre nós"
}
```

### Obter Balanço do Domicílio

```http
GET /expense-splits/household/{household_id}/balance
```

### Obter Balanço Individual

```http
GET /expense-splits/user/{user_id}/balance
```

### Listar Todas as Divisões

```http
GET /expense-splits/?household_id={household_id}
```

### Marcar Divisão como Resolvida

```http
POST /expense-splits/{split_id}/settle
```

---

## 💡 Tipos de Divisão Disponíveis

### 1. **Equal** (Divisão Igualitária)

Todos pagam o mesmo valor.

```json
{
  "split_type": "equal",
  "amount": 100.0,
  "split_users": [
    { "user_id": "joao" },
    { "user_id": "maria" }
  ]
}
```

**Resultado**: Cada um paga R$ 50

### 2. **Custom** (Divisão Customizada)

Você especifica exatamente quanto cada um deve pagar.

```json
{
  "split_type": "custom",
  "split_users": [
    { "user_id": "joao", "amount": 60.0 },
    { "user_id": "maria", "amount": 40.0 }
  ]
}
```

**Resultado**: João paga R$ 60, Maria paga R$ 40

### 3. **Percentage** (Divisão por Percentual)

Você especifica a percentagem que cada um paga.

```json
{
  "split_type": "percentage",
  "amount": 100.0,
  "split_users": [
    { "user_id": "joao", "percentage": 60 },
    { "user_id": "maria", "percentage": 40 }
  ]
}
```

**Resultado**: João paga R$ 60, Maria paga R$ 40

---

## 👥 Para 3+ Pessoas

Funciona exatamente igual! Exemplo com 3 roommates dividindo aluguel:

```json
{
  "description": "Aluguel do mês",
  "amount": 3000.0,
  "split_type": "equal",
  "split_users": [
    { "user_id": "joao", "paid": true },
    { "user_id": "maria", "paid": false },
    { "user_id": "pedro", "paid": false }
  ]
}
```

**Resultado**: Cada um deve R$ 1.000

---

## ✅ Checklist para Implementação

- [ ] MongoDB rodando
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Executar `python test_couple_expenses.py`
- [ ] Verificar saída com cálculos corretos
- [ ] Iniciar servidor: `uvicorn app.main:app --reload`
- [ ] Testar endpoint de balanço via curl/Postman
- [ ] Verificar que balanços batem com cálculos manuais

---

## 🐛 Troubleshooting

**Erro: Connection refused**
```
Solução: Certifique-se que MongoDB está rodando
docker run -d -p 27017:27017 mongo:latest
```

**Erro: ObjectId inválida**
```
Solução: Use os IDs retornados pelo script test_couple_expenses.py
```

**Balanço incorreto**
```
Solução: Verifique se split_type e split_users estão corretos
```

---

## 📚 Documentação Relacionada

- Ver `DIVISAO_DESPESAS.md` para mais exemplos
- Ver `README.md` para overview geral do projeto
- Ver `CADASTRO.md` para como registrar domicílios, usuários, contas
