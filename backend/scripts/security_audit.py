#!/usr/bin/env python3
"""
Security Audit Script for AI Learning Platform
Comprehensive security assessment covering common vulnerabilities and best practices
"""

import os
import sys
import re
import json
import subprocess
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict

# Add Django project to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection
from django.core.management import execute_from_command_line
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class SecurityAuditor:
    """Comprehensive security audit tool"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.findings = defaultdict(list)
        self.severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
    
    def run_full_audit(self) -> Dict[str, Any]:
        """Run complete security audit"""
        print("🔒 Starting AI Learning Platform Security Audit...")
        print("=" * 60)
        
        # Core security checks
        self.check_django_settings_security()
        self.check_authentication_security()
        self.check_database_security()
        self.check_api_security()
        self.check_input_validation()
        self.check_file_permissions()
        self.check_dependency_vulnerabilities()
        self.check_code_quality_security()
        self.check_environment_security()
        self.check_logging_security()
        
        # Generate report
        return self.generate_security_report()
    
    def add_finding(self, category: str, severity: str, title: str, description: str, 
                   recommendation: str = "", file_path: str = "", line_number: int = 0):
        """Add security finding"""
        finding = {
            'severity': severity,
            'title': title,
            'description': description,
            'recommendation': recommendation,
            'file_path': file_path,
            'line_number': line_number
        }
        
        self.findings[category].append(finding)
        self.severity_counts[severity] += 1
    
    def check_django_settings_security(self):
        """Check Django settings for security issues"""
        print("🔧 Checking Django Settings Security...")
        
        # Debug mode check
        if getattr(settings, 'DEBUG', False):
            self.add_finding(
                'django_settings',
                'critical',
                'Debug Mode Enabled in Production',
                'DEBUG=True exposes sensitive information and error details',
                'Set DEBUG=False in production environment',
                'config/settings.py'
            )
        
        # Secret key security
        secret_key = getattr(settings, 'SECRET_KEY', '')
        if len(secret_key) < 50:
            self.add_finding(
                'django_settings',
                'high',
                'Weak Secret Key',
                'SECRET_KEY should be at least 50 characters long',
                'Generate a strong, random SECRET_KEY',
                'config/settings.py'
            )
        
        if 'django-insecure' in secret_key:
            self.add_finding(
                'django_settings',
                'high',
                'Default/Insecure Secret Key',
                'Using default or obviously insecure SECRET_KEY',
                'Generate a unique, secure SECRET_KEY for production',
                'config/settings.py'
            )
        
        # HTTPS/SSL settings
        if not getattr(settings, 'SECURE_SSL_REDIRECT', False):
            self.add_finding(
                'django_settings',
                'medium',
                'HTTPS Redirect Not Enforced',
                'SECURE_SSL_REDIRECT is not enabled',
                'Enable SECURE_SSL_REDIRECT for production',
                'config/settings.py'
            )
        
        if not getattr(settings, 'SECURE_HSTS_SECONDS', 0):
            self.add_finding(
                'django_settings',
                'medium',
                'HSTS Not Configured',
                'HTTP Strict Transport Security not configured',
                'Set SECURE_HSTS_SECONDS to at least 3600',
                'config/settings.py'
            )
        
        # CORS settings
        cors_allow_all = getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False)
        if cors_allow_all:
            self.add_finding(
                'django_settings',
                'high',
                'Permissive CORS Policy',
                'CORS_ALLOW_ALL_ORIGINS=True allows any origin',
                'Restrict CORS to specific trusted origins',
                'config/settings.py'
            )
        
        # Database password in settings
        databases = getattr(settings, 'DATABASES', {})
        for db_name, db_config in databases.items():
            if 'password' in str(db_config).lower() and 'password' in db_config.get('PASSWORD', ''):
                self.add_finding(
                    'django_settings',
                    'medium',
                    'Database Password in Settings',
                    f'Database {db_name} password visible in settings',
                    'Use environment variables for sensitive credentials',
                    'config/settings.py'
                )
    
    def check_authentication_security(self):
        """Check authentication and authorization security"""
        print("🔐 Checking Authentication Security...")
        
        # Password validation
        auth_password_validators = getattr(settings, 'AUTH_PASSWORD_VALIDATORS', [])
        if not auth_password_validators:
            self.add_finding(
                'authentication',
                'medium',
                'No Password Validation',
                'AUTH_PASSWORD_VALIDATORS is empty',
                'Configure strong password validation rules',
                'config/settings.py'
            )
        
        # JWT settings
        jwt_settings = getattr(settings, 'SIMPLE_JWT', {})
        access_token_lifetime = jwt_settings.get('ACCESS_TOKEN_LIFETIME')
        if access_token_lifetime and access_token_lifetime.total_seconds() > 3600:
            self.add_finding(
                'authentication',
                'medium',
                'Long JWT Access Token Lifetime',
                f'JWT access tokens valid for {access_token_lifetime}',
                'Reduce ACCESS_TOKEN_LIFETIME to maximum 1 hour',
                'config/settings.py'
            )
        
        # Check for default/weak admin users
        try:
            admin_users = User.objects.filter(role='admin')
            for user in admin_users:
                if user.email in ['admin@example.com', 'admin@test.com', 'root@localhost']:
                    self.add_finding(
                        'authentication',
                        'high',
                        'Default Admin Account',
                        f'Default admin account found: {user.email}',
                        'Remove or secure default admin accounts'
                    )
        except Exception as e:
            logger.warning(f"Could not check admin users: {e}")
    
    def check_database_security(self):
        """Check database security configuration"""
        print("🗄️ Checking Database Security...")
        
        # Check database connection encryption
        db_config = settings.DATABASES['default']
        
        if 'sqlite' in db_config.get('ENGINE', '').lower():
            self.add_finding(
                'database',
                'low',
                'SQLite Database in Production',
                'Using SQLite database which has limitations for production',
                'Consider using PostgreSQL or MySQL for production'
            )
        
        # Check for SQL injection protection
        if 'OPTIONS' not in db_config or 'sql_mode' not in db_config.get('OPTIONS', {}):
            self.add_finding(
                'database',
                'medium',
                'Database SQL Mode Not Configured',
                'Database SQL mode not explicitly configured',
                'Set appropriate SQL mode for security'
            )
        
        # Check database permissions
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")  # Basic connectivity test
        except Exception as e:
            self.add_finding(
                'database',
                'info',
                'Database Connection Test',
                f'Database connectivity: {str(e)}',
                'Ensure database is properly configured'
            )
    
    def check_api_security(self):
        """Check API endpoint security"""
        print("🌐 Checking API Security...")
        
        # Check for API rate limiting
        middleware = getattr(settings, 'MIDDLEWARE', [])
        has_rate_limiting = any('throttl' in mw.lower() or 'rate' in mw.lower() for mw in middleware)
        
        if not has_rate_limiting:
            self.add_finding(
                'api_security',
                'medium',
                'No API Rate Limiting',
                'No rate limiting middleware detected',
                'Implement API rate limiting to prevent abuse'
            )
        
        # Check REST framework settings
        rest_settings = getattr(settings, 'REST_FRAMEWORK', {})
        
        # Check authentication classes
        auth_classes = rest_settings.get('DEFAULT_AUTHENTICATION_CLASSES', [])
        if not auth_classes:
            self.add_finding(
                'api_security',
                'high',
                'No Default Authentication Required',
                'No default authentication classes configured',
                'Configure default authentication for API endpoints'
            )
        
        # Check permission classes
        permission_classes = rest_settings.get('DEFAULT_PERMISSION_CLASSES', [])
        if 'AllowAny' in str(permission_classes):
            self.add_finding(
                'api_security',
                'high',
                'Permissive Default Permissions',
                'Default permissions allow any access',
                'Configure restrictive default permissions'
            )
        
        # Check for CSRF exemption
        self.check_csrf_exemptions()
    
    def check_csrf_exemptions(self):
        """Check for CSRF exemptions"""
        csrf_exempt_files = []
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                if '@csrf_exempt' in content:
                    csrf_exempt_files.append(str(py_file))
            except (UnicodeDecodeError, PermissionError):
                continue
        
        if csrf_exempt_files:
            self.add_finding(
                'api_security',
                'medium',
                'CSRF Exemptions Found',
                f'CSRF exempt views found in {len(csrf_exempt_files)} files',
                'Review CSRF exemptions and ensure they are necessary',
                ', '.join(csrf_exempt_files[:3])  # Show first 3 files
            )
    
    def check_input_validation(self):
        """Check input validation and sanitization"""
        print("🔍 Checking Input Validation...")
        
        # Check for potential SQL injection points
        sql_injection_patterns = [
            r'\.raw\(',
            r'\.extra\(',
            r'cursor\.execute\(',
            r'connection\.cursor\(\)'
        ]
        
        vulnerable_files = []
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                for pattern in sql_injection_patterns:
                    if re.search(pattern, content):
                        vulnerable_files.append(str(py_file))
                        break
            except (UnicodeDecodeError, PermissionError):
                continue
        
        if vulnerable_files:
            self.add_finding(
                'input_validation',
                'high',
                'Potential SQL Injection Points',
                f'Raw SQL usage found in {len(vulnerable_files)} files',
                'Review raw SQL usage and ensure proper parameterization',
                ', '.join(vulnerable_files[:3])
            )
        
        # Check for XSS vulnerabilities
        xss_patterns = [
            r'mark_safe\(',
            r'\|safe',
            r'SafeString\(',
            r'Markup\('
        ]
        
        xss_vulnerable_files = []
        for py_file in self.project_root.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                for pattern in xss_patterns:
                    if re.search(pattern, content):
                        xss_vulnerable_files.append(str(py_file))
                        break
            except (UnicodeDecodeError, PermissionError):
                continue
        
        if xss_vulnerable_files:
            self.add_finding(
                'input_validation',
                'medium',
                'Potential XSS Vulnerabilities',
                f'Unsafe string handling found in {len(xss_vulnerable_files)} files',
                'Review use of mark_safe and |safe filter',
                ', '.join(xss_vulnerable_files[:3])
            )
    
    def check_file_permissions(self):
        """Check file and directory permissions"""
        print("📁 Checking File Permissions...")
        
        # Check critical files permissions
        critical_files = [
            'config/settings.py',
            '.env',
            'manage.py'
        ]
        
        for file_path in critical_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                stat = full_path.stat()
                permissions = oct(stat.st_mode)[-3:]
                
                # Check if file is world-readable
                if int(permissions[2]) >= 4:
                    self.add_finding(
                        'file_permissions',
                        'medium',
                        'World-Readable Sensitive File',
                        f'{file_path} is world-readable ({permissions})',
                        'Restrict file permissions to owner/group only',
                        str(full_path)
                    )
    
    def check_dependency_vulnerabilities(self):
        """Check for known vulnerabilities in dependencies"""
        print("📦 Checking Dependency Vulnerabilities...")
        
        requirements_files = [
            'requirements.txt',
            'requirements/production.txt',
            'requirements/base.txt',
            'Pipfile'
        ]
        
        for req_file in requirements_files:
            req_path = self.project_root / req_file
            if req_path.exists():
                try:
                    # Run safety check if available
                    result = subprocess.run(
                        ['safety', 'check', '-r', str(req_path)],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode != 0 and 'vulnerabilities found' in result.stdout:
                        self.add_finding(
                            'dependencies',
                            'high',
                            'Vulnerable Dependencies Found',
                            'Safety check found vulnerabilities in dependencies',
                            'Update vulnerable packages using: pip install --upgrade <package>',
                            str(req_path)
                        )
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    self.add_finding(
                        'dependencies',
                        'info',
                        'Dependency Security Check Unavailable',
                        'Could not run dependency vulnerability check',
                        'Install safety: pip install safety'
                    )
    
    def check_code_quality_security(self):
        """Check code quality related to security"""
        print("🧹 Checking Code Quality Security...")
        
        # Check for hardcoded secrets
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded Password'),
            (r'api_key\s*=\s*["\'][^"\']+["\']', 'Hardcoded API Key'),
            (r'secret\s*=\s*["\'][^"\']+["\']', 'Hardcoded Secret'),
            (r'token\s*=\s*["\'][^"\']+["\']', 'Hardcoded Token'),
        ]
        
        secret_files = []
        
        for py_file in self.project_root.rglob("*.py"):
            if 'test' in str(py_file) or 'migrations' in str(py_file):
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8')
                for pattern, desc in secret_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        secret_files.append((str(py_file), desc))
            except (UnicodeDecodeError, PermissionError):
                continue
        
        if secret_files:
            self.add_finding(
                'code_quality',
                'high',
                'Hardcoded Secrets Detected',
                f'Found {len(secret_files)} potential hardcoded secrets',
                'Move secrets to environment variables',
                ', '.join([f[0] for f in secret_files[:3]])
            )
        
        # Check for debug statements
        debug_patterns = [
            r'print\(',
            r'pdb\.set_trace\(',
            r'breakpoint\(',
            r'console\.log\('
        ]
        
        debug_files = []
        for py_file in self.project_root.rglob("*.py"):
            if 'test' in str(py_file) or 'migrations' in str(py_file):
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8')
                for pattern in debug_patterns:
                    if re.search(pattern, content):
                        debug_files.append(str(py_file))
                        break
            except (UnicodeDecodeError, PermissionError):
                continue
        
        if debug_files:
            self.add_finding(
                'code_quality',
                'low',
                'Debug Statements in Code',
                f'Found debug statements in {len(debug_files)} files',
                'Remove debug statements before production',
                ', '.join(debug_files[:3])
            )
    
    def check_environment_security(self):
        """Check environment and deployment security"""
        print("🌍 Checking Environment Security...")
        
        # Check .env file
        env_file = self.project_root / '.env'
        if env_file.exists():
            try:
                content = env_file.read_text()
                
                # Check for example values
                example_patterns = [
                    'changeme',
                    'your-secret-key',
                    'password123',
                    'localhost'
                ]
                
                for pattern in example_patterns:
                    if pattern in content.lower():
                        self.add_finding(
                            'environment',
                            'medium',
                            'Example Values in Environment',
                            f'Found example/default values in .env file',
                            'Replace all example values with production values'
                        )
                        break
                
                # Check for weak values
                if 'SECRET_KEY' in content:
                    secret_match = re.search(r'SECRET_KEY\s*=\s*([^\n]+)', content)
                    if secret_match and len(secret_match.group(1).strip('"\'')) < 32:
                        self.add_finding(
                            'environment',
                            'high',
                            'Weak Secret Key in Environment',
                            'SECRET_KEY in .env file is too short',
                            'Generate a strong SECRET_KEY with at least 32 characters'
                        )
            except (UnicodeDecodeError, PermissionError):
                pass
        else:
            self.add_finding(
                'environment',
                'info',
                'No Environment File Found',
                'No .env file found - ensure environment variables are configured',
                'Create .env file with necessary environment variables'
            )
        
        # Check for Docker security
        dockerfile = self.project_root / 'Dockerfile'
        if dockerfile.exists():
            try:
                content = dockerfile.read_text()
                if 'FROM' in content and ':latest' in content:
                    self.add_finding(
                        'environment',
                        'medium',
                        'Using Latest Docker Tag',
                        'Using :latest tag in Dockerfile',
                        'Pin specific versions for Docker base images'
                    )
            except (UnicodeDecodeError, PermissionError):
                pass
    
    def check_logging_security(self):
        """Check logging configuration for security"""
        print("📋 Checking Logging Security...")
        
        logging_config = getattr(settings, 'LOGGING', {})
        
        if not logging_config:
            self.add_finding(
                'logging',
                'medium',
                'No Logging Configuration',
                'LOGGING setting not configured',
                'Configure comprehensive logging for security monitoring'
            )
        else:
            # Check log levels
            loggers = logging_config.get('loggers', {})
            root_logger = loggers.get('', {})
            root_level = root_logger.get('level', 'DEBUG')
            
            if root_level == 'DEBUG' and not getattr(settings, 'DEBUG', False):
                self.add_finding(
                    'logging',
                    'low',
                    'Debug Logging in Production',
                    'Root logger set to DEBUG level in production',
                    'Set logging level to INFO or WARNING in production'
                )
            
            # Check for security-related loggers
            security_loggers = [
                'django.security',
                'django.request',
                'apps.authentication',
                'apps.users'
            ]
            
            missing_security_loggers = []
            for logger_name in security_loggers:
                if logger_name not in loggers:
                    missing_security_loggers.append(logger_name)
            
            if missing_security_loggers:
                self.add_finding(
                    'logging',
                    'medium',
                    'Missing Security Loggers',
                    f'Missing loggers for: {", ".join(missing_security_loggers)}',
                    'Configure loggers for security-related events'
                )
    
    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        print("\n" + "=" * 60)
        print("📊 SECURITY AUDIT REPORT")
        print("=" * 60)
        
        # Summary
        total_findings = sum(self.severity_counts.values())
        print(f"\n📈 SUMMARY:")
        print(f"Total Findings: {total_findings}")
        print(f"Critical: {self.severity_counts['critical']}")
        print(f"High: {self.severity_counts['high']}")
        print(f"Medium: {self.severity_counts['medium']}")
        print(f"Low: {self.severity_counts['low']}")
        print(f"Info: {self.severity_counts['info']}")
        
        # Risk assessment
        risk_score = (
            self.severity_counts['critical'] * 10 +
            self.severity_counts['high'] * 7 +
            self.severity_counts['medium'] * 4 +
            self.severity_counts['low'] * 2 +
            self.severity_counts['info'] * 1
        )
        
        if risk_score >= 50:
            risk_level = "HIGH RISK"
            risk_color = "🔴"
        elif risk_score >= 25:
            risk_level = "MEDIUM RISK"
            risk_color = "🟡"
        else:
            risk_level = "LOW RISK"
            risk_color = "🟢"
        
        print(f"\n{risk_color} OVERALL RISK LEVEL: {risk_level} (Score: {risk_score})")
        
        # Detailed findings by category
        print(f"\n📋 DETAILED FINDINGS:")
        print("-" * 40)
        
        for category, findings in self.findings.items():
            if not findings:
                continue
                
            print(f"\n🔶 {category.upper().replace('_', ' ')} ({len(findings)} findings)")
            
            for i, finding in enumerate(findings, 1):
                severity_emoji = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🔵',
                    'info': '⚪'
                }
                
                print(f"\n  {i}. {severity_emoji[finding['severity']]} {finding['title']}")
                print(f"     Severity: {finding['severity'].upper()}")
                print(f"     Description: {finding['description']}")
                
                if finding['recommendation']:
                    print(f"     Recommendation: {finding['recommendation']}")
                
                if finding['file_path']:
                    file_path = finding['file_path']
                    if len(file_path) > 80:
                        file_path = "..." + file_path[-77:]
                    print(f"     File: {file_path}")
                    
                    if finding['line_number']:
                        print(f"     Line: {finding['line_number']}")
        
        # Priority actions
        print(f"\n🎯 PRIORITY ACTIONS:")
        print("-" * 30)
        
        critical_high = [
            finding for findings in self.findings.values() 
            for finding in findings 
            if finding['severity'] in ['critical', 'high']
        ]
        
        if critical_high:
            print("Address these critical/high severity issues immediately:")
            for i, finding in enumerate(critical_high[:5], 1):
                print(f"{i}. {finding['title']}")
                if finding['recommendation']:
                    print(f"   → {finding['recommendation']}")
        else:
            print("✅ No critical or high severity issues found!")
        
        # Security checklist
        print(f"\n✅ SECURITY CHECKLIST:")
        print("-" * 30)
        
        checklist_items = [
            ("DEBUG mode disabled in production", self.severity_counts['critical'] == 0),
            ("Strong SECRET_KEY configured", 'Weak Secret Key' not in str(self.findings)),
            ("HTTPS/SSL configured", 'HTTPS Redirect' not in str(self.findings)),
            ("CORS properly configured", 'Permissive CORS' not in str(self.findings)),
            ("Input validation in place", self.severity_counts['high'] < 3),
            ("Dependencies up to date", 'Vulnerable Dependencies' not in str(self.findings)),
            ("No hardcoded secrets", 'Hardcoded Secrets' not in str(self.findings)),
            ("Logging configured", 'No Logging Configuration' not in str(self.findings))
        ]
        
        for item, status in checklist_items:
            status_emoji = "✅" if status else "❌"
            print(f"{status_emoji} {item}")
        
        # Generate report data
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_findings': total_findings,
                'severity_counts': self.severity_counts,
                'risk_score': risk_score,
                'risk_level': risk_level
            },
            'findings': dict(self.findings),
            'checklist': dict(checklist_items)
        }
        
        # Save report to file
        report_file = self.project_root / 'security_audit_report.json'
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n💾 Report saved to: {report_file}")
        print(f"\n🔒 Security audit completed!")
        
        return report_data

def main():
    """Main function to run security audit"""
    auditor = SecurityAuditor()
    report = auditor.run_full_audit()
    
    # Exit with error code if critical issues found
    if report['summary']['severity_counts']['critical'] > 0:
        sys.exit(1)
    elif report['summary']['severity_counts']['high'] > 0:
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()
