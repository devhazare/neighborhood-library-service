# gRPC-Web Service Documentation

This document describes the gRPC-Web service definitions for the Neighborhood Library Service.

## Overview

The library service provides gRPC endpoints alongside REST APIs for better performance and type safety. The gRPC services are defined using Protocol Buffers (protobuf) and support gRPC-Web for browser clients.

## Proto Files

All proto files are located in `backend/protos/`:

| File | Description |
|------|-------------|
| `common.proto` | Common message types (pagination, ID requests, status responses) |
| `books.proto` | Book service - CRUD operations, PDF upload, AI enrichment |
| `members.proto` | Member service - CRUD operations, borrowing history, recommendations |
| `borrow.proto` | Borrow service - borrow/return operations, overdue management |
| `auth.proto` | Auth service - registration, login, token management |

## Services

### BookService

| Method | Request | Response | Description |
|--------|---------|----------|-------------|
| `CreateBook` | `CreateBookRequest` | `BookResponse` | Create a new book |
| `GetBook` | `IdRequest` | `BookResponse` | Get book by ID |
| `ListBooks` | `PaginationRequest` | `BookListResponse` | List books with pagination |
| `UpdateBook` | `UpdateBookRequest` | `BookResponse` | Update a book |
| `DeleteBook` | `IdRequest` | `StatusResponse` | Delete a book |
| `UploadBookPdf` | `UploadPdfRequest` | `BookResponse` | Upload PDF for a book |
| `ExtractPdfMetadata` | `ExtractPdfMetadataRequest` | `PdfMetadataResponse` | Extract metadata from PDF using AI |
| `AiEnrichBook` | `IdRequest` | `AiEnrichmentResponse` | Enrich book with AI content |
| `SearchBooks` | `SearchBooksRequest` | `BookListResponse` | Search books |

### MemberService

| Method | Request | Response | Description |
|--------|---------|----------|-------------|
| `CreateMember` | `CreateMemberRequest` | `MemberResponse` | Create a new member |
| `GetMember` | `IdRequest` | `MemberResponse` | Get member by ID |
| `ListMembers` | `PaginationRequest` | `MemberListResponse` | List members with pagination |
| `UpdateMember` | `UpdateMemberRequest` | `MemberResponse` | Update a member |
| `DeleteMember` | `IdRequest` | `StatusResponse` | Delete a member |
| `GetMemberBorrowedBooks` | `IdRequest` | `MemberBorrowedBooksResponse` | Get member's borrowed books |
| `GetMemberRecommendations` | `IdRequest` | `RecommendationsResponse` | Get AI book recommendations |
| `SearchMembers` | `SearchMembersRequest` | `MemberListResponse` | Search members |

### BorrowService

| Method | Request | Response | Description |
|--------|---------|----------|-------------|
| `BorrowBook` | `BorrowBookRequest` | `BorrowTransactionResponse` | Borrow a book |
| `ReturnBook` | `ReturnBookRequest` | `BorrowTransactionResponse` | Return a book |
| `GetBorrowTransaction` | `IdRequest` | `BorrowTransactionResponse` | Get transaction by ID |
| `ListActiveBorrowings` | `PaginationRequest` | `BorrowTransactionListResponse` | List active borrowings |
| `ListOverdueBorrowings` | `PaginationRequest` | `BorrowTransactionListResponse` | List overdue borrowings |
| `ListAllBorrowings` | `ListBorrowingsRequest` | `BorrowTransactionListResponse` | List all borrowings with filters |
| `GenerateReminder` | `IdRequest` | `ReminderResponse` | Generate AI overdue reminder |
| `ExtendDueDate` | `ExtendDueDateRequest` | `BorrowTransactionResponse` | Extend due date |
| `GetBookBorrowHistory` | `IdRequest` | `BorrowTransactionListResponse` | Get book's borrow history |

### AuthService

| Method | Request | Response | Description |
|--------|---------|----------|-------------|
| `Register` | `RegisterRequest` | `UserResponse` | Register new user |
| `Login` | `LoginRequest` | `TokenResponse` | Login and get token |
| `RefreshToken` | `RefreshTokenRequest` | `TokenResponse` | Refresh access token |
| `GetCurrentUser` | `Empty` | `UserResponse` | Get current user info |
| `Logout` | `Empty` | `StatusResponse` | Logout user |
| `ChangePassword` | `ChangePasswordRequest` | `StatusResponse` | Change password |
| `RequestPasswordReset` | `PasswordResetRequest` | `StatusResponse` | Request password reset |

## Generating Code

### Backend (Python)

```bash
cd backend
python scripts/generate_grpc.py
```

This generates Python gRPC code in `backend/app/grpc/generated/`.

### Frontend (TypeScript)

For gRPC-Web client code generation, you'll need `protoc` and the gRPC-Web plugin:

```bash
# Install protoc-gen-grpc-web
npm install -g protoc-gen-grpc-web

# Generate TypeScript code
protoc -I=backend/protos \
  --js_out=import_style=commonjs:frontend/src/grpc \
  --grpc-web_out=import_style=typescript,mode=grpcwebtext:frontend/src/grpc \
  backend/protos/*.proto
```

