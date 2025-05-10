# FastAPI Widget API

A RESTful API for managing widgets with user authentication, built with FastAPI and MongoDB.

# Module 3 Clip 2: Deploying to Production
##
Setting up the environment variables:
```
export MONGO_URI=mongodb://<MONGODB_URI>:27017
export MONGO_DB_NAME=widget_db
export SECRET_KEY="IdF5aErU&FcW6bl5$zO"
export ALGORITHM=HS256
export ACCESS_TOKEN_EXPIRE_MINUTES=30
export CORS_ALLOW_ORIGINS=http://localhost,http://localhost:3000,https://yourdomain.com
export RATE_LIMIT_ANON_REQUESTS=30
export RATE_LIMIT_AUTH_REQUESTS=100
export RATE_LIMIT_WINDOW_SECONDS=60
```

# Module 3 Clip 3: Deploying to Production
## Create a release in GitHub
Create the tag:
```
git tag <TAGNAME>
```

Push the tag to GitHub:
```
git push origin <TAGNAME>
```

## Deployint to Prod:
Setup:
```
sudo apt update
sudo apt upgrade -y
sudo apt install unzip -y
cd /opt
```

Download the app:
```
wget https://github.com/rivethead42/fastapi-securing-deploying-scaling-applications/archive/refs/tags/<TAG>.zip .
unzip <FILE>.zip
mv fastapi-securing-deploying-scaling-applications-test app
cd app
```

Create a virtual environment:
```
apt install python3.12-venv -y
python3 -m venv prod
source prod/bin/activate
```

Install dependencies:
```
pip install -r requirements.txt
```

## Running the app:
Install Node.JS:
```
curl -sL https://deb.nodesource.com/setup_22.x -o nodesource_setup.sh
sudo apt update
sudo apt upgrade -y
sudo apt install -y nodejs npm
```

Install pm2:
```
npm install pm2 -g
```
Create a .env file:
```
# MongoDB connection string
MONGO_URI=mongodb://<IP_ADDRESS>:27017

# Security - Generate a secure key in production
SECRET_KEY=IdF5aErU&FcW6bl5$zO

# API settings
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS settings
# Comma-separated list of allowed origins
CORS_ALLOW_ORIGINS=http://localhost,http://localhost:3000,https://yourdomain.com

# Rate limiting settings
# Number of requests per window for anonymous users
RATE_LIMIT_ANON_REQUESTS=30
# Number of requests per window for authenticated users
RATE_LIMIT_AUTH_REQUESTS=100
# Window size in seconds
RATE_LIMIT_WINDOW_SECONDS=60
```

Create a SSL Certificate:
```
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem -out cert.pem
```

Run uvicorn using pm2:
```
pm2 start uvicorn --name fastapi --interpreter python3 -- main:app --host 0.0.0.0 --port 8000 --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

## Setting up an Nginx proxy
Install Nginx:
```
sudo apt update
sudo apt install nginx -y
```

Edit default:
```
server {
  listen 80;

  server_name <IP_ADDRESS <DOMAIN_NAME>;

  location / {
    proxy_pass http://localhost:8000;
  }
}
```

Restart Nginx
```
sudo service nginx restart
```

# Module 3 Clip 5: Dockerizing FastAPI

## Building the Docker Image
Build the image:
```
docker image build -t <IMAGE_NAME> .
```

Test the image:
```
docker run -d -p 8000:8000 --env-file .env <IMAGE_NAME>
```

Push the image to AWS:
```
docker image push <IMAGE_NAME>:latest
```

# Module 3 Clip 7: Setting up Eksctl

## Install EksClt:
```
choco install eksctl
```
[EksCtl Install Docs](https://eksctl.io/installation/)

## Install AWS CLI on Windows:
```
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
```
[AWS CLI Install Docs](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

## AWS Policies Setup
Create a user group called eks-group witht the following policies:
```
AmazonEC2FullAccess
IAMFullAccess
AWSCloudFormationFullAccess
```

Create an inline policy called eks-policy:
```
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "Statement1",
			"Effect": "Allow",
			"Action": "eks:*",
			"Resource": "*"
		},
        {
            "Action": [
                "ssm:GetParamater",
                "ssm:GetParamaters"
            ],
            "Resource": "*",
            "Effect": "Allow"
        }
	]
}
```

# Module 3 Clip 8: Deploying EKS
## Create the EKS cluster
Configure the AWS credicials:
```
aws configure
```

Deploy the EKS Cluster:
```
eksctl create cluster --name pscluster --nodes-min=3 --nodes-max=4 --instance-selector-vcpus=2 --instance-selector-memory=4 --version=1.32
```
## Create ECR polocy
Setup IAM ecr-policy:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:BatchCheckLayerAvailability",
                "ecr:BatchGetImage",
                "ecr:GetDownloadUrlForLayer",
                "ecr:GetAuthorizationToken"
            ],
            "Resource": "*"
        }
    ]
}
```
## Remove the cluster
Deleting the EKS Cluster:
```
eksctl delete cluster --name pscluster
```

