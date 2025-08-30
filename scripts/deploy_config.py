#!/usr/bin/env python3
"""
⚙️ CONFIGURAÇÃO DO SISTEMA DE DEPLOY AUTOMÁTICO
===============================================

Configurações para deploy automático no GitHub
"""

# Configurações do repositório
REPO_CONFIG = {
    "remote": "origin",
    "branch": "master",
    "auto_update_readme": True,
    "run_tests_before_deploy": True,
    "commit_message_template": "🚀 DEPLOY: {feature} - {timestamp}"
}

# Configurações de validação
VALIDATION_CONFIG = {
    "min_e2e_success_rate": 0.9,  # 90% dos testes E2E devem passar
    "min_unit_success_rate": 0.8,  # 80% dos testes unitários devem passar
    "required_test_categories": ["e2e", "unit"],
    "skip_failing_tests": False
}

# Configurações de commit
COMMIT_CONFIG = {
    "auto_generate_message": True,
    "include_timestamp": True,
    "include_test_results": True,
    "emoji_prefixes": {
        "feature": "✨",
        "bugfix": "🐛",
        "refactor": "♻️",
        "docs": "📚",
        "test": "🧪",
        "deploy": "🚀"
    }
}

# Configurações de push
PUSH_CONFIG = {
    "force_push": False,
    "create_backup_branch": True,
    "backup_branch_prefix": "backup/",
    "notify_on_success": True,
    "notify_on_failure": True
}

# Configurações de notificação
NOTIFICATION_CONFIG = {
    "console_output": True,
    "log_file": "deploy.log",
    "log_level": "INFO",
    "show_progress": True
}

# Configurações de rollback
ROLLBACK_CONFIG = {
    "auto_rollback_on_failure": False,
    "keep_failed_commits": True,
    "max_rollback_depth": 3
}
