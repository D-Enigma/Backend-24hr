# Backend-24hr

A complaint management REST API built with Python, FastAPI, SQLAlchemy, and SQLite.

**Live API:** https://backend-24hr.onrender.com  
**API Documentation:** https://backend-24hr.onrender.com/docs  
**GitHub Repository:** https://github.com/D-Enigma/Backend-24hr

---

## 1. About the Project

I built Backend-24hr to understand how backend applications work in practice.

I already knew the basics of Python, but I wanted to understand what happens beyond writing scripts: how a server receives requests, how APIs communicate with clients, how data is stored in a database, how users are authenticated, and how an application is tested and deployed.

Instead of learning each concept separately, I brought them together in one project.

The result is a complaint management API where users can register, log in, submit complaints, view their complaints, update their status, and delete them.

Each complaint is associated with the user who created it. A user cannot access or modify another user's complaints through the complaint endpoints.

I also worked on automated testing, application logging, Docker containerization, Git version control, and deployment using Render.

The goal was to understand the complete backend development process by building something that works.

---

## 2. What Does This Application Do?

Imagine a system where people can report problems such as broken streetlights, damaged roads, or other local issues.

The backend provides the functionality needed to manage those complaints.

A user can:

- Create an account.
- Log in and receive an access token.
- Submit a complaint with its title, description, and location.
- View all complaints associated with their account.
- Retrieve a particular complaint using its ID.
- Change a complaint's status.
- Delete a complaint.

The application supports three complaint statuses:

- `Pending`
- `In Progress`
- `Resolved`

The API handles the requests and database operations. A frontend application could be built separately and connected to these endpoints.

---

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| FastAPI | Building the API and handling HTTP requests |
| Uvicorn | Running the FastAPI application |
| SQLAlchemy | Communicating with the database using Python objects |
| SQLite | Storing users and complaints |
| Pydantic | Validating incoming data and defining response formats |
| PyJWT | Creating and verifying JWT access tokens |
| pwdlib | Hashing and verifying passwords |
| Argon2 | Password hashing algorithm |
| Pytest | Testing application behaviour |
| HTTPX | Making HTTP requests in tests through FastAPI's test client |
| Docker | Packaging the application and its dependencies |
| Render | Hosting the deployed API |
| Git and GitHub | Version control and source code hosting |

---

## 4. How the Project Is Structured

The project is divided into separate files so that each part has a clear responsibility.

```text
Backend-24hr/
│
├── routers/
│   ├── __init__.py
│   ├── auth.py
│   └── complaints.py
│
├── tests/
│   └── test_complaints.py
│
├── main.py
├── database.py
├── dependencies.py
├── models.py
├── schemas.py
├── security.py
├── logging_config.py
├── migrate.py
│
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
└── README.md
```

The `.venv`, cache directories, database files, and log files may also appear locally. They are runtime or development files rather than the main application modules.

### Understanding the Files

#### `main.py` — Application Entry Point

This is where the FastAPI application is created.

It registers the authentication and complaint routers, initializes database tables, and defines the home endpoint.

When Uvicorn starts the application using:

```bash
uvicorn main:app --reload
```

`main` refers to `main.py`, and `app` refers to the FastAPI instance inside that file.

The home endpoint returns a simple JSON response to confirm that the API is running.

#### `database.py` — Database Configuration

This file creates the database engine, session factory, and SQLAlchemy base class.

The database engine manages the connection to the configured database. The session factory creates sessions that the application uses to read and write data.

The database URL can be supplied through the `DATABASE_URL` environment variable. If it is not supplied, the application uses a local SQLite database named `complaints.db`.

The `Base` class is inherited by the database models so SQLAlchemy can keep track of their table definitions.

#### `dependencies.py` — Shared Database Dependency

This file defines `get_db()`, which provides a database session to FastAPI endpoints.

It uses `yield` to make the session available while the request is being handled and closes the session in a `finally` block.

This avoids having to write the same database session setup and cleanup code inside every endpoint.

FastAPI's `Depends()` mechanism allows endpoints to request this dependency automatically.

#### `models.py` — Database Models

