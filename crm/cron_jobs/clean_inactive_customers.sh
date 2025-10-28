#!/bin/bash

# Navigate to the project directory
cd "$(dirname "$0")/../.." || exit

# Execute Django shell command to delete inactive customers
DELETED_COUNT=$(python manage.py shell <<EOF
from crm.models import Customer
from django.utils import timezone
from datetime import timedelta

# Calculate date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders in the last year
# Assuming Customer model has a related 'orders' field
inactive_customers = Customer.objects.filter(
    orders__isnull=True
) | Customer.objects.exclude(
    orders__created_at__gte=one_year_ago
).distinct()

# Delete and count
count = inactive_customers.count()
inactive_customers.delete()
print(count)
EOF
)

# Log the result with timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] Deleted $DELETED_COUNT inactive customers" >> /tmp/customer_cleanup_log.txt
