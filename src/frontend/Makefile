build:
	minikube image build -t frontend .

deploy: delete
	minikube image build -t frontend .
	kubectl apply  -f ../../kubernetes-manifests/frontend.yaml

delete:
	minikube image rm frontend
	kubectl delete  -f ../../kubernetes-manifests/frontend.yaml

clean:
	rm -f *~

docker:
	docker image build -t frontend .

push-to-gke-will-not-work-from-Makefile-use-CLI-instead:
	export PROJECT_ID="$(gcloud config get-value project -q)"
	gcloud auth configure-docker
	docker tag frontend:latest "gcr.io/${PROJECT_ID}/frontend:latest"
	docker push "gcr.io/${PROJECT_ID}/frontend:latest"
