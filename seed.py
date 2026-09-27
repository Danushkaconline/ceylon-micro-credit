"""Default content loaded the first time the database is created.

Everything here can be changed later from the admin panel (/admin), so you
rarely need to edit this file. Run `python seed.py --reset` to rebuild the
database from these defaults (this deletes existing data).
"""
from datetime import date

from models import AdminUser, Category, News, Product, Setting, Slide, db

def photo(name):
    """Default photo stored in static/img/stock/ (free Pexels photos, https://www.pexels.com/license/)."""
    return f"/static/img/stock/{name}.jpg"


# Default pictures. Change any of them from the admin panel (upload your own photo or paste a link).
IMAGE_KEYS = [
    "img_about", "img_about_home", "img_services", "img_calculator", "img_apply", "img_contact", "img_news",
    "business-loans", "micro-leasing", "micro-group-loans",
    "business-loan", "mortgage-loan", "motor-bicycle-leasing", "three-wheeler-leasing", "group-loans", "sme-loan",
    "slide-business", "slide-leasing", "slide-group",
    "ceylon-micro-credit-opens-at-kadawatha", "three-wheeler-leasing-plans",
]
IMAGES = {key: photo(key) for key in IMAGE_KEYS}

SETTINGS = [
    # key, label, value
    ("company_name", "Company name", "Ceylon Micro Credit"),
    ("tagline", "Tagline", "Small loans. Big dreams."),
    ("address", "Address", "62, Jaya Mawatha, Kadawatha"),
    ("city", "City / Branch", "Kadawatha"),
    ("phone", "Telephone", "011-2224578"),
    ("email", "Email", "info@ceylonmicrocredit.lk"),
    ("hours", "Opening hours", "Mon - Fri 8.30 AM - 5.00 PM | Sat 8.30 AM - 1.00 PM"),
    ("hero_title", "Home banner title", "Finance that grows with your business"),
    ("hero_text", "Home banner text",
     "Business loans, micro leasing and group loans designed for Sri Lankan entrepreneurs, "
     "families and self-employed people. Fast approval, simple documents and friendly service from Kadawatha."),
    ("about_text", "About us text",
     "Ceylon Micro Credit is a community-focused micro finance company based in Kadawatha. "
     "We help small business owners, self-employed people and women-led groups access fair, "
     "affordable credit so they can start, grow and protect their livelihoods.\n"
     "Our team believes in simple processes, transparent pricing and long-term relationships. "
     "Every customer is served personally by an officer who understands the local community."),
    ("mission", "Mission", "To empower small businesses and families across Sri Lanka with fast, fair and responsible financial services."),
    ("vision", "Vision", "To be the most trusted micro finance partner for every growing community in Sri Lanka."),
    ("map_embed", "Google Map search text", "62 Jaya Mawatha, Kadawatha, Sri Lanka"),
    ("facebook", "Facebook URL", ""),
    ("whatsapp", "WhatsApp number (e.g. 94112224578)", ""),
    ("about_short", "Home page 'About us' intro",
     "Ceylon Micro Credit is a Kadawatha-based micro finance company helping small business owners, "
     "self-employed people and community groups access fair, affordable credit. Along with finance we "
     "offer friendly guidance so our customers can grow with confidence."),
    ("values", "Our values (comma separated)",
     "Integrity, Trust, Care, Accountability, Transparency, Efficiency, Confidentiality, Reliability"),
    ("highlight_1", "Highlight 1 (title | text)",
     "Fast & Simple Approval | Minimal paperwork and quick decisions - most applications are approved within 24-48 hours."),
    ("highlight_2", "Highlight 2 (title | text)",
     "Experienced Local Team | Our officers know the Kadawatha community and give every customer personal attention."),
    ("highlight_3", "Highlight 3 (title | text)",
     "Transparent & Fair | Clear rates and instalments with no hidden charges - responsible lending you can trust."),
    ("stat_years", "Counter: years of experience", "10"),
    ("stat_customers", "Counter: clients helped", "5000"),
    ("stat_disbursed", "Counter: loans disbursed (Rs. millions)", "500"),
    ("stat_products", "Counter: loan products", "6"),
    ("img_about_home", "Image: home page 'About us'", IMAGES["img_about_home"]),
    ("img_about", "Image: About Us page banner", IMAGES["img_about"]),
    ("img_services", "Image: Services page banner", IMAGES["img_services"]),
    ("img_calculator", "Image: Calculator page banner", IMAGES["img_calculator"]),
    ("img_apply", "Image: Apply page banner", IMAGES["img_apply"]),
    ("img_contact", "Image: Contact page banner", IMAGES["img_contact"]),
    ("img_news", "Image: News page banner", IMAGES["img_news"]),
]

