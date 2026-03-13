#!/bin/bash

if [ -f .env ]; then
    export $(cat .env | xargs)
    echo "✅ Loaded secrets from .env"
else
    echo "❌ Error: .env file not found! Please create it."
    exit 1
fi

echo "---  PRE-DEPLOY CLEANUP ---"
kubectl delete -f deployment.yaml --ignore-not-found=true
docker rmi $IMAGE_NAME:$TAG --force 2>/dev/null
docker image prune -f

echo " Building Docker image: $IMAGE_NAME:$TAG"
docker build -t $IMAGE_NAME:$TAG .

kubectl create secret generic slack-secrets \
  --from-literal=token=$SLACK_TOKEN \
  --from-literal=channel=$SLACK_CHANNEL \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Deploying to Kubernetes..."
kubectl apply -f rbac.yaml
kubectl apply -f deployment.yaml

echo "Restarting deployment to pick up latest changes..."
kubectl rollout restart deployment/k8s-engine

echo "--- DEPLOY SMOKE TEST POSITIVE RESOURCES ---"
kubectl apply -f smoke-tests/positive-scenarios/
sleep 30
kubectl delete -f smoke-tests/positive-scenarios/ --grace-period=0 --force

sleep 5

echo "--- DEPLOY SMOKE TEST NEGATIVE RESOURCES ---"
kubectl apply -f smoke-tests/negative-scenarios/
sleep 30
kubectl delete -f smoke-tests/negative-scenarios/ --grace-period=0 --force

echo "Test resources removed. k8s-engine is now running in 'Watch Mode'."