#!/usr/bin/env python3
"""Score retrieval quality against a labeled gold set.

Stdlib only. Computes recall@k, precision@k, MRR, hit@k, and nDCG@k.

Inputs are two JSONL files:

  gold.jsonl   one object per query:
     {"id": "q1", "query": "...", "relevant_ids": ["art_42", "art_99"]}

  preds.jsonl  one object per query, ranked best-first:
     {"id": "q1", "retrieved_ids": ["art_99", "art_7", "art_42", ...]}

Usage:
    python eval_retrieval.py gold.jsonl preds.jsonl --k 1 3 5 10
    python eval_retrieval.py gold.jsonl preds.jsonl --k 5 --per-query

Ids in gold's relevant_ids are matched exactly against preds' retrieved_ids.
Queries present in gold but missing from preds are scored as all-misses.
"""
import argparse
import json
import math
import sys


def load_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise SystemExit(f"{path}:{ln}: invalid JSON: {e}")
    return rows


def dcg(relevances):
    return sum(rel / math.log2(i + 2) for i, rel in enumerate(relevances))


def ndcg_at_k(retrieved, relevant_set, k):
    gains = [1.0 if rid in relevant_set else 0.0 for rid in retrieved[:k]]
    ideal = [1.0] * min(len(relevant_set), k)
    idcg = dcg(ideal)
    if idcg == 0:
        return 0.0
    return dcg(gains) / idcg


def evaluate(gold, preds, ks):
    pred_by_id = {p["id"]: p.get("retrieved_ids", []) for p in preds}
    n = 0
    agg = {k: {"recall": 0.0, "precision": 0.0, "hit": 0.0, "ndcg": 0.0} for k in ks}
    mrr_total = 0.0
    per_query = []

    for g in gold:
        qid = g["id"]
        relevant = set(g.get("relevant_ids", []))
        if not relevant:
            continue
        n += 1
        retrieved = pred_by_id.get(qid, [])

        # MRR over full list
        rr = 0.0
        for rank, rid in enumerate(retrieved, 1):
            if rid in relevant:
                rr = 1.0 / rank
                break
        mrr_total += rr

        row = {"id": qid, "rr": round(rr, 4)}
        for k in ks:
            topk = retrieved[:k]
            found = sum(1 for rid in topk if rid in relevant)
            recall = found / len(relevant)
            precision = found / k if k else 0.0
            hit = 1.0 if found > 0 else 0.0
            nd = ndcg_at_k(retrieved, relevant, k)
            agg[k]["recall"] += recall
            agg[k]["precision"] += precision
            agg[k]["hit"] += hit
            agg[k]["ndcg"] += nd
            row[f"recall@{k}"] = round(recall, 4)
            row[f"ndcg@{k}"] = round(nd, 4)
        per_query.append(row)

    if n == 0:
        raise SystemExit("no gold queries with relevant_ids found")

    summary = {"queries": n, "mrr": round(mrr_total / n, 4)}
    for k in ks:
        summary[f"recall@{k}"] = round(agg[k]["recall"] / n, 4)
        summary[f"precision@{k}"] = round(agg[k]["precision"] / n, 4)
        summary[f"hit@{k}"] = round(agg[k]["hit"] / n, 4)
        summary[f"ndcg@{k}"] = round(agg[k]["ndcg"] / n, 4)
    return summary, per_query


def main(argv=None):
    ap = argparse.ArgumentParser(description="Score retrieval against a gold set.")
    ap.add_argument("gold", help="gold.jsonl with id + relevant_ids")
    ap.add_argument("preds", help="preds.jsonl with id + retrieved_ids")
    ap.add_argument("--k", type=int, nargs="+", default=[1, 3, 5, 10])
    ap.add_argument("--per-query", action="store_true", help="also print per-query rows")
    ap.add_argument("--json", action="store_true", help="emit summary as JSON")
    args = ap.parse_args(argv)

    gold = load_jsonl(args.gold)
    preds = load_jsonl(args.preds)
    ks = sorted(set(args.k))
    summary, per_query = evaluate(gold, preds, ks)

    if args.json:
        print(json.dumps({"summary": summary, "per_query": per_query if args.per_query else []},
                         indent=2))
        return 0

    print(f"queries={summary['queries']}  MRR={summary['mrr']}")
    print("-" * 60)
    header = f"{'k':>4} | {'recall':>7} | {'prec':>6} | {'hit':>5} | {'ndcg':>6}"
    print(header)
    for k in ks:
        print(f"{k:>4} | {summary[f'recall@{k}']:>7} | {summary[f'precision@{k}']:>6} | "
              f"{summary[f'hit@{k}']:>5} | {summary[f'ndcg@{k}']:>6}")
    if args.per_query:
        print("-" * 60)
        for row in per_query:
            print(json.dumps(row))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
