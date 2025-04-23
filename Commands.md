# FastAPI Widget API

A RESTful API for managing widgets with user authentication, built with FastAPI and MongoDB.

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
python3 -m venv venv
source venv/bin/activate
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

Run uvicorn using pm2:
```
pm2 start uvicorn --name fastapi --interpreter python3 -- main:app --host 0.0.0.0 --port 8000
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

# Module 3 Clip 10:
```
aws eks --region us-east-1 update-kubeconfig --name pscluster
```