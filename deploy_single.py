# deploy_single.py - Deploy to a single environment with more options

import subprocess
import sys
import json
import os
from datetime import datetime

def load_config(env_name):
    """Load environment configuration"""
    try:
        with open(f"config/{env_name}.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Configuration file for {env_name} not found. Using defaults.")
        return {}

def deploy_single_environment(env_name, options=None):
    """Deploy to a single environment with options"""

    print(f"\n🚀 Deploying to {env_name} environment")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)

    # Base command
    cmd = ["npx", "cdk", "deploy", "-c", f"env={env_name}", "--all"]

    # Add options
    if options:
        if options.get("hotswap", False):
            cmd.append("--hotswap")
        if options.get("no_rollback", False):
            cmd.append("--no-rollback")
        if options.get("require_approval", True):
            cmd.extend(["--require-approval", "never"])
        if options.get("verbose", False):
            cmd.append("-v")

    # Execute
    try:
        subprocess.run(cmd, check=True)
        print(f"\n✅ Successfully deployed to {env_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Deployment to {env_name} failed with error code: {e.returncode}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python deploy_single.py <environment> [options]")
        print("Environments: dev, test, prod")
        print("Options: --hotswap, --no-rollback, --verbose")
        sys.exit(1)

    env_name = sys.argv[1]

    # Parse options
    options = {
        "hotswap": "--hotswap" in sys.argv,
        "no_rollback": "--no-rollback" in sys.argv,
        "verbose": "--verbose" in sys.argv or "-v" in sys.argv,
        "require_approval": "--require-approval" not in sys.argv
    }

    # Deploy
    success = deploy_single_environment(env_name, options)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()