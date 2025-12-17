# AgentVerify

## Setup

1. Clone this repository:

```bash
git clone https://github.com/avaljotsingh/tau-bench.git && cd ./tau-bench
```

2. Install from source (which also installs required packages):

```bash
pip install -e .
```


## Run

In the following commands, the agent-name can be one of the following: 
1. Original tau bench baseline: tool-calling 
2. Tool calling with preconditions in the form of advice: tool-calling-with-preconditions 
3. Tool calling with preconditions in the form of advice and python code generation: tool-calling-with-preconditions-and-python 
4. Symbolic multi-agent system: orchestrator 
5. With pre and post conditions: assertions-agent 


To run specific tasks, use the `--task-ids` flag. For example:

```bash
python run.py --agent-strategy <agent-name> --env retail --model none --model-provider openai --user-model none --user-model-provider openai --user-strategy llm --max-concurrency 10 --task-ids 1
```

To run a range of tasks, use the `--start-index` and `--end-index` flags. For example:
 
```bash
python run.py --agent-strategy <agent-name> --env retail --model none --model-provider openai --user-model none --user-model-provider openai --user-strategy llm --max-concurrency 10 --start-index 10 --end-index 100
```

## Tau Bench Running

TRAPI is prioritized for LibGen (function suggestion/definition/correction). Tau Bench can run either:
- via TRAPI (no OpenAI-compatible base URL set; providers set to `azure`)
- via OpenAI-compatible endpoints (e.g., vLLM) when `OPENAI_API_BASE` is present

### Tau Bench Running (TRAPI):

```bash
az login
unset OPENAI_API_BASE
unset VLLM_BASE_URL

# TRAPI selection (deployment/model) via environment (authoritative for TRAPI)
export TRAPI_API_VERSION=2025-03-01-preview
export TRAPI_INSTANCE=redmond/interactive/openai
export TRAPI_MODEL_NAME=gpt-4o
export TRAPI_MODEL_VERSION=2024-11-20
export TRAPI_DEPLOYMENT_NAME=gpt-4o_2024-11-20

python run.py \
  --agent-strategy tool-calling \
  --env airline \
  --model $TRAPI_MODEL_NAME \
  --model-provider azure \
  --user-model $TRAPI_MODEL_NAME \
  --user-model-provider azure \
  --user-strategy llm \
  --num-trials 1 \
  --task-split test \
  --temperature 0.1
```

Notes:
- Ensure `OPENAI_API_BASE` is unset so requests route through TRAPI.
 - TRAPI selection is controlled by the environment variables above (api version, instance, model name/version, deployment name). The `--model/--user-model` flags are forwarded but do not change the TRAPI deployment.



## Library Learning
Preferred (TRAPI) setup for LibGen:

1) Ensure your config points to the correct MCP server (absolute path recommended). 

Key fields to verify for airline:
- `"env": "airline"`
- `"library.base_library_path": "mcp/airline_server.py"`
- `"input_tasks.mode": "latest_for_env"` or `"base_library"`
- Leave `"agent.model"` and `"agent.user_model"` as `null` to use env vars

Important:
- Change `"experiment_name"` in your config for each new run. The runner writes to `experiments/libgen/<experiment_name>/`. Reusing the same name will overwrite prior results in that folder.

2) Use TRAPI for LibGen (function suggestion/definition/correction):

```bash
az login
export LIBGEN_PROVIDER=azure_trapi
unset OPENAI_API_BASE
unset VLLM_BASE_URL
# optional: export DEFAULT_IDENTITY_CLIENT_ID=<your-identity-client-id>
# TRAPI selection for LibGen (deployment/model) via environment (authoritative for TRAPI)
export TRAPI_API_VERSION=2025-03-01-preview
export TRAPI_INSTANCE=redmond/interactive/openai
export TRAPI_MODEL_NAME=gpt-4.1
export TRAPI_MODEL_VERSION=2025-04-14
export TRAPI_DEPLOYMENT_NAME=gpt-4.1_2025-04-14
export LIBGEN_AGENT_MODEL=$TRAPI_MODEL_NAME
export LIBGEN_USER_MODEL=$LIBGEN_AGENT_MODEL

python libgen_experiment.py \
  --config configs/libgen/airline.json
```

Notes:
- If `OPENAI_API_BASE` is set in the shell, LibGen calls will route to your OpenAI-compatible endpoint instead of TRAPI.
- To run TRAPI for LibGen and vLLM for env in the same process, a small code change is needed to force TRAPI regardless of `OPENAI_API_BASE`.
 - TRAPI selection for LibGen is controlled by the same environment variables:
   - `TRAPI_API_VERSION`, `TRAPI_INSTANCE`, `TRAPI_MODEL_NAME`, `TRAPI_MODEL_VERSION`, `TRAPI_DEPLOYMENT_NAME`
