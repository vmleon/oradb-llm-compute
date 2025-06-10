# AI Models on Compute

## Introduction

This solution helps organizations test and deploy Large Language Models (LLMs) while maintaining complete control over their data and infrastructure. Instead of relying on external AI services, you can run AI models entirely within your own environment.

### Key Benefits

- Keep sensitive data within your infrastructure
- Test different AI models without vendor lock-in
- Full control over model selection and configuration
- Works across cloud, on-premises, and hybrid environments

### Technical Implementation

The platform deploys configurable compute instances (CPU or GPU) for LLM inference testing on **Oracle Cloud Infrastructure**, **on-premises** environments, or **Oracle Cloud@Customer (C3)**.

Deployment uses Terraform for Oracle Cloud and you can run the script [bootstrap.tftpl](./terraform/userdata/bootstrap.tftpl) for on-premises provisioning.

The solution currently implements [Ollama](https://ollama.com/) server as the inference engine, with straightforward adaptation paths for [vLLM](https://docs.vllm.ai/en/latest/) or [llama.cpp](https://github.com/ggml-org/llama.cpp).

This is a single-node foundation designed for testing and development. Production scaling with load balancers and multi-node clusters can be added based on specific workload requirements.

## Work In Progress

Pending items:

- GPU support: for now only CPU support

## Oracle Cloud Deployment

### Prerequisites

- Oracle Cloud account with appropriate permissions
- Oracle Cloud CLI tool installed and configured
- Python 3 installed
- Terraform installed

### Setup Steps

1. Create Python virtual environment (only the first time)

   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment

   ```bash
   source ./venv/bin/activate
   ```

3. Install required Python dependencies

   ```bash
   pip install -r requirements.txt
   ```

4. Generate Oracle Cloud configuration files

   ```bash
   python stack.py setup
   ```

   _This creates the necessary config files like SSH keys and config.json_

5. Generate Terraform variables file

   ```bash
   python stack.py tfvars
   ```

   _Creates terraform.tfvars with your specific Oracle Cloud settings_

6. Navigate to Terraform directory

   ```bash
   cd terraform
   ```

7. Initialize Terraform

   ```bash
   terraform init
   ```

   _Downloads required providers and modules_

8. Review deployment plan

   ```bash
   terraform plan -out=tfplan
   ```

   _Shows what resources will be created - review before applying_

9. Deploy infrastructure

   ```bash
   terraform apply -auto-approve tfplan
   ```

   _Creates the compute instance and networking resources_

10. Return to project root
    ```bash
    cd ..
    ```

After deployment completes, note the public IP address from the Terraform output.

## Running the Client

Once your infrastructure is deployed:

1. Navigate to client directory

   ```bash
   cd client
   ```

2. Activate the Python environment (only the first time)

   ```bash
   python -m venv venv
   ```

3. Activate the Python environment

   ```bash
    source ./venv/bin/activate
   ```

4. Connect to your deployed Ollama server
   ```bash
   python client.py -u "http://PUBLIC_IP:11434/"
   ```
   _Replace PUBLIC_IP with the actual IP from your Terraform output_

## Clean Up

To avoid ongoing charges, destroy the infrastructure when finished:

1. Move to terraform folder

   ```bash
   cd terraform
   ```

2. Remove Oracle Cloud resources

   ```bash
   terraform destroy
   ```

3. Return to project root

   ```bash
   cd ..
   ```

4. Clean up local configuration files
   ```bash
   python stack.py cleanup
   ```

## Local Deployment

Follow the steps in [LOCAL.md](./LOCAL.md)