SLIDES = [
    {"eyebrow": "Business Loans", "title": "Finance that grows with your business",
     "text": "Working capital and mortgage-backed loans for traders, shop owners and entrepreneurs.",
     "button_text": "Explore Business Loans", "button_link": "/services/business-loans",
     "image": IMAGES["slide-business"]},
    {"eyebrow": "Micro Leasing", "title": "Own the vehicle that powers your income",
     "text": "Easy leasing for motor bicycles and three-wheelers with a low down payment.",
     "button_text": "Explore Leasing", "button_link": "/services/micro-leasing",
     "image": IMAGES["slide-leasing"]},
    {"eyebrow": "Micro Group Loans", "title": "Grow together with your community",
     "text": "Collateral-free group loans and SME loans designed for Sri Lankan entrepreneurs.",
     "button_text": "Explore Group Loans", "button_link": "/services/micro-group-loans",
     "image": IMAGES["slide-group"]},
]

NEWS = [
    {"title": "Ceylon Micro Credit opens at Kadawatha", "slug": "ceylon-micro-credit-opens-at-kadawatha",
     "summary": "Our office at 62, Jaya Mawatha, Kadawatha is now open to serve customers in the area.",
     "body": "We are happy to welcome customers to our office at 62, Jaya Mawatha, Kadawatha.\n"
             "Visit us for business loans, micro leasing and group loans, or call 011-2224578."},
    {"title": "Special three-wheeler leasing plans for hiring drivers", "slug": "three-wheeler-leasing-plans",
     "summary": "Flexible repayment plans that match the daily income of three-wheeler hiring drivers.",
     "body": "Our new three-wheeler leasing plans offer flexible instalments designed around the income of hiring drivers.\n"
             "Speak to our officers to find the right plan for you."},
]

CATEGORIES = [
    {
        "name": "Business Loans", "slug": "business-loans", "icon": "bi-briefcase-fill",
        "tagline": "Capital to start, run and expand your business",
        "description": "Flexible business financing for traders, shop owners, manufacturers and service providers. "
                       "Choose an unsecured business loan for working capital or a mortgage-backed loan for larger amounts.",
        "products": [
            {
                "name": "Business Loan", "slug": "business-loan", "icon": "bi-shop",
                "short_description": "Working capital and expansion finance for small and medium businesses.",
                "description": "Buy stock, purchase equipment, renovate your shop or manage cash flow. "
                               "Our business loan is quick to approve and repaid in easy monthly instalments.",
                "features": "Loans from Rs. 50,000 up to Rs. 2,000,000\nRepayment periods up to 36 months\n"
                            "Approval within 24-48 hours\nMonthly or weekly repayment options\nNo hidden charges",
                "requirements": "Copy of NIC\nBusiness registration (if available)\nProof of business income / bank statements\n"
                                "Utility bill for address confirmation\nGuarantor details",
                "min_amount": 50000, "max_amount": 2000000, "interest_rate": 24, "max_term_months": 36,
            },
            {
                "name": "Mortgage Loan", "slug": "mortgage-loan", "icon": "bi-house-door-fill",
                "short_description": "Larger loans secured against land or property at lower rates.",
                "description": "Unlock the value of your land or house. Mortgage loans give you access to higher amounts "
                               "with longer repayment periods and lower interest rates.",
                "features": "Loans up to Rs. 10,000,000\nRepayment periods up to 60 months\nLower interest rates\n"
                            "Free property valuation guidance\nUse for business, construction or personal needs",
                "requirements": "Copy of NIC\nOriginal deed and survey plan\nLatest extracts (Folio)\n"
                                "Proof of income\nUtility bill",
                "min_amount": 500000, "max_amount": 10000000, "interest_rate": 18, "max_term_months": 60,
            },
        ],
    },
    {
        "name": "Micro Leasing", "slug": "micro-leasing", "icon": "bi-truck-front-fill",
        "tagline": "Own the vehicle that powers your income",
        "description": "Easy leasing facilities for motor bicycles and three-wheelers - ideal for delivery riders, "
                       "hiring drivers and small business owners who need reliable transport.",
        "products": [
            {
                "name": "Motor Bicycle Leasing", "slug": "motor-bicycle-leasing", "icon": "bi-bicycle",
                "short_description": "Lease a brand new or registered motor bicycle with a low down payment.",
                "description": "Get on the road quickly with affordable motor bicycle leasing. Suitable for brand new "
                               "and registered bikes from all leading brands.",
                "features": "Brand new and registered bikes\nLow down payment\nRepayment up to 48 months\n"
                            "Quick documentation\nInsurance guidance provided",
                "requirements": "Copy of NIC\nDriving licence\nProof of income\nUtility bill\nGuarantor details",
                "min_amount": 100000, "max_amount": 1000000, "interest_rate": 26, "max_term_months": 48,
            },
            {
                "name": "Three-Wheeler Leasing", "slug": "three-wheeler-leasing", "icon": "bi-car-front-fill",
                "short_description": "Start your own hiring business with a leased three-wheeler.",
                "description": "Three-wheeler leasing for hiring, delivery and personal use. We finance brand new and "
                               "registered three-wheelers with flexible repayment plans.",
                "features": "Brand new and registered three-wheelers\nUp to 70% financing\nRepayment up to 60 months\n"
                            "Fast approval\nSpecial plans for hiring drivers",
                "requirements": "Copy of NIC\nDriving licence\nProof of income\nUtility bill\nGuarantor details",
                "min_amount": 300000, "max_amount": 2500000, "interest_rate": 26, "max_term_months": 60,
            },
        ],
    },
    {
        "name": "Micro Group Loans", "slug": "micro-group-loans", "icon": "bi-people-fill",
        "tagline": "Grow together with community-based finance",
        "description": "Group-based lending for self-employed people and small entrepreneurs, plus SME loans "
                       "for growing enterprises. No collateral needed for group loans - the group supports each other.",
        "products": [
            {
                "name": "Group Loans", "slug": "group-loans", "icon": "bi-people",
                "short_description": "Collateral-free loans for groups of 5-10 members at your local centre.",
                "description": "Form a group with people you trust and access small loans without collateral. "
                               "Our field officers meet your centre regularly to collect instalments and give guidance.",
                "features": "No collateral required\nGroups of 5-10 members\nWeekly or bi-weekly repayments\n"
                            "Centre meetings in your village\nRepeat loans with higher limits",
                "requirements": "Copy of NIC for each member\nMembers from the same area\nSmall income-generating activity\n"
                                "Attendance at centre meetings",
                "min_amount": 20000, "max_amount": 200000, "interest_rate": 30, "max_term_months": 18,
            },
            {
                "name": "SME Loan", "slug": "sme-loan", "icon": "bi-building",
                "short_description": "Finance for small and medium enterprises ready for the next step.",
                "description": "Designed for established small and medium enterprises that need larger capital to buy "
                               "machinery, increase stock or open new outlets.",
                "features": "Loans up to Rs. 5,000,000\nRepayment periods up to 48 months\nTailored repayment plans\n"
                            "Dedicated relationship officer\nBusiness advisory support",
                "requirements": "Copy of NIC\nBusiness registration certificate\nLast 6 months bank statements\n"
                                "Financial statements (if available)\nGuarantor or security",
                "min_amount": 250000, "max_amount": 5000000, "interest_rate": 22, "max_term_months": 48,
            },
        ],
    },
]


