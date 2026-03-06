# 📊 Control of Moedinhas

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Async-green)
![MongoDB](https://img.shields.io/badge/MongoDB-NoSQL-brightgreen)
![Motor](https://img.shields.io/badge/Motor-Async%20Driver-success)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-blueviolet)
![Status](https://img.shields.io/badge/Status-Development-orange)
![License](https://img.shields.io/badge/License-Not%20Defined-lightgrey)

Sistema de controle financeiro desenvolvido com **FastAPI + MongoDB**, focado em organização de contas, transações, cartões de crédito e geração automática de lançamentos.

---

## 🚀 Visão Geral

O **Control of Moedinhas** é uma API REST para controle financeiro pessoal com suporte a:

- 💳 Contas bancárias (`checking`, `savings`, `credit_card`)
- 📌 Transações simples
- 🔁 Transações parceladas
- 🔄 Transações recorrentes
- 📅 Geração automática de lançamentos
- 👥 Estrutura multi-usuário (household)
- 📊 Controle de saldo atualizado por conta

Arquitetura organizada em camadas:

- `routes` → Endpoints  
- `schemas` → Validação com Pydantic v2  
- `services` → Regras de negócio  
- `db` → Conexão MongoDB  

---

## 🛠️ Stack Tecnológica

- Python 3.12+
- FastAPI
- MongoDB
- Motor (async Mongo driver)
- Pydantic v2
- Uvicorn

---

## 📂 Estrutura do Projeto

```
control-of-moedinhas/
│
├── app/
│   ├── main.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   └── mongo.py
│   ├── routes/
│   ├── schemas/
│   └── services/
│
├── .env
├── requirements.txt
└── README.md
```

---

## ⚙️ Instalação

### 1️⃣ Clone o repositório

```bash
git clone https://github.com/Lucahosilva/control-of-moedinhas.git
cd control-of-moedinhas
```

### 2️⃣ Crie um ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3️⃣ Instale as dependências

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure o arquivo `.env`

```env
MONGO_URI=mongodb://localhost:27017
LOG_LEVEL=DEBUG
```

---

## ▶️ Executando a Aplicação

```bash
uvicorn app.main:app --reload
```

Acesse a documentação interativa:

```
http://127.0.0.1:8000/docs
```

---

## 🧾 Exemplos de Uso

### 📌 Criar Conta Bancária

```json
{
  "name": "Banco Inter",
  "type": "checking",
  "initial_balance": 1000
}
```

### 💳 Criar Cartão de Crédito

```json
{
  "name": "Nubank",
  "type": "credit_card",
  "initial_balance": 0,
  "closing_day": 5,
  "due_day": 12
}
```

---

## 📌 Validações Importantes

- `type` deve ser:
  - `checking`
  - `savings`
  - `credit_card`

- Para `credit_card`, os campos abaixo são obrigatórios:
  - `closing_day`
  - `due_day`

- Datas devem estar no formato:
  ```
  YYYY-MM-DD
  ```

- Não envie `""` (string vazia) para campos inteiros.  
  Use `null` ou simplesmente omita o campo.

---

## 🧠 Regras de Negócio

- Parcelas geram múltiplos `transaction_entries`
- Transações recorrentes geram lançamentos baseados na data
- Cartões utilizam `closing_day` para cálculo de competência
- O saldo da conta é atualizado automaticamente após cada transação

---

## 🔐 Variáveis de Ambiente

| Variável   | Descrição                           |
|------------|-------------------------------------|
| MONGO_URI  | URI de conexão com MongoDB         |
| LOG_LEVEL  | DEBUG, INFO, WARNING, ERROR        |

---

## 📈 Roadmap

- [ ] Autenticação JWT
- [ ] Controle de permissões
- [ ] Dashboard financeiro
- [ ] Testes automatizados (pytest)
- [ ] Dockerização
- [ ] Deploy na AWS

---

## 📜 Licença

Ainda não definida.  
Sugestão: adicionar **MIT License** para permitir uso aberto e contribuições.

---

## 👨‍💻 Autor

Lucas Silva  
Software Engineer | Backend & Data  
Foco em AWS, Serverless e Arquitetura Orientada a Serviços
