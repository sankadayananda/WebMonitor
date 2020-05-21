# WebMonitor for HTTPD instance
WebMonitor is a two part solution where it uses WebMon lambda to monitor the website availability from outside and triggers WebHeal lambda to take corrective actions to restore the website.

### Prerequisites for the Setup
--------------------------------
 - Linux server with Python 2.7 or above
 - Python pip to download packages
 - AWS account with full access

### Preparing the Linux Server
```bash
sudo yum install python2-pip.noarch
```
### Create external library packages
These external libraries are used by lambda functions. These will be added as lambda layers later in the guide.
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
Optionally I have made them public via s3 bucket 
 - [https://sankalayers.s3.ap-south-1.amazonaws.com/requests.zip](https://sankalayers.s3.ap-south-1.amazonaws.com/requests.zip)
 - [https://sankalayers.s3.ap-south-1.amazonaws.com/paramiko.zip](https://sankalayers.s3.ap-south-1.amazonaws.com/paramiko.zip)

### Create Layers for Lambda

Creating requests Lambda Layer
[Add Requests Layer](https://webmon-images.s3.ap-south-1.amazonaws.com/layers_requests.PNG)
Creating paramiko  Lambda Layer
[Add Paramiko Layer](https://webmon-images.s3.ap-south-1.amazonaws.com/layers_paramiko.PNG)
Once both layers are added you'll have a simillar sort of a view in your console
[Layer view](https://webmon-images.s3.ap-south-1.amazonaws.com/layers_view.PNG)

### Configure the IAM Roles

### Configure the WebMon lambda
 - Create a WebMon role with basic access to CloudWatch. This role will be used during creation of WebMon Lambda
 - Role Policy JSON {}
```bash
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

### tree view
```bash
.
├── README.md
├── WebHeal.py
└── WebMon.py
```

