# FastAPI Widget API

A RESTful API for managing widgets with user authentication, built with FastAPI and MongoDB.

#Module 3 Clip 1

##Install EksClt:
```
choco install eksctl
```
[EksCtl Install Docs](https://eksctl.io/installation/)

##Install AWS CLI on Windows:
```
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
```
[AWS CLI Install Docs](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

##AWS Policies Setup
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