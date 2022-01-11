build:
	minikube image build -t websocketd .

docker:
	docker image build -t websocketd .

delete:
	minikube image rm websocketd

clean:
	rm -f *~

push-to-gke-will-not-work-from-Makefile-use-CLI-instead:
	export PROJECT_ID="$(gcloud config get-value project -q)"
	gcloud auth configure-docker
	docker tag websocketd:latest "gcr.io/${PROJECT_ID}/websocketd:latest"
	docker push "gcr.io/${PROJECT_ID}/websocketd:latest"