This file describes the structure of the database tables using SQLAlchemy.

It contains two models:

**`UserDB`**

Represents registered users. It stores:

- `id`: The user's unique database ID.
- `username`: The user's username, which must be unique.
- `hashed_password`: The hashed password used for login verification.

**`ComplaintDB`**

Represents complaints. It stores:

- `id`: The complaint's unique ID.
- `title`: A short description of the problem.
- `description`: More details about the complaint.
- `location`: Where the problem occurred.
- `status`: The current complaint status.
- `user_id`: The ID of the user associated with the complaint.

The `user_id` column references `users.id`. It is nullable to accommodate older complaints that may not have been associated with a registered user.

#### `schemas.py` — Data Validation and Response Formats

Database models and API schemas serve different purposes.

The models describe how data is stored in the database. The schemas describe what data the API accepts and returns.

This file contains:

- `ComplaintCreate`: Defines the fields required to submit a complaint.
- `ComplaintResponse`: Defines the complaint data returned by the API.
- `ComplaintUpdate`: Defines the fields accepted when updating a complaint.
- `ComplaintStatus`: Restricts complaint status values to the supported options.
- `UserCreate`: Validates registration details, including username and password length.
- `UserLogin`: Defines the username and password fields required for login.

Pydantic checks incoming data against these definitions. Invalid requests are rejected before the endpoint performs its normal operation.

The `from_attributes` configuration in `ComplaintResponse` allows Pydantic to read values from SQLAlchemy model objects.

#### `security.py` — Authentication and Token Verification

This file contains the main JWT authentication logic.

When a user logs in successfully, the application creates an access token containing the username and timestamps.

The token is signed using the `JWT_SECRET_KEY` environment variable and the HS256 algorithm. Its configured expiration time is 30 minutes.

Protected endpoints use `get_current_user()` to:

1. Read the bearer token from the request.
2. Verify the token's signature and expiration.
3. Extract the username from the token.
4. Find the corresponding user in the database.
5. Return the user so the endpoint can identify who is making the request.

Requests with invalid or expired tokens are rejected.

The secret key must remain private. It should never be committed to GitHub or hardcoded into the application.

#### `routers/auth.py` — Registration and Login

This file defines the authentication endpoints under the `/auth` prefix.

It contains two main operations:

**Registration — `POST /auth/register`**

- Checks whether the username is already registered.
- Hashes the supplied password.
- Creates a user record in the database.
- Returns the new user's ID and username.

**Login — `POST /auth/login`**

- Finds the account using the supplied username.
- Verifies the password against its stored hash.
- Returns a JWT access token if the credentials are valid.

Passwords are not stored as plain text. The application uses `pwdlib` with its recommended password hashing configuration, which uses Argon2 in this setup.

#### `routers/complaints.py` — Complaint Management

This file defines the complaint endpoints under the `/complaints` prefix.

It contains the operations for creating, retrieving, updating, and deleting complaints.

Every endpoint requires an authenticated user.

When a complaint is created, the current user's ID is saved alongside the complaint. When an existing complaint is requested, updated, or deleted, the query checks both its ID and the user's ID.

This ownership check is important because authentication alone does not mean a user should have access to every record in the database.

The file also uses application logging and rolls back the database session if complaint creation fails.

#### `dependencies.py` and `security.py` Work Together

These files solve different problems.

`dependencies.py` provides a database session to the endpoint.

`security.py` verifies the access token and identifies the current user.

An endpoint can use both dependencies to access the database and determine who is making the request.

#### `logging_config.py` — Application Logs

This file configures the application's logger.

The logger writes messages to `app.log`, including the timestamp, severity level, and message.

A rotating file handler limits the size of each log file to approximately 1 MB and retains up to three backup files.

Logs help investigate failures without printing every debugging message directly to the terminal.

#### `migrate.py` — Database Migration Script

This script was created to update an existing SQLite database after the application introduced user ownership for complaints.

It checks whether the `complaints` table already contains a `user_id` column.

If the column is missing, it adds the column. If it already exists, the script skips the change.

This makes the script safe to rerun for that specific migration.

