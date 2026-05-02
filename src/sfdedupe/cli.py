import json
import pandas as pd
import click
from .block import build_blocks
from .score import score_blocks
from .llm import tiebreak
from .sfdc import get_client


@click.group()
def cli():
    pass


@cli.command()
@click.option("--input", "input_path", required=True, type=click.Path(exists=True))
@click.option("--auto-threshold", default=90, show_default=True)
@click.option("--escalate-threshold", default=78, show_default=True)
@click.option("--out", "out_path", default="proposals.csv", show_default=True)
def scan(input_path: str, auto_threshold: int, escalate_threshold: int, out_path: str):
    """Find duplicate proposals; write CSV. Does not modify Salesforce."""
    df = pd.read_csv(input_path).fillna("")
    records = df.to_dict(orient="records")
    blocks = build_blocks(records)
    pairs = score_blocks(records, blocks)
    proposals = []
    for p in pairs:
        if p.score >= auto_threshold:
            proposals.append({**p.__dict__, "action": "auto_merge", "llm_reason": ""})
        elif p.score >= escalate_threshold:
            a = next(r for r in records if r["id"] == p.a_id)
            b = next(r for r in records if r["id"] == p.b_id)
            verdict = tiebreak(a, b)
            if verdict and verdict.get("same_company"):
                proposals.append({**p.__dict__, "action": "llm_merge",
                                  "llm_reason": verdict.get("reason", "")})
            else:
                proposals.append({**p.__dict__, "action": "escalate",
                                  "llm_reason": (verdict or {}).get("reason", "no LLM")})
    pd.DataFrame(proposals).to_csv(out_path, index=False)
    click.echo(f"wrote {len(proposals)} proposals to {out_path}")


@cli.command()
@click.option("--proposals", "proposals_path", required=True, type=click.Path(exists=True))
@click.option("--apply", is_flag=True, help="Actually call SFDC merge API")
def merge(proposals_path: str, apply: bool):
    df = pd.read_csv(proposals_path)
    auto = df[df["action"].isin(["auto_merge", "llm_merge"])]
    if not apply:
        click.echo(f"would merge {len(auto)} pairs (dry run; pass --apply to execute)")
        return
    client = get_client()
    audit = []
    for _, row in auto.iterrows():
        result = client.merge_accounts(master_id=row["a_id"], duplicate_ids=[row["b_id"]])
        audit.append({"pair": [row["a_id"], row["b_id"]], "score": int(row["score"]),
                      "action": row["action"], "sfdc": result})
    with open("audit.jsonl", "a") as f:
        for a in audit:
            f.write(json.dumps(a) + "\n")
    click.echo(f"merged {len(audit)} pairs; audit log appended to audit.jsonl")


if __name__ == "__main__":
    cli()
