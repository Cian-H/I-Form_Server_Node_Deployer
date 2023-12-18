from mkdocs.__main__ import build_command as mkdocs_build
from pylint.pyreverse.main import Run as pyreverse


README_FILES = (
    ("", "docs/index.md"),
    ("Installation", "docs/installation.md"),
    ("Usage", "docs/usage.md"),
    ("Deployment", "docs/deployment.md"),
)


def create_readme():
    with open("README.md", "wt") as r:
        for header, file in README_FILES:
            r.write(f"\n\n## {header}\n\n")
            with open(file, "rt") as f:
                r.write(f.read())


def update_license():
    with open("LICENSE", "rt") as source, open("docs/license.md", "wt") as target:
        target.write(source.read())


def generate_uml():
    pyreverse(["-o", "mmd", "-d", "docs/assets", "node_deployer"])


def main():
    create_readme()
    update_license()
    generate_uml()
    mkdocs_build()