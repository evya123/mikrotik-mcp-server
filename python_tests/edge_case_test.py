#!/usr/bin/env python3
"""
Edge Case Tests for MikroTik Client

This script tests edge cases and error handling in the MikroTik API client.
"""
import os
import sys
import json
import time
import asyncio
import argparse
from typing import Dict, List, Any, Optional, TypedDict, Union, Callable
from dotenv import load_dotenv

# Add parent directory to path to import from python_src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from python_src.client.mikrotik import MikroTikClient
from python_src.types.models import MikroTikConfig


class TestResult(TypedDict, total=False):
    """Test result structure."""
    name: str
    success: bool
    data: Any
    error: Optional[str]
    duration: int


class EdgeCaseTester:
    """Edge case tests for MikroTik API client."""
    
    def __init__(self, config: MikroTikConfig):
        """
        Initialize the tester.
        
        Args:
            config: MikroTik API configuration
        """
        self.client = MikroTikClient(config)
        self.results: List[TestResult] = []
    
    async def run_test(self, name: str, test_fn: Callable) -> TestResult:
        """
        Run a test and capture the result.
        
        Args:
            name: Test name
            test_fn: Test function
            
        Returns:
            Test result
        """
        start_time = time.time()
        try:
            data = await test_fn()
            duration = int((time.time() - start_time) * 1000)
            return {"name": name, "success": True, "data": data, "duration": duration}
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            return {
                "name": name,
                "success": False,
                "error": str(e),
                "duration": duration
            }
    
    async def test_special_characters_in_filter(self) -> TestResult:
        """Test filter with special characters."""
        async def test_func():
            # Test filters with special characters
            special_chars = [
                'message~"login\\"failure"',  # Double quote
                'message~"login\'failure"',   # Single quote
                'message~"login\\\\failure"', # Backslash
                'message~"login(failure"',    # Parentheses
                'message~"login[failure"',    # Square brackets
                'message~"login*failure"',    # Asterisk
                'message~"login+failure"',    # Plus sign
            ]
            
            results = {}
            for filter_str in special_chars:
                try:
                    logs = await self.client.get_logs({"where": filter_str, "brief": True})
                    results[filter_str] = {
                        "count": len(logs),
                        "success": True
                    }
                except Exception as e:
                    results[filter_str] = {
                        "error": str(e),
                        "success": False
                    }
            
            return {
                "specialCharFilters": results,
                "message": "Tested filters with special characters"
            }
        return await self.run_test("Special Characters in Filter", test_func)
    
    async def test_empty_filter(self) -> TestResult:
        """Test empty filter."""
        async def test_func():
            empty_filters = [
                "",           # Empty string
                None,         # None value
                "   ",        # Whitespace
            ]
            
            results = {}
            for filter_str in empty_filters:
                try:
                    if filter_str is None:
                        logs = await self.client.get_logs({"brief": True})
                    else:
                        logs = await self.client.get_logs({"where": filter_str, "brief": True})
                    
                    results[str(filter_str)] = {
                        "count": len(logs),
                        "success": True
                    }
                except Exception as e:
                    results[str(filter_str)] = {
                        "error": str(e),
                        "success": False
                    }
            
            return {
                "emptyFilters": results,
                "message": "Tested empty filters"
            }
        return await self.run_test("Empty Filter", test_func)
    
    async def test_invalid_filter_syntax(self) -> TestResult:
        """Test invalid filter syntax."""
        async def test_func():
            invalid_filters = [
                'topics="system',     # Unclosed quote
                'topics~~"system"',   # Double operator
                'topics~system',      # Missing quotes
                'topics="system" or message="error"',  # Unsupported 'or' operator
                'topics',             # Missing operator and value
                '="system"',          # Missing field
                'unknown="value"',    # Unknown field
            ]
            
            results = {}
            for filter_str in invalid_filters:
                try:
                    logs = await self.client.get_logs({"where": filter_str, "brief": True})
                    results[filter_str] = {
                        "count": len(logs),
                        "success": True,
                        "handledGracefully": True
                    }
                except Exception as e:
                    results[filter_str] = {
                        "error": str(e),
                        "success": False,
                        "handledGracefully": False
                    }
            
            return {
                "invalidFilters": results,
                "message": "Tested invalid filter syntax"
            }
        return await self.run_test("Invalid Filter Syntax", test_func)
    
    async def test_large_log_limit(self) -> TestResult:
        """Test large log limit."""
        async def test_func():
            # Test with different log limits
            limits = [10, 100, 1000, 5000]
            
            results = {}
            for limit in limits:
                start_time = time.time()
                try:
                    logs = await self.client.get_logs({"brief": True}, max_logs=limit)
                    duration = int((time.time() - start_time) * 1000)
                    results[str(limit)] = {
                        "count": len(logs),
                        "duration": duration,
                        "success": True
                    }
                except Exception as e:
                    duration = int((time.time() - start_time) * 1000)
                    results[str(limit)] = {
                        "error": str(e),
                        "duration": duration,
                        "success": False
                    }
            
            return {
                "logLimits": results,
                "message": "Tested different log limits"
            }
        return await self.run_test("Large Log Limit", test_func)
    
    async def test_complex_filter_combinations(self) -> TestResult:
        """Test complex filter combinations."""
        async def test_func():
            complex_filters = [
                'topics~"system" and message~"login"',
                'topics~"dhcp" and message~"assigned"',
                'topics~"error" and message~"failure"',
                'topics~"info" and message~"user"',
                'topics~"warning" and message~"conflict"',
            ]
            
            results = {}
            for filter_str in complex_filters:
                try:
                    logs = await self.client.get_logs({"where": filter_str, "brief": True})
                    results[filter_str] = {
                        "count": len(logs),
                        "success": True,
                        "sample": [log.get("message") for log in logs[:2]] if logs else []
                    }
                except Exception as e:
                    results[filter_str] = {
                        "error": str(e),
                        "success": False
                    }
            
            return {
                "complexFilters": results,
                "message": "Tested complex filter combinations"
            }
        return await self.run_test("Complex Filter Combinations", test_func)
    
    async def test_parameter_combinations(self) -> TestResult:
        """Test parameter combinations."""
        async def test_func():
            parameter_combinations = [
                {"brief": True, "withExtraInfo": True},
                {"detail": True, "terse": True},  # Conflicting parameters
                {"countOnly": True, "brief": True},
                {"countOnly": True, "withExtraInfo": True},
                {"proplist": ["time", "message"], "brief": True},
            ]
            
            results = {}
            for i, params in enumerate(parameter_combinations):
                try:
                    logs = await self.client.get_logs(params)
                    results[f"combination_{i+1}"] = {
                        "params": params,
                        "success": True,
                        "resultType": type(logs).__name__,
                        "count": len(logs) if isinstance(logs, list) else "not list"
                    }
                except Exception as e:
                    results[f"combination_{i+1}"] = {
                        "params": params,
                        "error": str(e),
                        "success": False
                    }
            
            return {
                "parameterCombinations": results,
                "message": "Tested parameter combinations"
            }
        return await self.run_test("Parameter Combinations", test_func)
    
    async def run_all_tests(self):
        """Run all edge case tests."""
        print("🧪 Running Edge Case Tests...")
        print("=" * 50)
        
        tests = [
            self.test_special_characters_in_filter,
            self.test_empty_filter,
            self.test_invalid_filter_syntax,
            self.test_large_log_limit,
            self.test_complex_filter_combinations,
            self.test_parameter_combinations,
        ]
        
        for test in tests:
            result = await test()
            self.results.append(result)
            self.print_result(result)
        
        self.print_summary()
    
    def print_result(self, result: TestResult):
        """
        Print a test result.
        
        Args:
            result: Test result to print
        """
        status = "✅" if result["success"] else "❌"
        duration = f"{result['duration']}ms"
        
        print(f"{status} {result['name']} ({duration})")
        
        if result["success"] and "data" in result:
            if isinstance(result["data"], dict):
                print(f"   📊 {json.dumps(result['data'], indent=2)}")
            else:
                print(f"   📊 {result['data']}")
        elif not result["success"] and "error" in result:
            print(f"   ❌ Error: {result['error']}")
        
        print("")
    
    def print_summary(self):
        """Print a summary of all test results."""
        print("📋 Edge Case Test Summary")
        print("=" * 30)
        
        passed = len([r for r in self.results if r["success"]])
        failed = len([r for r in self.results if not r["success"]])
        total = len(self.results)
        avg_duration = sum(r["duration"] for r in self.results) / total if total else 0
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {failed}/{total}")
        print(f"⏱️  Average Duration: {int(avg_duration)}ms")
        
        if failed > 0:
            print("\n❌ Failed Tests:")
            for r in self.results:
                if not r["success"]:
                    print(f"   - {r['name']}: {r.get('error', 'Unknown error')}")
        
        print(f"\n🎯 Success Rate: {(passed / total * 100) if total else 0:.1f}%")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="MikroTik API Edge Case Tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    is_verbose = args.verbose
    
    print("🧪 MikroTik API Edge Case Test Suite")
    print("=" * 40)
    
    # Load environment variables from .env file
    load_dotenv()
    
    config = {
        "host": os.environ.get("MIKROTIK_HOST", "192.168.88.1"),
        "username": os.environ.get("MIKROTIK_USERNAME", "admin"),
        "password": os.environ.get("MIKROTIK_PASSWORD", ""),
        "port": int(os.environ.get("MIKROTIK_PORT")) if os.environ.get("MIKROTIK_PORT") else None,
        "useSSL": os.environ.get("MIKROTIK_USE_SSL") == "true",
    }
    
    if is_verbose:
        print("🔧 Configuration:")
        print(f"   Host: {config['host']}")
        print(f"   Username: {config['username']}")
        print(f"   Port: {config['port'] or 'default'}")
        print(f"   SSL: {config['useSSL']}")
        print("")
    
    tester = EdgeCaseTester(config)
    
    try:
        await tester.run_all_tests()
    except Exception as e:
        print(f"💥 Test suite failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
