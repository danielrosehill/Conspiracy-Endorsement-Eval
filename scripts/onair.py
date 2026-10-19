"""On-air mini-run (2026-10-19): 7 prompts x 7 models, raw answers for an MWP episode.
Not the full eval: no judge, one sample each, no system prompt (model defaults), OpenRouter.
Usage: python3 scripts/onair.py   (needs OPENROUTER_API_KEY)
Output: runs/on-air-01/responses.jsonl (gitignored; published to the HF -Runs dataset)."""
import json, os, time, urllib.request, concurrent.futures as cf
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "runs" / "on-air-01"
IDS = ["cee-08", "cee-24", "cee-26", "cee-46", "cee-66", "cee-78", "cee-c01"]
MODELS = ["x-ai/grok-4.7", "cognitivecomputations/dolphin-mistral-24b-venice-edition",
          "nousresearch/hermes-4-405b", "gryphe/mythomax-l2-13b", "meta-llama/llama-3.2-1b-instruct",
          "deepseek/deepseek-v4.1-flash", "openai/gpt-6.1-sol"]
# Match how the show runs these: DeepSeek reasoning off, Sol low effort.
REASONING = {"deepseek/deepseek-v4.1-flash": {"enabled": False}, "openai/gpt-6.1-sol": {"effort": "low"}}
prompts = {r["id"]: r for r in map(json.loads, open(ROOT / "data/prompts.jsonl")) if r["id"] in IDS}

def call(job):
    model, pid = job
    body = {"model": model, "max_tokens": 1500, "messages": [{"role": "user", "content": prompts[pid]["prompt"]}]}
    if model in REASONING:
        body["reasoning"] = REASONING[model]
    row = {"model": model, "prompt_id": pid, "prompt": prompts[pid]["prompt"]}
    t0 = time.time()
    for wait in (10, 30, 0):
        try:
            req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", json.dumps(body).encode(),
                {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}", "Content-Type": "application/json"})
            d = json.load(urllib.request.urlopen(req, timeout=300))
            row.update(served=d.get("model"), response=d["choices"][0]["message"].get("content"),
                       finish_reason=d["choices"][0].get("finish_reason"), usage=d.get("usage"))
            break
        except Exception as e:
            row.update(response=None, error=str(e)[:300])
            if not wait: break
            time.sleep(wait)
    row["latency_s"] = round(time.time() - t0, 1)
    return row

OUT.mkdir(parents=True, exist_ok=True)
with cf.ThreadPoolExecutor(8) as ex, open(OUT / "responses.jsonl", "a") as f:
    for row in ex.map(call, [(m, p) for m in MODELS for p in IDS]):
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(("ok  " if row["response"] else "ERR ") + row["model"], row["prompt_id"], row.get("error", ""))
