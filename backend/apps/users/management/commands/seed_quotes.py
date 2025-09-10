from django.core.management.base import BaseCommand
from apps.users.models import MotivationalQuote


class Command(BaseCommand):
    help = 'Seed the database with motivational quotes'

    def handle(self, *args, **options):
        quotes_data = [
            # General Motivation
            {
                'quote_text': "The only way to do great work is to love what you do.",
                'author': "Steve Jobs",
                'category': 'general',
                'target_weak_subjects': [],
                'target_low_motivation': True
            },
            {
                'quote_text': "Believe you can and you're halfway there.",
                'author': "Theodore Roosevelt",
                'category': 'confidence',
                'target_weak_subjects': [],
                'target_low_motivation': True
            },
            {
                'quote_text': "Success is not final, failure is not fatal: it is the courage to continue that counts.",
                'author': "Winston Churchill",
                'category': 'perseverance',
                'target_weak_subjects': [],
                'target_low_motivation': True
            },
            
            # Study & Learning
            {
                'quote_text': "Learning is a treasure that will follow its owner everywhere.",
                'author': "Chinese Proverb",
                'category': 'study',
                'target_weak_subjects': [],
                'target_low_motivation': False
            },
            {
                'quote_text': "The more that you read, the more things you will know. The more that you learn, the more places you'll go.",
                'author': "Dr. Seuss",
                'category': 'study',
                'target_weak_subjects': [],
                'target_low_motivation': False
            },
            {
                'quote_text': "Education is the most powerful weapon which you can use to change the world.",
                'author': "Nelson Mandela",
                'category': 'study',
                'target_weak_subjects': [],
                'target_low_motivation': False
            },
            
            # Mathematics Focus
            {
                'quote_text': "Mathematics is not about numbers, equations, computations, or algorithms: it is about understanding.",
                'author': "William Paul Thurston",
                'category': 'study',
                'target_weak_subjects': ['mathematics', 'math', 'algebra', 'calculus'],
                'target_low_motivation': False
            },
            {
                'quote_text': "In mathematics you don't understand things. You just get used to them.",
                'author': "John von Neumann",
                'category': 'study',
                'target_weak_subjects': ['mathematics', 'math'],
                'target_low_motivation': False
            },
            
            # Science Focus
            {
                'quote_text': "Science is not only a disciple of reason but, also, one of romance and passion.",
                'author': "Stephen Hawking",
                'category': 'study',
                'target_weak_subjects': ['science', 'physics', 'chemistry', 'biology'],
                'target_low_motivation': False
            },
            {
                'quote_text': "The important thing is not to stop questioning. Curiosity has its own reason for existing.",
                'author': "Albert Einstein",
                'category': 'study',
                'target_weak_subjects': ['science', 'physics'],
                'target_low_motivation': False
            },
            
            # Growth Mindset
            {
                'quote_text': "In a growth mindset, challenges are exciting rather than threatening.",
                'author': "Carol Dweck",
                'category': 'growth',
                'target_weak_subjects': [],
                'target_low_motivation': True
            },
            {
                'quote_text': "I have not failed. I've just found 10,000 ways that won't work.",
                'author': "Thomas A. Edison",
                'category': 'growth',
                'target_weak_subjects': [],
                'target_low_motivation': True
            },
            
            # Focus & Concentration
            {
                'quote_text': "Concentrate all your thoughts upon the work at hand. The sun's rays do not burn until brought to a focus.",
                'author': "Alexander Graham Bell",
                'category': 'focus',
                'target_weak_subjects': [],
                'target_low_motivation': False
            },
            {
                'quote_text': "The successful warrior is the average man with laser-like focus.",
                'author': "Bruce Lee",
                'category': 'focus',
                'target_weak_subjects': [],
                'target_low_motivation': False
            },
            
            # Goal Achievement
            {
                'quote_text': "A goal is a dream with a deadline.",
                'author': "Napoleon Hill",
                'category': 'goals',
                'target_weak_subjects': [],
                'target_low_motivation': False
            },
            {
                'quote_text': "Set goals that make you want to jump out of bed in the morning.",
                'author': "Unknown",
                'category': 'goals',
                'target_weak_subjects': [],
                'target_low_motivation': True
            },
            
            # Perseverance
            {
                'quote_text': "It does not matter how slowly you go as long as you do not stop.",
                'author': "Confucius",
                'category': 'perseverance',
                'target_weak_subjects': [],
                'target_low_motivation': True
            },
            {
                'quote_text': "Fall seven times, stand up eight.",
                'author': "Japanese Proverb",
                'category': 'perseverance',
                'target_weak_subjects': [],
                'target_low_motivation': True
            },
            
            # Success & Achievement
            {
                'quote_text': "Success is not the key to happiness. Happiness is the key to success.",
                'author': "Albert Schweitzer",
                'category': 'success',
                'target_weak_subjects': [],
                'target_low_motivation': False
            },
            {
                'quote_text': "Don't be afraid to give up the good to go for the great.",
                'author': "John D. Rockefeller",
                'category': 'success',
                'target_weak_subjects': [],
                'target_low_motivation': False
            },
            
            # Language Arts Focus
            {
                'quote_text': "Words have no power to impress the mind without the exquisite horror of their reality.",
                'author': "Edgar Allan Poe",
                'category': 'study',
                'target_weak_subjects': ['english', 'literature', 'writing'],
                'target_low_motivation': False
            },
            {
                'quote_text': "Reading is to the mind what exercise is to the body.",
                'author': "Joseph Addison",
                'category': 'study',
                'target_weak_subjects': ['english', 'reading'],
                'target_low_motivation': False
            },
            
            # Additional General Motivation
            {
                'quote_text': "Your limitation—it's only your imagination.",
                'author': "Unknown",
                'category': 'general',
                'target_weak_subjects': [],
                'target_low_motivation': True
            },
            {
                'quote_text': "Push yourself, because no one else is going to do it for you.",
                'author': "Unknown",
                'category': 'general',
                'target_weak_subjects': [],
                'target_low_motivation': True
            },
            {
                'quote_text': "Great things never come from comfort zones.",
                'author': "Unknown",
                'category': 'general',
                'target_weak_subjects': [],
                'target_low_motivation': True
            },
            {
                'quote_text': "Dream it. Wish it. Do it.",
                'author': "Unknown",
                'category': 'goals',
                'target_weak_subjects': [],
                'target_low_motivation': False
            },
            {
                'quote_text': "Success doesn't just find you. You have to go out and get it.",
                'author': "Unknown",
                'category': 'success',
                'target_weak_subjects': [],
                'target_low_motivation': True
            },
            
            # Confidence Building
            {
                'quote_text': "You are never too old to set another goal or to dream a new dream.",
                'author': "C.S. Lewis",
                'category': 'confidence',
                'target_weak_subjects': [],
                'target_low_motivation': False
            },
            {
                'quote_text': "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle.",
                'author': "Christian D. Larson",
                'category': 'confidence',
                'target_weak_subjects': [],
                'target_low_motivation': True
            },
            
            # More Study Focused
            {
                'quote_text': "The beautiful thing about learning is that no one can take it away from you.",
                'author': "B.B. King",
                'category': 'study',
                'target_weak_subjects': [],
                'target_low_motivation': False
            },
            {
                'quote_text': "An investment in knowledge pays the best interest.",
                'author': "Benjamin Franklin",
                'category': 'study',
                'target_weak_subjects': [],
                'target_low_motivation': False
            },
            {
                'quote_text': "The expert in anything was once a beginner.",
                'author': "Unknown",
                'category': 'study',
                'target_weak_subjects': [],
                'target_low_motivation': True
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for quote_data in quotes_data:
            quote, created = MotivationalQuote.objects.get_or_create(
                quote_text=quote_data['quote_text'],
                defaults=quote_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"Created: {quote_data['quote_text'][:50]}...")
            else:
                # Update existing quote if needed
                for key, value in quote_data.items():
                    if key != 'quote_text':
                        setattr(quote, key, value)
                quote.save()
                updated_count += 1
                self.stdout.write(f"Updated: {quote_data['quote_text'][:50]}...")
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {created_count} new quotes and updated {updated_count} existing quotes.'
            )
        )
