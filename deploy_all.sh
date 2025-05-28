# deploy_all.py - Python script to deploy to all environments

import subprocess
import sys
import time
from typing import List, Optional

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_colored(message: str, color: str = Colors.NC):
    """Print message with color"""
    print(f"{color}{message}{Colors.NC}")

def run_cdk_command(env_name: str, command: str = "deploy", require_approval: bool = False) -> bool:
    """Run CDK command for specific environment"""
    print_colored(f"\n{'='*50}", Colors.BLUE)
    print_colored(f"Running CDK {command} for {env_name} environment...", Colors.YELLOW)
    print_colored(f"{'='*50}\n", Colors.BLUE)

    cmd = [
        "npx", "cdk", command,
        "-c", f"env={env_name}",
        "--all"
    ]

    if command == "deploy" and not require_approval:
        cmd.extend(["--require-approval", "never"])

    start_time = time.time()

    try:
        result = subprocess.run(cmd, check=True)
        elapsed_time = time.time() - start_time
        print_colored(f"\n✅ Successfully completed {command} for {env_name} (took {elapsed_time:.2f}s)", Colors.GREEN)
        return True
    except subprocess.CalledProcessError as e:
        elapsed_time = time.time() - start_time
        print_colored(f"\n❌ Error during {command} for {env_name} (failed after {elapsed_time:.2f}s)", Colors.RED)
        print_colored(f"Error code: {e.returncode}", Colors.RED)
        return False

def deploy_to_environments(environments: List[str], command: str = "deploy"):
    """Deploy to multiple environments"""
    print_colored(f"Starting CDK {command} for environments: {', '.join(environments)}", Colors.YELLOW)

    successful = []
    failed = []

    for env in environments:
        if run_cdk_command(env, command):
            successful.append(env)
        else:
            failed.append(env)
            if command == "deploy":
                print_colored(f"Stopping deployment due to error in {env}", Colors.RED)
                break

    # Print summary
    print_colored("\n" + "="*50, Colors.BLUE)
    print_colored("DEPLOYMENT SUMMARY", Colors.YELLOW)
    print_colored("="*50, Colors.BLUE)

    if successful:
        print_colored(f"✅ Successful: {', '.join(successful)}", Colors.GREEN)

    if failed:
        print_colored(f"❌ Failed: {', '.join(failed)}", Colors.RED)

    if not failed:
        print_colored("\n🎉 All operations completed successfully!", Colors.GREEN)
    else:
        print_colored("\n⚠️  Some operations failed. Please check the logs above.", Colors.RED)

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Deploy Brightpoint Stack to multiple environments")
    parser.add_argument("command", nargs="?", default="deploy",
                      choices=["deploy", "diff", "synth", "destroy"],
                      help="CDK command to run (default: deploy)")
    parser.add_argument("--environments", "-e", nargs="+",
                      default=["dev", "test", "prod"],
                      choices=["dev", "test", "prod"],
                      help="Environments to deploy to (default: all)")
    parser.add_argument("--sequential", "-s", action="store_true",
                      help="Deploy environments sequentially (default: true)")

    args = parser.parse_args()

    if args.command == "destroy":
        print_colored("WARNING: This will destroy infrastructure in the following environments:", Colors.RED)
        print_colored(f"  {', '.join(args.environments)}", Colors.YELLOW)
        response = input("\nAre you sure you want to continue? (yes/no): ")
        if response.lower() != "yes":
            print_colored("Operation cancelled.", Colors.YELLOW)
            return

    deploy_to_environments(args.environments, args.command)

if __name__ == "__main__":
    main()