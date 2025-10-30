"""
Módulo core - Tenant Resolver e Feature Management.

Este módulo contém a lógica central para identificação de tenants
e gerenciamento de features multi-tenant.
"""

from src.core.tenant_resolver import TenantResolver
from src.core.feature_manager import FeatureManager
from src.core.tenant_context import TenantContext

__all__ = [
    "TenantResolver",
    "FeatureManager",
    "TenantContext",
]
