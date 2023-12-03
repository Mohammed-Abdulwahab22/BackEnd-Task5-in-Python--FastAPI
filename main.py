import uuid
from enum import Enum
from fastapi import FastAPI, HTTPException, Form, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel,UUID4
from typing import List
import csv
import os
from datetime import datetime

#to run on swagger http://127.0.0.1:8000/docs



app = FastAPI()


class CreateAccount(BaseModel):
    Name: str
    salary: float

class DeleteAccount(BaseModel):
    Id: UUID4

class DepositAccount(BaseModel):
    Id: UUID4
    depositAmount: float

class WithdrawAccount(BaseModel):
    Id: UUID4
    withdrawAmount: float

class TransferAccount(BaseModel):
    senderId: UUID4
    receiverId: UUID4
    transferAmount: float

class Client(BaseModel):
    Id: UUID4
    Name: str
    salary: float
    balance: float
    creationDate: str

clients = []
def write_to_csv(clients):
    csv_file_path = "clients.csv"
    fieldnames = ["Id", "Name", "salary", "balance", "creationDate"]

    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(clients)
@app.post("/api/BankClients/createAccount")
async def create_account(create: CreateAccount):
    if create.Name and create.salary is not None:
        client_exists = any(
            c["Name"] == create.Name and c["salary"] == create.salary
            for c in clients
        )

        if client_exists:
            raise HTTPException(status_code=400, detail="Client already exists.")

        new_client = {
            "Id": str(uuid.uuid4()),
            "Name": create.Name,
            "salary": create.salary,
            "balance": create.salary,
            "creationDate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        clients.append(new_client)

        write_to_csv(clients)

        return new_client
    else:
        raise HTTPException(status_code=400, detail="Name and Salary are required.")

@app.post("/api/BankClients/deleteAccount")
async def delete_account(delete: DeleteAccount):
    
    client_to_delete = next((c for c in clients if c["Id"] == str(delete.Id)), None)

    if client_to_delete:
        clients.remove(client_to_delete)

        write_to_csv(clients)

        return {"message": "Account deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Account not found")

@app.post("/api/BankClients/deposit")
async def deposit_account(deposit: DepositAccount):
    client_to_deposit = next((c for c in clients if c["Id"] == str(deposit.Id)), None)

    if client_to_deposit:
        client_to_deposit["balance"] += deposit.depositAmount

        write_to_csv(clients)

        return {
            "message": f"Deposited {deposit.depositAmount} successfully. New balance: {client_to_deposit['balance']}"}
    else:
        raise HTTPException(status_code=404, detail="Account not found")

@app.post("/api/BankClients/withdraw")
async def withdraw_account(withdraw: WithdrawAccount):
    client_to_withdraw = next((c for c in clients if c["Id"] == str(withdraw.Id)), None)

    if client_to_withdraw:
        if client_to_withdraw["balance"] >= withdraw.withdrawAmount:
            client_to_withdraw["balance"] -= withdraw.withdrawAmount

            write_to_csv(clients)

            return {
                "message": f"Withdrew {withdraw.withdrawAmount} successfully. New balance: {client_to_withdraw['balance']}"}
        else:
            raise HTTPException(status_code=400, detail="Insufficient balance for withdrawal")
    else:
        raise HTTPException(status_code=404, detail="Account not found")

@app.post("/api/BankClients/transfer")
async def transfer_account(transfer: TransferAccount):
    sender = next((c for c in clients if c["Id"] == str(transfer.senderId)), None)
    receiver = next((c for c in clients if c["Id"] == str(transfer.receiverId)), None)

    if sender and receiver:
        if sender["balance"] >= transfer.transferAmount:
            sender["balance"] -= transfer.transferAmount
            receiver["balance"] += transfer.transferAmount

            write_to_csv(clients)

            return {"message": f"Transferred {transfer.transferAmount} from {sender['Name']} to {receiver['Name']}"}
        else:
            raise HTTPException(status_code=400, detail="Insufficient balance for transfer")
    else:
        raise HTTPException(status_code=404, detail="Sender or receiver account not found")

@app.get("/api/BankClients/RetrieveByID")
async def get_client_by_id(clientId: str = Query(...)):
    client = next((c for c in clients if c["Id"] == clientId), None)

    if client:
        return client
    else:
        raise HTTPException(status_code=404, detail="Client not found")


@app.get("/api/BankClients/RetrieveBySalary")
async def get_by_salary():
    high_salary_clients = [c for c in clients if c["salary"] > 50]
    return high_salary_clients

@app.get("/api/BankClients/RetrieveByBalance")
async def get_by_balance():
    high_balance_clients = [c for c in clients if c["balance"] > 50]
    return high_balance_clients


@app.get("/api/BankClients/RetrieveByCreationDate")
async def get_by_date(creation_date: str):
    clients_created_after = [c for c in clients if datetime.strptime(c["creationDate"], "%Y-%m-%d %H:%M:%S") > datetime.strptime(creation_date, "%Y-%m-%d %H:%M:%S")]
    return clients_created_after

@app.get("/api/BankClients/RetrieveTheClientWithTheHighestSalary")
async def get_highest_salary():
    highest_salary_client = max(clients, key=lambda c: c["salary"])
    return highest_salary_client


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
