from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import os
from dotenv import load_dotenv
import fitz
import base64
from io import BytesIO

# Load environment variables
load_dotenv()

# MongoDB connection
uri = os.getenv('MONGO_URI')
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.writeshelf

def generate_pdf_cover(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        if doc.page_count > 0:
            # Get first page and render at higher quality
            pix = doc[0].get_pixmap(matrix=fitz.Matrix(2, 2))
            img_data = BytesIO(pix.tobytes('png'))
            img_base64 = base64.b64encode(img_data.getvalue()).decode()
            return f'data:image/png;base64,{img_base64}'
    except Exception as e:
        print(f"Error generating PDF cover: {e}")
    return None

def migrate_activities():
    # Clear existing activities
    db.activities.delete_many({})
    
    # Migrate reviews to activities
    reviews = db.reviews.find()
    for review in reviews:
        db.activities.insert_one({
            'username': review['reviewer'],
            'type': 'review',
            'details': {
                'book_id': str(review['book_id']),
                'rating': review['rating'],
                'review_id': str(review['_id'])
            },
            'timestamp': review.get('created_at', review.get('date', datetime.utcnow()))
        })
    
    # Migrate follows to activities
    follows = db.follows.find()
    for follow in follows:
        db.activities.insert_one({
            'username': follow['follower'],
            'type': 'follow',
            'details': {
                'followed_user': follow['followed']
            },
            'timestamp': follow.get('created_at', follow.get('date', datetime.utcnow()))
        })
    
    # Update user stats
    users = db.users.find()
    for user in users:
        username = user['username']
        reviews_given = db.reviews.count_documents({'reviewer': username})
        reviews_received = db.reviews.count_documents({'author': username})
        following = db.follows.count_documents({'follower': username})
        followers = db.follows.count_documents({'followed': username})
        
        db.users.update_one(
            {'username': username},
            {'$set': {
                'stats': {
                    'reviews_given': reviews_given,
                    'reviews_received': reviews_received,
                    'following': following,
                    'followers': followers
                }
            }}
        )

if __name__ == '__main__':
    print("Starting database migration...")
    migrate_activities()
    print("Migration completed successfully!")

# Clear existing collections
print("Clearing existing collections...")
db.users.delete_many({})
db.books.delete_many({})
db.reviews.delete_many({})
db.follows.delete_many({})
db.activities.delete_many({})

# Sample books data with proper content
books_data = [
    {
        "title": "The Digital Revolution",
        "author": "James Anderson",
        "cover_image": "https://picsum.photos/seed/book1/400/600",
        "description": "A comprehensive look at how technology has transformed our world in the 21st century.",
        "content": """Chapter 1: The Dawn of Computing

In the early hours of the digital age, when computers occupied entire rooms and processed data through punch cards, few could have imagined the revolution that would unfold. The story of digital transformation begins not with smartphones or social media, but with the fundamental question of how to represent information in a form that machines could understand.

The binary system, using only ones and zeros, became the foundation of all modern computing. This simple yet powerful concept would eventually enable the creation of devices that could fit in our pockets while possessing more computing power than the machines that guided astronauts to the moon.

Chapter 2: The Internet Age

The development of the Internet marked a pivotal moment in human history. What started as a military project to create a decentralized communication network evolved into the global information superhighway we know today. The World Wide Web, introduced in the early 1990s, democratized information access and forever changed how we share knowledge.

As connection speeds increased and technology became more sophisticated, the Internet evolved from a simple text-based system into a rich multimedia platform. Social networks emerged, transforming how we maintain relationships and share our lives with others.

Chapter 3: The Mobile Revolution

The introduction of smartphones represented another quantum leap in the digital revolution. These powerful pocket computers have become essential tools in our daily lives, changing everything from how we navigate cities to how we shop and communicate.

The app economy has created new opportunities for entrepreneurs and developers, while mobile payment systems have begun to replace traditional banking in many parts of the world. The ability to be constantly connected has its drawbacks, but it has also enabled unprecedented levels of productivity and connectivity.

Chapter 4: The Future Ahead

As we look to the future, artificial intelligence and quantum computing promise to usher in the next phase of the digital revolution. Machine learning algorithms are already transforming industries from healthcare to transportation, while quantum computers may soon solve problems that are impossible for traditional computers to tackle.

The challenges ahead are significant, from protecting privacy to ensuring equitable access to technology. However, the potential benefits of continued digital innovation are enormous. As we move forward, it's crucial to shape this revolution in ways that benefit all of humanity while mitigating potential risks.

[Content continues...]""",
        "genres": ["Technology", "Non-Fiction", "Science"],
        "rating": 4.5,
        "reviews": [],
        "published_date": "2023-01-15",
        "pages": 320,
        "language": "English",
        "isbn": "978-1234567890"
    },
    {
        "title": "Echoes of Tomorrow",
        "author": "Emily Chen",
        "cover_image": "https://picsum.photos/seed/book2/400/600",
        "description": "A science fiction epic about humanity's first interstellar colony and the challenges they face.",
        "content": """Chapter 1: Departure

The massive colony ship Horizon hung in Earth's orbit like a silver needle against the black velvet of space. Sarah Chen stood at the observation deck, watching her home planet grow smaller with each passing moment. After fifteen years of preparation, humanity's first interstellar colony mission was finally underway.

"Final checks complete, all systems nominal," the ship's AI announced in its characteristic calm tone. "Preparing for quantum jump in T-minus 60 minutes."

Sarah's heart raced. As the mission's lead xenobiologist, she had trained for every conceivable scenario they might encounter on Kepler-186f. But nothing could truly prepare them for what lay ahead in the unknown.

Chapter 2: The Long Sleep

The cryogenic chambers hummed softly as five thousand colonists slept their way through the vast distance between stars. In their frozen dreams, they carried humanity's hopes for a new beginning. The journey would take fifty years, but for the sleeping passengers, it would feel like mere moments.

Only the ship's AI and a rotating crew of maintenance androids remained awake, tirelessly monitoring the vessel's systems and making course corrections as needed. The vast emptiness of interstellar space stretched endlessly in all directions.

Chapter 3: First Contact

The unexpected signal came during the forty-third year of their journey. At first, the ship's AI dismissed it as background radiation, but the pattern was too regular, too deliberate to be natural. Someone, or something, was trying to communicate.

Sarah, temporarily awakened for her scheduled maintenance check, found herself facing humanity's first potential contact with alien intelligence. The signal's source appeared to be their destination: Kepler-186f. Whatever awaited them there knew they were coming.

Chapter 4: New Earth

As they approached Kepler-186f, the planet's true nature began to reveal itself. The atmospheric readings matched Earth's almost exactly - too exactly. The more data they gathered, the more questions arose. Had someone been here before them? Had they been chosen, or had they been lured?

The colony ship Horizon carried not just humanity's hopes, but now also its fears into orbit around their new home. As the colonists began to wake from their long sleep, they would face decisions that would affect not just their own future, but potentially the future of all human civilization.

[Content continues...]""",
        "genres": ["Science Fiction", "Adventure", "Mystery"],
        "rating": 4.2,
        "reviews": [],
        "published_date": "2023-03-20",
        "pages": 405,
        "language": "English",
        "isbn": "978-0987654321"
    },
    {
        "title": "The Last Garden",
        "author": "Sarah Williams",
        "cover_image": "https://picsum.photos/seed/book3/400/600",
        "description": "A poetic exploration of nature and humanity in a world struggling with environmental change.",
        "content": """Chapter 1: Seeds of Change

The last garden on Earth wasn't in a place you'd expect. It wasn't in some government facility or wealthy estate. It was in my grandmother's backyard, hidden behind walls of recycled materials and protected by a canopy of solar panels that powered its artificial climate system.

I remember the day she first showed it to me, just after my sixteenth birthday. The world outside was brown and gray, the sky perpetually hazy with pollution and dust. But stepping into her garden was like entering another world entirely.

Chapter 2: The Green Memory

"Plants remember," Grandmother told me as she guided me through narrow paths between beds of vegetables and flowers. "They carry the memory of Earth as it once was, in every seed and every cell."

The air inside the garden was thick with humidity and the scent of growing things. Bees - real bees, not the mechanical pollinators that serviced the industrial crop facilities - buzzed between bright flowers. A small fountain recycled and purified the precious water that kept everything alive.

Chapter 3: Guardians of Life

We weren't supposed to have gardens anymore. The Resource Conservation Act had made private cultivation illegal, claiming it was wasteful and inefficient. But Grandmother was part of a secret network of gardeners who believed that maintaining Earth's biodiversity was worth any risk.

She taught me the ancient skills of saving seeds, of understanding soil composition, of working with nature instead of against it. Each plant in her garden had a story, a purpose, a place in the delicate web of life she maintained.

Chapter 4: Hope Grows

As the outside world continued to deteriorate, the garden became our sanctuary. More than that, it became our hope. Each successful harvest, each new seedling that pushed through the soil, was proof that life could persist, even thrive, if given the chance.

But we couldn't keep it secret forever. The day the authorities discovered our garden would change everything - though not in the way any of us expected. Sometimes the smallest seeds of resistance can grow into the mightiest movements for change.

[Content continues...]""",
        "genres": ["Literary Fiction", "Environmental", "Drama"],
        "rating": 4.0,
        "reviews": [],
        "published_date": "2023-05-10",
        "pages": 298,
        "language": "English",
        "isbn": "978-5432109876"
    },
    {
        "title": "Code of Honor",
        "author": "Michael Chang",
        "cover_image": "https://picsum.photos/seed/book4/400/600",
        "description": "A gripping military thriller about loyalty, betrayal, and the cost of keeping secrets.",
        "content": """Chapter 1: The Mission

Captain Sarah Chen knew something was wrong the moment her team landed in the drop zone. The intel had been too perfect, the insertion too smooth. After fifteen years in Special Operations, she had learned to trust her instincts.

"Delta Team, radio check," she whispered into her comm unit. Four clicks responded - all present and accounted for. The mountains of northern Afghanistan loomed around them, their peaks lost in the pre-dawn darkness.

Chapter 2: Betrayal

The target compound was exactly where it was supposed to be, but the security patterns were all wrong. Instead of the regular patrols they'd observed for weeks, the guards seemed to be waiting for something. Or someone.

"Command, this is Delta Lead," Sarah transmitted on the secure channel. "Request immediate verification of intel source." The response came back garbled, but one word came through clearly: "Abort."

It was already too late. The first explosions lit up the night sky, and Sarah realized with horrifying clarity - this wasn't just a compromised mission. It was a trap.

Chapter 3: The Code

Every Special Operations officer lived by the code: never leave anyone behind. But as Sarah watched her team members fall one by one to the ambush, she faced an impossible choice. The intel leak had come from inside their own organization, which meant the very people she was supposed to trust were the ones who had set them up.

The real mission, she now understood, wasn't the one in their briefing papers. It was finding out who had betrayed them, and why.

Chapter 4: Coming Home

The investigation led Sarah down a rabbit hole of classified operations, hidden agendas, and decades-old secrets. The code of honor that had guided her military career now pushed her to expose a conspiracy that reached the highest levels of command.

But in a world of shadows and secrets, the truth could be the deadliest weapon of all. As she pieced together the puzzle, Sarah realized that some codes were worth breaking to preserve the values they were meant to protect.

[Content continues...]""",
        "genres": ["Thriller", "Military", "Action"],
        "rating": 4.4,
        "reviews": [],
        "published_date": "2023-02-28",
        "pages": 456,
        "language": "English",
        "isbn": "978-6789054321"
    },
    {
        "title": "Whispers in Time",
        "author": "Isabella Romano",
        "cover_image": "https://picsum.photos/seed/book5/400/600",
        "description": "A romantic historical fiction weaving together past and present through a mysterious family heirloom.",
        "content": """Chapter 1: The Locket

The antique shop was exactly the kind of place Emma avoided - dusty, cramped, and full of other people's memories. But the locket in the window had caught her eye, its golden surface gleaming despite years of tarnish. Something about it seemed familiar, though she knew she'd never seen it before.

"It's been waiting for you," the elderly shopkeeper said when Emma entered. Before she could respond, he added, "Just like it waited for her, all those years ago."

Chapter 2: 1895

Catherine Montgomery straightened her gloves and took one last look in the mirror. The London season was in full swing, and tonight's ball at the Ashworth estate could change her life. The locket around her neck - her grandmother's final gift - felt warm against her skin.

She couldn't have known then how right she was, though not in any way she could have imagined. The secrets contained within that locket would spark a mystery that would span generations.

Chapter 3: Echoes

As Emma researched the locket's history, the parallels between her life and Catherine's became impossible to ignore. The same dreams, the same choices, even the same man - though separated by over a century.

The locket, she discovered, was more than just a family heirloom. It was a bridge between times, carrying messages from the past that could shape the future. But some messages came with a price.

Chapter 4: Time's Keeper

The truth about the locket emerged slowly, like a photograph developing in darkroom chemicals. It had been crafted by a clockmaker who claimed to have found a way to capture moments in time within its mechanical heart.

Those who wore it reported strange experiences - memories that weren't their own, knowledge they couldn't have possessed, and an overwhelming sense of destiny. As Emma delved deeper into its mysteries, she began to understand that some loves were strong enough to echo across centuries.

[Content continues...]""",
        "genres": ["Historical Fiction", "Romance", "Mystery"],
        "rating": 4.1,
        "reviews": [],
        "published_date": "2023-04-15",
        "pages": 368,
        "language": "English",
        "isbn": "978-3456789012"
    }
]

# PDF books data
pdf_books = [
    {
        "title": "WriteShelf Performance Summary",
        "author": "Seif Khashaba",
        "cover_image": "https://picsum.photos/seed/perf/400/600",
        "description": "A comprehensive analysis of WriteShelf's performance metrics and optimization strategies.",
        "is_pdf": True,
        "pdf_path": "docs/Performance Summary.pdf",
        "genres": ["Technical", "Documentation", "Performance"],
        "rating": 0,
        "reviews": [],
        "published_date": "2023-12-22",
        "pages": 25,
        "language": "English",
        "isbn": "978-0001112223"
    },
    {
        "title": "WriteShelf Software Design Specification",
        "author": "Seif Khashaba",
        "cover_image": "https://picsum.photos/seed/sds/400/600",
        "description": "Detailed software design specifications for the WriteShelf platform.",
        "is_pdf": True,
        "pdf_path": "docs/SDS document of writeshelf.pdf",
        "genres": ["Technical", "Documentation", "Design"],
        "rating": 0,
        "reviews": [],
        "published_date": "2023-12-22",
        "pages": 40,
        "language": "English",
        "isbn": "978-0001112224"
    },
    {
        "title": "WriteShelf Software Requirements Specification",
        "author": "Seif Khashaba",
        "cover_image": "https://picsum.photos/seed/srs/400/600",
        "description": "Comprehensive software requirements specification document for WriteShelf.",
        "is_pdf": True,
        "pdf_path": "docs/SRS document of Writeshelf.pdf",
        "genres": ["Technical", "Documentation", "Requirements"],
        "rating": 0,
        "reviews": [],
        "published_date": "2023-12-22",
        "pages": 50,
        "language": "English",
        "isbn": "978-0001112225"
    },
    {
        "title": "WriteShelf Functional Documentation",
        "author": "Seif Khashaba",
        "cover_image": "https://picsum.photos/seed/func/400/600",
        "description": "Functional documentation covering all features and capabilities of WriteShelf.",
        "is_pdf": True,
        "pdf_path": "docs/WriteShelf - Functional Documentation.pdf",
        "genres": ["Technical", "Documentation", "Functional"],
        "rating": 0,
        "reviews": [],
        "published_date": "2023-12-22",
        "pages": 35,
        "language": "English",
        "isbn": "978-0001112226"
    },
    {
        "title": "WriteShelf Project Reflections",
        "author": "Seif Khashaba",
        "cover_image": "https://picsum.photos/seed/refl/400/600",
        "description": "Personal reflections and insights from the development of WriteShelf.",
        "is_pdf": True,
        "pdf_path": "docs/reflections on the work done.pdf",
        "genres": ["Technical", "Documentation", "Reflection"],
        "rating": 0,
        "reviews": [],
        "published_date": "2023-12-22",
        "pages": 20,
        "language": "English",
        "isbn": "978-0001112227"
    }
]

# Insert books
books_data.extend(pdf_books)
db.books.delete_many({})
db.books.insert_many(books_data)

print("Database initialized with sample data!")
