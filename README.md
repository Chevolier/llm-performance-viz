# LLM Test Tool

A comprehensive tool for testing LLM API performance with automated deployment and extensive test matrices.

## Features

- Test LLM API performance with multiple parallel processes
- Automated vLLM Docker deployment and management
- Comprehensive test matrix with configurable input/output tokens and concurrency levels
- Measure first token latency, end-to-end latency, and output tokens per second
- Generate detailed statistical reports with percentiles (p25, p50, p75, p90)
- Support for prompt caching optimization with fixed and random prompt parts
- Token usage tracking and analysis
- Automated warmup and cooldown between test cases

## Installation

Using uv:

```bash
uv pip install -e .
```

## Usage

### Manual Testing

```bash
llm-test --processes 4 --requests 10 --model_id "Qwen/Qwen3-30B-A3B-FP8" --input_tokens 20 --random_tokens 5 --output_tokens 100 --url "http://localhost:8080/v1/chat/completions"
```

### Automated Testing with Docker Deployment

The tool now supports automated testing with Docker deployment management:

```bash
# Basic usage
python run_auto_test.py --config model_configs/vllm-v0.9.2/g6e.4xlarge/config.yaml

# With custom output directory
python run_auto_test.py --config config.yaml --output-dir my_results

# Dry run to see what tests would be executed
python run_auto_test.py --config config.yaml --dry-run

# Verbose output for debugging
python run_auto_test.py --config config.yaml --verbose

# Force rerun all tests (ignore existing results)
python run_auto_test.py --config config.yaml --force-rerun
```

Or using the module directly:

```bash
python -m llm_test_tool auto-test --config model_configs/vllm-v0.9.2/g6e.4xlarge/config.yaml --output-dir test_results
```

### Deployment Only (No Benchmarking)

For cases where you only want to deploy a server without running benchmarks:

```bash
# Deploy a server
python deploy_server.py --config model_configs/vllm-v0.9.2/g6e.4xlarge/Qwen3-30B-A3B-FP8.yaml

# Show the Docker command without executing
python deploy_server.py --config config.yaml --show-command

# Deploy without health check
python deploy_server.py --config config.yaml --no-health-check

# Check deployment status
python deploy_server.py --config config.yaml --status

# Stop a deployment
python deploy_server.py --config config.yaml --stop
```

Or using the module directly:

```bash
python -m llm_test_tool deploy --config config.yaml
```

### Parameters

- `--processes`: Number of parallel processes (default: 2)
- `--requests`: Number of requests per process (default: 5)
- `--model_id`: Model ID to test (default: "gpt-3.5-turbo")
- `--input_tokens`: Total approximate input token length (default: 10)
- `--random_tokens`: Number of random tokens to add to the prompt (default: 2)
- `--output_tokens`: Maximum output tokens to generate (default: 50)
- `--url`: API endpoint URL (default: "http://localhost:8080/v1/chat/completions")
- `--output`: Results output file (default: "test_results.json")

## Example Output

```
Starting LLM API test:
- Processes: 4
- Requests per process: 10
- Total requests: 40
- Model ID: Qwen/Qwen3-30B-A3B-FP8
- Total input tokens: 20
- Random tokens: 5
- Output tokens: 100
- API endpoint: http://localhost:8080/v1/chat/completions
--------------------------------------------------

Test completed!
Total duration: 12.45 seconds
Success rate: 100.00%
Throughput: 3.21 requests/second

First Token Latency (seconds):
- Min: 0.4521
- Max: 0.8976
- Mean: 0.6234

Percentiles:
- p25: 0.5123
- p50: 0.5987
- p75: 0.7234
- p90: 0.8456

End-to-End Latency (seconds):
- Min: 1.2345
- Max: 2.3456
- Mean: 1.7890

Percentiles:
- p25: 1.4567
- p50: 1.6789
- p75: 2.0123
- p90: 2.2345

Token Usage Statistics:

Prompt Tokens:
- Min: 18
- Max: 22
- Mean: 20.15

Percentiles:
- p25: 19
- p50: 20
- p75: 21
- p90: 22

Completion Tokens:
- Min: 95
- Max: 105
- Mean: 99.8

Percentiles:
- p25: 97
- p50: 100
- p75: 102
- p90: 104

Output Tokens Per Second:
- Min: 45.23
- Max: 78.91
- Mean: 62.45

Percentiles:
- p25: 55.67
- p50: 61.23
- p75: 68.89
- p90: 74.56

Detailed results saved to: test_results.json
```
## Co
nfiguration

### Deployment Configuration

The automated testing uses a YAML configuration file with a universal parameter system that supports any Docker and application arguments:

