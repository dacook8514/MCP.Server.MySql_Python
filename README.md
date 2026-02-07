# MCP.Server.MySql_Python

This project is a Python re-implementation of the `MCP.Server.MySql` .NET project, utilizing FastAPI for the web API and PyMySQL for MySQL database interactions. It provides both HTTP endpoints for health checks and schema retrieval, and a JSON RPC server for handling various application logic.

## Features

-   **FastAPI**: Modern, fast (high-performance) web framework for building APIs with Python 3.8+.
-   **PyMySQL**: Pure Python client for MySQL.
-   **JSON RPC 2.0 Server**: Implements a flexible JSON RPC server with pluggable handlers and pipeline behaviors (exception handling, logging, validation).
-   **Database Schema Retrieval**: HTTP endpoint to expose MySQL database schema as JSON.
-   **Extensible Architecture**: Designed with extensibility in mind for adding new JSON RPC methods, database interactions, and other features.

## Setup and Installation

1.  **Clone the Repository**:
    ```bash
    git clone <your-repository-url>
    cd MCP.Server.MySql_Python
    ```
    *(Note: This step assumes the user has already cloned the generated repository.)*

2.  **Create and Activate a Virtual Environment**:
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: I will create `requirements.txt` next.)*

4.  **Configure Database Connection**:
    Edit the `db_options` in `main.py` (or implement a more robust configuration loading mechanism using environment variables or a separate config file).
    ```python
    # main.py
    db_options = DatabaseOptions(
        connection_string="server=localhost;port=3306;database=your_database;uid=your_user;pwd=your_password",
        command_timeout_seconds=60
    )
    ```
    **IMPORTANT**: Replace `your_database`, `your_user`, and `your_password` with your actual MySQL credentials.

## Running the Application

To run the FastAPI application:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag is useful for development as it automatically restarts the server on code changes.

The API documentation will be available at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc` (ReDoc).

## API Endpoints

-   **GET `/api/mysql/health`**: Returns "OK" if the service is running.
-   **GET `/api/mysql/schema`**: Retrieves and returns the schema of the configured MySQL database.
-   **POST `/mcp`**: The main JSON RPC 2.0 endpoint. Accepts JSON RPC requests and dispatches them to registered handlers.

### Example JSON RPC Requests

**Ping Request:**

```json
{
    "jsonrpc": "2.0",
    "method": "ping",
    "id": 1
}
```

**Initialize Request:**

```json
{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {},
    "id": 2
}
```

**Prompts List Request:**

```json
{
    "jsonrpc": "2.0",
    "method": "prompts/list",
    "id": 3
}
```

## Project Structure

```
MCP.Server.MySql_Python/
├── main.py                     # Main FastAPI application entry point
├── config.py                   # Database configuration options
├── database_service.py         # Python equivalent of DatabaseService.cs
├── models/                     # Pydantic data models
│   ├── __init__.py
│   ├── column_schema.py
│   ├── foreign_key_schema.py
│   ├── query_result.py
│   └── table_schema.py
├── rpc/                        # JSON RPC server implementation
│   ├── __init__.py
│   ├── json_rpc_interfaces.py  # Abstract base classes and RPC models
│   ├── json_rpc_router.py      # Dispatches RPC requests to handlers
│   ├── behaviors/              # RPC pipeline behaviors
│   │   ├── __init__.py
│   │   ├── exception_behavior.py
│   │   ├── logging_behavior.py
│   │   └── validation_behavior.py
│   └── handlers/               # RPC method handlers
│       ├── __init__.py
│       ├── ping_handler.py
│       └── initialize_handler.py
│       └── prompts_list_handler.py
├── features/                   # Application features (e.g., prompts, resources, tools)
│   ├── __init__.py
│   └── prompts/
│       ├── __init__.py
│       └── prompt_registry.py  # Manages prompts
└── requirements.txt            # Project dependencies
```
