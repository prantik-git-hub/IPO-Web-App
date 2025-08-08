import os
import sys
import django

sys.path.append("/code")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ipo_project.settings")
django.setup()

from ipo_app.models import Company, IPO

# Create or get the company
company, created = Company.objects.get_or_create(
    company_name="ABC Corp",
    defaults={'company_logo': None}
)

# Create IPO linked to this company
ipo = IPO.objects.create(
    company=company,
    price_band="₹100-120",
    open_date="2025-07-01",
    close_date="2025-07-03",
    issue_size="₹500 Cr",
    issue_type="Book Built",
    status="open",
    ipo_price=110,
    listing_price=130,
    current_market_price=140,
    listing_date="2025-07-10"
)

print(f"IPO created successfully for company: {company.company_name}")
