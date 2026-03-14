# AWS Deployment Guide — Neighborhood Library Service

## Overview

This guide describes deploying the Neighborhood Library Service to AWS using a
fully managed, container-based architecture. The application runs as two
separate services (backend and frontend) on **ECS Fargate**, backed by
**RDS PostgreSQL**, with PDF files stored in **S3** and secrets managed via
**AWS Secrets Manager**.

---

## Architecture

```
Internet
   │
   ▼
Application Load Balancer (ALB)
   ├── /api/*  ──► ECS Fargate — library-backend  (port 8000)
   │                    │
   │              RDS PostgreSQL (library_db)
   │              S3 Bucket (library-pdfs)
   │
   └── /*      ──► ECS Fargate — library-frontend  (port 3000)
```

### AWS Services Used

| Service | Purpose |
|---|---|
| **ECS Fargate** | Runs backend (FastAPI) and frontend (Next.js) containers |
| **ECR** | Stores Docker images for backend and frontend |
| **RDS PostgreSQL 15** | Managed relational database |
| **S3** | Stores uploaded PDF files |
| **ALB** | Routes HTTP/HTTPS traffic to backend and frontend |
| **Secrets Manager** | Stores `DATABASE_URL`, `SECRET_KEY`, `OPENAI_API_KEY` |
| **CloudWatch Logs** | Centralised container log aggregation |
| **IAM** | Task execution roles and task roles |
| **VPC** | Private subnets for ECS tasks and RDS; public subnets for ALB |

---

## Prerequisites

- AWS CLI configured (`aws configure`)
- Docker installed locally
- An ECR registry created for each service

---

## Deployment Steps

### 1. Create ECR Repositories

```bash
aws ecr create-repository --repository-name library-backend --region us-east-1
aws ecr create-repository --repository-name library-frontend --region us-east-1
```

### 2. Build and Push Docker Images

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS \
    --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Backend
docker build -t library-backend ./backend
docker tag library-backend:latest \
  ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/library-backend:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/library-backend:latest

# Frontend
docker build -t library-frontend ./frontend
docker tag library-frontend:latest \
  ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/library-frontend:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/library-frontend:latest
```

### 3. Provision RDS PostgreSQL

```bash
aws rds create-db-instance \
  --db-instance-identifier library-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version "15" \
  --master-username library \
  --master-user-password <password> \
  --db-name library_db \
  --allocated-storage 20 \
  --no-publicly-accessible \
  --vpc-security-group-ids <sg-id> \
  --db-subnet-group-name <subnet-group>
```

### 4. Create S3 Bucket for PDFs

```bash
aws s3api create-bucket \
  --bucket library-pdfs-ACCOUNT_ID \
  --region us-east-1

# Block all public access
aws s3api put-public-access-block \
  --bucket library-pdfs-ACCOUNT_ID \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

### 5. Store Secrets in AWS Secrets Manager

```bash
aws secretsmanager create-secret \
  --name library/database-url \
  --secret-string "postgresql://library:<password>@<rds-endpoint>:5432/library_db"

aws secretsmanager create-secret \
  --name library/secret-key \
  --secret-string "<your-secret-key>"

aws secretsmanager create-secret \
  --name library/openai-api-key \
  --secret-string "<your-openai-api-key>"
```

### 6. Create IAM Roles

**ecsTaskExecutionRole** — allows ECS to pull images and write logs:
- `AmazonECSTaskExecutionRolePolicy`
- `SecretsManagerReadWrite` (scoped to `library/*` secrets)

**libraryTaskRole** — allows the running container to access S3:
- Custom policy granting `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject`
  on `arn:aws:s3:::library-pdfs-ACCOUNT_ID/*`

### 7. Register ECS Task Definitions

```bash
# Replace ACCOUNT_ID and REGION placeholders in docs/ecs-task-definition.json
aws ecs register-task-definition \
  --cli-input-json file://docs/ecs-task-definition.json
```

Create a similar task definition for the frontend, pointing to the frontend
image and exposing port 3000.

### 8. Create ECS Cluster and Services

```bash
aws ecs create-cluster --cluster-name library-cluster

# Backend service
aws ecs create-service \
  --cluster library-cluster \
  --service-name library-backend \
  --task-definition library-backend \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration \
    "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=DISABLED}" \
  --load-balancers \
    "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=library-backend,containerPort=8000"

# Frontend service (similar, port 3000)
```

### 9. Run Database Migrations

Run migrations as a one-off ECS task after deploying the backend:

```bash
aws ecs run-task \
  --cluster library-cluster \
  --task-definition library-backend \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={...}" \
  --overrides \
    '{"containerOverrides":[{"name":"library-backend","command":["alembic","upgrade","head"]}]}'
```

### 10. Configure ALB Listener Rules

- `HTTPS :443 /* → library-frontend target group`
- `HTTPS :443 /api/* → library-backend target group` (or use a separate subdomain)

---

## Environment Variables Mapping

| Variable | Source in AWS |
|---|---|
| `DATABASE_URL` | Secrets Manager `library/database-url` |
| `SECRET_KEY` | Secrets Manager `library/secret-key` |
| `OPENAI_API_KEY` | Secrets Manager `library/openai-api-key` |
| `MAX_BORROW_DAYS` | ECS task definition environment (plain text) |
| `MAX_ACTIVE_BORROWINGS` | ECS task definition environment (plain text) |
| `PDF_UPLOAD_DIR` | Set to `/app/uploads/pdfs`; actual files written to S3 via task role |
| `NEXT_PUBLIC_API_URL` | ECS task definition environment — ALB DNS or custom domain |

---

## CloudWatch Logging

All container logs are shipped to CloudWatch Logs automatically via the
`awslogs` log driver configured in the task definition. Log groups:

- `/ecs/library-backend`
- `/ecs/library-frontend`

Create log groups before the first deployment:

```bash
aws logs create-log-group --log-group-name /ecs/library-backend
aws logs create-log-group --log-group-name /ecs/library-frontend
```

---

## Cost Estimate (us-east-1, minimal production setup)

| Resource | Estimated monthly cost |
|---|---|
| ECS Fargate (0.25 vCPU / 0.5 GB × 2 tasks) | ~$15 |
| RDS PostgreSQL db.t3.micro, 20 GB | ~$15 |
| ALB | ~$20 |
| S3 (< 5 GB) | < $1 |
| CloudWatch Logs (minimal ingest) | < $2 |
| ECR (2 repos, < 1 GB) | < $1 |
| **Total** | **~$53 / month** |

> Costs will vary based on traffic, storage usage, and data transfer. Use the
> [AWS Pricing Calculator](https://calculator.aws/) for accurate estimates.

---

## Scaling Considerations

- Set ECS service `desired-count` to 2+ for high availability across AZs.
- Enable ECS Service Auto Scaling based on CPU/memory metrics.
- Upgrade RDS to `db.t3.small` or higher for > 50 concurrent users.
- Use RDS Multi-AZ for production failover.
