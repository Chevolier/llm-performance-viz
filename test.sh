#!/bin/bash

# Wait for 10 minutes (600 seconds)
echo "Waiting for 10 minutes before running the command..."
echo "Start time: $(date)"

sleep 600

echo "10 minutes elapsed. Running command now..."
echo "Current time: $(date)"

# Run the command
uv run run_auto_test.py --config model_configs/vllm-0.10.1+gptoss/p5en.48xlarge/gpt-oss-120b-tp8.yaml --skip-deployment

echo "Command completed at: $(date)"