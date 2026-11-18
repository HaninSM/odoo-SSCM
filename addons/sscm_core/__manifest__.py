# -*- coding: utf-8 -*-
{
    'name': 'SSCM Core - Commission & Payment Foundation',
    'version': '17.0.1.0.0',
    'category': 'Services/Supply Chain',
    'summary': 'Core engine for Service Supply Chain Management, Staff Commissions, and Payment Integration',
    'description': """
Service Supply Chain Management (SSCM) Core Module
==================================================
Provides shared foundations for service industries:
- Employee Service Roles and Commission Schemes (Flat & Percentage)
- Automated Commission Ledger for Service Execution & Product Upselling
- Shared security groups and access controls
    """,
    'author': 'HaninSM',
    'website': 'https://github.com/HaninSM/odoo-SSCM',
    'depends': [
        'base',
        'mail',
        'hr',
        'account',
        'product',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/hr_employee_views.xml',
        'views/service_commission_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