def seed_defaults(admin_username, admin_password):
    """Insert default rows that are missing. Safe to call on every start."""
    for order, (key, label, value) in enumerate(SETTINGS):
        if not db.session.get(Setting, key):
            db.session.add(Setting(key=key, label=label, value=value, sort_order=order))

    if not Category.query.first():
        for c_order, cat in enumerate(CATEGORIES):
            data = {k: v for k, v in cat.items() if k != "products"}
            category = Category(sort_order=c_order, image=IMAGES.get(cat["slug"], ""), **data)
            db.session.add(category)
            for p_order, prod in enumerate(cat["products"]):
                db.session.add(Product(category=category, sort_order=p_order,
                                       image=IMAGES.get(prod["slug"], ""), **prod))

    if not Slide.query.first():
        for order, s in enumerate(SLIDES):
            db.session.add(Slide(sort_order=order, **s))

    if not News.query.first():
        for n in NEWS:
            db.session.add(News(published_on=date.today(), image=IMAGES.get(n["slug"], ""), **n))

    if not AdminUser.query.first():
        admin = AdminUser(username=admin_username)
        admin.set_password(admin_password)
        db.session.add(admin)

    db.session.commit()


def fill_missing_images():
    """Give the default pictures to items that have no image yet (keeps your own images)."""
    count = 0
    for model in (Category, Product, News):
        for item in model.query.all():
            if (not item.image or "images.unsplash.com" in item.image) and item.slug in IMAGES:
                item.image = IMAGES[item.slug]
                count += 1
    slide_keys = {"/services/business-loans": "slide-business", "/services/micro-leasing": "slide-leasing",
                  "/services/micro-group-loans": "slide-group"}
    for slide in Slide.query.all():
        if (not slide.image or "images.unsplash.com" in slide.image) and slide.button_link in slide_keys:
            slide.image = IMAGES[slide_keys[slide.button_link]]
            count += 1
    for setting in Setting.query.filter(Setting.key.like("img_%")).all():
        if (not setting.value or "images.unsplash.com" in setting.value) and setting.key in IMAGES:
            setting.value = IMAGES[setting.key]
            count += 1
    db.session.commit()
    return count


if __name__ == "__main__":
    import sys

    from app import create_app

    app = create_app()
    with app.app_context():
        if "--reset" in sys.argv:
            db.drop_all()
            db.create_all()
            seed_defaults(app.config["ADMIN_USERNAME"], app.config["ADMIN_PASSWORD"])
            print("Database reset with default content.")
        elif "--images" in sys.argv:
            print(f"Added default images to {fill_missing_images()} item(s).")
        else:
            print("Use: python seed.py --images   (add default pictures to items without one)")
            print("  or python seed.py --reset    (rebuild database - deletes all data!)")
