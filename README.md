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

## Oracle Cloud Deployment

```bash
python -m venv venv
```

```bash
source ./venv/bin/activate
```

```bash
pip install -r requirements.txt
```

```bash
python stack.py setup
```

```bash
python stack.py tfvars
```

```bash
cd terraform
```

```bash
terraform init
```

```bash
terraform plan -out=tfplan
```

```bash
terraform apply -auto-approve tfplan
```

```bash
cd ..
```

## Clean Up

```bash
cd terraform
```

```bash
terraform destroy
```

```bash
cd ..
```

```bash
python stack.py cleanup
```

## Local Deployment

Follow the steps in [LOCAL.md](./LOCAL.md)
