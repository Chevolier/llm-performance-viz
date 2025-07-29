#!/bin/bash

# Simple batch testing script for vLLM model configurations
# Runs tests for each model config with organized output directories

set -e

# Function to run test for a specific config
run_test() {
    local config_path="$1"
    # local model_name="$2"
    
    # Extract vllm version and instance type from path
    local vllm_version=$(echo "$config_path" | cut -d'/' -f2)
    local instance_type=$(echo "$config_path" | cut -d'/' -f3)
    local model_name=$(echo "$config_path" | cut -d'/' -f4)
    
    # Strip .yaml suffix from model name
    model_name="${model_name%.yaml}"
    
    # Generate output directory in your format
    local output_dir="archive_results/${vllm_version}--${instance_type}--${model_name}"
    
    echo "=========================================="
    echo "Testing: $model_name"
    echo "Config: $config_path"
    echo "Output: $output_dir"
    echo "=========================================="
    # exit
    # Run the test
    uv run run_auto_test.py --config "$config_path" --output-dir "$output_dir" # --skip-deployment
    
    echo "✓ Completed: $model_name"
    echo ""
}

# Create output directory
mkdir -p archive_results

# Run tests for each model configuration
echo "Starting batch tests for vLLM model configurations..."
echo ""

# Test Qwen3-30B-A3B-FP8
# if [ -f "model_configs/vllm-v0.9.2/g6e.4xlarge/Qwen3-30B-A3B-FP8.yaml" ]; then
#     run_test "model_configs/vllm-v0.9.2/g6e.4xlarge/Qwen3-30B-A3B-FP8.yaml" "Qwen3-30B-A3B-FP8"
# fi

# Test Qwen3-14B-FP8


# Add more model tests here as needed
# run_test "model_configs/vllm-v0.9.2/g6e.4xlarge/NewModel.yaml"

# run_test "model_configs/vllm-v0.9.2/g6e.4xlarge/Qwen3-14B-FP8.yaml" "Qwen3-14B-FP8"
# run_test "model_configs/vllm-v0.9.2/g6e.4xlarge/Qwen3-4B-FP8.yaml" "Qwen3-4B-FP8"
# run_test "model_configs/vllm-v0.9.2/g6e.4xlarge/Qwen3-8B-FP8.yaml" "Qwen3-8B-FP8"
# run_test "model_configs/vllm-v0.9.2/g6e.4xlarge/Qwen3-32B-FP8.yaml" "Qwen3-32B-FP8"
# run_test "model_configs/vllm-v0.9.2/p5en.48xlarge/DeepSeek-R1-0528.yaml" "DeepSeek-R1-0528-default"

# run_test "model_configs/vllm-v0.9.2/p5en.48xlarge/DeepSeek-R1-0528.yaml" "DeepSeek-R1-0528-mtp"
# run_test "model_configs/v0.4.9.post4-cu126/p5en.48xlarge/DeepSeek-R1-0528.yaml" "DeepSeek-R1-0528-mtp-compile"

# run_test "model_configs/sglang-v0.4.9.post4-cu126/p5en.48xlarge/DeepSeek-R1-0528-mtp-compile.yaml"
run_test "model_configs/sglang-v0.4.9.post4-cu126/p5en.48xlarge/DeepSeek-R1-0528-mtp.yaml"
run_test "model_configs/sglang-v0.4.9.post4-cu126/p5en.48xlarge/DeepSeek-R1-0528.yaml"




echo "=========================================="
echo "All tests completed!"
echo "Results saved in archive_results/"
echo "=========================================="