# src/translations.py

TEXTS = {
    "app_title": {
        "en": "Sanzad Global Ecosystem Dashboard",
        "fr": "Tableau de bord de l'écosystème Sanzad Global",
        "sw": "Dashibodi ya Mfumo wa Sanzad Global",
    },
    "role_label": {
        "en": "User Role",
        "fr": "Rôle utilisateur",
        "sw": "Jukumu la Mtumiaji",
    },
    "module_label": {
        "en": "Module",
        "fr": "Module",
        "sw": "Moduli",
    },
    "home_title": {
        "en": "Welcome to Sanzad Global",
        "fr": "Bienvenue à Sanzad Global",
        "sw": "Karibu Sanzad Global",
    },
    "home_sub_student": {
        "en": "Student Dashboard",
        "fr": "Tableau de bord Élève",
        "sw": "Dashibodi ya Mwanafunzi",
    },
    "home_sub_teacher": {
        "en": "Teacher Dashboard",
        "fr": "Tableau de bord Enseignant",
        "sw": "Dashibodi ya Mwalimu",
    },
    "home_sub_parent": {
        "en": "Parent Dashboard",
        "fr": "Tableau de bord Parent",
        "sw": "Dashibodi ya Mzazi",
    },
    "home_sub_institution": {
        "en": "Institution Dashboard",
        "fr": "Tableau de bord Établissement",
        "sw": "Dashibodi ya Taasisi",
    },
    "home_sub_admin": {
        "en": "Super Admin Dashboard",
        "fr": "Tableau de bord Super Admin",
        "sw": "Dashibodi ya Msimamizi Mkuu",
    },
    "smart_title": {
        "en": "Smart Teacher Module",
        "fr": "Module Prof Intelligent",
        "sw": "Moduli ya Mwalimu Mahiri",
    },
    "overview_tab": {
        "en": "Overview",
        "fr": "Aperçu",
        "sw": "Muhtasari",
    },
    "assign_tab": {
        "en": "Assignments & PDFs",
        "fr": "Devoirs & PDF",
        "sw": "Tasnifu & PDF",
    },
    "grades_tab": {
        "en": "Grades & Students",
        "fr": "Notes & Élèves",
        "sw": "Alama & Wanafunzi",
    },
    "messages_tab": {
        "en": "Class Messages",
        "fr": "Messages de Classe",
        "sw": "Ujumbe wa Darasa",
    },
    "ai_tab": {
        "en": "AI & Tools",
        "fr": "IA & Outils",
        "sw": "AI & Zana",
    },
    "language_button": {
        "en": "Change Language",
        "fr": "Changer de langue",
        "sw": "Badilisha Lugha",
    },
}


def t(key: str, lang: str = "en") -> str:
    """Simple translation helper. Falls back to English or the key itself."""
    if key in TEXTS and lang in TEXTS[key]:
        return TEXTS[key][lang]
    return TEXTS.get(key, {}).get("en", key)
