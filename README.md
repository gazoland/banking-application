# Banking Application

## Introduction

The purpose of this project is to build an online banking web application for a banking system, where bank clients and bank employees can manage client's accounts and cards.

## Application Requirements

### Bank clients

- Update personal information (username, password, email, phone number and treatment pronoun);
- Make transactions (deposit, withdraw, transfer) and view account's statement;
- Manage their debit/credit cards (change PIN, lock/unlock card, change card limit and statement day);
- View card statements and pay them with their account's balance;
- Make requests for new cards and activate them.

### Bank Employees

- Register new clients;
- Make deposits, withdrawals and close a client account (like a bank cashier);
- Analyze new card requests from clients and grant or deny those requests.

### Payment Terminal
- Register new purchases (credit card machine).

### Banking System
- Automatically close statements, open new ones and calculate overdue insterest.

## Project Architecture

This project will have a server-client approach. 

The server-side will consist in the Database (PostgreSQL), the server API (Python-Flask) and an ETL manager (with Apache Airflow) to automate a few features of the banking system: 
e.g. Automatically open and close credit card statements, calculate interest if overdue etc. (To be added in the future).

The client-side will consist in 3 different applications: one for the bank clients, another for bank employees and a third one for a payment terminal (credit card machine).
Clients and employees will be able to login into their accounts and manage it as they desire.
The payment terminal will act just like a credit card machine, registering purchases for a fictional retail company.

For now, the frontend interface will be a Command-Line Interface (CLI). A proper HTML-web interface will be added in the short future.

IMAGE HERE

## Data Model

In a banking system:
 - All data, its attributes and properties are well-defined; 
 - We do not expect our data model to change much;
 - We need to ensure ACID compliance;
 - There will be many transactions happening;
 - There are many relations between entities.

A OLTP (optimized for transactions) relational database management system (RDBMS) is a good option. 
PostgreSQL is the RDBMS of choice.

### RDBMS Schema

There are a few entities to consider:

- Clients: the bank clients and their information;
- Emplyees: the bank employees;
- Treatment Pronouns: Mr., Mrs., Miss, etc.;
- Accounts: information of each client's account;
- Transactions: All actions that change a client's account balance (deposits, withdrawals, transfers and debit purchases);
- Cards: all client's debit/credit cards;
- Card Brands: Visa, MasterCard etc.
- Card Categories: Gold, Platinum, Black etc.
- Card Requests: Clients can make requests for additional debit/credit cards;
- Invoices: The credit cards statements;
- Purchases: Every credit card transaction.

IMAGE HERE
