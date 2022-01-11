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
