# Casini Loan Manager API
```
Project Description: Building a Comprehensive Loan Management System with Django

This project is a robust Loan Management System built using Django, and we've leveraged Django Rest Framework (DRF) to provide a set of API endpoints for seamless interaction. This system is designed to efficiently manage loan applications, automate credit score calculations, and facilitate easy loan repayment tracking.

Key Features and Components:

Django Rest Framework for API Endpoints: I used Django Rest Framework to create API endpoints that serve as the backbone of our loan management system. These endpoints enable users to interact with the system programmatically.

Celery for Asynchronous Task Processing: To enhance the system's responsiveness and scalability, I integrated Celery, a powerful asynchronous task queue. This allowed me to process resource-intensive tasks, such as credit score calculations, in the background while keeping the system responsive.

RabbitMQ as Message Broker: I adopted RabbitMQ as our message broker to facilitate communication between the application and Celery. RabbitMQ ensures reliable message delivery and helps manage the workload efficiently.

Token Authentication with DRF: Security is paramount in financial applications. I implemented Token Authentication using DRF to secure our API endpoints, ensuring that only authorized users can access the system.

Loan Application Processing: Our system provides an API endpoint for users to apply for loans. I meticulously covered all the conditional logic and criteria mentioned in the assignment problem statement to evaluate loan eligibility and provide quick responses.

Payment Processing: Users can make payments against their EMI (Equated Monthly Installments) through another API endpoint. This feature helps borrowers manage their repayments conveniently.

Loan Statement Retrieval: To keep borrowers informed about their loan status, I offer an API endpoint to fetch loan statements. Users can access detailed information about their loans, including outstanding balances and payment histories.

Dynamic Credit Score Calculation: I use Celery to calculate credit scores on-the-fly, providing real-time credit assessments for loan applications. This feature ensures that borrowers receive up-to-date credit evaluations.
```

### Screenshots
#### User Registration API
<img width="960" alt="image" src="https://github.com/PsuedoGuy2020/casini_loan_management_app/assets/76483737/33ca1779-e244-420d-b605-f3a8bc209aaf">

# Loan Manager Project

This is a Loan Manager project built with Django, Celery, and RabbitMQ. It provides API endpoints for registering users, processing loan applications, managing payments, and fetching loan statements.

## Installation

Follow these steps to set up the project on your local machine:

## 1. Clone the repository:
- git clone https://github.com/PsuedoGuy2020/casini_loan_management.git

## 2. Create a virtual environment and activate it:
- python -m venv venv
- source venv/bin/activate

## 3. Install Django:
- python -m pip install django

## 4. Install Celery and RabbitMQ:
- python -m pip install celery
- sudo apt-get install rabbitmq-server

## 5. Perform database migrations:
- python manage.py migrate

## 6. Configure Celery settings in your Django project's settings file (settings.py):
- Celery settings
- CELERY_BROKER_URL = "amqp://guest:guest@localhost:5672//"
- CELERY_RESULT_BACKEND = "rpc://"
- CELERY_ACCEPT_CONTENT = ["application/json"]
- CELERY_TASK_SERIALIZER = "json"
- CELERY_RESULT_SERIALIZER = "json"
- CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

## 7. Set DEBUG to False and specify allowed hosts in your Django project's settings file (settings.py):
- (Debug mode)
- DEBUG = False
- (Allowed hosts)
- ALLOWED_HOSTS = ["127.0.0.1"]

## 8. Start Celery worker:
- python -m celery -A LoanManager worker -l info

## 9. Update the loanmanager/__init__.py file to include Celery:
- from .celery import app as celery_app
- __all__ = ("celery_app",)

## 7. Start the Django development server:
- python manage.py runserver

# Usage
You can now use Postman or any other API testing tool to interact with the Loan Manager API. Here are the available endpoints:
- Register a new user
- Apply for a loan
- Make payments against EMIs
- Fetch loan statements