# Module 3 Clip 9: Setting Up ECR:
Create an ECR repository:
Add the following policy:
```
AmazonEC2ContainerRegistryFullAccess
```

Create repository:
```
aws ecr create-repository --repository-name <RESPOSITORY> --region us-east-1
```

Build the image to be pushed to ECR:
```
docker image build -t <RESPOSITORY>:latest .
```

Login to ECR:
```
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <RESPOSITORY>
```

Push the image to ECR:
```
docker push <RESPOSITORY>:latest
```

# Module 3 Clip 10: Setting Up Storage
Install Kubectl:
```
https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/
```
Setup kubeconfig:
```
aws eks --region us-east-1 update-kubeconfig --name pscluster
```

Setup IAM OIDC provider for a cluster to enable IAM roles for pods:
```
eksctl utils associate-iam-oidc-provider --cluster pscluster --approve
```

Create an iamserviceaccount - AWS IAM role bound to a Kubernetes service account
```
eksctl create iamserviceaccount \
    --name ebs-csi-controller-sa \
    --namespace kube-system \
    --cluster pscluster \
    --role-name AmazonEKS_EBS_CSI_DriverRole \
    --role-only \
    --attach-policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy \
    --approve
```

Create ebs cli driver:
```
eksctl create addon \
    --name aws-ebs-csi-driver \
    --cluster pscluster \
    --service-account-role-arn <ARN> --force
```

Create a mongodb.yml:
```
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mongodb-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: gp2
  resources:
    requests:
      storage: 10Gi
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongodb
  labels:
    app: mongodb
spec:
  serviceName: mongodb
  replicas: 1
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:6
        ports:
        - containerPort: 27017
        volumeMounts:
        - name: mongodb-data
          mountPath: /data/db
        resources:
          requests:
            cpu: 200m
            memory: 512Mi
          limits:
            cpu: 500m
            memory: 1Gi
      volumes:
      - name: mongodb-data
        persistentVolumeClaim:
          claimName: mongodb-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: mongodb
  labels:
    app: mongodb
spec:
  ports:
  - port: 27017
    targetPort: 27017
    protocol: TCP
    name: mongodb
  selector:
    app: mongodb
  clusterIP: None
```

Apply the manifest:
```
kubectl apply -f mongodb.yml
```

List all pods:
```
kubectl get pods
```

# Module 3 Clip 11: Deploy FastAPI to EKS

Create deployment.yml
```
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: widget-api
  labels:
    app: widget-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: widget-api
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: widget-api
    spec:
      containers:
      - name: widget-api
        image: <RESPOSITORY>
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
        env:
        - name: MONGO_URI
          value: "mongodb://mongodb:27017"
        - name: SECRET_KEY
          value: Y2hhbmdlLXRoaXMtaW4tcHJvZHVjdGlvbg==
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 20
```

Apply the manifest:
```
kubectl apply -f mongodb.yml
```

List all pods:
```
kubectl get pods
```
# Module 3 Clip 12: Working with Sensitive Data
Enode the secret:
```
echo -n "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0" | base64
```

Create secret.yml
```
apiVersion: v1
kind: Secret
metadata:
  name: widget-api-secrets
type: Opaque
data:
  # Replace with actual values using: echo -n "your-secret-key" | base64
  secret-key: <ENCODED_VALUE>
```

Update deployment.yml:
```
 - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: widget-api-secrets
              key: secret-key
```