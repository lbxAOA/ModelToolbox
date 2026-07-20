"""CLI：pipeline datagen / train / serve —— 串起四阶段。"""
from __future__ import annotations

import argparse
from pathlib import Path


def _cmd_datagen(args) -> int:
    from .datagen import DatagenConfig, generate, make_provider_teacher

    cfg = DatagenConfig(
        corpus_dir=Path(args.corpus),
        out_path=Path(args.out),
        per_chunk=args.per_chunk,
        limit_files=args.limit,
    )
    teacher = make_provider_teacher(args.role)
    stats = generate(cfg, teacher)
    print("datagen:", stats)
    return 0


def _cmd_train(args) -> int:
    from .train import build_train_cmd, run

    cmd = build_train_cmd(Path(args.config), dry_run=not args.execute)
    return run(cmd, execute=args.execute)


def _cmd_serve(args) -> int:
    from .serve import ModelfileSpec, ollama_create, write_modelfile

    spec = ModelfileSpec(
        gguf_path=Path(args.gguf),
        name=args.name,
        mmproj_path=Path(args.mmproj) if args.mmproj else None,
    )
    mf = write_modelfile(spec, Path(args.modelfile))
    print("wrote", mf)
    cmd = ollama_create(args.name, mf, run=args.execute)
    print("$", " ".join(cmd))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pipeline", description="ModelToolbox 四阶段管线")
    sub = p.add_subparsers(dest="command", required=True)

    dg = sub.add_parser("datagen", help="阶段0: 从 md 蒸馏训练样本(JSONL)")
    dg.add_argument("--corpus", required=True, help="md 语料目录(ModelIngest 产物)")
    dg.add_argument("--out", default="pipeline/out/train.jsonl")
    dg.add_argument("--per-chunk", type=int, default=3, dest="per_chunk")
    dg.add_argument("--limit", type=int, default=None, help="限制文件数(试运行)")
    dg.add_argument("--role", default="teacher")
    dg.set_defaults(func=_cmd_datagen)

    tr = sub.add_parser("train", help="阶段1: 子进程调 unsloth 训练(默认dry-run)")
    tr.add_argument("--config", required=True, help="训练 YAML 配置")
    tr.add_argument("--execute", action="store_true", help="真正执行(否则仅打印命令)")
    tr.set_defaults(func=_cmd_train)

    sv = sub.add_parser("serve", help="阶段2: 生成 Modelfile 并 ollama create")
    sv.add_argument("--gguf", required=True, help="导出的 GGUF 路径")
    sv.add_argument("--mmproj", default=None, help="视觉投影 mmproj.gguf(Gemma视觉必需)")
    sv.add_argument("--name", default="modeltoolbox-private")
    sv.add_argument("--modelfile", default="pipeline/out/Modelfile")
    sv.add_argument("--execute", action="store_true", help="真正执行 ollama create")
    sv.set_defaults(func=_cmd_serve)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
