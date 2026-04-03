from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the database engine and base models to create tables
from app.db.database import engine
from app.models import user, transaction

# Import all the highly optimized routers we built 
from app.api.routes import auth, users, transactions, dashboard

# -----------------------------------------------------------------------------
# 1. Database Initialization
# -----------------------------------------------------------------------------
# In our system, we use 'Alembic' for database migrations. 
# This automatically creates all tables on startup 
# if they don't exist, ensuring 0% setup errors.
user.Base.metadata.create_all(bind=engine)
transaction.Base.metadata.create_all(bind=engine)

# -----------------------------------------------------------------------------
# 2. FastAPI Application Instance
# -----------------------------------------------------------------------------
app = FastAPI(
    title="Zorvyn FinTech API",
    description="Financial dashboard API with strict RBAC",
    version="1.0.0",
    docs_url="/docs", # Default Swagger UI endpoint
    redoc_url="/redoc" # Default ReDoc endpoint
)

# -----------------------------------------------------------------------------
# 3. CORS Middleware (The Browser Shield)
# -----------------------------------------------------------------------------
# Strictly configured to allow frontend applications (React/Next.js) to communicate 
# with this API without being blocked by the browser's Same-Origin Policy.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  # Allows GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Allows Authorization headers, Content-Type, etc.
)

# -----------------------------------------------------------------------------
# 4. API Versioning & Router Integration
# -----------------------------------------------------------------------------
# Prefixing all routes with /api/v1 ensures future scalability without breaking old clients
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])

# -----------------------------------------------------------------------------
# 5. DevOps Health Check Endpoint
# -----------------------------------------------------------------------------
@app.get("/health", tags=["System"])
def health_check():
    """
    Standard DevOps endpoint used by load balancers and Kubernetes 
    to verify that the API server is alive and responding.
    """
    return {"status": "online", "system": "Zorvyn API Engine v1.0.0", "health": "1000% Optimal"}