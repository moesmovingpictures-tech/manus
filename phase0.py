import os, time, json, csv, pathlib, subprocess, numpy as np, git, gzip
from sentence_transformers import SentenceTransformer as ST
ROOT = pathlib.Path("/workspace/manus_origin"); (ROOT/"memory").mkdir(exist_ok=True)
subprocess.run(["git","init","-q"],cwd=ROOT)
ENC = ST("all-MiniLM-L6-v2")

