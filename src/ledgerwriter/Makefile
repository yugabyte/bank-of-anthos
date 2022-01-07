build:
	mvn package -Dmaven.test.skip

deploy:
	minikube image rm ledgerwriter
	minikube image build -t ledgerwriter .
	kubectl apply  -f ../../kubernetes-manifests/ledger-writer.yaml

delete:
	kubectl delete -f ../../kubernetes-manifests/ledger-writer.yaml
	
