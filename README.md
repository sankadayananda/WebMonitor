# WebMonitor for HTTPD instance
 > WebMonitor is a two part lambda solution where it uses WebMon lambda to monitor the website availability from outside and trigger WebHeal lambda to take corrective actions to restore the website when needed.

### Prerequisites for the Setup
 - Linux server with Python 2.7 or above
 - Python pip to download packages
 - AWS account with full access

### Preparing the Linux Server
```bash
sudo yum install python2-pip.noarch
```

### Create external library packages
 > These external libraries are used by lambda functions. These will be added as lambda layers later in the guide.
 - [WebMon.py](https://github.com/sankadayananda/WebMonitor/blob/master/WebMon.py) --> response
 - [WebHeal.py](https://github.com/sankadayananda/WebMonitor/blob/master/WebHeal.py) --> paramiko

```bash
mkdir -p  ~/layers_requests/python
cd  ~/layers_requests/python
pip install requests -t ./
zip -r ../requests.zip .

mkdir -p  ~/layers_paramiko/python
cd ~/layers_paramiko/python
pip install paramiko -t ./
zip -r ../paramiko.zip .
```
 > Optionally I have made them public via s3 bucket 
 - [https://sankalayers.s3.ap-south-1.amazonaws.com/requests.zip](https://sankalayers.s3.ap-south-1.amazonaws.com/requests.zip)
 - [https://sankalayers.s3.ap-south-1.amazonaws.com/paramiko.zip](https://sankalayers.s3.ap-south-1.amazonaws.com/paramiko.zip)

### Create Layers for Lambda
 > Creating package dependancies as layers in Lambda makes it easier to sperate user code from libraries. These layers are reusable and can be called by any lambda function withing the reigon.
 > Additionally this makes the deployment packages light weight since it only contains the user code.
 > Console --> Lambda --> Layers --> Create layer
 > Creating requests Lambda Layer
 - [Add Requests Layer](https://webmon-images.s3.ap-south-1.amazonaws.com/layers_requests.PNG)
 > Creating paramiko  Lambda Layer
 - [Add Paramiko Layer](https://webmon-images.s3.ap-south-1.amazonaws.com/layers_paramiko.PNG)
 > Once both layers are added you'll have a simillar sort of a view in your console
 - [Layer view](https://webmon-images.s3.ap-south-1.amazonaws.com/layers_view.PNG)

### Configure the IAM Role for WebMon Lambda
 > Two IAM roles need to be created in order to run the both lambda functions.
 > Create a role named WebMonRole which has **AWSLambdaBasicExecutionRole** & **AWSLambdaRole** policies attached to it.
[WebMonRole Policy View](https://webmon-images.s3.ap-south-1.amazonaws.com/WebMon_IAM_Role.PNG)
 - AWSLambdaBasicExecutionRole Role json
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
```
 - AWSLambdaRole Role json
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}
```
 > If you know your way around IAM policies you could give permissions to exact ARN's. This way you can prevent this role from having unwanted permissions.

### Configure the IAM Role for WebHeal Lambda


### Configure WebMon Lambda
 > Create a Lambda function named WebMon with runtime environment python 2.7 as shown on the below image. Attach the previously created WebMonRole as the execution role.
[Step 1](https://webmon-images.s3.ap-south-1.amazonaws.com/WebMon_Lambda_Create_1.PNG)

[Step 2](https://webmon-images.s3.ap-south-1.amazonaws.com/WebMon_Lambda_Create_2.PNG) 

### tree view
```bash
.
├── README.md
├── WebHeal.py
└── WebMon.py
```