The script targets `complaints.db` in the current working directory. It should be run only against the intended database, with a backup available if the existing data matters.

For larger applications, a database migration tool such as Alembic is generally more suitable than manually maintained migration scripts.

#### `tests/test_complaints.py` — Automated Tests

This file tests the API's behaviour.

The tests cover:

- The home endpoint.
- Complaint creation.
- Complaint retrieval.
- Complaint status updates.
- Complaint deletion.
- Requests for nonexistent complaints.
- Attempts to access another user's complaints.
- Missing and invalid access tokens.
- Expired tokens.
- Registration with an invalid password length.

The tests use FastAPI's `TestClient` to send HTTP requests to the application.

They override the normal database dependency with a separate in-memory SQLite database. This helps prevent tests from modifying the regular application database.

Fixtures prepare the test database and provide authentication tokens when needed.

Tests are important because they help verify that the application behaves as expected after code changes.

#### `requirements.txt` — Python Dependencies

This file lists the Python packages required by the project, along with their pinned versions.

Installing these dependencies allows another developer or a deployment environment to recreate the package setup used by the application.

#### `Dockerfile` — Container Configuration

The Dockerfile describes how to package the application into a Docker image.

It starts from a Python base image, sets the working directory, installs dependencies, copies the project files, and defines the command used to start Uvicorn.

The container listens on the port supplied by the hosting environment, falling back to port `8000` when no `PORT` variable is provided.

#### `.dockerignore` — Files Excluded from the Image

This file tells Docker which files and directories should be excluded from the build context.

It helps avoid copying unnecessary local files, such as virtual environments, caches, logs, and local configuration files, into the Docker image.

#### `.gitignore` — Files Git Should Ignore

This file prevents selected local and generated files from being tracked by Git.

Typical examples include the virtual environment, Python cache files, local database files, logs, and environment files.

It is important to remember that `.gitignore` does not automatically remove a file that Git is already tracking.

---

## 5. Understanding the Complete Request Flow

The easiest way to understand the application is to follow what happens when someone uses it.

### Example: A User Creates a Complaint

Suppose a user wants to report a broken streetlight.

**Step 1: The client sends a request**

The client sends a `POST` request to:

`/complaints`

The request contains the complaint's title, description, and location. It also includes an access token in the `Authorization` header.

**Step 2: FastAPI receives the request**

FastAPI matches the URL and HTTP method to the `create_complaint()` endpoint in `routers/complaints.py`.

The `ComplaintCreate` schema validates the submitted fields.

**Step 3: Authentication is checked**

The `get_current_user()` dependency in `security.py` verifies the JWT and identifies the user who made the request.

If the token is invalid or expired, the request is rejected.

**Step 4: The endpoint prepares the database record**

The endpoint creates a `ComplaintDB` object using the submitted details and the authenticated user's ID.

This associates the new complaint with its creator.

**Step 5: SQLAlchemy saves the complaint**

The endpoint adds the object to the database session and commits the transaction.

The database stores the new complaint.

**Step 6: The API returns a response**

The endpoint returns the created complaint.

FastAPI uses `ComplaintResponse` to format the response, and the client receives the result with HTTP status `201 Created`.

The same general process applies to the other endpoints, although each operation performs a different database action.

### Why Are the Files Separate?

Each file has a different responsibility.

For example, the complaint router should not need to implement password hashing itself. It relies on the security module for authentication and the database modules for data access.

Keeping these responsibilities separate makes the project easier to understand, test, and maintain.

---

## 6. API Endpoints

The following endpoints are implemented in the application.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Check whether the API is running |
| POST | `/auth/register` | Register a user |
| POST | `/auth/login` | Log in and receive an access token |
| POST | `/complaints` | Create a complaint |
| GET | `/complaints` | List the current user's complaints |
| GET | `/complaints/{id}` | Retrieve one of the current user's complaints |
| PATCH | `/complaints/{id}` | Update a complaint's status |
| DELETE | `/complaints/{id}` | Delete one of the current user's complaints |

The complaint endpoints require authentication. Registration and login are used to obtain an access token.