```yaml
deployment:
  docker_image: "vllm/vllm-openai:v0.9.2"
  container_name: "vllm-qwen3-30b"
  port: 8080
  
  # Optional: Custom command to run inside container (for non-vLLM servers)
  # command: "python3 -m sglang.launch_server"  # String format
  # command: ["python3", "-m", "sglang.launch_server"]  # List format
  
  # Universal Docker parameters - any Docker run parameter
  docker_params:
    gpus: "all"
    shm-size: "747g"
    ipc: "host"
    volume:
      - "/efs/200005/.cache/huggingface/hub:/root/.cache/huggingface/hub"
    environment:
      CUDA_VISIBLE_DEVICES: "0,1,2,3"
    # Any other Docker parameter: memory, cpus, ulimit, etc.
  
  # Universal application arguments - any server argument
  app_args:
    model: "Qwen/Qwen3-30B-A3B-FP8"  # or model-path for SGLang
    gpu-memory-utilization: 0.95
    max-model-len: 16384
    trust-remote-code: true
    enable-reasoning: true
    tool-call-parser: "hermes"
    reasoning-parser: "deepseek_r1"
    # Any other argument: tensor-parallel-size, max-num-seqs, etc.

test_matrix:
  input_tokens: [100, 200, 400, 800, 2000, 4000, 8000]
  output_tokens: [20, 100, 400, 1000]
  processing_num: [1, 4, 16, 32, 64, 128]
  random_tokens: [2, 10, 50, 100]

test_config:
  requests_per_process: 5
  warmup_requests: 3
  cooldown_seconds: 5
```

#### SGLang Support

The system supports SGLang and other inference servers using the `command` parameter:

```yaml
deployment:
  docker_image: "lmsysorg/sglang:v0.4.9.post4-cu126"
  container_name: "sglang-qwen3-30b"
  port: 8080
  
  # Custom command for SGLang
  command: "python3 -m sglang.launch_server"
  
  docker_params:
    gpus: "all"
    shm-size: "32g"
    volume:
      - "/cache:/root/.cache"
  
  app_args:
    model-path: "Qwen/Qwen3-30B-A3B-FP8"
    tokenizer-path: "Qwen/Qwen3-30B-A3B-FP8"
    host: "0.0.0.0"
    tp-size: 4
    context-length: 16384
```

#### Legacy Format Support

The system maintains backward compatibility with the old format:

```yaml
deployment:
  docker_image: "vllm/vllm-openai:v0.9.2"
  container_name: "vllm-qwen3-30b"
  port: 8080
  gpu_config:
    gpus: "all"
    gpu_memory_utilization: 0.95
    shm_size: "747g"
  model_config:
    model: "Qwen/Qwen3-30B-A3B-FP8"
    max_model_len: 16384
    trust_remote_code: true
  volumes:
    - "/cache:/root/.cache"
```

### Test Matrix

The automated testing runs through all combinations of:
- **Input tokens**: [100, 200, 400, 800, 2000, 4000, 8000]
- **Output tokens**: [20, 100, 400, 1000]  
- **Processing numbers**: [1, 4, 16, 32, 64, 128]
- **Random tokens**: [2, 10, 50, 100]

Test cases where `random_tokens > input_tokens` are automatically skipped to ensure valid configurations.

This creates a comprehensive performance profile across different load conditions and prompt caching scenarios.

## Command Line Options

### Testing Commands (`run_auto_test.py`)

- `--config, -c`: Path to YAML or JSON configuration file (required)
- `--output-dir, -o`: Output directory for test results (default: auto-generated timestamp under test_results/)
- `--verbose, -v`: Enable verbose output for debugging
- `--skip-deployment`: Skip Docker deployment (assume server is already running)
- `--force-rerun`: Force rerun all tests, ignoring existing results
- `--dry-run`: Show what tests would be executed without running them

Use `python run_auto_test.py --help` for full usage information.

### Deployment Commands (`deploy_server.py`)

- `--config, -c`: Path to YAML or JSON configuration file (required)
- `--show-command`: Show the generated Docker command without executing it
- `--no-health-check`: Skip health check after deployment
- `--stop`: Stop and remove the deployment instead of starting it
- `--status`: Check the status of the deployment
- `--verbose, -v`: Enable verbose output

Use `python deploy_server.py --help` for full usage information.

## Automated Testing Features

- **Docker Management**: Automatically starts, stops, and manages vLLM Docker containers
- **Health Checking**: Waits for the server to become healthy before testing
- **Warmup Requests**: Runs warmup requests before each test case to ensure consistent results
- **Cooldown Periods**: Configurable cooldown between test cases
- **Comprehensive Results**: Saves individual test results and generates summary statistics
- **Error Handling**: Continues testing even if individual test cases fail
- **Resource Cleanup**: Automatically cleans up Docker containers after testing
- **Dry Run Mode**: Preview test cases without executing them
- **Verbose Logging**: Detailed output for troubleshooting
- **Result Caching**: Automatically skips test cases with existing results
- **Force Rerun**: Option to ignore cached results and rerun all tests

## Output

The automated testing generates:
- Individual test result files for each test case
- A comprehensive results file with all test data and summary statistics
- Console output showing progress and real-time results
- Performance comparisons across different configurations