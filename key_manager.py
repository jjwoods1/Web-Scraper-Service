#!/usr/bin/env python3
"""
API Key Management CLI Tool
"""
import os
import sys
import argparse
from datetime import datetime
from auth import api_key_manager

def generate_key(name):
    """Generate a new API key."""
    key = api_key_manager.generate_api_key(name)
    print(f"Generated new API key: {key}")
    print(f"Name: {name}")
    print(f"Created: {datetime.utcnow().isoformat()}")
    print("\n⚠️  IMPORTANT: Store this key securely. It will not be shown again.")
    return key

def list_keys():
    """List all API keys."""
    keys = api_key_manager.list_api_keys()
    
    if not keys:
        print("No API keys found.")
        return
    
    print(f"Found {len(keys)} API keys:")
    print("-" * 60)
    for key in keys:
        status = "✅ Active" if key['active'] else "❌ Revoked"
        print(f"Key: {key['key_id']}")
        print(f"Name: {key['name']}")
        print(f"Created: {key['created_at']}")
        print(f"Status: {status}")
        print("-" * 60)

def revoke_key(key):
    """Revoke an API key."""
    success = api_key_manager.revoke_api_key(key)
    
    if success:
        print(f"✅ API key revoked successfully: {key[:8]}...")
    else:
        print(f"❌ API key not found: {key[:8]}...")

def validate_key(key):
    """Validate an API key."""
    key_info = api_key_manager.validate_api_key(key)
    
    if key_info:
        print(f"✅ API key is valid")
        print(f"Name: {key_info['name']}")
        print(f"Created: {key_info['created_at']}")
        print(f"Active: {key_info['active']}")
    else:
        print(f"❌ API key is invalid or revoked")

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description='API Key Management Tool')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate key command
    generate_parser = subparsers.add_parser('generate', help='Generate a new API key')
    generate_parser.add_argument('name', help='Name for the API key')
    
    # List keys command
    list_parser = subparsers.add_parser('list', help='List all API keys')
    
    # Revoke key command
    revoke_parser = subparsers.add_parser('revoke', help='Revoke an API key')
    revoke_parser.add_argument('key', help='API key to revoke')
    
    # Validate key command
    validate_parser = subparsers.add_parser('validate', help='Validate an API key')
    validate_parser.add_argument('key', help='API key to validate')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'generate':
            generate_key(args.name)
        elif args.command == 'list':
            list_keys()
        elif args.command == 'revoke':
            revoke_key(args.key)
        elif args.command == 'validate':
            validate_key(args.key)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()