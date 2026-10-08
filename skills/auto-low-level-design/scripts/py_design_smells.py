"""Flag two checkable design smells in a Python tree:
pass-through functions (body is one call forwarding the same parameters) and
Protocols/ABCs with fewer than two implementing classes (premature extension points)."""
import ast
import pathlib
import sys

trees = {p: ast.parse(p.read_text()) for p in pathlib.Path(sys.argv[1]).rglob("*.py")}
findings = []

for path, tree in trees.items():
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = [s for s in fn.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
        if len(body) != 1 or not isinstance(body[0], (ast.Return, ast.Expr)):
            continue
        call = body[0].value
        if not isinstance(call, ast.Call):
            continue
        params = [a.arg for a in fn.args.args if a.arg != "self"]
        passed = [a.id for a in call.args if isinstance(a, ast.Name)]
        if params and passed == params:
            findings.append(f"{path}:{fn.lineno} pass-through: {fn.name} only forwards to {ast.unparse(call.func)}")

ports, bases = {}, {}
for path, tree in trees.items():
    for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
        names = [ast.unparse(b) for b in cls.bases]
        if any(n in ("Protocol", "ABC") for n in names):
            ports[cls.name] = f"{path}:{cls.lineno}"
        for n in names:
            bases.setdefault(n, []).append(cls.name)
for port, where in ports.items():
    impls = bases.get(port, [])
    if len(impls) < 2:
        findings.append(f"{where} extension point {port} has {len(impls)} declared implementation(s); needs 2 real variants or an ADR")

print("\n".join(findings) or "clean")
sys.exit(1 if findings else 0)
