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

Create redis.yml:
```
apiVersion: v1
kind: ConfigMap
metadata:
  name: redis-cluster-config
data:
  redis.conf: |
    cluster-enabled yes
    cluster-config-file nodes.conf
    cluster-node-timeout 5000
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
  name: redis-cluster
  labels:
    app: redis-cluster
spec:
  ports:
  - port: 6379
    targetPort: 6379
    name: client
  - port: 16379
    targetPort: 16379
    name: gossip
  clusterIP: None
  selector:
    app: redis-cluster
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-cluster
spec:
  serviceName: redis-cluster
  replicas: 6  # For a minimal Redis Cluster, we need at least 6 nodes (3 masters, 3 slaves)
  selector:
    matchLabels:
      app: redis-cluster
  template:
    metadata:
      labels:
        app: redis-cluster
    spec:
      terminationGracePeriodSeconds: 30
      containers:
      - name: redis
        image: redis:7.0-alpine
        command:
          - redis-server
          - "/etc/redis/redis.conf"
        ports:
        - containerPort: 6379
          name: client
        - containerPort: 16379
          name: gossip
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
          name: redis-cluster-config
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: gp2
      resources:
        requests:
          storage: 5Gi
---
apiVersion: batch/v1
kind: Job
metadata:
  name: redis-cluster-init
  annotations:
    "helm.sh/hook": post-install
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  backoffLimit: 5
  template:
    spec:
      containers:
      - name: cluster-init
        image: redis:7.0-alpine
        command:
        - sh
        - -c
        - |
          # Wait for all Redis pods to be ready
          echo "Waiting for Redis pods to be ready..."
          for i in $(seq 0 5); do
            until redis-cli -h redis-cluster-$i.redis-cluster ping; do
              echo "Waiting for redis-cluster-$i.redis-cluster to be ready..."
              sleep 2
            done
          done
          
          # Create the cluster
          echo "Creating Redis Cluster..."
          echo yes | redis-cli --cluster create \
            redis-cluster-0.redis-cluster:6379 \
            redis-cluster-1.redis-cluster:6379 \
            redis-cluster-2.redis-cluster:6379 \
            redis-cluster-3.redis-cluster:6379 \
            redis-cluster-4.redis-cluster:6379 \
            redis-cluster-5.redis-cluster:6379 \
            --cluster-replicas 1
          
          echo "Redis Cluster initialized successfully!"
      restartPolicy: OnFailure
```

Apply the maninfest:
```
kubectl apply -f redis.yml
```

```
- name: REDIS_URI
          value: "redis://redis:6379/0"
        - name: REDIS_TTL
          value: "3600"
```