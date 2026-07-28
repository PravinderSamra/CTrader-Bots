"""Bot compilation: ``.cs`` → ``.algo`` (build-spec §1).

Two routes, tried in order:

1. **The cTrader CLI's own ``build`` subcommand.** The console image bundles the
   Algo toolchain, so this needs no .NET SDK on the host. Its ``--help`` claims
   "No auth" — but ``create`` makes the same claim and then demands ``--ctid``,
   so the auth requirement here is treated as unknown and credentials are passed
   when available (03-Verification-Findings §3.7).
2. **A .NET SDK container** building a generated classlib that references the
   ``cTrader.Automate`` NuGet package.

Target framework is **net6.0**, not net8.0: the console image ships runtime
6.0.10 and no SDK, so a net8.0 ``.algo`` will not load (§3.2). Override only
after checking what runtime your console tag actually ships.

The compiled artefact is cached on the SHA256 of (source + target + package
version), which is also what enters the runner's cache key — recompiling an
unchanged bot never invalidates a study's results.
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

CSPROJ_TEMPLATE = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>{target}</TargetFramework>
    <LangVersion>latest</LangVersion>
    <EnableDefaultCompileItems>false</EnableDefaultCompileItems>
    <AssemblyName>{assembly}</AssemblyName>
    <Nullable>disable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="cTrader.Automate" Version="{package_version}" />
  </ItemGroup>
  <ItemGroup>
    <Compile Include="{source_name}" />
  </ItemGroup>
</Project>
"""

DEFAULT_PACKAGE_VERSION = "1.*"
SDK_IMAGE = "mcr.microsoft.com/dotnet/sdk:8.0"


class CompileError(RuntimeError):
    """The bot did not compile. Never patched silently — reported to the trader."""


@dataclass(frozen=True)
class CompileResult:
    algo: Path
    algo_hash: str
    route: str            # "ctrader-cli" | "dotnet-sdk" | "cached"
    output: str = ""


def source_hash(source: Path, target: str, package_version: str) -> str:
    h = hashlib.sha256()
    h.update(Path(source).read_bytes())
    h.update(target.encode())
    h.update(package_version.encode())
    return h.hexdigest()[:16]


def _run(cmd: list[str], cwd: Path | None = None, timeout: int = 900) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, f"timed out after {timeout}s"
    except OSError as exc:
        return 127, str(exc)
    return p.returncode, p.stdout + p.stderr


def compile_bot(
    source: Path,
    out_dir: Path,
    console_tag: str,
    target: str = "net6.0",
    package_version: str = DEFAULT_PACKAGE_VERSION,
    credentials=None,
    sudo: bool = False,
    force: bool = False,
) -> CompileResult:
    """Compile ``source`` to a ``.algo``, caching on content hash."""
    source = Path(source)
    if not source.is_file():
        raise CompileError(f"bot source not found: {source}")

    digest = source_hash(source, target, package_version)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cached = out_dir / f"{source.stem}_{digest}.algo"
    if cached.is_file() and not force:
        return CompileResult(cached, digest, "cached")

    build_dir = out_dir / f"build_{digest}"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)
    shutil.copy2(source, build_dir / source.name)

    (build_dir / f"{source.stem}.csproj").write_text(CSPROJ_TEMPLATE.format(
        target=target, assembly=source.stem, source_name=source.name,
        package_version=package_version,
    ))

    errors = []
    for route, fn in (
        ("ctrader-cli", _build_with_ctrader_cli),
        ("dotnet-sdk", _build_with_dotnet_sdk),
    ):
        rc, output = fn(build_dir, console_tag, credentials, sudo)
        if rc == 0:
            algo = _find_algo(build_dir)
            if algo:
                shutil.copy2(algo, cached)
                shutil.rmtree(build_dir, ignore_errors=True)
                return CompileResult(cached, digest, route, output)
            errors.append(f"[{route}] exited 0 but produced no .algo")
        else:
            errors.append(f"[{route}] exit {rc}\n{output[-1500:]}")

    raise CompileError(
        f"could not compile {source.name}.\n\n" + "\n\n".join(errors)
        + "\n\nThe bot source is never patched automatically. If this is a genuine "
          "API incompatibility, fix it deliberately and commit the change."
    )


def _build_with_ctrader_cli(build_dir: Path, console_tag: str, credentials, sudo: bool):
    if shutil.which("ctrader-cli"):
        cmd = ["ctrader-cli", "build", str(build_dir)]
    else:
        docker = (["sudo", "-n"] if sudo else []) + ["docker"]
        cmd = [*docker, "run", "--rm", "-v", f"{build_dir}:/work", "-w", "/work",
               f"ghcr.io/spotware/ctrader-console:{console_tag}", "build", "/work"]
    if credentials:
        cmd += [f"--ctid={credentials.ctid}", f"--account={credentials.account_id}"]
    return _run(cmd, cwd=build_dir)


def _build_with_dotnet_sdk(build_dir: Path, console_tag: str, credentials, sudo: bool):
    if shutil.which("dotnet"):
        return _run(["dotnet", "build", "-c", "Release"], cwd=build_dir)
    docker = (["sudo", "-n"] if sudo else []) + ["docker"]
    return _run([*docker, "run", "--rm", "-v", f"{build_dir}:/src", "-w", "/src",
                 SDK_IMAGE, "dotnet", "build", "-c", "Release"])


def _find_algo(build_dir: Path) -> Path | None:
    candidates = sorted(build_dir.rglob("*.algo"), key=lambda p: p.stat().st_mtime)
    return candidates[-1] if candidates else None