The API returns HTTP status codes to communicate the outcome of a request. Examples include:

- `200 OK`: The request succeeded.
- `201 Created`: A resource was created.
- `204 No Content`: The deletion succeeded without a response body.
- `401 Unauthorized`: Authentication failed or a valid token was not provided.
- `404 Not Found`: The requested complaint was not found for that user.
- `409 Conflict`: The username is already registered.
- `422 Unprocessable Entity`: The request data failed validation.
- `500 Internal Server Error`: An unexpected server-side failure occurred.

---

## 7. Try the API

The deployed API includes interactive documentation generated by FastAPI.

Open:

https://backend-24hr.onrender.com/docs

The documentation lets you inspect the available endpoints, view their expected inputs, send requests, and examine their responses.

A typical way to explore the application is:

1. Register a user through `/auth/register`.
2. Log in through `/auth/login`.
3. Copy the access token from the response.
4. Click **Authorize** in the documentation interface.
5. Enter the token according to the authentication prompt.
6. Create a complaint.
7. Retrieve, update, or delete the complaint.

The documentation interface is useful for learning how HTTP methods, request bodies, headers, and response codes work together.

---

## 8. Run the Project Locally

These instructions assume Windows PowerShell and a working Python installation.

### Step 1: Clone the repository

```powershell
git clone https://github.com/D-Enigma/Backend-24hr.git
cd Backend-24hr
```

### Step 2: Create a virtual environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

A virtual environment keeps the project's Python packages separate from those installed globally.

### Step 3: Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### Step 4: Configure the JWT secret

The application requires a secret key for signing and verifying tokens.

Generate one for your current PowerShell session:

```powershell
$env:JWT_SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
```

This is suitable for local development. The generated value will not automatically persist across separate terminal sessions.

If you start another session, configure the secret again. Existing tokens signed with a previous secret will no longer validate if the secret changes.

Never commit your real secret to GitHub.

### Step 5: Start the application

```powershell
uvicorn main:app --reload
```

The `--reload` option restarts the development server when it detects code changes.

Open the following addresses:

- API: http://127.0.0.1:8000
- Interactive documentation: http://127.0.0.1:8000/docs

The default database configuration creates or uses `complaints.db` in the application's working directory.

---

## 9. Run the Tests

Make sure the virtual environment is activated and `JWT_SECRET_KEY` is configured.

Run:

```powershell
python -m pytest -v
```

Pytest discovers the tests, executes them, and displays the results.

The test suite uses an in-memory SQLite database rather than the application's normal database. This allows the tests to create and remove test records without deliberately changing the regular database file.

A passing test suite gives confidence that the tested behaviour still works. It does not guarantee that every possible input, deployment condition, or security issue has been covered.

---

## 10. Run with Docker

Docker packages the application and its dependencies into an image so it can run in a consistent environment.

### Build the image

```powershell
docker build -t backend-24hr .
```

### Configure a JWT secret

If one is not already set in your terminal:

```powershell
$env:JWT_SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
```

### Run the container

```powershell
docker run --name backend-24hr-container -p 8000:8000 -e JWT_SECRET_KEY=$env:JWT_SECRET_KEY backend-24hr
```

The `-p 8000:8000` option maps port `8000` on your computer to port `8000` in the container.

Open:

http://127.0.0.1:8000/docs

To stop the container, press `Ctrl+C` if it is running in the foreground.

If you started it in detached mode, you can stop it using:

```powershell
docker stop backend-24hr-container
```

The Docker image does not automatically make a local SQLite database persistent. If the container is removed, data stored only inside its writable filesystem may be lost. Persistent storage must be configured separately when required.

---

## 11. Deployment on Render

I deployed the application on Render using Docker.

The deployment process involved:

1. Pushing the application source code to GitHub.
2. Connecting the GitHub repository to Render.
3. Configuring Render to build the application using the Dockerfile.
4. Setting the `JWT_SECRET_KEY` environment variable in Render.
5. Deploying the application and checking the live endpoint.

The Dockerfile starts the FastAPI application with Uvicorn. The command uses the hosting platform's `PORT` environment variable when available.

