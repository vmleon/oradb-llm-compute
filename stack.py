#!/usr/bin/env python3

import sys
import json
import chevron
import subprocess
import configparser
import logging
import os
from pathlib import Path

OCI_CONFIG_FILE = '~/.oci/config'
CONFIG_FILE = 'config.json'
TFPLAN_FILE = 'terraform/tfplan'
TFVARS_TEMPLATE = 'terraform/terraform.tfvars.mustache'
TFVARS_OUTPUT = 'terraform/terraform.tfvars'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

def read_oci_config():
    """Read OCI config file and return profiles"""
    oci_config_path = Path(OCI_CONFIG_FILE).expanduser()
    
    if not oci_config_path.exists():
        logging.error(f"OCI config file not found at {oci_config_path}")
        logging.error("Please ensure OCI CLI is configured or create the config file manually")
        sys.exit(1)
    
    config = configparser.ConfigParser()
    config.read(oci_config_path)
    
    return config

def select_profile():
    """Let user select OCI profile and return profile data"""
    config = read_oci_config()
    profiles = list(config.sections())
    
    # If only DEFAULT exists, use it automatically
    if len(profiles) == 1 and profiles[0] == 'DEFAULT':
        logging.info("Using profile: DEFAULT")
        return 'DEFAULT', dict(config['DEFAULT'])
    
    # Show available profiles
    logging.info("Available OCI profiles:")
    for i, profile in enumerate(profiles, 1):
        print(f"  {i}. {profile}")
    
    # Get user selection with DEFAULT as default
    default_choice = profiles.index('DEFAULT') + 1 if 'DEFAULT' in profiles else 1
    choice = input(f"Select profile (default: {default_choice}): ") or str(default_choice)
    
    try:
        selected_profile = profiles[int(choice) - 1]
        logging.info(f"Using profile: {selected_profile}")
        return selected_profile, dict(config[selected_profile])
    except (ValueError, IndexError):
        logging.warning("Invalid selection, using DEFAULT")
        return 'DEFAULT', dict(config['DEFAULT'])

def create_ssh_key():
    """Create SSH key pair and return private key path and public key content"""
    key_name = input("SSH key name (default: llmc): ") or "llmc"
    key_path = Path.home() / ".ssh" / key_name
    public_key_path = Path(f"{key_path}.pub")
    
    # Check for existing keys
    if key_path.exists() or public_key_path.exists():
        logging.warning(f"SSH key already exists at {key_path}")
        choice = input("Overwrite existing key? (y/n, default: n): ") or "n"
        
        if choice.lower() != 'y':
            logging.info("Using existing SSH key")
            # Read existing public key content
            with open(public_key_path, 'r') as f:
                public_key_content = f.read().strip()
            return str(key_path), public_key_content
        else:
            logging.info("Overwriting existing SSH key")
    
    # Ensure .ssh directory exists
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(mode=0o700, exist_ok=True)
    
    # Create SSH key pair
    cmd = [
        "ssh-keygen", 
        "-t", "rsa", 
        "-b", "4096",
        "-f", str(key_path),
        "-N", ""  # No passphrase
    ]
    
    logging.info(f"Creating SSH key pair at {key_path}")
    subprocess.run(cmd, check=True)
    
    # Set correct permissions
    os.chmod(key_path, 0o600)  # Private key: read/write for owner only
    os.chmod(public_key_path, 0o644)  # Public key: read for all, write for owner
    logging.debug(f"Set permissions: {key_path} (600), {public_key_path} (644)")
    
    # Read public key content
    with open(public_key_path, 'r') as f:
        public_key_content = f.read().strip()
    
    return str(key_path), public_key_content

def setup():
    """Create config file with user input"""
    logging.info("Setting up configuration...")
    
    # Select OCI profile and get region/tenancy from it
    profile_name, profile_data = select_profile()
    region_name = profile_data.get('region', 'eu-frankfurt-1')
    tenancy_id = profile_data.get('tenancy')
    
    logging.info(f"Using region: {region_name}")
    logging.info(f"Using tenancy: {tenancy_id}")
    
    compartment_id = input("Compartment OCID: ")
    
    # Create SSH key
    ssh_private_key_path, ssh_public_key = create_ssh_key()
    
    instance_shape = input("Instance shape (default: VM.Standard.E5.Flex): ") or "VM.Standard.E5.Flex"
    
    config = {
        'region_name': region_name,
        'config_file_profile': profile_name,
        'tenancy_id': tenancy_id,
        'compartment_id': compartment_id,
        'ssh_public_key': ssh_public_key,
        'ssh_private_key_path': ssh_private_key_path,
        'instance_shape': instance_shape
    }
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    logging.info(f"Configuration saved to {CONFIG_FILE}")

def tfvars():
    """Generate terraform.tfvars from template using config"""
    logging.info("Generating terraform.tfvars from template...")
    
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    with open(TFVARS_TEMPLATE, 'r') as template_file:
        template = template_file.read()
    
    rendered = chevron.render(template, config)
    
    with open(TFVARS_OUTPUT, 'w') as output_file:
        output_file.write(rendered)
    
    logging.info(f"Generated {TFVARS_OUTPUT} from {TFVARS_TEMPLATE}")

def cleanup():
    """Remove config file and SSH keys"""
    logging.info("Cleaning up configuration and SSH keys...")
    
    # Remove SSH keys
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        private_key_path = Path(config['ssh_private_key_path'])
        public_key_path = Path(f"{config['ssh_private_key_path']}.pub")
        
        if private_key_path.exists():
            private_key_path.unlink()
            logging.info(f"Removed {private_key_path}")
        
        if public_key_path.exists():
            public_key_path.unlink()
            logging.info(f"Removed {public_key_path}")
            
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        logging.warning("Could not find SSH keys to remove (config file missing or invalid)")
    except Exception as e:
        logging.error(f"Error removing SSH keys: {e}")
    
    # Remove tfplan file
    tfplan_path = Path(TFPLAN_FILE)
    if tfplan_path.exists():
        tfplan_path.unlink()
        logging.info(f"Removed {TFPLAN_FILE}")
    else:
        logging.warning(f"{CONFIG_FILE} not found")
    
    # Remove tfplan file
    tfplan_path = Path(TFPLAN_FILE)
    if tfplan_path.exists():
        tfplan_path.unlink()
        logging.info(f"Removed {TFPLAN_FILE}")
    else:
        logging.warning(f"{TFPLAN_FILE} not found")
    
    # Remove tfvars file
    config_path = Path(TFVARS_OUTPUT)
    if config_path.exists():
        config_path.unlink()
        logging.info(f"Removed {TFVARS_OUTPUT}")
    else:
        logging.warning(f"{TFVARS_OUTPUT} not found")

def main():
    if len(sys.argv) != 2:
        logging.error("Usage: python stack.py [setup|tfvars|cleanup]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'setup':
        setup()
    elif command == 'tfvars':
        tfvars()
    elif command == 'cleanup':
        cleanup()
    else:
        logging.error(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()