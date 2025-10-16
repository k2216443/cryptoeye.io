#!/bin/bash
set +e

VENVPATH="../.venv"
TEMPPATH=$(mktemp -d)

# Function to print text in red
red() {
    echo -e "\033[31m[$(date)] $1\033[0m"
}

# Function to echo -e text in green
green() {
    echo -e "\033[32m[$(date)] $1\033[0m"
}

# Function to echo -e text in blue
blue() {
    echo -e "\033[34m[$(date)] $1\033[0m"
}

# Function to echo -e text in yellow
yellow() {
    echo -e "\033[33m[$(date)] $1\033[0m"
}

# Function to echo -e text in cyan
cyan() {
    echo -e "\033[36m[$(date)] $1\033[0m"
}

if [ -f collections ]; then
  yellow "Directory found: collections. Removing"
  rm -f collections
fi

blue "Installing virtual environment: ${VENVPATH}/"
python3 -m venv ${VENVPATH}/

source ${VENVPATH}/bin/activate

blue "Upgrading: pip.."
pip install --upgrade pip &> /dev/null
if [ $? -eq 0 ]; then
  green "Upgraded: pip"
else
  red "Error: pip upgrading error"
  exit 1
fi

blue "Installing: ansible ansible-lint boto3.."
pip install ansible ansible-lint passlib boto3  &> /dev/null
if [ $? -eq 0 ]; then
  green "Installed: ansible ansible-lint boto3"
else
  red "Error: ansible ansible-lint installing error"
  exit 1
fi&> /dev/null
if [ $? -eq 0 ]; then
  green "Installed: ansible ansible-lint boto3"
else
  red "Error: ansible ansible-lint installing error"
  exit 1
fi


if [ -f "requirements.yml" ]; then
  blue "Installing: requirements.yml"
  ansible-galaxy install -r requirements.yml -f &> ${TEMPPATH}/6.log
  if [ $? -eq 0 ]; then
    green "Installed: requirements.yml"
  else
    red "Error: requirements.yml: ${TEMPPATH}/6.log"
    
    exit 1
  fi
fi
