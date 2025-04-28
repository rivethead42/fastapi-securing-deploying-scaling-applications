# FastAPI Widget API

A RESTful API for managing widgets with user authentication, built with FastAPI and MongoDB.

# Module 4 Clip 1: 

Create service.yml:
```
apiVersion: v1
kind: Service
metadata:
  name: widget-api
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"  # Use Network Load Balancer
    service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
    service.beta.kubernetes.io/aws-load-balancer-backend-protocol: "http"
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

# Module 4 Clip 2: 

Create hpa.yml:
```
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: widget-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: widget-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

Apply the maninfest:
```
kubectl apply -f hpa.yml
```

# Module 4 Clip 3:
## Deploy Redis to EKS
Create redis.yml:
```
apiVersion: v1
kind: ConfigMap
metadata:
  name: redis-config
data:
  redis.conf: |
    appendonly yes
    appendfsync everysec
    save 900 1
    save 300 10
    save 60 10000
    maxmemory 512mb
    maxmemory-policy allkeys-lru
    protected-mode no
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  labels:
    app: redis
spec:
  ports:
  - port: 6379
    name: redis
  clusterIP: None
  selector:
    app: redis
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: gp2  # AWS EBS storage class
  resources:
    requests:
      storage: 5Gi
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis
spec:
  serviceName: redis
  replicas: 1  # Scale this for Redis Cluster, adjust config accordingly
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7.0-alpine
        command:
          - redis-server
          - "/etc/redis/redis.conf"
        ports:
        - containerPort: 6379
          name: redis
        volumeMounts:
        - name: data
          mountPath: /data
        - name: config
          mountPath: /etc/redis
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 300m
            memory: 512Mi
        livenessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 30
          timeoutSeconds: 5
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 5
          timeoutSeconds: 5
          periodSeconds: 10
      volumes:
      - name: config
        configMap:
          name: redis-config
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: gp2
      resources:
        requests:
          storage: 5Gi
```

Apply the maninfest:
```
kubectl apply -f redis.yml
```

## Update the Dockerfile
Add Redis environmental variable to the Dockerfile:
```
ENV REDIS_URI redis://localhost:6379/0
ENV REDIS_TTL 3600
```

Rebuild the Docker image:
```
docker image build -t <RESPOSITORY>:redis .
```

Login to ECR:
```
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <RESPOSITORY>
```

Push the image to ECR:
```
docker push <RESPOSITORY>:redis
```

## Update the deployment
Add Redis environmental variable to deployment.yml:
```
- name: REDIS_URI
  value: "redis://redis:6379/0"
- name: REDIS_TTL
  value: "3600"
```

Update the image to use the image tagged with redis:
```
spec:
  containers:
  - name: widget-api
    image: <RESPOSITORY>:redis
```

Apply the maninfest:
```
kubectl apply -f deployment.yml
```