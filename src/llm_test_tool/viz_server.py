#!/usr/bin/env python3
"""
FastAPI server for LLM performance visualization data API.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
import uvicorn

app = FastAPI(title="LLM Performance Visualization API", version="1.0.0")


class ResultsDataProvider:
    """Data provider for LLM performance test results"""
    
    def __init__(self, results_dir: str = "archive_results"):
        self.results_dir = Path(results_dir)
        self.data = []
        self.df = None
        self.load_all_results()
    
    def parse_filename(self, filename: str) -> Optional[Dict[str, str]]:
        """Parse test result filename to extract parameters"""
        pattern = r'test_in:(\d+)_out:(\d+)_proc:(\d+)_rand:(\d+)\.json'
        match = re.match(pattern, filename)
        
        if match:
            return {
                'input_tokens': int(match.group(1)),
                'output_tokens': int(match.group(2)),
                'processes': int(match.group(3)),
                'random_tokens': int(match.group(4))
            }
        return None
    
    def parse_directory_name(self, dirname: str) -> Optional[Dict[str, str]]:
        """Parse directory name to extract runtime, instance type, and model"""
        parts = dirname.split('--')
        if len(parts) >= 3:
            model_name = '--'.join(parts[2:])
            # Strip .yaml suffix if present
            if model_name.endswith('.yaml'):
                model_name = model_name[:-5]
            
            return {
                'runtime': parts[0],
                'instance_type': parts[1],
                'model_name': model_name
            }
        return None
    
    def load_all_results(self):
        """Load all test results from the archive directory"""
        print(f"Loading results from {self.results_dir}...")
        self.data = []
        for result_dir in self.results_dir.iterdir():
            if not result_dir.is_dir():
                continue
            
            dir_info = self.parse_directory_name(result_dir.name)
            if not dir_info:
                continue
            
            for result_file in result_dir.glob("test_*.json"):
                file_info = self.parse_filename(result_file.name)
                if not file_info:
                    continue
                
                try:
                    with open(result_file, 'r') as f:
                        result_data = json.load(f)
                    
                    stats = result_data.get('statistics', {})
                    metadata = result_data.get('metadata', {})
                    
                    record = {
                        **dir_info,
                        **file_info,
                        'first_token_latency_mean': stats.get('first_token_latency', {}).get('mean', 0),
                        'first_token_latency_p50': stats.get('first_token_latency', {}).get('p50', 0),
                        'first_token_latency_p90': stats.get('first_token_latency', {}).get('p90', 0),
                        'first_token_latency_min': stats.get('first_token_latency', {}).get('min', 0),
                        'first_token_latency_max': stats.get('first_token_latency', {}).get('max', 0),
                        'end_to_end_latency_mean': stats.get('end_to_end_latency', {}).get('mean', 0),
                        'end_to_end_latency_p50': stats.get('end_to_end_latency', {}).get('p50', 0),
                        'end_to_end_latency_p90': stats.get('end_to_end_latency', {}).get('p90', 0),
                        'output_tokens_per_second_mean': stats.get('output_tokens_per_second', {}).get('mean', 0),
                        'output_tokens_per_second_p50': stats.get('output_tokens_per_second', {}).get('p50', 0),
                        'output_tokens_per_second_p90': stats.get('output_tokens_per_second', {}).get('p90', 0),
                        'output_tokens_per_second_min': stats.get('output_tokens_per_second', {}).get('min', 0),
                        'output_tokens_per_second_max': stats.get('output_tokens_per_second', {}).get('max', 0),
                        'success_rate': stats.get('success_rate', 0),
                        'requests_per_second': metadata.get('requests_per_second', 0),
                        'total_requests': metadata.get('total_requests', 0),
                        'successful_requests': stats.get('successful_requests', 0),
                        'failed_requests': stats.get('failed_requests', 0),
                        'total_tokens_mean': stats.get('token_usage', {}).get('total_tokens', {}).get('mean', 0),
                        'server_throughput': metadata.get('requests_per_second', 0) * stats.get('token_usage', {}).get('total_tokens', {}).get('mean', 0),
                        'file_path': str(result_file)
                    }
                    
                    self.data.append(record)
                    
                except Exception as e:
                    print(f"Error loading {result_file}: {e}")
        
        self.df = pd.DataFrame(self.data)
        print(f"Loaded {len(self.data)} test results")
    
    def get_combinations(self) -> List[Dict[str, str]]:
        """Get all available runtime-instance-model combinations"""
        if self.df is None or self.df.empty:
            return []
        
        combinations = self.df[['runtime', 'instance_type', 'model_name']].drop_duplicates()
        return [
            {
                'runtime': row['runtime'],
                'instance_type': row['instance_type'],
                'model_name': row['model_name'],
                'id': f"{row['runtime']}--{row['instance_type']}--{row['model_name']}"
            }
            for _, row in combinations.iterrows()
        ]
    
    def get_test_parameters(self, runtime: str, instance_type: str, model_name: str) -> Dict[str, List]:
        """Get available test parameters for a specific combination"""
        if self.df is None or self.df.empty:
            return {}
        
        filtered = self.df[
            (self.df['runtime'] == runtime) & 
            (self.df['instance_type'] == instance_type) & 
            (self.df['model_name'] == model_name)
        ]
        
        return {
            'input_tokens': sorted(filtered['input_tokens'].unique().tolist(), key=int),
            'output_tokens': sorted(filtered['output_tokens'].unique().tolist(), key=int),
            'random_tokens': sorted(filtered['random_tokens'].unique().tolist(), key=int)
        }
    
    def get_performance_data(self, filters: Dict) -> List[Dict]:
        """Get performance data based on filters"""
        if self.df is None or self.df.empty:
            return []
        
        filtered_df = self.df.copy()
        
        # Apply filters
        for key, value in filters.items():
            if key in filtered_df.columns and value is not None:
                if isinstance(value, list):
                    filtered_df = filtered_df[filtered_df[key].isin(value)]
                else:
                    filtered_df = filtered_df[filtered_df[key] == value]
        
        # Sort by processes for proper line plotting
        filtered_df = filtered_df.sort_values('processes')
        
        return filtered_df.to_dict('records')


# Pydantic models for request/response
class ComparisonRequest(BaseModel):
    combinations: List[Dict]

class CombinationInfo(BaseModel):
    runtime: str
    instance_type: str
    model_name: str
    id: str

# Initialize data provider
data_provider = ResultsDataProvider()


@app.get("/")
async def index():
    """Serve the main HTML page"""
    # Get the directory where this script is located
    current_dir = Path(__file__).parent
    html_file = current_dir / 'viz_client.html'
    return FileResponse(str(html_file))


@app.get("/api/combinations", response_model=List[CombinationInfo])
async def get_combinations():
    """Get all available runtime-instance-model combinations"""
    combinations = data_provider.get_combinations()
    return combinations


@app.get("/api/parameters")
async def get_parameters(
    runtime: str = Query(..., description="Runtime name"),
    instance_type: str = Query(..., description="Instance type"),
    model_name: str = Query(..., description="Model name")
):
    """Get available test parameters for a specific combination"""
    parameters = data_provider.get_test_parameters(runtime, instance_type, model_name)
    return parameters


@app.get("/api/performance-data")
async def get_performance_data(
    runtime: Optional[str] = Query(None),
    instance_type: Optional[str] = Query(None),
    model_name: Optional[str] = Query(None),
    input_tokens: Optional[int] = Query(None),
    output_tokens: Optional[int] = Query(None),
    random_tokens: Optional[int] = Query(None)
):
    """Get performance data based on filters"""
    filters = {}
    
    # Build filters from query parameters
    if runtime:
        filters['runtime'] = runtime
    if instance_type:
        filters['instance_type'] = instance_type
    if model_name:
        filters['model_name'] = model_name
    if input_tokens is not None:
        filters['input_tokens'] = input_tokens
    if output_tokens is not None:
        filters['output_tokens'] = output_tokens
    if random_tokens is not None:
        filters['random_tokens'] = random_tokens
    
    data = data_provider.get_performance_data(filters)
    return data


@app.post("/api/comparison-data")
async def get_comparison_data(request: ComparisonRequest):
    """Get performance data for multiple combinations for comparison"""
    try:
        result = []
        for combo in request.combinations:
            data = data_provider.get_performance_data(combo)
            result.append({
                'combination': combo,
                'data': data
            })
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tree-structure")
async def get_tree_structure():
    """Get hierarchical tree structure of Runtime -> Instance Type -> Model"""
    # Reload all results from disk to get the latest data
    data_provider.load_all_results()
    
    if data_provider.df is None or data_provider.df.empty:
        return {"tree": []}
    
    df = data_provider.df
    tree = {}
    
    # Build hierarchical structure
    for _, row in df.iterrows():
        runtime = row['runtime']
        instance_type = row['instance_type']
        model_name = row['model_name']
        
        if runtime not in tree:
            tree[runtime] = {}
        
        if instance_type not in tree[runtime]:
            tree[runtime][instance_type] = set()
        
        tree[runtime][instance_type].add(model_name)
    
    # Convert to list format with counts
    result = []
    for runtime in sorted(tree.keys()):
        runtime_node = {
            'id': runtime,
            'label': runtime,
            'type': 'runtime',
            'count': len(df[df['runtime'] == runtime]),
            'children': []
        }
        
        for instance_type in sorted(tree[runtime].keys()):
            instance_node = {
                'id': f"{runtime}--{instance_type}",
                'label': instance_type,
                'type': 'instance_type',
                'count': len(df[(df['runtime'] == runtime) & (df['instance_type'] == instance_type)]),
                'children': []
            }
            
            for model_name in sorted(tree[runtime][instance_type]):
                model_node = {
                    'id': f"{runtime}--{instance_type}--{model_name}",
                    'label': model_name,
                    'type': 'model',
                    'count': len(df[(df['runtime'] == runtime) & 
                                   (df['instance_type'] == instance_type) & 
                                   (df['model_name'] == model_name)]),
                    'runtime': runtime,
                    'instance_type': instance_type,
                    'model_name': model_name
                }
                instance_node['children'].append(model_node)
            
            runtime_node['children'].append(instance_node)
        
        result.append(runtime_node)
    
    return {"tree": result}


@app.get("/api/stats")
async def get_stats():
    """Get overall statistics about the dataset"""
    if data_provider.df is None or data_provider.df.empty:
        raise HTTPException(status_code=404, detail="No data available")
    
    df = data_provider.df
    
    stats = {
        'total_tests': len(df),
        'unique_combinations': len(df[['runtime', 'instance_type', 'model_name']].drop_duplicates()),
        'runtimes': sorted(df['runtime'].unique().tolist()),
        'instance_types': sorted(df['instance_type'].unique().tolist()),
        'models': sorted(df['model_name'].unique().tolist()),
        'input_token_range': [int(df['input_tokens'].min()), int(df['input_tokens'].max())],
        'output_token_range': [int(df['output_tokens'].min()), int(df['output_tokens'].max())],
        'process_range': [int(df['processes'].min()), int(df['processes'].max())],
        'performance_summary': {
            'avg_first_token_latency': float(df['first_token_latency_mean'].mean()),
            'avg_throughput': float(df['output_tokens_per_second_mean'].mean()),
            'avg_server_throughput': float(df['server_throughput'].mean()) if 'server_throughput' in df.columns else 0,
            'avg_success_rate': float(df['success_rate'].mean())
        }
    }
    
    return stats


def main():
    """Main entry point for the visualization server"""
    print("Starting LLM Performance Visualization Server...")
    print("Access the visualization at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == '__main__':
    main()