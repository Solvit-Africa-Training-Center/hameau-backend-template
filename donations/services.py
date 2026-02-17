import logging
import openai
from django.conf import settings
from .models import ChildMonthlySummary
from programs.models.residentials_models import ChildProgress

logger = logging.getLogger(__name__)

def get_ai_summary(child, year, month, force_refresh=False):
    """
    Generates a natural language summary of a child's progress for a given month using OpenAI.
    Caches the results in ChildMonthlySummary to avoid redundant API calls.
    
    Args:
        child (Child): The child instance.
        year (int): The year of the progress notes.
        month (int): The month of the progress notes (1-12).
        force_refresh (bool): If True, regenerates the summary even if cached.
        
    Returns:
        str: The generated summary or an error message if the API call fails.
    """
    # 1. Check Cache
    if not force_refresh:
        cached = ChildMonthlySummary.objects.filter(
            child=child, month=month, year=year
        ).first()
        if cached:
            return cached.summary_text

    try:
        # 2. Query ChildProgress data
        progress_records = ChildProgress.objects.filter(
            child=child,
            created_on__year=year,
            created_on__month=month
        ).prefetch_related('progress_media') # Optimize query for media

        if not progress_records.exists():
            return f"No progress records found for {child.first_name} in {month}/{year}."

        # 3. Aggregate data
        notes_list = []
        total_images = 0
        total_videos = 0

        for record in progress_records:
            date_str = record.created_on.strftime("%d %b")
            notes_list.append(f"- {date_str}: {record.notes}")
            
            # Count media
            media_items = record.progress_media.all()
            for media in media_items:
                if media.progress_image:
                    total_images += 1
                if media.progress_video:
                    total_videos += 1

        formatted_notes = "\n".join(notes_list)

        # 4. Construct Prompt
        prompt = (
            f"Write a short, warm, and encouraging summary of the child's progress based on the following monthly updates. "
            f"The child's name is {child.first_name}. "
            f"The period is {month}/{year}. "
            f"Mention key activities and improvements. "
            f"Mention that there are {total_images} photos and {total_videos} videos attached if the counts are greater than zero. "
            f"Keep the tone positive and suitable for a sponsor report.\n\n"
            f"Updates:\n{formatted_notes}"
        )

        # 5. Call OpenAI API
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": "You are a helpful assistant writing progress summaries for child sponsorship reports."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7,
        )

        summary = response.choices[0].message.content.strip()

        # 6. Save to Cache
        ChildMonthlySummary.objects.update_or_create(
            child=child,
            month=month,
            year=year,
            defaults={"summary_text": summary}
        )

        return summary

    except Exception as e:
        logger.error(f"Error generating AI summary for child {child.id}: {e}")
        return "An error occurred while generating the summary. Please check the logs."

def calculate_next_deduction_date(start_date, interval):
    """
    Calculates the next deduction date based on the interval.
    """
    if interval == "MONTHLY":
        # Add a month
        next_date = start_date + datetime.timedelta(days=31)
        return next_date.replace(day=start_date.day)
    elif interval == "YEARLY":
        # Add a year
        try:
            return start_date.replace(year=start_date.year + 1)
        except ValueError:
            # Handle leap year Feb 29
            return start_date + datetime.timedelta(days=365)
    return None
