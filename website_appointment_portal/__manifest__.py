{
    "name": "Website Appointment Portal",
    "summary": "Website booking of appointments with portal 'My Appointments'",
    "version": "18.0.1.0.0",
    "category": "Website",
    "author": "Custom",
    "license": "LGPL-3",
    "website": "https://example.com",
    "depends": [
        "base",
        "website",
        "portal",
        "mail"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequences.xml",
        # "views/appointment_views.xml",
        # "views/menus.xml",
        # "templates/website_templates.xml",
        # "templates/portal_templates.xml"
    ],
    "assets": {
        "website.assets_frontend": [
            "website_appointment_portal/static/src/scss/website_appointment.scss",
            "website_appointment_portal/static/src/js/website_appointment.js"
        ]
    },
    "application": True,
}


