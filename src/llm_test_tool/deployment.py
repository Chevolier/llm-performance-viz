"""
Docker deployment module for vLLM servers.
"""

import json
import yaml
import subprocess
import time
import requests
from typing import Dict, Any
from pathlib import Path


class VllmDeployment:
    """Manages vLLM Docker container deployment and lifecycle"""
    
    def __init__(self, config_path: str):
        """Initialize with deployment configuration"""
        self.config_path = Path(config_path)
        
        # Load config file (support both YAML and JSON)
        with open(self.config_path, 'r') as f:
            if self.config_path.suffix.lower() in ['.yaml', '.yml']:
                self.config = yaml.safe_load(f)
            else:
                self.config = json.load(f)
        
        self.deployment_config = self.config['deployment']
        self.container_name = self.deployment_config['container_name']
        self.port = self.deployment_config['port']
    
    def build_docker_command(self) -> list:
        """Build the docker run command from configuration"""
        cmd = [
            'docker', 'run',
            '--gpus', self.deployment_config['gpu_config']['gpus'],
            '-p', f"{self.port}:{self.port}",
            '--name', self.container_name,
            '-d',
            '--shm-size', self.deployment_config['gpu_config']['shm_size']
        ]
        
        # Add volume mounts
        for volume in self.deployment_config['volumes']:
            cmd.extend(['-v', volume])
        
        # Add the image
        cmd.append(self.deployment_config['docker_image'])
        
        # Add model configuration arguments
        model_config = self.deployment_config['model_config']
        cmd.extend([
            '--port', str(self.port),
            '--model', model_config['model'],
            '--gpu-memory-utilization', str(self.deployment_config['gpu_config']['gpu_memory_utilization']),
            '--max-model-len', str(model_config['max_model_len'])
        ])
        
        if model_config.get('trust_remote_code'):
            cmd.append('--trust-remote-code')
        if model_config.get('enable_reasoning'):
            cmd.append('--enable-reasoning')
        if model_config.get('tool_call_parser'):
            cmd.extend(['--tool-call-parser', model_config['tool_call_parser']])
        if model_config.get('reasoning_parser'):
            cmd.extend(['--reasoning-parser', model_config['reasoning_parser']])
        
        return cmd
    
    def is_container_running(self) -> bool:
        """Check if the container is already running"""
        try:
            result = subprocess.run(
                ['docker', 'ps', '--filter', f'name={self.container_name}', '--format', '{{.Names}}'],
                capture_output=True, text=True, check=True
            )
            return self.container_name in result.stdout
        except subprocess.CalledProcessError:
            return False
    
    def stop_container(self) -> bool:
        """Stop and remove existing container"""
        try:
            # Stop the container
            subprocess.run(['docker', 'stop', self.container_name], 
                         capture_output=True, check=True)
            # Remove the container
            subprocess.run(['docker', 'rm', self.container_name], 
                         capture_output=True, check=True)
            print(f"Stopped and removed container: {self.container_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error stopping container: {e}")
            return False
    
    def start_container(self) -> bool:
        """Start the vLLM container"""
        # Stop existing container if running
        if self.is_container_running():
            print(f"Container {self.container_name} is already running. Stopping it first...")
            if not self.stop_container():
                return False
        
        # Build and run the docker command
        cmd = self.build_docker_command()
        print(f"Starting container with command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"Container started successfully: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error starting container: {e}")
            print(f"stderr: {e.stderr}")
            return False
    
    def wait_for_health(self, timeout: int = 300) -> bool:
        """Wait for the server to become healthy"""
        health_url = f"http://localhost:{self.port}/health"
        print(f"Waiting for server to become healthy at {health_url}...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    print("Server is healthy!")
                    return True
            except requests.RequestException:
                pass
            
            print(".", end="", flush=True)
            time.sleep(5)
        
        print(f"\nServer failed to become healthy within {timeout} seconds")
        return False
    
    def deploy(self) -> bool:
        """Deploy the vLLM server and wait for it to be ready"""
        if not self.start_container():
            return False
        
        return self.wait_for_health()
    
    def cleanup(self) -> bool:
        """Clean up the deployment"""
        return self.stop_container()
    
    def get_api_url(self) -> str:
        """Get the API endpoint URL"""
        return f"http://localhost:{self.port}/v1/chat/completions"
    
    def get_model_id(self) -> str:
        """Get the model ID from configuration"""
        return self.deployment_config['model_config']['model']