import logging
import datetime
from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from donations.models import Donation, Donor, SponsorEmailLog
from donations.services import get_ai_summary

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Sends monthly progress emails to donors for their supported children."

    def add_arguments(self, parser):
        parser.add_argument(
            "--month", type=int, help="Month to generate summary for (1-12)"
        )
        parser.add_argument(
            "--year", type=int, help="Year to generate summary for"
        )
        parser.add_argument(
            "--force", action="store_true", help="Force send even if already sent"
        )
        parser.add_argument(
            "--refresh-ai", action="store_true", help="Force regenerate AI summary"
        )

    def handle(self, *args, **options):
        # 1. Determine target month and year (default to previous month)
        today = timezone.now().date()
        first_day_of_current_month = today.replace(day=1)
        last_day_of_prev_month = first_day_of_current_month - datetime.timedelta(days=1)
        
        target_month = options.get("month") or last_day_of_prev_month.month
        target_year = options.get("year") or last_day_of_prev_month.year
        force = options.get("force")

        self.stdout.write(
            self.style.SUCCESS(f"Processing donor reports for {target_month}/{target_year}...")
        )

        # 2. Find donors linked to children via donations
        # We look for donors who have *any* donation linked to a child.
        # In a real scenario, you might want to filter for active sponsorships (e.g. donations in the last N months).
        active_donor_child_pairs = Donation.objects.filter(
            child__isnull=False,
            donor__isnull=False
        ).values('donor', 'child').distinct()

        total_sent = 0
        total_errors = 0

        for pair in active_donor_child_pairs:
            donor = Donor.objects.get(id=pair['donor'])
            child = pair['child'] # This is the ID, but get_ai_summary needs the object
            from programs.models.residentials_models import Child
            child_obj = Child.objects.get(id=child)

            if not donor.email:
                self.stdout.write(self.style.WARNING(f"Donor {donor.fullname} has no email, skipping."))
                continue

            # Check if already sent
            if not force:
                if SponsorEmailLog.objects.filter(
                    donor=donor,
                    child=child_obj,
                    month=target_month,
                    year=target_year,
                    status="SUCCESS"
                ).exists():
                    self.stdout.write(
                        f"Skipping {donor.fullname} for {child_obj.full_name} (Already sent)"
                    )
                    continue

            try:
                # 3. Get AI Summary
                refresh_ai = options.get("refresh_ai")
                summary = get_ai_summary(child_obj, target_year, target_month, force_refresh=refresh_ai)
                
                if "No progress records found" in summary:
                    self.stdout.write(
                        self.style.WARNING(f"No progress records for {child_obj.full_name}, skipping.")
                    )
                    continue
                
                if "An error occurred" in summary:
                    raise Exception(f"AI Summary Error: {summary}")

                # 4. Prepare Email
                context = {
                    "child_name": child_obj.full_name,
                    "child_photo": child_obj.profile_image.url if child_obj.profile_image else None,
                    "report_month": datetime.date(2000, target_month, 1).strftime("%B"),
                    "report_year": target_year,
                    "ai_summary": summary,
                    "dashboard_url": settings.FRONTEND_URL if hasattr(settings, "FRONTEND_URL") else "#",
                }

                html_content = render_to_string("emails/donor_progress_report.html", context)
                text_content = render_to_string("emails/donor_progress_report.txt", context)

                subject = f"Monthly Progress Update: {child_obj.full_name} - {context['report_month']} {target_year}"
                from_email = settings.DEFAULT_FROM_EMAIL
                to_email = [donor.email]

                # 5. Send Email
                msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                # 6. Log Success
                SponsorEmailLog.objects.create(
                    donor=donor,
                    child=child_obj,
                    month=target_month,
                    year=target_year,
                    status="SUCCESS"
                )
                
                total_sent += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully sent email to {donor.email} for {child_obj.full_name}")
                )

            except Exception as e:
                total_errors += 1
                error_msg = str(e)
                self.stdout.write(
                    self.style.ERROR(f"Failed to send email to {donor.email}: {error_msg}")
                )
                
                # Log Failure
                SponsorEmailLog.objects.create(
                    donor=donor,
                    child=child_obj,
                    month=target_month,
                    year=target_year,
                    status="FAILED",
                    error_message=error_msg
                )

        self.stdout.write(
            self.style.SUCCESS(f"Completed. Sent: {total_sent}, Errors: {total_errors}")
        )
