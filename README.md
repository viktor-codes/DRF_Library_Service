# Library Service API

Welcome to the Library Service API! This API allows users to borrow and return books, manage users and books, and handle payments for fines and borrowing fees.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.9+
- Django
- Django REST Framework
- Redis (for Celery tasks)
- Stripe account (for handling payments)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/viktor-codes/DRF_Library_Service
   cd library-service
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:

   Use a `.env.sample` file to create and set up your environment variables:

4. Apply migrations:

   ```bash
   python manage.py migrate
   ```

5. Run the development server:

   ```bash
   python manage.py runserver
   ```

6. Access the API at `http://localhost:8000/`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Obtain tokens via the `/token/` endpoint.

## Custom Endpoints

### Borrowings

#### List Borrowings

- **GET** `/borrowings/`

  Retrieves a list of borrowings belonging to the authenticated user or all borrowings if requested by an admin.

  **Query Parameters**:
  - `user_id`: Filters borrowings by user ID (admin only).
  - `is_active`: Filters active or inactive borrowings (`true` or `false`).

  Example: `/borrowings/?user_id=1&is_active=true`

#### Create Borrowing

- **POST** `/borrowings/`

  Creates a new borrowing for the authenticated user.

  **Request Body**:
  ```json
  {
    "book": 1,
    "borrowing_date": "2024-07-01",
    "expected_returning_date": "2024-07-10"
  }
  ```

#### Return Borrowing

- **POST** `/borrowings/{borrowing_id}/return/`

  Marks a borrowing as returned and updates book inventory. Requires borrowing ID.

  Example: `/borrowings/1/return/`

### Payments

#### Payment Success

- **GET** `/payments/success/`

  Handles successful payment for a borrowing or fine.

  **Query Parameters**:
  - `session_id`: Stripe session ID for payment confirmation.

  Example: `/payments/success/?session_id=cs_test_123`

#### Payment Cancel

- **GET** `/payments/cancel/`

  Cancels a pending payment for a borrowing or fine.

  **Query Parameters**:
  - `session_id`: Stripe session ID for payment cancellation.

  Example: `/payments/cancel/?session_id=cs_test_123`

## Configuration

Configure your settings in `settings.py`, including database, Celery tasks, Stripe keys, and other environment variables.

## Important Notes

- Ensure proper setup of environment variables for security and functionality.
- Handle Stripe and Celery configurations carefully to manage payments and background tasks effectively.
