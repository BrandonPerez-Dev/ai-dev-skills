"""Print the public API of a package, one line per symbol, for snapshot diffing."""
import sys
import griffe


def walk(obj, out):
    for _, member in sorted(obj.members.items()):
        if not member.is_public or member.is_alias:
            continue
        sig = ""
        if member.is_function:
            params = ", ".join(f"{p.name}: {p.annotation}" for p in member.parameters)
            sig = f"({params}) -> {member.returns}"
        elif member.is_attribute:
            sig = f": {member.annotation}"
        out.append(f"{member.kind.value} {member.path}{sig}")
        if member.is_class:
            walk(member, out)


out: list[str] = []
walk(griffe.load(sys.argv[1], search_paths=[sys.argv[2]]), out)
print("\n".join(out))
