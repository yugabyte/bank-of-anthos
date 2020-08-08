![Continuous Integration](https://github.com/GoogleCloudPlatform/anthos-finance-demo/workflows/Continuous%20Integration/badge.svg)

# Demo Bank - Next Keynote Demo Part 2

This branch contains the demo code used in Part 2 of the [Application Modernization Hands-on Keynote](https://cloud.withgoogle.com/next/sf/sessions?session=GENKEY02#application-modernization)
where the User Service is refactored to a separate Java microservice.

***NOTE:** In the Keynote we referred to the bank's name as "Demo Bank", but it is also known as the
"Bank of Anthos" demo application.*

This project simulates a bank's payment processing network using [Anthos](https://cloud.google.com/anthos/).
Bank of Anthos allows users to create artificial accounts and simulate transactions between accounts.
Bank of Anthos was developed to create an end-to-end sample demonstrating Anthos best practices.

This branch contains the work done to refactor the User Service from a Python-based microservice
to a Java one using the Spring Boot Framework.

Some of the tools used to do this include:

- [Spring Cloud GCP](https://spring.io/projects/spring-cloud-gcp) - A set of libraries and
  integrations to make it easier to use the Java Spring Framework on Google Cloud Platform.
  
- [Cloud Code](https://cloud.google.com/intellij) - An extension for IntelliJ and VSCode IDEs
  that accelerates developing and deploying applications on GCP.
  
- [Skaffold](https://skaffold.dev/) - Allows for continuous development of Kubernetes applications.
  
- [Jib](https://github.com/GoogleContainerTools/jib) - A tool which helps you build optimized
  Docker and OCI images for your Java applications without deep mastery of Docker best-practices.
  
All of the application migration work is placed in the `src/userservice-java` directory, and it can
be compared with the previous Python version in the `src/userservice` directory.

## Installation

### 1 - Project setup

[Create a Google Cloud Platform project](https://cloud.google.com/resource-manager/docs/creating-managing-projects#creating_a_project) or use an existing project. Set the PROJECT_ID environment variable and ensure the Google Kubernetes Engine API is enabled.

```
PROJECT_ID=<your-project-id>
gcloud beta services enable container --project ${PROJECT_ID}
```

### 2 - Clone the repo

Clone this repository to your local environment and cd into the directory.

```
git clone https://github.com/GoogleCloudPlatform/bank-of-anthos.git
cd bank-of-anthos
```


### 3 - Create a Kubernetes cluster

```
ZONE=<your-zone>
gcloud beta container clusters create bank-of-anthos \
    --project=${PROJECT_ID} --zone=${ZONE} \
    --machine-type=n1-standard-2 --num-nodes=4 \
    --scopes=gke-default,sql-admin,cloud-platform
```

### 3.5 - Create a Cloud SQL instance

First, enable the [Cloud SQL APIs](https://console.developers.google.com/apis/api/sqladmin.googleapis.com/).

Using the [Google Cloud SQL Cloud Console](https://console.cloud.google.com/sql), create a new
Postgres instance called `test-instance-pg` and set the password for the default user to `postgres`.
Then, create a database named `test-db`.

Ensure that instance connection name, database, database user, and database password, are set
correctly in `kubernetes-manifests/config.yaml` in the `accounts-db-config` config map.

### 4 - Generate RSA key pair secret

```
openssl genrsa -out jwtRS256.key 4096
openssl rsa -in jwtRS256.key -outform PEM -pubout -out jwtRS256.key.pub
openssl pkcs8 -topk8 -nocrypt -inform pem -in jwtRS256.key -outform pem -out jwtRS256-pkcs8.key
kubectl create secret generic jwt-key --from-file=./jwtRS256.key --from-file=./jwtRS256.key.pub --from-file=./jwtRS256-pkcs8.key
```

### 4.5 - Add Secret to Google Secret Manager (For Java Userservice)

We will store several secrets in Google Secret Manager for the Java User Service to read.
This will demonstrate how to best access secrets from a Spring Boot application.

```
gcloud beta secrets create jwt-key-private --data-file=jwtRS256-pkcs8.key --replication-policy=automatic
printf "postgres" | gcloud beta secrets create postgres-pass --data-file=- --replication-policy=automatic
printf "postgres" | gcloud beta secrets create postgres-user --data-file=- --replication-policy=automatic
```

Next, go to the [Secret Manager Cloud Console](https://console.cloud.google.com/security/secret-manager) to verify
that your secrets were created.

In the console UI, give the service account running your cluster
[the `roles/secretmanager.secretAccessor` permission](https://cloud.google.com/secret-manager/docs/managing-secrets#secretmanager-create-secret-web)
for each secret you created.
By default, the service account running your cluster should be in the form: `${GCP_PROJECT_NUMBER}-compute@developer.gserviceaccount.com`

---
**Note**: In true production use, we would recommend using [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)
to manage access to your secrets.

The this method allows you to map a Kubernetes Service Account to a Google Service Account. This allows you to reduce
the scope of access of your secrets to only the pods which need it rather than to all of your pods.

---


### 5 - Deploy Kubernetes manifests

```
kubectl apply -f ./kubernetes-manifests
```

After 1-2 minutes, you should see that all the pods are running:

```
kubectl get pods
```

*Example output - do not copy*

```
NAME                                  READY   STATUS    RESTARTS   AGE
accounts-db-6f589464bc-6r7b7          1/1     Running   0          99s
balancereader-797bf6d7c5-8xvp6        1/1     Running   0          99s
contacts-769c4fb556-25pg2             1/1     Running   0          98s
frontend-7c96b54f6b-zkdbz             1/1     Running   0          98s
ledger-db-5b78474d4f-p6xcb            1/1     Running   0          98s
ledgerwriter-84bf44b95d-65mqf         1/1     Running   0          97s
loadgenerator-559667b6ff-4zsvb        1/1     Running   0          97s
transactionhistory-5569754896-z94cn   1/1     Running   0          97s
userservice-78dc876bff-pdhtl          1/1     Running   0          96s
```

### 6 - Get the frontend IP

```
kubectl get svc frontend | awk '{print $4}'
```

*Example output - do not copy*

```
EXTERNAL-IP
35.223.69.29
```

**Note:** you may see a `<pending>` IP for a few minutes, while the GCP load balancer is provisioned.

### 7 - Navigate to the web frontend

Paste the frontend IP into a web browser. You should see a log-in screen:

![](/docs/login.png)

Using the pre-populated username and password fields, log in as `testuser`. You should see a list of transactions, indicating that the frontend can successfully reach the backend transaction services.

![](/docs/transactions.png)

## Setup for Workload Identity clusters

If you have enabled [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity) on your GKE cluster ([a requirement for Anthos Service Mesh](https://cloud.google.com/service-mesh/docs/gke-anthos-cli-new-cluster#requirements)), follow these instructions to ensure that Bank of Anthos pods can communicate with GCP APIs.

*Note* - These instructions have only been validated in GKE on GCP clusters. [Workload Identity is not yet supported](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity#creating_a_relationship_between_ksas_and_gsas) in Anthos GKE on Prem. 


1. **Set up Workload Identity** on your GKE cluster [using the instructions here](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity#enable_on_new_cluster). These instructions create the Kubernetes Service Account (KSA) and Google Service Account (GSA) that the Bank of Anthos pods will use to authenticate to GCP. Take note of what Kubernetes `namespace` you use during setup.

2. **Add IAM Roles** to your GSA. These roles allow workload identity-enabled Bank of Anthos pods to send traces and metrics to GCP. 

```bash
PROJECT_ID=<your-gcp-project-id>
GSA_NAME=<your-gsa>

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member "serviceAccount:${GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role roles/cloudtrace.agent

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member "serviceAccount:${GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role roles/monitoring.metricWriter
```

3. **Generate Bank of Anthos manifests** using your KSA as the Pod service account. In `kubernetes-manifests/`, replace `serviceAccountName: default` with the name of your KSA. (**Note** - sample below is Bash.)

```bash

KSA_NAME=<your-ksa>

mkdir -p wi-kubernetes-manifests
FILES="`pwd`/kubernetes-manifests/*"
for f in $FILES; do
    echo "Processing $f..."
    sed "s/serviceAccountName: default/serviceAccountName: ${KSA_NAME}/g" $f > wi-kubernetes-manifests/`basename $f`
done
```

4. **Deploy Bank of Anthos** to your GKE cluster using the install instructions above, except make sure that instead of the default namespace, you're deploying the manifests into your KSA namespace: 

```bash
NAMESPACE=<your-ksa-namespace>
kubectl apply -n ${NAMESPACE} -f ./wi-kubernetes-manifests 
```


## Variant: Ledger Monolith Service

The default app deployment uses a microservices architecture on Kubernetes. The Ledger Monolith variant deploys part of the app as a monolith service on a separate VM hosted by [Google Compute Engine](https://cloud.google.com/compute).

Read more about the Ledger Monolith service under its subdirectory: [src/ledgermonolith](src/ledgermonolith/README.md)

### Quick Start

Deploy the Ledger Monolith to a VM and update the banking app to use it to track the bank ledger.

```
make monolith
```

## Local Development

See the [Development Guide](./docs/development.md) for instructions on how to build and develop services locally, and the [Contributing Guide](./CONTRIBUTING.md) for pull request and code review guidelines.

---

This is not an official Google project.
