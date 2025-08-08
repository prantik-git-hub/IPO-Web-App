from django.db import models

class Company(models.Model):
    company_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.company_name


class IPO(models.Model):
    STATUS_CHOICES = [
       ('coming', 'Coming'),
        ('newlisted', 'Newlisted'),
        ('ongoing', 'Ongoing'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    company_logo = models.ImageField(upload_to='logos/', null=True, blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    price_band = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    issue_size = models.CharField(max_length=100, null=True, blank=True)
    issue_type = models.CharField(max_length=100, null=True, blank=True)
    open_date = models.DateField(null=True, blank=True)
    close_date = models.DateField(null=True, blank=True)

    ipo_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    listing_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    listing_date = models.DateField(null=True, blank=True)
    current_market_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    @property
    def listing_gain(self):
        if self.ipo_price and self.listing_price:
            return round(((self.listing_price - self.ipo_price) / self.ipo_price) * 100, 2)
        return None

    @property
    def current_return(self):
        if self.ipo_price and self.current_market_price:
            return round(((self.current_market_price - self.ipo_price) / self.ipo_price) * 100, 2)
        return None

    def __str__(self):
        return f"{self.company.company_name} - {self.status}"

class Document(models.Model):
    DOC_TYPE_CHOICES = [
        ('RHP', 'RHP'),
        ('DRHP', 'DRHP'),
    ]

    ipo = models.ForeignKey(IPO, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='docs/')
    doc_type = models.CharField(max_length=10, choices=DOC_TYPE_CHOICES)

    def __str__(self):
        return f"{self.doc_type} for {self.ipo.company.company_name}"
