# -*- coding: utf-8 -*-
"""
系统数据生成工具 - 支持 API Fox 系统类动态变量
Git、文件系统、版本号、目录结构等
"""
import random
import string
import os
from typing import Dict, Any, List


class SystemTools:
    """系统数据工具类 - 100% 兼容 API Fox"""
    
    # Git 数据
    GIT_BRANCHES = [
        'main', 'master', 'develop', 'feature/login', 'feature/payment',
        'bugfix/issue-123', 'hotfix/critical', 'release/v1.0.0',
        'feature/user-profile', 'feature/dashboard', 'feature/api-integration'
    ]
    
    GIT_COMMIT_MESSAGES = [
        'Initial commit', 'Update README', 'Fix bug', 'Add feature',
        'Refactor code', 'Update dependencies', 'Merge pull request',
        'Fix typo', 'Add tests', 'Update documentation',
        'Optimize performance', 'Handle edge cases', 'Clean up code',
        'Fix security issue', 'Add validation', 'Update config'
    ]
    
    # 文件相关
    FILE_EXTENSIONS = [
        'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'ico',
        'mp3', 'mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv',
        'zip', 'rar', '7z', 'tar', 'gz', 'bz2',
        'js', 'ts', 'py', 'java', 'cpp', 'c', 'h', 'go', 'rs',
        'html', 'css', 'scss', 'less', 'json', 'xml', 'yaml', 'yml'
    ]
    
    FILE_NAMES = [
        'document', 'report', 'data', 'config', 'settings',
        'index', 'main', 'app', 'server', 'client',
        'README', 'LICENSE', 'CHANGELOG', 'package', 'requirements'
    ]
    
    DIRECTORY_NAMES = [
        'src', 'dist', 'build', 'public', 'assets', 'images',
        'components', 'utils', 'services', 'models', 'controllers',
        'test', 'tests', 'spec', 'docs', 'config', 'scripts',
        'node_modules', 'venv', 'env', 'tmp', 'cache', 'logs'
    ]
    
    MIME_TYPES = [
        'text/plain', 'text/html', 'text/css', 'text/javascript',
        'application/json', 'application/xml', 'application/pdf',
        'image/jpeg', 'image/png', 'image/gif', 'image/svg+xml',
        'audio/mpeg', 'video/mp4', 'application/zip',
        'application/octet-stream', 'multipart/form-data'
    ]
    
    # 版本号
    SEMVER_VERSIONS = ['0.1.0', '1.0.0', '1.2.3', '2.0.0', '2.1.0', '3.0.0-beta']
    
    # 系统相关
    PLATFORM_NAMES = ['win32', 'darwin', 'linux', 'aix', 'freebsd', 'openbsd', 'sunos']
    
    ARCHITECTURES = ['x64', 'x32', 'arm', 'arm64', 'mips', 'mipsel', 'ppc', 'ppc64']
    
    @staticmethod
    def git_branch(count: int = 1) -> Dict[str, Any]:
        """随机 Git 分支名"""
        branches = random.choices(SystemTools.GIT_BRANCHES, k=count)
        return {'result': branches[0] if count == 1 else branches}
    
    @staticmethod
    def git_commit_message(count: int = 1) -> Dict[str, Any]:
        """随机 Git 提交信息"""
        messages = random.choices(SystemTools.GIT_COMMIT_MESSAGES, k=count)
        return {'result': messages[0] if count == 1 else messages}
    
    @staticmethod
    def git_commit_sha() -> Dict[str, Any]:
        """随机 Git commit SHA"""
        sha = ''.join(random.choices(string.hexdigits.lower(), k=40))
        return {'result': sha}
    
    @staticmethod
    def git_short_commit_sha() -> Dict[str, Any]:
        """随机短 Git commit SHA (7位)"""
        sha = ''.join(random.choices(string.hexdigits.lower(), k=7))
        return {'result': sha}
    
    @staticmethod
    def system_file_name(ext: str = None) -> Dict[str, Any]:
        """随机文件名"""
        name = random.choice(SystemTools.FILE_NAMES)
        if ext is None:
            ext = random.choice(SystemTools.FILE_EXTENSIONS)
        return {'result': f"{name}.{ext}"}
    
    @staticmethod
    def system_file_ext() -> Dict[str, Any]:
        """随机文件扩展名"""
        return {'result': random.choice(SystemTools.FILE_EXTENSIONS)}
    
    @staticmethod
    def system_directory_path(depth: int = 3) -> Dict[str, Any]:
        """随机目录路径"""
        parts = [''] + random.sample(SystemTools.DIRECTORY_NAMES, min(depth, len(SystemTools.DIRECTORY_NAMES)))
        return {'result': '/'.join(parts)}
    
    @staticmethod
    def system_file_path() -> Dict[str, Any]:
        """随机文件路径"""
        dir_path = SystemTools.system_directory_path(depth=random.randint(1, 4))['result']
        file_name = SystemTools.system_file_name()['result']
        return {'result': f"{dir_path}/{file_name}"}
    
    @staticmethod
    def system_mime_type() -> Dict[str, Any]:
        """随机 MIME 类型"""
        return {'result': random.choice(SystemTools.MIME_TYPES)}
    
    @staticmethod
    def system_semver() -> Dict[str, Any]:
        """随机语义化版本号"""
        major = random.randint(0, 9)
        minor = random.randint(0, 99)
        patch = random.randint(0, 99)
        pre_release = random.choice(['', '-alpha', '-beta', '-rc'])
        return {'result': f"{major}.{minor}.{patch}{pre_release}"}
    
    @staticmethod
    def system_platform() -> Dict[str, Any]:
        """随机平台名"""
        return {'result': random.choice(SystemTools.PLATFORM_NAMES)}
    
    @staticmethod
    def system_arch() -> Dict[str, Any]:
        """随机系统架构"""
        return {'result': random.choice(SystemTools.ARCHITECTURES)}
