

# Prepare environment

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

# Test

```
aws --profile cryptoeye ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 292875404443.dkr.ecr.us-west-2.amazonaws.com/cryptoeye
```