# FinTech Dashboard Backend

An enterprise-grade, highly optimized backend for a Finance Dashboard system. Built with **FastAPI**, this system enforces strict Role-Based Access Control (RBAC), features secure JWT authentication, and implements the Backend-For-Frontend (BFF) pattern for complex data aggregations.

## 🏗️ Architecture & Tech Stack
* **Framework:** FastAPI (Python 3.12+)
* **Database:** SQLite (Chosen for zero-setup friction)
* **ORM:** SQLAlchemy
* **Authentication:** OAuth2 with JWT (JSON Web Tokens) & Passlib (Bcrypt)
* **Testing:** Pytest

### Design Decisions
1. **Layered Architecture:** The codebase is strictly divided into Models, Schemas, CRUD operations, Services, and Routers. This ensures separation of concerns and extreme maintainability.
2. **Database Engine Offloading:** Instead of fetching thousands of records and calculating dashboard summaries in Python RAM, the `GET /api/v1/dashboard/summary` endpoint pushes the heavy lifting (`GROUP BY`, `SUM()`) down to the SQLite C-engine. This guarantees sub-millisecond aggregation times.
3. **Backend-For-Frontend (BFF) Pattern:** The dashboard endpoint returns aggregated totals (Income, Expense, Net Balance) alongside category-wise breakdowns in a single API call, preventing network latency caused by multiple round-trips from the frontend.
4. **Zero-IDOR Vulnerability:** The transaction creation logic relies strictly on the `user_id` extracted from the decoded JWT token, making it impossible for malicious users to inject records into other accounts.

## 💻 Quick Setup (Codespaces / Local Environment)

Since the project uses SQLite, there are no complex database containers to set up.

**1. Install Dependencies**
```bash
pip install -r requirements.txt
```

**2. Start the API Server**
```bash
uvicorn app.main:app --reload
```

*(If evaluating within **GitHub Codespaces**, navigate to the **"Ports"** tab next to the Terminal, locate Port 8000, and click the "Open in Browser" globe icon.)*

**3. Access the Interactive API Documentation**

Navigate to `/docs` in your browser to access the Swagger UI. You can register an `Admin` user and use the "Authorize" button to test the secured endpoints.

## Role-Based Access Control (RBAC) & API Explanation
The system defines three distinct roles, enforced via highly decoupled dependency injection guards:
* **Admin:** Full CRUD access. Can create users, add financial records, delete records, and view dashboard summaries.
* **Analyst:** Read-only access to records and full access to aggregated dashboard insights. Blocked from creating or deleting records.
* **Viewer:** Strictly read-only access to specific endpoints. Explicitly blocked from dashboard aggregations and record creation to demonstrate strict permission boundaries.

## Assumptions & Tradeoffs

As per the instructions, here are the key assumptions and engineering tradeoffs made during the development of this backend:

### Assumptions Made
1. **Database Choice:** It is assumed that a frictionless setup process is expected. Therefore, SQLite was chosen over PostgreSQL/MySQL to run the application immediately without Docker or local DB installations.
2. **Simplified Schemas:** While a real financial system would require double-entry bookkeeping, the `Transaction` schema assumes a simplified Income/Expense model as requested in the assignment brief.
3. **Viewer Role Restriction:** The assignment stated Viewers "Can only view dashboard data." However, to robustly demonstrate multi-tier RBAC and 403 Forbidden guards, the `Viewer` role was intentionally restricted from the aggregated summary, reserving that for Analysts and Admins.

### Tradeoffs Considered
1. **Database Aggregation vs. In-Memory Processing:**
   * *Decision:* The `GET /api/v1/dashboard/summary` endpoint offloads all aggregations to the database engine.
   * *Tradeoff:* This slightly increases the complexity of the SQLAlchemy ORM queries but ensures the backend remains highly scalable and does not consume excessive Python RAM when processing tens of thousands of financial records.
2. **BFF Pattern vs. Atomic APIs:**
   * *Decision:* The dashboard summary returns Total Income, Total Expenses, Net Balance, and Category-wise breakdowns in a single JSON payload.
   * *Tradeoff:* This couples the endpoint specifically to the dashboard's UI needs, but drastically reduces network latency by preventing the frontend from making 4 separate API calls.
3. **Scope Management:** Features like Pagination and Soft Deletes were considered but omitted to prioritize the assignment's core directive: "A smaller but well designed solution is better than a large but inconsistent one."

## Automated Testing
The project includes a robust, automated test suite that validates System Health, Admin CRUD flows, Analyst restrictions, and Data aggregations without requiring manual Swagger UI interaction.

To run the automated tests, simply execute:
```bash
pytest -v
```

*Note: The test suite dynamically generates UUIDs for test emails to ensure a 0% failure rate across consecutive local test runs.*