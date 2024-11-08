Loan Management System API
This project is a simple Loan Management System API built with Flask, allowing users to register, log in, and manage loans. The API provides endpoints to create, retrieve, update, and delete loans, with JWT-based authentication.

Table of Contents
Getting Started
Project Setup
API Endpoints
Testing with Postman
Getting Started

Prerequisites
Python 3.8+ installed on your system.
Postman to test API endpoints.
SQLite3 (default for development; other RDBMS options can be configured if desired).

Installation
Clone the Repository:
git clone https://github.com/mekayashwanth/PHP-Backend-Engineer-Take-Home-Assessment-2.git
cd PHP-Backend-Engineer-Take-Home-Assessment-2

Create a Virtual Environment and Activate It:
python3 -m venv venv
source venv/bin/activate # On Windows, use `venv\Scripts\activate`

Install Dependencies:
pip install -r requirements.txt

Run the Application: Start the Flask development server:
flask run
The API will be running at http://localhost:5000.

API Endpoints

Authentication
Register - /register [POST]

Request: { "username": "user1", "password": "password123" }
Response: { "message": "User created successfully!" }

Login - /login [POST]

Request: { "username": "user1", "password": "password123" }
Response: { "token": "<JWT_TOKEN>" }

Loan Management
Create Loan - /loans [POST]

Authentication Required: Bearer token

Request: { "amount": 50000, "lender": "lender_username", "borrower": "borrower_username" }
Response: Loan details with loan_id, amount, status, created_at, lender, and borrower.

Retrieve All Loans - /loans [GET]
Authentication Required: Bearer token
Response: List of all loans.

Update Loan - /loans/<loan_id> [PUT]
Authentication Required: Bearer token
Request: { "amount": 60000, "status": "approved" }
Response: Updated loan details.

Delete Loan - /loans/<loan_id> [DELETE]
Authentication Required: Bearer token
Response: { "message": "Loan deleted successfully" }

Testing with Postman

1. Register a User
   Endpoint: POST /register
   Body (JSON):
   json

   {
   "username": "user1",
   "password": "password123"
   }
   Expected Response: { "message": "User created successfully!" }

2. Log in to Get a JWT Token
   Endpoint: POST /login
   Body (JSON):
   json

   {
   "username": "user1",
   "password": "password123"
   }
   Expected Response: { "token": "<JWT_TOKEN>" }
   Copy the token from the response to use in subsequent requests.

3. Create a Loan
   Endpoint: POST /loans
   Headers:
   Authorization: Bearer <JWT_TOKEN>
   Content-Type: application/json
   Body (JSON):
   json

   {
   "amount": 50000,
   "lender": "lender_username",
   "borrower": "borrower_username"
   }
   Expected Response: JSON object with the loan details.

4. Retrieve All Loans
   Endpoint: GET /loans
   Headers:
   Authorization: Bearer <JWT_TOKEN>
   Expected Response: List of all loans in JSON format.
5. Update a Loan
   Endpoint: PUT /loans/<loan_id>
   Replace <loan_id> with the specific ID of the loan.
   Headers:
   Authorization: Bearer <JWT_TOKEN>
   Content-Type: application/json
   Body (JSON):
   json

   {
   "amount": 60000,
   "status": "approved"
   }
   Expected Response: Updated loan details in JSON format.

6. Delete a Loan
   Endpoint: DELETE /loans/<loan_id>
   Replace <loan_id> with the specific ID of the loan.
   Headers:
   Authorization: Bearer <JWT_TOKEN>
   Expected Response: { "message": "Loan deleted successfully" }
   Notes
   Replace <JWT_TOKEN> with the token received from the login endpoint.
   Ensure that both lender and borrower exist before creating a loan.
