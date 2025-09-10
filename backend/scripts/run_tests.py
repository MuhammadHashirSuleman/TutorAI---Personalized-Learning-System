#!/usr/bin/env python3
"""
Comprehensive Test Runner for AI Learning Platform
Runs all tests including unit tests, integration tests, security audit, and performance tests
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple
import argparse

# Add Django project to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

class TestRunner:
    """Comprehensive test runner"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_results = {}
        self.start_time = time.time()
    
    def run_all_tests(self, test_types: List[str] = None) -> Dict:
        """Run all specified test types"""
        if test_types is None:
            test_types = ['unit', 'integration', 'security', 'performance']
        
        print("🚀 Starting AI Learning Platform Test Suite")
        print("=" * 60)
        
        results = {}
        
        if 'unit' in test_types:
            results['unit_tests'] = self.run_unit_tests()
        
        if 'integration' in test_types:
            results['integration_tests'] = self.run_integration_tests()
        
        if 'api' in test_types:
            results['api_tests'] = self.run_api_tests()
        
        if 'security' in test_types:
            results['security_audit'] = self.run_security_audit()
        
        if 'performance' in test_types:
            results['performance_tests'] = self.run_performance_tests()
        
        if 'lint' in test_types:
            results['code_quality'] = self.run_code_quality_checks()
        
        # Generate summary report
        self.generate_test_report(results)
        
        return results
    
    def run_unit_tests(self) -> Dict:
        """Run Django unit tests"""
        print("\n🧪 Running Unit Tests...")
        print("-" * 30)
        
        try:
            # Run Django tests
            cmd = [sys.executable, 'manage.py', 'test', '--verbosity=2', '--keepdb']
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            success = result.returncode == 0
            
            return {
                'success': success,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'duration': time.time() - self.start_time
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Unit tests timed out after 300 seconds',
                'duration': 300
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'duration': time.time() - self.start_time
            }
    
    def run_integration_tests(self) -> Dict:
        """Run integration tests"""
        print("\n🔗 Running Integration Tests...")
        print("-" * 30)
        
        try:
            # Run pytest for integration tests
            cmd = [
                sys.executable, '-m', 'pytest',
                'tests/test_ai_learning_platform.py::IntegrationTestCase',
                '-v', '--tb=short'
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=180
            )
            
            success = result.returncode == 0
            
            return {
                'success': success,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'duration': time.time() - self.start_time
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Integration tests timed out after 180 seconds',
                'duration': 180
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'duration': time.time() - self.start_time
            }
    
    def run_api_tests(self) -> Dict:
        """Run API endpoint tests"""
        print("\n🌐 Running API Tests...")
        print("-" * 30)
        
        try:
            # Run API-specific tests
            cmd = [
                sys.executable, '-m', 'pytest',
                'tests/test_ai_learning_platform.py::QuizManagementTestCase',
                'tests/test_ai_learning_platform.py::AuthenticationTestCase',
                'tests/test_ai_learning_platform.py::RecommendationEngineTestCase',
                '-v', '--tb=short'
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            success = result.returncode == 0
            
            return {
                'success': success,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'duration': time.time() - self.start_time
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'duration': time.time() - self.start_time
            }
    
    def run_security_audit(self) -> Dict:
        """Run security audit"""
        print("\n🔒 Running Security Audit...")
        print("-" * 30)
        
        try:
            # Run security audit script
            cmd = [sys.executable, 'scripts/security_audit.py']
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Security audit returns exit codes based on severity
            # 0 = no issues, 1 = critical issues, 2 = high issues
            success = result.returncode == 0
            
            return {
                'success': success,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'critical_issues': result.returncode == 1,
                'high_issues': result.returncode == 2,
                'duration': time.time() - self.start_time
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Security audit timed out after 60 seconds',
                'duration': 60
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'duration': time.time() - self.start_time
            }
    
    def run_performance_tests(self) -> Dict:
        """Run performance tests"""
        print("\n⚡ Running Performance Tests...")
        print("-" * 30)
        
        try:
            # Run performance-specific tests
            cmd = [
                sys.executable, '-m', 'pytest',
                'tests/test_ai_learning_platform.py::PerformanceTestCase',
                '-v', '--tb=short'
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            success = result.returncode == 0
            
            return {
                'success': success,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'duration': time.time() - self.start_time
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'duration': time.time() - self.start_time
            }
    
    def run_code_quality_checks(self) -> Dict:
        """Run code quality checks"""
        print("\n🧹 Running Code Quality Checks...")
        print("-" * 30)
        
        results = {}
        
        # Run flake8 if available
        try:
            cmd = ['flake8', '--max-line-length=120', '--exclude=migrations,venv', '.']
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            results['flake8'] = {
                'success': result.returncode == 0,
                'issues': result.stdout.count('\n') if result.stdout else 0,
                'output': result.stdout
            }
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            results['flake8'] = {'success': None, 'error': 'flake8 not available'}
        
        # Run black format check if available
        try:
            cmd = ['black', '--check', '--diff', '.']
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            results['black'] = {
                'success': result.returncode == 0,
                'issues': result.stdout.count('would reformat') if result.stdout else 0,
                'output': result.stdout
            }
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            results['black'] = {'success': None, 'error': 'black not available'}
        
        # Check imports with isort if available
        try:
            cmd = ['isort', '--check-only', '--diff', '.']
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            results['isort'] = {
                'success': result.returncode == 0,
                'issues': result.stdout.count('ERROR') if result.stdout else 0,
                'output': result.stdout
            }
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            results['isort'] = {'success': None, 'error': 'isort not available'}
        
        # Overall success
        success = all(
            r.get('success', True) for r in results.values() 
            if r.get('success') is not None
        )
        
        results['overall_success'] = success
        return results
    
    def run_coverage_analysis(self) -> Dict:
        """Run test coverage analysis"""
        print("\n📊 Running Coverage Analysis...")
        print("-" * 30)
        
        try:
            # Run tests with coverage
            cmd = [
                'coverage', 'run', '--source=.', 'manage.py', 'test',
                '--verbosity=0'
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                # Generate coverage report
                report_cmd = ['coverage', 'report', '--skip-empty']
                report_result = subprocess.run(
                    report_cmd,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                # Extract coverage percentage
                coverage_line = None
                for line in report_result.stdout.split('\n'):
                    if 'TOTAL' in line:
                        coverage_line = line
                        break
                
                coverage_percent = 0
                if coverage_line:
                    parts = coverage_line.split()
                    if len(parts) >= 4 and '%' in parts[-1]:
                        coverage_percent = int(parts[-1].replace('%', ''))
                
                return {
                    'success': True,
                    'coverage_percent': coverage_percent,
                    'report': report_result.stdout,
                    'duration': time.time() - self.start_time
                }
            else:
                return {
                    'success': False,
                    'error': 'Coverage tests failed',
                    'stderr': result.stderr
                }
                
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            return {
                'success': False,
                'error': f'Coverage analysis failed: {str(e)}'
            }
    
    def generate_test_report(self, results: Dict):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 TEST EXECUTION REPORT")
        print("=" * 60)
        
        total_duration = time.time() - self.start_time
        
        # Summary
        print(f"\n⏱️  EXECUTION SUMMARY:")
        print(f"Total Duration: {total_duration:.2f} seconds")
        print(f"Test Categories: {len(results)}")
        
        # Results by category
        passed = failed = skipped = 0
        
        for category, result in results.items():
            print(f"\n🔸 {category.upper().replace('_', ' ')}:")
            
            if isinstance(result, dict) and 'success' in result:
                status = "✅ PASSED" if result['success'] else "❌ FAILED"
                print(f"   Status: {status}")
                
                if result['success']:
                    passed += 1
                else:
                    failed += 1
                    if 'error' in result:
                        print(f"   Error: {result['error']}")
                
                if 'duration' in result:
                    print(f"   Duration: {result['duration']:.2f}s")
                
                # Special handling for security audit
                if category == 'security_audit' and not result['success']:
                    if result.get('critical_issues'):
                        print("   ⚠️  Critical security issues found!")
                    elif result.get('high_issues'):
                        print("   ⚠️  High severity security issues found!")
                
            elif category == 'code_quality':
                # Handle code quality results
                quality_passed = result.get('overall_success', False)
                status = "✅ PASSED" if quality_passed else "❌ FAILED"
                print(f"   Status: {status}")
                
                if quality_passed:
                    passed += 1
                else:
                    failed += 1
                
                for tool, tool_result in result.items():
                    if tool == 'overall_success':
                        continue
                    
                    if isinstance(tool_result, dict):
                        if tool_result.get('success') is None:
                            print(f"   {tool}: SKIPPED ({tool_result.get('error', 'not available')})")
                        elif tool_result['success']:
                            print(f"   {tool}: ✅ PASSED")
                        else:
                            issues = tool_result.get('issues', 'unknown')
                            print(f"   {tool}: ❌ FAILED ({issues} issues)")
            else:
                skipped += 1
                print("   Status: ⏭️  SKIPPED")
        
        # Overall summary
        print(f"\n📈 OVERALL RESULTS:")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️  Skipped: {skipped}")
        
        success_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        # Final verdict
        if failed == 0:
            print(f"\n🎉 ALL TESTS PASSED! 🎉")
            verdict = "PASS"
        elif any(results.get('security_audit', {}).get('critical_issues', False) for results in [results]):
            print(f"\n🚨 CRITICAL SECURITY ISSUES FOUND! 🚨")
            verdict = "CRITICAL_FAIL"
        else:
            print(f"\n⚠️  SOME TESTS FAILED")
            verdict = "FAIL"
        
        # Save report
        report_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': total_duration,
            'verdict': verdict,
            'summary': {
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'success_rate': success_rate
            },
            'results': results
        }
        
        import json
        report_file = self.project_root / 'test_report.json'
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n💾 Detailed report saved to: {report_file}")
        
        return report_data

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='AI Learning Platform Test Runner')
    parser.add_argument(
        '--tests',
        nargs='+',
        choices=['unit', 'integration', 'api', 'security', 'performance', 'lint', 'coverage'],
        default=['unit', 'integration', 'api', 'security'],
        help='Test types to run (default: unit integration api security)'
    )
    parser.add_argument(
        '--fast',
        action='store_true',
        help='Run fast tests only (skip security and performance)'
    )
    parser.add_argument(
        '--security-only',
        action='store_true',
        help='Run security audit only'
    )
    
    args = parser.parse_args()
    
    if args.fast:
        test_types = ['unit', 'api', 'lint']
    elif args.security_only:
        test_types = ['security']
    else:
        test_types = args.tests
    
    runner = TestRunner()
    results = runner.run_all_tests(test_types)
    
    # Exit with appropriate code
    if any(not result.get('success', False) for result in results.values() if isinstance(result, dict) and 'success' in result):
        # Check for critical security issues
        if results.get('security_audit', {}).get('critical_issues'):
            sys.exit(3)  # Critical security issues
        else:
            sys.exit(1)  # General test failures
    else:
        sys.exit(0)  # All tests passed

if __name__ == '__main__':
    main()
