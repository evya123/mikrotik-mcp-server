#!/usr/bin/env python3
"""
Full API Test Suite for MikroTik Client

This script tests the MikroTik API client with various test cases.
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


class MikroTikAPITester:
    """Test suite for MikroTik API client."""
    
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
    
    async def test_general_logs(self) -> TestResult:
        """Test retrieving general logs."""
        async def test_func():
            logs = await self.client.get_logs({"brief": True})
            return {
                "count": len(logs),
                "hasData": len(logs) > 0,
                "sample": [
                    {
                        "time": log.get("time"),
                        "topics": log.get("topics"),
                        "message": (log.get("message") or "")[:50] + "..."
                    }
                    for log in logs[:3]
                ]
            }
        return await self.run_test("General Logs", test_func)
    
    async def test_logs_with_different_filters(self) -> TestResult:
        """Test retrieving logs with different filters."""
        async def test_func():
            debug_logs = await self.client.get_debug_logs()
            error_logs = await self.client.get_error_logs()
            warning_logs = await self.client.get_warning_logs()
            info_logs = await self.client.get_info_logs()
            
            return {
                # Test that different filters actually return different results
                "debugCount": len(debug_logs),
                "errorCount": len(error_logs),
                "warningCount": len(warning_logs),
                "infoCount": len(info_logs),
                "hasData": any([debug_logs, error_logs, warning_logs, info_logs]),
                "sample": {
                    "debug": [
                        {
                            "time": log.get("time"),
                            "message": (log.get("message") or "")[:30] + "..."
                        }
                        for log in debug_logs[:1]
                    ],
                    "error": [
                        {
                            "time": log.get("time"),
                            "message": (log.get("message") or "")[:30] + "..."
                        }
                        for log in error_logs[:1]
                    ]
                }
            }
        return await self.run_test("Logs with Different Filters", test_func)
    
    async def test_logs_with_extra_info(self) -> TestResult:
        """Test retrieving logs with extra info."""
        async def test_func():
            logs = await self.client.get_logs_with_extra_info({"brief": True})
            return {
                "count": len(logs),
                "hasData": len(logs) > 0,
                "hasExtraInfo": any(log.get("extra_info") is not None for log in logs),
                "sample": [
                    {
                        "time": log.get("time"),
                        "message": (log.get("message") or "")[:50] + "...",
                        "extraInfo": log.get("extra_info")
                    }
                    for log in logs[:3]
                ]
            }
        return await self.run_test("Logs with Extra Info", test_func)
    
    async def test_logs_with_count_only(self) -> TestResult:
        """Test retrieving logs with count only."""
        async def test_func():
            count_only_result = await self.client.get_logs({"countOnly": True})
            regular_logs = await self.client.get_logs({"brief": True})
            return {
                # Test count-only vs regular logs
                "countOnlyResult": count_only_result,
                "regularLogsCount": len(regular_logs),
                "isCountOnlyDifferent": isinstance(count_only_result, list) and len(count_only_result) == 0,
                "message": f"Count-only returned {len(count_only_result) if isinstance(count_only_result, list) else 'N/A'} items, regular logs returned {len(regular_logs)} items"
            }
        return await self.run_test("Logs Count Only", test_func)
    
    async def test_filtered_logs(self) -> TestResult:
        """Test retrieving filtered logs."""
        async def test_func():
            filtered_logs = await self.client.get_logs_by_condition("topics~\"dhcp\"", {"brief": True})
            all_logs = await self.client.get_logs({"brief": True})
            return {
                # Test filtered vs unfiltered logs
                "filteredCount": len(filtered_logs),
                "allLogsCount": len(all_logs),
                "isSubset": len(filtered_logs) <= len(all_logs),
                "sample": [
                    {
                        "time": log.get("time"),
                        "topics": log.get("topics"),
                        "message": (log.get("message") or "")[:50] + "..."
                    }
                    for log in filtered_logs[:3]
                ]
            }
        return await self.run_test("Filtered Logs (DHCP)", test_func)
    
    async def test_filtering_behavior(self) -> TestResult:
        """Test filtering behavior."""
        async def test_func():
            no_filter = await self.client.get_logs({"brief": True})
            system_filter = await self.client.get_logs_by_condition("topics~\"system\"", {"brief": True})
            dns_filter = await self.client.get_logs_by_condition("topics~\"dns\"", {"brief": True})
            firewall_filter = await self.client.get_logs_by_condition("topics~\"firewall\"", {"brief": True})
            
            actual_system_logs = len([log for log in no_filter if log.get("topics") and "system" in log.get("topics", "")])
            actual_dns_logs = len([log for log in no_filter if log.get("topics") and "dns" in log.get("topics", "")])
            actual_firewall_logs = len([log for log in no_filter if log.get("topics") and "firewall" in log.get("topics", "")])
            
            return {
                # Test different filter approaches to understand behavior
                "noFilterCount": len(no_filter),
                "systemFilterCount": len(system_filter),
                "dnsFilterCount": len(dns_filter),
                "firewallFilterCount": len(firewall_filter),
                "actualSystemLogs": actual_system_logs,
                "actualDnsLogs": actual_dns_logs,
                "actualFirewallLogs": actual_firewall_logs,
                "sampleTopics": [log.get("topics") for log in no_filter[:5]],
                "message": f"Available topics: system({actual_system_logs}),"
                          f" dns({actual_dns_logs}),"
                          f" firewall({actual_firewall_logs}))"
            }
        return await self.run_test("Filtering Behavior Analysis", test_func)
    
    async def test_filter_syntax(self) -> TestResult:
        """Test different filter syntaxes."""
        async def test_func():
            dot_system = await self.client.get_logs_by_condition("topics~\".system\"", {"brief": True})
            dot_dns = await self.client.get_logs_by_condition("topics~\".dns\"", {"brief": True})
            exact_system = await self.client.get_logs_by_condition("topics=\"system\"", {"brief": True})
            exact_dns = await self.client.get_logs_by_condition("topics=\"dns\"", {"brief": True})
            
            return {
                # Test different filter syntaxes
                "dotSystemCount": len(dot_system),
                "dotDnsCount": len(dot_dns),
                "exactSystemCount": len(exact_system),
                "exactDnsCount": len(exact_dns),
                "message": f"Dot syntax: system({len(dot_system)}), dns({len(dot_dns)}) | Exact: system({len(exact_system)}), dns({len(exact_dns)})"
            }
        return await self.run_test("Filter Syntax Testing", test_func)
    
    async def test_diagnostic_analysis(self) -> TestResult:
        """Test diagnostic analysis."""
        async def test_func():
            # Test the exact same request multiple times to see if it's consistent
            request1 = await self.client.get_logs({"brief": True})
            request2 = await self.client.get_logs({"brief": True})
            request3 = await self.client.get_logs({"brief": True})
            
            # Test with and without where parameter
            no_where = await self.client.get_logs({"brief": True})
            with_where = await self.client.get_logs({"brief": True, "where": "topics~\"system\""})
            
            # Test count-only behavior
            count_only_result = await self.client.get_logs({"countOnly": True})
            
            # Test with extra info
            with_extra_info = await self.client.get_logs({"withExtraInfo": True})
            
            return {
                "request1Count": len(request1),
                "request2Count": len(request2),
                "request3Count": len(request3),
                "isConsistent": len(request1) == len(request2) == len(request3),
                
                "noWhereCount": len(no_where),
                "withWhereCount": len(with_where),
                "whereParameterWorks": len(no_where) != len(with_where),
                
                "countOnlyType": str(type(count_only_result)),
                "countOnlyLength": len(count_only_result) if isinstance(count_only_result, list) else "not array",
                
                "withExtraInfoCount": len(with_extra_info),
                "hasExtraInfoField": any(log.get("extra_info") is not None for log in with_extra_info),
                
                # Sample data analysis
                "sampleTopics": [log.get("topics") for log in no_where[:3]],
                "sampleMessages": [(log.get("message") or "")[:30] for log in no_where[:3]],
                
                "message": f"Consistent: {len(request1) == len(request2)}, Where works: {len(no_where) != len(with_where)}, Count-only type: {type(count_only_result).__name__}"
            }
        return await self.run_test("Diagnostic Analysis", test_func)
    
    async def test_find_endpoint(self) -> TestResult:
        """Test the /log/find endpoint."""
        async def test_func():
            all_logs = await self.client.get_logs({"brief": True})
            system_logs = await self.client.find_logs("topics~\"system\"")
            dns_logs = await self.client.find_logs("topics~\"dns\"")
            
            actual_system_logs = len([log for log in all_logs if log.get("topics") and "system" in log.get("topics", "")])
            actual_dns_logs = len([log for log in all_logs if log.get("topics") and "dns" in log.get("topics", "")])
            
            find_endpoint_works = len(system_logs) != len(all_logs) or len(dns_logs) != len(all_logs)
            
            return {
                # Test the /log/find endpoint which should properly support where parameter
                "allLogsCount": len(all_logs),
                "systemLogsCount": len(system_logs),
                "dnsLogsCount": len(dns_logs),
                "actualSystemLogs": actual_system_logs,
                "actualDnsLogs": actual_dns_logs,
                "findEndpointWorks": find_endpoint_works,
                "systemFilterRatio": len(system_logs) / len(all_logs) if len(all_logs) > 0 else 0,
                "dnsFilterRatio": len(dns_logs) / len(all_logs) if len(all_logs) > 0 else 0,
                "message": f"Find endpoint {'WORKS' if find_endpoint_works else 'BROKEN'}: "
                          f"system({len(system_logs)}/{len(all_logs)}), dns({len(dns_logs)}/{len(all_logs)})"
            }
        return await self.run_test("Find Endpoint Test", test_func)
    
    async def test_filter_syntax_discovery(self) -> TestResult:
        """Test filter syntax discovery."""
        async def test_func():
            print('\n🔍 Testing Filter Syntax Discovery...')
            
            # Get sample logs to understand the data structure
            sample_logs = await self.client.get_logs({"brief": True})
            sample_topics = [log.get("topics") for log in sample_logs[:10] if log.get("topics")]
            
            print('📊 Sample topics found:', sample_topics[:5])
            
            # Test various filter syntaxes with /log/print
            test_filters = [
                'topics~"system"',
                'topics~"info"', 
                'topics~"error"',
                'topics~"dhcp"',
                'message~"login"',
                'topics~"system" and message~"login"'
            ]
            
            filter_results = {}
            
            for filter_str in test_filters:
                try:
                    filtered_logs = await self.client.get_logs({"where": filter_str, "brief": True})
                    filter_results[filter_str] = len(filtered_logs)
                    print(f"✅ Filter \"{filter_str}\": {len(filtered_logs)} results")
                    if filtered_logs:
                        print(f"   Sample: {filtered_logs[0].get('topics')} - {(filtered_logs[0].get('message') or '')[:50]}")
                except Exception as e:
                    print(f"❌ Filter \"{filter_str}\": {str(e)}")
                    filter_results[filter_str] = 0
            
            # Test /log/find endpoint with correct syntax
            find_filters = [
                'topics~"system"',
                'topics~"info"',
                'message~"login"'
            ]
            
            find_results = {}
            
            for filter_str in find_filters:
                try:
                    find_logs = await self.client.find_logs(filter_str, {})
                    find_results[filter_str] = len(find_logs)
                    print(f"🔍 Find \"{filter_str}\": {len(find_logs)} results")
                    if find_logs:
                        print(f"   Sample: {find_logs[0].get('topics')} - {(find_logs[0].get('message') or '')[:50]}")
                except Exception as e:
                    print(f"❌ Find \"{filter_str}\": {str(e)}")
                    find_results[filter_str] = 0
            
            return {
                "sampleTopics": sample_topics[:5],
                "filterResults": filter_results,
                "findResults": find_results,
                "message": "Filter syntax discovery tests completed with correct ~ syntax"
            }
        return await self.run_test("Filter Syntax Discovery", test_func)
    
    async def test_logs_with_different_parameters(self) -> TestResult:
        """Test logs with different parameters."""
        async def test_func():
            brief_logs = await self.client.get_logs({"brief": True})
            detailed_logs = await self.client.get_logs({"detail": True})
            terse_logs = await self.client.get_logs({"terse": True})
            
            return {
                # Test different parameter combinations
                "briefCount": len(brief_logs),
                "detailedCount": len(detailed_logs),
                "terseCount": len(terse_logs),
                "allHaveData": all([brief_logs, detailed_logs, terse_logs]),
                "message": f"Brief: {len(brief_logs)}, Detailed: {len(detailed_logs)}, Terse: {len(terse_logs)}"
            }
        return await self.run_test("Logs with Different Parameters", test_func)
    
    async def test_system_info(self) -> TestResult:
        """Test retrieving system information."""
        async def test_func():
            # Get system info
            info = await self.client.get_system_info()
            
            # Validate that we got meaningful system info
            has_required_fields = info.get("uptime") and info.get("version") and info.get("cpu")
            
            return {
                "uptime": info.get("uptime"),
                "version": info.get("version"),
                "cpu": info.get("cpu"),
                "memory": f"{info.get('free_memory')}/{info.get('total_memory')}",
                "platform": info.get("platform"),
                "hasRequiredFields": info.get("cpu") if has_required_fields else False
            }
        return await self.run_test("System Information", test_func)
    
    async def test_connection(self) -> TestResult:
        """Test connection to the MikroTik device."""
        async def test_func():
            return {
                "connected": await self.client.test_connection()
            }
        return await self.run_test("Connection Test", test_func)
    
    async def test_user_working_example(self) -> TestResult:
        """Test the user's working example."""
        async def test_func():
            print('\n🔍 Testing User Working Example...')
            
            # Test the exact working example: "log print where message~"deassigned" and topics~"info""
            working_filter = 'message~"deassigned" and topics~"info"'
            
            try:
                results = await self.client.get_logs({"where": working_filter, "brief": True})
                print(f"✅ Working filter \"{working_filter}\": {len(results)} results")
                
                if results:
                    print('📊 Sample results:')
                    for i, log in enumerate(results[:3]):
                        print(f"   {i + 1}. {log.get('time')} {log.get('topics')} {log.get('message')}")
                
                return {
                    "filter": working_filter,
                    "resultCount": len(results),
                    "hasResults": bool(results),
                    "sampleResults": [
                        {
                            "time": log.get("time"),
                            "topics": log.get("topics"),
                            "message": (log.get("message") or "")[:50]
                        }
                        for log in results[:3]
                    ],
                    "message": f"Working example test: {len(results)} results found"
                }
            except Exception as e:
                print(f"❌ Working filter failed: {str(e)}")
                return {
                    "filter": working_filter,
                    "resultCount": 0,
                    "hasResults": False,
                    "error": str(e),
                    "message": f"Working example test failed: {str(e)}"
                }
        return await self.run_test("User Working Example", test_func)
    
    async def run_quick_test(self):
        """Run a quick test suite (essential APIs)."""
        print("🚀 Running Quick Test (Essential APIs)...")
        print("=" * 50)
        
        tests = [
            self.test_connection,
            self.test_system_info,
            self.test_general_logs
        ]
        
        for test in tests:
            result = await test()
            self.results.append(result)
            self.print_result(result)
        
        self.print_summary()
    
    async def run_full_test(self):
        """Run the full test suite."""
        print("🔍 Running Full API Test Suite...")
        print("=" * 50)
        
        tests = [
            self.test_connection,
            self.test_system_info,
            self.test_general_logs,
            self.test_logs_with_different_filters,
            self.test_logs_with_extra_info,
            self.test_logs_with_count_only,
            self.test_filtered_logs,
            self.test_filtering_behavior,
            self.test_filter_syntax,
            self.test_diagnostic_analysis,
            self.test_find_endpoint,
            self.test_filter_syntax_discovery,
            self.test_logs_with_different_parameters,
            self.test_user_working_example
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
        print("📋 Test Summary")
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
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="MikroTik API Test Suite")
    parser.add_argument("--full", "-f", action="store_true", help="Run full test suite")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    is_full_test = args.full
    is_verbose = args.verbose
    
    print("🧪 MikroTik API Test Suite")
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
    
    tester = MikroTikAPITester(config)
    
    try:
        if is_full_test:
            await tester.run_full_test()
        else:
            await tester.run_quick_test()
    except Exception as e:
        print(f"💥 Test suite failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())