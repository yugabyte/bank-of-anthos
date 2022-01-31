# Demonstration Guide

## Introduction

This demo simulates a retail fraud detection scenario.  It is based on the [Bank of Anthos](https://github.com/GoogleCloudPlatform/bank-of-anthos) demo.

Pre-requisites:

 * [skaffold **1.27+**](https://skaffold.dev/docs/install/) - This builds docker containers and deploys them for you.  It also saves you from having to fiddle with YAML files.

The following services have changed from the base Bank of Anthos code:

 * ledgerwriter - publishes each transaction to a redis topic
 * frontend - websocketd prints redis topic subscriber's output
 * redis - additional container
 * accounts-db - config map has postgres URI for YugabyteDB, you need this pod to initialize the db
 * ledger-db - config map has postgres URI for YugabyteDB, you need this pod to initialize the db

Optional: You may find the tools [kubectx and kubens](https://github.com/ahmetb/kubectx) helpful in navigating multiple contexts and namespaces.

The password to just about everything in the application is `password`.

## Minikube Setup

This mode puts Docker images directly into minikube's container repository using skaffold for automation.

1. Start minikube, and add the GCP auth extension.

    ```
    minikube start --cpus 4 --memory 5120 --vm-driver virtualbox
    minikube addons enable gcp-auth
    ```

1. Ensure your [helm charts](https://docs.yugabyte.com/latest/quick-start/install/kubernetes/) are up to date so you can run YugabyteDB in minikube.

    ```
    helm repo update

    ```

1. Create two YugabyteDB clusters in different namespaces.  Give them a minute or two to start up.

    ```
    for namespace in yb-east yb-west
    do
    helm install $namespace yugabytedb/yugabyte \
    --set resource.master.requests.cpu=0.5,resource.master.requests.memory=0.5Gi,\
    resource.tserver.requests.cpu=0.5,resource.tserver.requests.memory=0.5Gi,\
    replicas.master=1,replicas.tserver=1,enableLoadBalancer=False \
    --create-namespace --namespace $namespace
    done

    ```

1. Build the Docker containers and deploy them into Minikube.  The [magic](https://skaffold.dev/docs/environment/local-cluster/) happens in the first eval where your environment variables point skaffold to Minikube.  I like to turn off the load generator until everything settles and it's time to start the demo.

    ```
    eval $(minikube -p minikube docker-env)
    skaffold run
    ```

1. Create the database schema on the consumer side of xCluster.

    ```
    kubectl exec -it accounts-db-0 -- /bin/bash -c 'psql -f /docker-entrypoint-initdb.d/0-accounts-schema.sql -h yb-tserver-0.yb-tservers.yb-west.svc.cluster.local -p 5433 --dbname yugabyte --username yugabyte'
    kubectl exec -it ledger-db-0   -- /bin/bash -c 'psql -f /docker-entrypoint-initdb.d/0_init_tables.sql     -h yb-tserver-0.yb-tservers.yb-west.svc.cluster.local -p 5433 --dbname yugabyte --username yugabyte'
    ```

1. Configure xCluster replication by running the following script on any YB master pod.

    ```
    kubectl exec -i -n yb-east -c yb-master yb-master-0 -- /bin/bash <<'EOF'
    #!/bin/bash
    # setup unidirectional xCluster replication for Bank of Anthos.
    # you can run this script on any master.
    # make sure you create the database and setup DDL on the consumer beforehand.

    producer_master_addresses=yb-master-0.yb-masters.yb-east.svc.cluster.local:7100
    consumer_master_addresses=yb-master-0.yb-masters.yb-west.svc.cluster.local:7100

    table_ids=$(yb-admin -master_addresses $producer_master_addresses list_tables include_db_type include_table_id include_table_type | egrep 'yugabyte\.(idx_)?(contacts|users|transactions)' | awk '{print $2}' | tr '\n' , | sed 's/,$//')

    producer_uuid=$(yb-admin -master_addresses $producer_master_addresses get_universe_config | grep -oP '(?<="clusterUuid":")[^"]*')

    set -x
    yb-admin -master_addresses $consumer_master_addresses setup_universe_replication $producer_uuid $producer_master_addresses $table_ids
    EOF
    ```


1. Enable port forwarding, and then open a browser to http://localhost:8080

    ```
    kubectl port-forward svc/frontend 8080:80 8181:8181
    ```


## GKE Setup

The following steps assume you already have a GKE cluster created with its credentials in your current kubectl context.  You will also need the Docker daemon running on your local machine to stage the containers before they are pushed to GKE.

1. Unset any minikube Docker environment variables, if present.

    ```
    eval $(minikube -p minikube docker-env -u)
    ```

1. Ensure a firewall rule exists for the websocket to reach TCP port <b>8181</b> of the GKE cluster nodes.  The "[target tags](https://stackoverflow.com/questions/60744761/adding-firewall-rule-for-gke-nodes)" of the firewall rule must match the network tag of the VMs running the k8s cluster nodes.  To find the target tag for the firewall rule in GCP, navigate to Kubernetes Engine -> Clusters -> click on your cluster -> Nodes tab -> click any node -> Details tab -> click VM Instance -> scroll down to Network Tags.  It will look something like "gke-mycluster-9894ac0e-node".

1. If using Open Source YugabyteDB:

    Ensure your [helm charts](https://docs.yugabyte.com/latest/quick-start/install/kubernetes/) are up to date so you can run YugabyteDB in minikube.

    ```
    helm repo update

    ```

    Create two YugabyteDB clusters in different namespaces.  Give them a minute or two to start up.

    ```
    for namespace in yb-east yb-west
    do
    helm install $namespace yugabytedb/yugabyte \
    --set resource.master.requests.cpu=0.5,resource.master.requests.memory=0.5Gi,\
    resource.tserver.requests.cpu=0.5,resource.tserver.requests.memory=0.5Gi,\
    replicas.master=1,replicas.tserver=1,enableLoadBalancer=False \
    --create-namespace --namespace $namespace
    done

    ```

1. If _not_ using Open Source YugabyteDB, you will need to install your enterprise cluster and edit the postgres URIs in accounts-db.yaml and ledger-db.yaml with appropriate hostname, port, username, and password.  The jdbc URL as well as the POSTGRES_* environment variables matter.

    Important notes:
    * You _must_ have a database password; empty passwords are not permitted.
    * If the URI begins with `postgresql:` then you put the username and password into the URI itself (as well as the other lines in that file).
    * If the URI begins with `jdbc:` then that is a SPRING_DATASOURCE URI that _does not_ include the username and password; those go in separate variables on other lines (only).
    * The values for the `POSTGRES_*` environment variables duplicate what's in the jdbc URI, but that's the way it is.
    * Keep "double quotes" around things that already have them: don't try to be clever.


1. Deploy the pods to GKE.  You will need to tell skaffold the name of your GCP project's [image registry](https://skaffold.dev/docs/environment/image-registries/).  The registry name can be determined by navigating to your project's Container Registry and clicking on the copy icon next to the repository to get the full name.

    ```
    skaffold run --default-repo gcr.io/dataengineeringdemos/yugabyte
    ```

1. Setup xCluster replication by running the two steps from the Minikube section above entitled, "Create the database schema on the consumer side" and "Configure xCluster replication".  You won't need to run the port forwarding step because it is already done for you.

1. Open a browser to the IP address of the frontend service.  To find the IP address, list the k8s services and find the external IP of the frontend service's load balancer.  In the example below, the external IP is 104.198.9.211.

    ```
    % kubectl get svc
    NAME                 TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)                       AGE
    accounts-db          ClusterIP      10.43.255.146   <none>          5432/TCP                      2d4h
    balancereader        ClusterIP      10.43.250.67    <none>          8080/TCP                      2d2h
    contacts             ClusterIP      10.43.244.156   <none>          8080/TCP                      2d4h
    frontend             LoadBalancer   10.43.242.238   104.198.9.211   80:31941/TCP,8181:31906/TCP   2d4h
    kubernetes           ClusterIP      10.43.240.1     <none>          443/TCP                       8d
    ledger-db            ClusterIP      10.43.244.139   <none>          5432/TCP                      2d4h
    ledgerwriter         ClusterIP      10.43.242.58    <none>          8080/TCP                      2d4h
    redis                ClusterIP      10.43.240.174   <none>          6379/TCP                      2d4h
    transactionhistory   ClusterIP      10.43.253.229   <none>          8080/TCP                      2d4h
    userservice          ClusterIP      10.43.247.207   <none>          8080/TCP                      2d4h
    ```

## Demo setup


1. Watch the transaction counts in each of the two databases using port-forwarding to their respective ysqlsh ports.

    ```
    kubectl port-forward -n yb-east svc/yb-tservers 5444:5433 &
    kubectl port-forward -n yb-west svc/yb-tservers 5333:5433 &
    export PGPASSWORD='yugabyte'
    watch -t "ysqlsh -p 5444 -c 'select count(*) from transactions;'"
    watch -t "ysqlsh -p 5333 -c 'select count(*) from transactions;'"
    
    ```

1. Start the load generator after you have logged in as `testuser` in your browser.  You should see transactions start to scroll in the browser.

   ```
   kubectl scale --replicas=1 deployment/loadgenerator
   ```

1. Login to another browser window as user `alice`.  Any financial transaction performed by Alice will be flagged in red in the Test User browser window.

## Talk Track

1. This retail scenario is a fictitious retail store ("edge") with payment transactions. There is a microservices application and YugabyteDB instance running on k8s in the store, and each payment transaction is replicating asynchronously to another YugabyteDB instance in Anthos in the cloud ("hub").

1. The hub would train machine learning models for fraudulent activity, and the model would be pushed down to the edge (retail store).

1. The microservices application is a modified version of the Bank Of Anthos application which was written to utilize Postgres. From a database perspective, only the database connection string was changed to utilize YugabyteDB instead. There were no schema changes.

1. The browser on the left side represents a real-time view of payment transactions happening in the store. This is accomplished with a load generator.

1. The two shell windows at the bottom show repeated row counts of the transaction tables; the left window is for the edge, and the right window is for the hub. (Note: you will see the hub count sometimes outnumber the edge count due to the 2 second refresh intervals being staggered)

1. The browser on the right represents a fraudulent payment transaction by malicious user Alice. Her payment is flagged in red as being fraudulent. 

## Teardown

1. Delete the pods you have deployed.

    ```
    skaffold delete
    ```

1. Delete the databases.  Deleting the namespaces is a brute force approach.

    ```
    kubectl delete ns yb-east  &&  kubectl delete ns yb-west
    ```