build:
	mvn package -Dmaven.test.skip

deploy:
	minikube image rm ledgerwriter
	minikube image build -t ledgerwriter .
	kubectl apply  -f ../../kubernetes-manifests/ledger-writer.yaml

delete:
	kubectl delete -f ../../kubernetes-manifests/ledger-writer.yaml
	

docker:
	docker image build -t ledgerwriter .

push-to-gke-will-not-work-from-Makefile-use-CLI-instead:
	export PROJECT_ID="$(gcloud config get-value project -q)"
	gcloud auth configure-docker
	docker tag ledgerwriter:latest "gcr.io/${PROJECT_ID}/ledgerwriter:latest"
	docker push "gcr.io/${PROJECT_ID}/ledgerwriter:latest"
