"""
Exemplo completo: Casal dividindo despesas

Este script demonstra como usar o sistema para registrar despesas compartilhadas
entre dois usuários (casal) com divisão automática de saldos.

Fluxo:
1. Criar um domicílio
2. Criar dois usuários (casal)
3. Criar contas e categorias
4. Registrar transações compartilhadas
5. Verificar quem deve para quem
"""

import asyncio
import json
from datetime import date, datetime, timedelta
from motor.motor_asyncio import AsyncClient

# Configurar MongoDB
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "control_of_moedinhas"

async def main():
    client = AsyncClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print("\n" + "="*60)
        print("🏠 EXEMPLO: CASAL DIVIDINDO DESPESAS")
        print("="*60)
        
        # 1. Criar domicílio
        print("\n1️⃣  Criando domicílio...")
        household_doc = {
            "name": "Casa do Casal Silva",
            "description": "Domicílio da família Silva",
            "members": [],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        household_result = await db.households.insert_one(household_doc)
        household_id = household_result.inserted_id
        print(f"   ✓ Domicílio criado: {household_id}")
        
        # 2. Criar usuários
        print("\n2️⃣  Criando usuários...")
        users = [
            {
                "name": "João Silva",
                "email": "joao@silva.com",
                "password_hash": "hash_joao",
                "role": "admin",
                "household_id": household_id,
                "created_at": datetime.now()
            },
            {
                "name": "Maria Silva",
                "email": "maria@silva.com",
                "password_hash": "hash_maria",
                "role": "member",
                "household_id": household_id,
                "created_at": datetime.now()
            }
        ]
        
        users_result = await db.users.insert_many(users)
        joao_id = users_result.inserted_ids[0]
        maria_id = users_result.inserted_ids[1]
        print(f"   ✓ João criado: {joao_id}")
        print(f"   ✓ Maria criada: {maria_id}")
        
        # Adicionar membros ao domicílio
        await db.households.update_one(
            {"_id": household_id},
            {"$set": {"members": [joao_id, maria_id]}}
        )
        
        # 3. Criar conta bancária
        print("\n3️⃣  Criando conta bancária...")
        account_doc = {
            "name": "Conta Conjunta",
            "account_type": "checking",
            "balance": 5000.0,
            "household_id": household_id,
            "created_at": datetime.now()
        }
        account_result = await db.accounts.insert_one(account_doc)
        account_id = account_result.inserted_id
        print(f"   ✓ Conta criada: {account_id}")
        
        # 4. Criar categorias
        print("\n4️⃣  Criando categorias...")
        categories_data = [
            {"name": "Alimentação", "household_id": household_id},
            {"name": "Lazer", "household_id": household_id},
            {"name": "Utilidades", "household_id": household_id}
        ]
        categories_result = await db.categories.insert_many(categories_data)
        alimentacao_id = categories_result.inserted_ids[0]
        lazer_id = categories_result.inserted_ids[1]
        utilidades_id = categories_result.inserted_ids[2]
        print(f"   ✓ Alimentação: {alimentacao_id}")
        print(f"   ✓ Lazer: {lazer_id}")
        print(f"   ✓ Utilidades: {utilidades_id}")
        
        # 5. Registrar transações compartilhadas
        print("\n5️⃣  Registrando transações compartilhadas...\n")
        
        transactions = [
            {
                "description": "Supermercado Carrefour",
                "amount": 250.0,
                "flow_type": "expense",
                "transaction_type": "single",
                "payment_method": {"type": "debit"},
                "date": datetime.now(),
                "account_id": account_id,
                "category_id": alimentacao_id,
                "household_id": household_id,
                "paid_by": "João",
                "paid_by_user_id": str(joao_id),
                "split_users": [
                    {"user_id": str(joao_id), "amount": 125.0, "paid": True},
                    {"user_id": str(maria_id), "amount": 125.0, "paid": False}
                ],
                "split_type": "equal"
            },
            {
                "description": "Cinema e pipoca",
                "amount": 80.0,
                "flow_type": "expense",
                "transaction_type": "single",
                "payment_method": {"type": "credit_card"},
                "date": datetime.now(),
                "account_id": account_id,
                "category_id": lazer_id,
                "household_id": household_id,
                "paid_by": "Maria",
                "paid_by_user_id": str(maria_id),
                "split_users": [
                    {"user_id": str(joao_id), "amount": 40.0, "paid": False},
                    {"user_id": str(maria_id), "amount": 40.0, "paid": True}
                ],
                "split_type": "equal"
            },
            {
                "description": "Conta de luz",
                "amount": 180.0,
                "flow_type": "expense",
                "transaction_type": "single",
                "payment_method": {"type": "pix"},
                "date": datetime.now(),
                "account_id": account_id,
                "category_id": utilidades_id,
                "household_id": household_id,
                "paid_by": "João",
                "paid_by_user_id": str(joao_id),
                "split_users": [
                    {"user_id": str(joao_id), "amount": 90.0, "paid": True},
                    {"user_id": str(maria_id), "amount": 90.0, "paid": False}
                ],
                "split_type": "equal"
            }
        ]
        
        trans_ids = []
        for i, trans in enumerate(transactions, 1):
            result = await db.transactions.insert_one(trans)
            trans_ids.append(result.inserted_id)
            print(f"   ✓ Transação {i}: {trans['description']} (R$ {trans['amount']})")
            print(f"     Pago por: {trans['paid_by']}")
            print(f"     Divisão: {trans['split_type']}")
        
        # 6. Criar registros de divisão de despesas
        print("\n6️⃣  Criando registros de divisão de despesas...\n")
        
        splits = [
            {
                "transaction_id": trans_ids[0],
                "household_id": household_id,
                "split_users": [
                    {"user_id": str(joao_id), "amount": 125.0, "paid_by_user": True},
                    {"user_id": str(maria_id), "amount": 125.0, "paid_by_user": False}
                ],
                "split_type": "equal",
                "description": "Supermercado dividido em partes iguais",
                "settled": False,
                "created_at": datetime.now()
            },
            {
                "transaction_id": trans_ids[1],
                "household_id": household_id,
                "split_users": [
                    {"user_id": str(joao_id), "amount": 40.0, "paid_by_user": False},
                    {"user_id": str(maria_id), "amount": 40.0, "paid_by_user": True}
                ],
                "split_type": "equal",
                "description": "Cinema dividido em partes iguais",
                "settled": False,
                "created_at": datetime.now()
            },
            {
                "transaction_id": trans_ids[2],
                "household_id": household_id,
                "split_users": [
                    {"user_id": str(joao_id), "amount": 90.0, "paid_by_user": True},
                    {"user_id": str(maria_id), "amount": 90.0, "paid_by_user": False}
                ],
                "split_type": "equal",
                "description": "Luz dividida em partes iguais",
                "settled": False,
                "created_at": datetime.now()
            }
        ]
        
        split_results = await db.expense_splits.insert_many(splits)
        for i, split_id in enumerate(split_results.inserted_ids, 1):
            print(f"   ✓ Divisão {i} registrada: {split_id}")
        
        # 7. Calcular saldos
        print("\n7️⃣  Calculando saldos finais...\n")
        
        # Resumo das transações
        print("📋 RESUMO DAS TRANSAÇÕES:")
        print("-" * 60)
        print(f"{'Transação':<30} {'Pago por':<12} {'Valor':<10}")
        print("-" * 60)
        print(f"{'Supermercado':<30} {'João':<12} {'R$ 250,00':<10}")
        print(f"{'Cinema e pipoca':<30} {'Maria':<12} {'R$ 80,00':<10}")
        print(f"{'Conta de luz':<30} {'João':<12} {'R$ 180,00':<10}")
        print("-" * 60)
        print(f"{'TOTAL':<30} {'':<12} {'R$ 510,00':<10}")
        
        # Calcular quem deve para quem
        print("\n💰 CÁLCULO DE QUEM DEVE PARA QUEM:")
        print("-" * 60)
        
        joao_total_pago = 250 + 180  # R$ 430
        maria_total_pago = 80  # R$ 80
        total_despesas = 510
        por_pessoa = total_despesas / 2  # R$ 255
        
        print(f"\nJoão pagou: R$ {joao_total_pago:.2f}")
        print(f"Maria pagou: R$ {maria_total_pago:.2f}")
        print(f"Total de despesas: R$ {total_despesas:.2f}")
        print(f"Por pessoa: R$ {por_pessoa:.2f}")
        
        joao_deve_receber = joao_total_pago - por_pessoa  # 430 - 255 = 175
        maria_deve_pagar = por_pessoa - maria_total_pago  # 255 - 80 = 175
        
        print(f"\n📊 RESULTADO FINAL:")
        print(f"   João deve RECEBER: R$ {joao_deve_receber:.2f}")
        print(f"   Maria deve PAGAR: R$ {maria_deve_pagar:.2f}")
        
        print("\n✅ CONCLUSÃO:")
        print(f"   Maria faz uma transferência PIX de R$ {maria_deve_pagar:.2f} para João")
        print(f"   E as contas ficam ZERADAS! 🎉")
        
        print("\n" + "="*60)
        print("DADOS PARA TESTAR VIA API:")
        print("="*60)
        print(f"\nHousehold ID: {household_id}")
        print(f"João ID: {joao_id}")
        print(f"Maria ID: {maria_id}")
        print(f"\nAccount ID: {account_id}")
        print(f"Categoria Alimentação ID: {alimentacao_id}")
        print(f"Categoria Lazer ID: {lazer_id}")
        print(f"Categoria Utilidades ID: {utilidades_id}")
        
        print("\n📌 PRÓXIMOS PASSOS:")
        print("1. Inicie o servidor: uvicorn app.main:app --reload")
        print("2. Consulte o balanço via API:")
        print(f"   GET http://localhost:8000/expense-splits/household/{household_id}/balance")
        print("\n3. Ou consulte o balanço de um usuário:")
        print(f"   GET http://localhost:8000/expense-splits/user/{joao_id}/balance")
        
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())
