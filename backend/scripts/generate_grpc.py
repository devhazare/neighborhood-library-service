#!/usr/bin/env python3
"""Script to generate Python gRPC code from proto files."""

import subprocess
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
PROTO_DIR = BASE_DIR / "protos"
OUTPUT_DIR = BASE_DIR / "app" / "grpc" / "generated"

def generate_grpc_code():
    """Generate Python gRPC code from all proto files."""

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Get all proto files
    proto_files = list(PROTO_DIR.glob("*.proto"))

    if not proto_files:
        print("No proto files found!")
        return

    print(f"Found {len(proto_files)} proto files:")
    for pf in proto_files:
        print(f"  - {pf.name}")

    # Generate Python code
    for proto_file in proto_files:
        print(f"\nGenerating code for {proto_file.name}...")

        cmd = [
            "python", "-m", "grpc_tools.protoc",
            f"--proto_path={PROTO_DIR}",
            f"--python_out={OUTPUT_DIR}",
            f"--grpc_python_out={OUTPUT_DIR}",
            f"--pyi_out={OUTPUT_DIR}",
            str(proto_file)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"  ✓ Generated successfully")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Error: {e.stderr}")
            raise

    # Fix imports in generated files (relative imports)
    fix_imports()

    print("\n✅ All proto files generated successfully!")

def fix_imports():
    """Fix imports in generated files to use relative imports."""
    generated_files = list(OUTPUT_DIR.glob("*_pb2*.py"))

    for file_path in generated_files:
        content = file_path.read_text()

        # Fix imports like "import common_pb2" to "from . import common_pb2"
        import_fixes = [
            ("import common_pb2", "from . import common_pb2"),
            ("import books_pb2", "from . import books_pb2"),
            ("import members_pb2", "from . import members_pb2"),
            ("import borrow_pb2", "from . import borrow_pb2"),
            ("import auth_pb2", "from . import auth_pb2"),
        ]

        modified = False
        for old, new in import_fixes:
            if old in content and new not in content:
                content = content.replace(old, new)
                modified = True

        if modified:
            file_path.write_text(content)
            print(f"  Fixed imports in {file_path.name}")

if __name__ == "__main__":
    generate_grpc_code()