## Running the Services

### Docker Compose

The gRPC server runs alongside the REST API:

```yaml
ports:
  - "8000:8000"   # REST API
  - "50051:50051" # gRPC Server
```

### Standalone gRPC Server

```bash
cd backend
python -m app.grpc.server 50051
```

## Client Usage

### Python Client Example

```python
import grpc
from app.grpc.generated import books_pb2, books_pb2_grpc, common_pb2

# Connect to server
channel = grpc.insecure_channel('localhost:50051')
stub = books_pb2_grpc.BookServiceStub(channel)

# List books
request = common_pb2.PaginationRequest(skip=0, limit=10)
response = stub.ListBooks(request)
for book in response.items:
    print(f"{book.title} by {book.author}")

# Create a book
create_request = books_pb2.CreateBookRequest(
    title="The Great Gatsby",
    author="F. Scott Fitzgerald",
    category="Fiction",
    total_copies=3,
    available_copies=3,
)
book = stub.CreateBook(create_request)
print(f"Created book: {book.book.id}")
```

### gRPC-Web Client Example (TypeScript)

```typescript
import { BookServiceClient } from './grpc/BooksServiceClientPb';
import { PaginationRequest } from './grpc/common_pb';

const client = new BookServiceClient('http://localhost:8080'); // Envoy proxy

const request = new PaginationRequest();
request.setSkip(0);
request.setLimit(10);

client.listBooks(request, {}, (err, response) => {
  if (err) {
    console.error(err);
    return;
  }
  response.getItemsList().forEach(book => {
    console.log(`${book.getTitle()} by ${book.getAuthor()}`);
  });
});
```

## gRPC-Web Proxy (Envoy)

For browser clients, you need a gRPC-Web proxy like Envoy. Example config:

```yaml
# envoy.yaml
static_resources:
  listeners:
    - name: listener_0
      address:
        socket_address: { address: 0.0.0.0, port_value: 8080 }
      filter_chains:
        - filters:
            - name: envoy.filters.network.http_connection_manager
              typed_config:
                "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
                codec_type: auto
                stat_prefix: ingress_http
                route_config:
                  name: local_route
                  virtual_hosts:
                    - name: local_service
                      domains: ["*"]
                      routes:
                        - match: { prefix: "/" }
                          route:
                            cluster: grpc_service
                            timeout: 0s
                            max_stream_duration:
                              grpc_timeout_header_max: 0s
                      cors:
                        allow_origin_string_match:
                          - prefix: "*"
                        allow_methods: GET, PUT, DELETE, POST, OPTIONS
                        allow_headers: keep-alive,user-agent,cache-control,content-type,content-transfer-encoding,x-accept-content-transfer-encoding,x-accept-response-streaming,x-user-agent,x-grpc-web,grpc-timeout,authorization
                        max_age: "1728000"
                        expose_headers: grpc-status,grpc-message
                http_filters:
                  - name: envoy.filters.http.grpc_web
                    typed_config:
                      "@type": type.googleapis.com/envoy.extensions.filters.http.grpc_web.v3.GrpcWeb
                  - name: envoy.filters.http.cors
                    typed_config:
                      "@type": type.googleapis.com/envoy.extensions.filters.http.cors.v3.Cors
                  - name: envoy.filters.http.router
                    typed_config:
                      "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router
  clusters:
    - name: grpc_service
      connect_timeout: 0.25s
      type: logical_dns
      http2_protocol_options: {}
      lb_policy: round_robin
      load_assignment:
        cluster_name: grpc_service
        endpoints:
          - lb_endpoints:
              - endpoint:
                  address:
                    socket_address:
                      address: backend
                      port_value: 50051
```

## Error Handling

gRPC uses status codes for errors:

| gRPC Status | HTTP Equivalent | Description |
|-------------|-----------------|-------------|
| `OK` | 200 | Success |
| `NOT_FOUND` | 404 | Resource not found |
| `ALREADY_EXISTS` | 409 | Resource already exists |
| `INVALID_ARGUMENT` | 400 | Invalid request |
| `UNAUTHENTICATED` | 401 | Missing/invalid authentication |
| `PERMISSION_DENIED` | 403 | Not authorized |
| `FAILED_PRECONDITION` | 412 | Business rule violation |
| `INTERNAL` | 500 | Internal server error |

## Testing with grpcurl

```bash
# List services
grpcurl -plaintext localhost:50051 list

# List methods for a service
grpcurl -plaintext localhost:50051 list library.books.BookService

# Call a method
grpcurl -plaintext -d '{"skip": 0, "limit": 10}' \
  localhost:50051 library.books.BookService/ListBooks

# Create a book
grpcurl -plaintext -d '{
  "title": "Test Book",
  "author": "Test Author",
  "total_copies": 1,
  "available_copies": 1
}' localhost:50051 library.books.BookService/CreateBook
```