### Live deployment

**API:**

https://backend-24hr.onrender.com

**Interactive documentation:**

https://backend-24hr.onrender.com/docs

The home endpoint returns:

```json
{
  "message": "24HR Backend is LIVE!"
}
```

This confirms that the application can respond to requests through its deployed URL.

### A note about database persistence

The application currently uses SQLite.

The deployed service uses a free hosting setup without a configured persistent disk. Therefore, the SQLite database file should not be assumed to survive service restarts or redeployments.

The API's successful deployment demonstrates that the application can run online, but it does not guarantee permanent storage of user accounts or complaints.

Reliable long-term storage requires a suitable persistent storage configuration or a managed database.

---

## 12. Important Concepts to Understand

This section summarises some of the backend concepts used in the project.

### API

An API defines how one application can communicate with another. Here, clients send HTTP requests to the FastAPI application and receive responses.

### REST

REST is an architectural style commonly used when designing HTTP APIs. This project uses resource-oriented URLs and HTTP methods to represent complaint operations.

### HTTP Methods

- `GET` retrieves information.
- `POST` creates a resource or performs an operation.
- `PATCH` partially updates a resource.
- `DELETE` removes a resource.

### ORM

An Object-Relational Mapper allows application code to work with database records through objects.

SQLAlchemy maps Python classes such as `ComplaintDB` to database tables and lets the application perform database operations without writing every query manually.

### Database Session

A database session manages interactions with the database during a unit of work. Changes are committed when they should be saved, and failed transactions may need to be rolled back.

### Validation

Validation checks whether incoming data meets the application's requirements. Pydantic schemas help FastAPI validate request bodies before the endpoint processes them.

### Authentication and Authorization

Authentication answers: **Who are you?**

Authorization answers: **What are you allowed to access?**

JWT validation helps identify the current user. The complaint queries then enforce ownership by checking the user's ID.

### Password Hashing

A password hash is not the original password. During login, the supplied password is verified against the stored hash.

Argon2 is designed for password hashing and is more appropriate for this purpose than storing passwords directly or using a fast general-purpose hash.

### Environment Variables

Environment variables allow configuration values to be supplied outside the source code.

This project uses them for settings such as `JWT_SECRET_KEY` and `DATABASE_URL`.

### Automated Testing

Automated tests send requests to the application and check whether the results match expectations.

They help catch regressions when code is changed.

### Containerization

Docker packages an application with the environment and dependencies it needs to run.

A container makes it easier to run the same application locally and on a compatible hosting platform.

---

## 13. What I Learned from Building It

This project helped me understand how separate backend concepts fit together in a working application.

I worked on:

- Creating REST endpoints with FastAPI.
- Organizing routes and shared application logic into separate modules.
- Defining database tables using SQLAlchemy.
- Validating requests and formatting responses with Pydantic.
- Hashing passwords and implementing JWT authentication.
- Restricting access to user-owned resources.
- Managing database sessions and handling failures.
- Writing automated API tests with Pytest.
- Using Git and GitHub to manage source code.
- Building and running a Docker image.
- Configuring environment variables and deploying the application to Render.

The most useful part was connecting these pieces rather than treating each topic as an isolated tutorial.

I also learned that getting an application to run locally is only one part of backend development. Testing, configuration, security, deployment, and data persistence need attention too.

---

## 14. Current Limitations and Possible Improvements

This project is a learning application, and there are areas that could be improved further.

- **Database persistence:** Configure reliable persistent storage for deployed data.
- **Database migrations:** Introduce a migration tool such as Alembic instead of relying on a manually maintained migration script.
- **Testing:** Expand coverage for more edge cases and failure scenarios.
- **Production configuration:** Review logging, error handling, environment configuration, and deployment settings for production use.
- **API improvements:** Add features such as pagination, filtering, and more flexible complaint updates if the application requirements grow.

These are potential next steps rather than features that are already implemented.

---

## Author

**D-Enigma**

GitHub: https://github.com/D-Enigma

---

*Built as a hands-on project to learn backend development, from writing API endpoints to testing, containerization, and deployment.*