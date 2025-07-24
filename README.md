# LLM Test Tool

A lightweight tool for testing LLM API performance with customizable parameters.

## Features

- Test LLM API performance with multiple parallel processes
- Customize model ID, input tokens, random tokens, and output tokens
- Measure first token latency, end-to-end latency, and output tokens per second
- Generate detailed statistical reports with percentiles (p25, p50, p75, p90)
- Support for prompt caching optimization with fixed and random prompt parts
- Token usage tracking and analysis

## Installation

Using uv:

```bash
uv pip install -e .
```

## Usage

```bash
llm-test --processes 4 --requests 10 --model_id "Qwen/Qwen3-30B-A3B-FP8" --input_tokens 20 --random_tokens 5 --output_tokens 100 --url "http://localhost:8080/v1/chat/completions"
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