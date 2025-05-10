# FastAPI Widget API

A RESTful API for managing widgets with user authentication, built with FastAPI and MongoDB.

# Module 5 Clip 1: Prometheus and Grafana
## Setup Helm
Install Helm on Windows:
```
choco install kubernetes-helm
```

## Configure Prometheus
Add the Prometheus Helm Repository:
```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

Create the moinitoring namespace:
```
kubectl create namespace monitoring
```

Install Prometheus using Helm:
```
helm install prometheus prometheus-community/prometheus \
  --namespace monitoring \
  --set alertmanager.persistentVolume.storageClass=gp2 \
  --set server.persistentVolume.storageClass=gp2 \
  --values - <<EOF
server:
  additionalScrapeConfigs:
    - job_name: 'widget-api'
      static_configs:
        - targets: ['widget-api:8000']
EOF
```

## Configure Grafana:
Add the Grafana Helm Repository:
```
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

Install Grafana using Helm:
```
helm install grafana grafana/grafana \
  --namespace monitoring \
  --set persistence.storageClassName=gp2 \
  --set persistence.enabled=true \
  --set adminPassword='YourSecurePassword' \
  --values - <<EOF
datasources:
  datasources.yaml:
    apiVersion: 1
    datasources:
    - name: Prometheus
      type: prometheus
      url: http://prometheus-server.monitoring.svc.cluster.local
      access: proxy
      isDefault: true
EOF
```

Setup port forwarding to access Grafana:
```
kubectl port-forward -n monitoring svc/grafana 3000:80
```

Get the Admin password:
```
kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode
```

# Module 5 Clip 3: Instrumenting FastAPI
## Update the Dockerfile
Rebuild the Docker image:
```
docker image build -t <RESPOSITORY>:prometheus .
```

Login to ECR:
```
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <RESPOSITORY>
```

Push the image to ECR:
```
docker push <RESPOSITORY>:prometheus
```
## Update the Kubernetes Depolymnet
Update deployment.yml:
```
spec:
  containers:
  - name: widget-api
    image: <RESPOSITORY>:prometheus
```

Apply the maninfest:
```
kubectl apply -f deployment.yml
```

## Update the Kubernetes Service
Update service.yml:
```
apiVersion: v1
kind: Service
metadata:
  name: widget-api
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"  # Use Network Load Balancer
    service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
    service.beta.kubernetes.io/aws-load-balancer-backend-protocol: "http"
    # Prometheus annotations for service discovery
    prometheus.io/scrape: "true"
    prometheus.io/path: "/metrics"
    prometheus.io/port: "8000"
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: widget-api
```

Apply the maninfest:
```
kubectl apply -f service.yml
```

Setup port-forwarding for Grafana:
```
kubectl port-forward -n monitoring svc/grafana 3000:80
```

Setup port-forwarding for Prometheus:
```
kubectl port-forward -n monitoring svc/prometheus-server 3001:80
```

# Module 5 Clip 5: Configuring Prometheus Alerting
## Setting up Alertmanager

Create the Alertmanager PVC:
```
kubectl apply -f Prometheus\pvc.yml
```

Setup Prometheus with Alertmanager:
```
helm install prometheus prometheus-community/prometheus \
  --namespace monitoring \
  --set server.persistentVolume.storageClass=gp2 \
  --values Prometheus/values.yml
```

## Setup port-forwarding
Setup port-forwarding for Grafana:
```
kubectl port-forward -n monitoring svc/grafana 3000:80
```

```
kubectl port-forward -n monitoring svc/prometheus-server 3001:80
```

```
kubectl port-forward -n monitoring svc/prometheus-alertmanager  3002:9093
```

# Module 5 Clip 6: Tearing down the Stack
## Setting up Alertmanager

Delete the EKS cluster:
```
eksctl delete cluster --name pscluster
```