# User Service - Java

This directory contains the demo application refactoring work done [Application Modernization Hands-on Keynote](https://cloud.withgoogle.com/next/sf/sessions?session=GENKEY02#application-modernization).

The user service manages user accounts and authentication. 
It creates and signs JWTs that are used by other services to authenticate users.

### Endpoints

| Endpoint            | Type  | Auth? | Description                                                      |
| ------------------- | ----- | ----- | ---------------------------------------------------------------- |
| `/login`            | GET   |       |  Returns a JWT if authentication is successful.                  |
| `/ready`            | GET   |       |  Readiness probe endpoint.                                       |
| `/users`            | POST  |       |  Validates and creates a new user record.                        |
| `/version`          | GET   |       |  Returns the contents of `$VERSION`                              |

### Environment Variables

- `VERSION`
  - a version string for the service
- `TOKEN_EXPIRY_SECONDS`
  - how long JWTs are valid before forcing user logout
- `CLOUD_SQL_INSTANCE_NAME`
  - The instance connection name to the PostgreSQL Cloud SQL database.
- `POSTGRES_DB`
  - The name of the PostgreSQL database to connect to in the Cloud SQL instance.

- Secret Manager Secrets:
  - `jwt-key-private`
    - A PKCS8 RSA private key in `pem` format used to encrypt authentication tokens.
  - `postgres-user`
    - The PostgreSQL database user
  - `postgres-pass`
    - The PostgreSQL database password
    
### Kubernetes Resources

- [deployments/userservice](/kubernetes-manifests/userservice.yaml)
- [service/userservice](/kubernetes-manifests/userservice.yaml)
