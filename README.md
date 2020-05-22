# WebMonitor
 > WebMonitor is a two part lambda solution where it uses WebMon lambda to monitor the website availability from outside and trigger WebHeal lambda to take corrective actions to restore the website when needed.
 > The WebMon lambda uses python response library to monitor Web site availability. A private s3 bucket is used to store the ec2 instance public keys.
 > The WebHeal lambda uses python paramiko library along with the s3 stored public keys to access the ec2 instance.  

### Architecture Diagram
![Architecture](https://webmon-images.s3.ap-south-1.amazonaws.com/WebMoitor_Diagram.png)

### Notes
 > This is not a fully fledged application that is capable of handling all Web Site errors.

### AWS services used
 - AWS Lambda
 - AWS S3 Storage
 - CloudWatch Service
 - AWS IAM

### Prerequisites for the Setup
These prerequisites are only required to create the "requests" & "paramiko" package bundles.
 - Linux server with Python 2.7 or above
 - python pip to download packages

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
 > Optionally I have made them public via s3 bucket. The below links could be directly pasted when adding layers.
 - [https://sankalayers.s3.ap-south-1.amazonaws.com/requests.zip](https://sankalayers.s3.ap-south-1.amazonaws.com/requests.zip)
 - [https://sankalayers.s3.ap-south-1.amazonaws.com/paramiko.zip](https://sankalayers.s3.ap-south-1.amazonaws.com/paramiko.zip)

### Create Layers for Lambda
 > Creating package dependencies as layers in lambda makes it easier to separate user code from libraries.These layers are reusable and can be called by any lambda function withing the region.
 > Additionally this makes the deployment packages light weight since it only contains the user code.
 > Console --> Lambda --> Layers --> Create layer
 > Creating requests lambda Layer - [Add Requests Layer](https://webmon-images.s3.ap-south-1.amazonaws.com/layers_requests.PNG)
 > Creating paramiko  lambda Layer - [Add Paramiko Layer](https://webmon-images.s3.ap-south-1.amazonaws.com/layers_paramiko.PNG)
 > Once both layers are added you'll have a simillar sort of a view in your console - [Layer view](https://webmon-images.s3.ap-south-1.amazonaws.com/layers_view.PNG)

### Configure the IAM Role for WebMon Lambda
 > Two IAM roles need to be created in order to run the both lambda functions.
 > Create a role named WebMonRole which has **AWSLambdaBasicExecutionRole** & **AWSLambdaRole** policies attached to it.
 > [WebMonRole Policy View](https://webmon-images.s3.ap-south-1.amazonaws.com/WebMon_IAM_Role.PNG)

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
 > Create a role named WebHealRole which has **AWSLambdaBasicExecutionRole** & **AmazonS3ReadOnlyAccess** policies attached to it.
 > [WebHealRole Policy View](https://webmon-images.s3.ap-south-1.amazonaws.com/WebHeal_IAM_Role.PNG)
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
 - AmazonS3ReadOnlyAccess Role json
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:Get*",
                "s3:List*"
            ],
            "Resource": "*"
        }
    ]
}
```
### Configure WebMon Lambda
 > Create a Lambda function named WebMon with runtime environment python 2.7 as shown in the below image. Attach the previously created WebMonRole as the execution role.
 > [Step 1](https://webmon-images.s3.ap-south-1.amazonaws.com/WebMon_Lambda_Create_1.PNG)
 > The lambda function handler info need to updated with the python script name and trigger function name of lambda. In our example it's "WebMon.trigger_handler".
 > [Step 2](https://webmon-images.s3.ap-south-1.amazonaws.com/WebMon_Lambda_Create_2.PNG)
 > Now we need to add the previously added "requests" layer to the function. You can do it in the following manner
 - In the designer view click on Layers box - [select layers](https://webmon-images.s3.ap-south-1.amazonaws.com/WebMon_requests_layer1.PNG)
 - Click on Add a layer button to get the view - [add layer to function](https://webmon-images.s3.ap-south-1.amazonaws.com/WebMon_requests_layer2.PNG)
 - Once finished it'll show the layer count as (1) - [function view](https://webmon-images.s3.ap-south-1.amazonaws.com/WebMon_requests_layer3.PNG)
 > Add the required environment variables as shown in the below screen captures
 - keydir --> s3 bucket name that holds the public key file.(Ex: - keyfiledir )Need to make sure this is a private bucket since it holds the ec2 instance key
 - keyfile  --> name of the keyfile to connect to ec2 instance.(Ex: - server1.pem)
 - server_ip --> ec2 instance IP
 - luser --> ec2 instance login name(This user need to have sudo permissions to execute privileged commands)
 - server_reigon --> ec2 instance region
 - url --> Server health monitor url
 - worker_lambda --> lambda to call when the above mentioned url is not accessible.In our example it's WebHeal
 > Once added you will see a similar view as shown below
 > [Environment Variables](https://webmon-images.s3.ap-south-1.amazonaws.com/WebMon_Environment.PNG)
 > Once all set change the execution timeout value higher than 5s
 > [Change Execution Timeout](https://webmon-images.s3.ap-south-1.amazonaws.com/WebMon_Execution_time.PNG)

### Configure WebHeal Lambda
 > Create a lambda function named WebHeal with runtime environment python 2.7 as shown on the below image. Attach the previously created WebHealRole as the execution role.
 > [Step 1](https://webmon-images.s3.ap-south-1.amazonaws.com/WebHeal_Lambda_Create_1.PNG)
 > The lambda function handler info need to updated with the python script name and trigger function name of lambda. In our example it's "WebHeal.rexec_handler".
 > [Step 2](https://webmon-images.s3.ap-south-1.amazonaws.com/WebHeal_Lambda_Create_2.PNG)
 > Now we need to add the previously added "paramiko" layer to the function. You can follow same steps we did for the "requests" in the previous topic.
 > Once all set change the execution timeout value higher than 60s
 > [Change Execution Timeout](https://webmon-images.s3.ap-south-1.amazonaws.com/WebHeal_Execution_time.PNG)

### Configure tests for Lambda
 > It is highly recommended to test each lambda individually before running a integrated test.Once both individual and integrated tests are completed we can schedule the WebMon lambda via CloudWatch events.Testing for lambda can be configured in the following manner.
 > Inside the lambda in-between Actions and Tests buttons there's a drop down list. In that list select Configure test events.
 > Once inside, configure and run the tests in the following manner.
 - Configure WebMon lambda tests --> [WebMon Test Configure](https://webmon-images.s3.ap-south-1.amazonaws.com/WebMon_Test_Configure.PNG)
 - WebMon lambda test output --> [WebMon Test Output](https://webmon-images.s3.ap-south-1.amazonaws.com/WebMon_Test_Out.PNG)
 - Configure WebHeal lambda tests --> [WebHeal Test Configure](https://webmon-images.s3.ap-south-1.amazonaws.com/WebHeal_Test_Configure.PNG)
 - WebHeal lambda test output --> [WebHeal Test Output](https://webmon-images.s3.ap-south-1.amazonaws.com/WebHeal_Test_Out.PNG)
 > For the integrated testing to happen the httpd service need to be shutdown temporary and run the WebMon lambda test.Once the WebMon identifies the website is down, it will trigger the WebHeal lambda to start the httpd service.
 - [Integrated Test Output](https://webmon-images.s3.ap-south-1.amazonaws.com/WebMonitor_integrated_test.PNG)
 > The two lambda functions will create logs under CloudWatch log groups
 - [CloudWatch Log Groups View](https://webmon-images.s3.ap-south-1.amazonaws.com/WebMonitor_CloudWatch_Log_Groups.PNG)
 > The WebHeal lambda output can be seen via CloudWatch log groups
 - [CloudWatch WebHeal Output](https://webmon-images.s3.ap-south-1.amazonaws.com/WebMonitor_CloudWatch_WebHeal_Log.PNG)

### Schedule WebMon Lambda via CloudWatch
 > Final Stage of this excersie is to periodically execute the WebMon lambda. This could be done via CloudWatch Events.
 > Go To lambda -> Functions -> WebMon -> [Add trigger] Button
 > Inside the trigger configuration select "CloudWatch Events/EventBridge" as the trigger source and create a new rule with a trigger frequency. In the current example it's set as 5 minutes.
 > [Trigger Configuration](https://webmon-images.s3.ap-south-1.amazonaws.com/WebMon_Schedule.PNG)
 > Once trigger is in place the WebMon lambda will look like this [WebMon View](https://webmon-images.s3.ap-south-1.amazonaws.com/WebMon_Trigger_View.PNG)  

### Tree view
```bash
.
├── README.md
├── WebHeal.py
└── WebMon.py
```

