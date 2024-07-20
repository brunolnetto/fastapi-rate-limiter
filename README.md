# FastAPI Rate-Limited Application

## Overview

This repository contains a FastAPI application with integrated rate limiting using Redis. The application includes endpoints with different rate limits and serves static files.
Prerequisites

- Python 3.11 or higher
- Redis server running locally or on a remote server
- pip for installing Python packages

## Installation

1. Clone the Repository

```bash
git clone https://github.com/trouchet/fastapi-rate-limiter.git
cd fastapi-rate-limiter
```

2. Create a Virtual Environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install Dependencies

```bash
pip install -r requirements.txt
```

4. Set Up Environment Variables

Create a .env file in the root of the project and add the following:

```bash
REDIS_URL=redis://localhost:6379
```

Replace localhost:6379 with the appropriate Redis server URL if it differs.
5. Start Redis Server (if not already running)
On Ubuntu/Debian

```bash
sudo systemctl start redis-server
```

On macOS

```bash
brew services start redis
```

6. Run the FastAPI Application

```bash
uvicorn main:app --reload
```

Replace main with the name of your Python file if it's different from main.py.
Endpoints

- GET /favicon.ico: Returns the favicon for the application.
- GET /health: Health check endpoint to verify the service is running.
- GET /: Welcome endpoint with a rate limit of 5 requests per minute.
- GET /limited: Rate-limited endpoint allowing 3 requests per minute.
- GET /open: Open endpoint without rate limiting.

## Rate Limiting

- **Root Endpoint (/)**: Limited to 5 requests per minute.
- **Limited Endpoint (/limited)**: Limited to 3 requests per minute.
- **Open Endpoint (/open)**: Not rate-limited.

## Exception Handling

Rate limit errors are handled by custom exception handlers that return a 429 Too Many Requests response with a message.

## Logging

The application uses Python's logging module to log errors during startup and other informational messages.

## Testing

To run tests, ensure you have the necessary testing dependencies installed:

```bash
pip install pytest
```

Then run:

```bash
pytest
```

## Troubleshooting

Application Stalls on Startup: Check that Redis is running and accessible. Verify the REDIS_URL in the .env file is correct.
Rate Limit Errors: Ensure that the rate limiting settings in the code match your expectations and test scenarios.

## Contribution

Feel free to fork the repository, make improvements, and create pull requests.

## License

This project is licensed under the MIT License. See the LICENSE file for details.