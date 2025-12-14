#!/usr/bin/env python3
"""
Enrich dream database with missing categories:
- Emotional-state dreams
- Situational/stress-pattern dreams  
- Dream-state experiences
- Spiritual/archetypal symbols
"""

import json
import os
import re
from pathlib import Path
from normalize_dream_database import normalize_explanation, create_normalized_short

DREAM_DB_FILE = Path("data/dream_database.json")
BOOKS_DIR = Path("without background BOOK")
EMOJIS_DIR = Path("without background")

# Emotion keyword mapping (from assign_books_emojis.py)
EMOJI_RULES = {
    "Angry": ["anger", "rage", "fight", "attack", "violence", "enemy", "quarrel", "quarrels", "suspicion", "distress", "distressing", "ruin", "ruinous", "bickerings", "false dealings", "dislike", "abhor", "resent", "resentment", "hostile", "hostility", "wrath", "fury", "outrage", "indignation", "irritation", "annoyance", "displeasure"],
    "Rage": ["rage", "fury", "violent", "violence", "outburst", "temper", "wrath", "outrage", "frenzy", "storm", "explosion", "eruption"],
    "Pissed": ["annoyed", "irritated", "frustrated", "displeased", "vexed", "bothered", "irked", "exasperated"],
    "Sad": ["loss", "grief", "sorrow", "cry", "tears", "misery", "unhappy", "unhappiness", "difficulty", "difficulties", "failure", "failures", "disappointment", "disappointments", "gloomy", "gloom", "melancholy", "dejection", "despondency", "downcast", "downhearted", "forlorn", "woeful", "wretched"],
    "Crying": ["cry", "weep", "tears", "mourn", "lament", "sob", "bawl", "wail", "whimper", "snivel"],
    "Heartbroken": ["heartbreak", "betrayal", "abandon", "abandoned", "rejection", "despair", "desperate", "hopeless", "crushed", "devastated", "shattered", "broken heart"],
    "Hurt": ["wound", "wounded", "injury", "injured", "pain", "painful", "betray", "betrayed", "betrayal", "harm", "harmed", "suffer", "suffering", "hurt", "hurtful", "damage", "damaged", "affliction", "torment", "torture", "agony", "anguish"],
    "Fear": ["fear", "fears", "fearful", "danger", "dangerous", "threat", "threaten", "threatened", "anxiety", "anxious", "panic", "panicked", "terror", "terrified", "dread", "dreaded", "apprehension", "apprehensive", "alarm", "alarmed", "fright", "frightened", "horror", "horrified", "trepidation", "unease", "uneasy"],
    "Nervous": ["nervous", "nervousness", "anxious", "anxiety", "worried", "worry", "uneasy", "tension", "tense", "restless", "restlessness", "jittery", "edgy", "on edge", "apprehensive", "fretful"],
    "Love": ["love", "loved", "loving", "affection", "affectionate", "desire", "desired", "marriage", "marry", "married", "sweetheart", "romance", "romantic", "passion", "passionate", "adore", "adored", "cherish", "cherished", "fond", "fondness", "devotion", "devoted", "tender", "tenderness"],
    "Want": ["want", "wanted", "desire", "desired", "wish", "wished", "crave", "craved", "long", "longing", "yearn", "yearning", "covet", "coveted", "hunger", "hungered", "thirst", "thirsted"],
    "Money": ["wealth", "wealthy", "money", "monetary", "profit", "profits", "profitable", "gain", "gains", "fortune", "fortunes", "inheritance", "inherit", "riches", "rich", "financial", "finance", "finances", "treasure", "treasures", "valuables", "valuable", "prosperity", "prosperous", "affluence", "affluent", "opulence", "opulent"],
    "Risk": ["risk", "risks", "risky", "chance", "chances", "gamble", "gambling", "uncertain", "uncertainty", "uncertainties", "danger", "dangerous", "peril", "perilous", "hazard", "hazardous", "venture", "speculation", "speculate", "precarious", "unstable"],
    "Devil": ["evil", "evils", "sin", "sins", "sinful", "temptation", "temptations", "tempt", "tempted", "corruption", "corrupt", "corrupted", "wicked", "wickedness", "devil", "devilish", "satanic", "demonic", "diabolical", "malicious", "malice", "vicious", "vice"],
    "Evil": ["evil", "evils", "malicious", "malice", "harmful", "wicked", "wickedness", "vicious", "vice", "sinister", "nefarious", "villainous", "treacherous", "treachery", "deceitful", "deceit"],
    "Angel": ["protection", "protect", "protected", "help", "helped", "helpful", "guidance", "guide", "guided", "blessing", "bless", "blessed", "angel", "angelic", "divine", "holy", "sacred", "benevolent", "beneficent", "guardian", "savior", "saved"],
    "Question": ["doubt", "doubts", "doubtful", "confusion", "confused", "uncertain", "uncertainty", "uncertainties", "unknown", "question", "questions", "mystery", "mysteries", "mysterious", "puzzle", "puzzled", "bewilderment", "bewildered", "perplexed", "perplexity", "unclear", "unclear"],
    "Proud": ["success", "succeed", "succeeded", "successful", "victory", "victories", "victorious", "honor", "honored", "honorable", "pride", "proud", "triumph", "triumphant", "achievement", "achievements", "achieved", "accomplish", "accomplished", "glory", "glorious", "excellence", "excellent"],
    "Honor": ["honor", "honored", "honorable", "respect", "respected", "respectable", "dignity", "dignified", "noble", "nobility", "worthy", "worth", "esteem", "esteemed", "reputation", "repute", "prestige", "prestigious"],
    "Sick": ["illness", "ill", "disease", "diseased", "weakness", "weak", "sick", "sickness", "ailment", "ailments", "unwell", "ailing", "afflicted", "affliction", "contagion", "contagious", "infection", "infected", "malady", "disorder"],
    "Dead": ["death", "dead", "dying", "died", "ending", "endings", "ended", "final", "finally", "mortal", "mortality", "mortal", "demise", "deceased", "perish", "perished", "expire", "expired", "tragedy", "tragic", "fatal", "fatality"],
    "Surprised": ["unexpected", "sudden", "suddenly", "shock", "shocked", "surprise", "surprised", "astonish", "astonished", "astonishment", "amaze", "amazed", "amazement", "startle", "startled"],
    "Shocked": ["shock", "shocked", "surprise", "surprised", "astonish", "astonished", "amaze", "amazed", "stun", "stunned", "stunning", "astound", "astounded", "bewilder", "bewildered", "dumbfounded", "flabbergasted"],
    "Awe": ["awe", "awed", "wonder", "wondered", "wonderful", "amazement", "amazed", "reverence", "reverent", "admiration", "admire", "admired", "marvel", "marveled", "marvelous", "magnificent", "splendid", "sublime"],
    "Disgust": ["disgust", "disgusted", "disgusting", "revulsion", "revulsed", "repulsion", "repulsed", "loathing", "loathe", "loathed", "abhor", "abhorred", "abhorrence", "repugnance", "repugnant", "nauseate", "nauseated", "nauseating"],
    "Jealousy": ["jealous", "jealousy", "envy", "envied", "envious", "covet", "coveted", "covetous", "resent", "resented", "resentment", "resentful", "grudge", "grudged"],
    "Vengeance": ["vengeance", "revenge", "revenged", "retaliation", "retaliate", "retaliated", "retribution", "retributive", "avenge", "avenged", "reprisal", "reprisals"],
    "Sneaky": ["sneaky", "sneak", "sneaked", "deceit", "deceitful", "deceived", "trick", "tricked", "tricky", "stealth", "stealthy", "cunning", "crafty", "sly", "slyly", "scheme", "schemes", "scheming", "plot", "plots", "plotted", "treacherous", "treachery"],
    "Rightious": ["righteous", "righteousness", "just", "justice", "moral", "morality", "virtuous", "virtue", "upright", "honest", "honesty", "integrity", "ethical", "ethics", "principled"],
    "Judging": ["judge", "judged", "judgment", "judgments", "criticize", "criticized", "criticism", "condemn", "condemned", "condemnation", "evaluate", "evaluated", "evaluation", "censure", "censured", "reproach", "reproached", "rebuke", "rebuked"],
    "Planning": ["plan", "plans", "planned", "scheme", "schemes", "scheming", "strategy", "strategies", "strategic", "prepare", "prepared", "preparation", "arrange", "arranged", "arrangement", "organize", "organized", "organization", "design", "designed", "intend", "intended", "intention"],
    "Effort": ["effort", "efforts", "work", "worked", "working", "labor", "labored", "struggle", "struggled", "struggles", "endeavor", "endeavored", "endeavors", "strive", "strived", "striving", "toil", "toiled", "exertion", "exerted"],
    "Tired": ["tired", "tiredness", "exhausted", "exhaustion", "weary", "weariness", "fatigue", "fatigued", "drained", "drain", "spent", "worn", "worn out", "depleted", "depletion"],
    "Bored": ["bored", "boredom", "tedious", "tedium", "monotonous", "monotony", "dull", "dullness", "uninteresting", "uninterested", "apathetic", "apathy", "indifferent", "indifference"],
    "Cool": ["cool", "calm", "calmness", "composed", "composure", "collected", "serene", "serenity", "peaceful", "peace", "tranquil", "tranquility", "relaxed", "relaxation", "unbothered", "unfazed"],
    "Unbothered": ["unbothered", "unfazed", "indifferent", "indifference", "nonchalant", "nonchalance", "detached", "detachment", "unconcerned", "unconcern", "unmoved", "unaffected"],
    "Playful": ["playful", "play", "played", "fun", "funny", "humor", "humorous", "lighthearted", "lightheartedness", "cheerful", "cheer", "cheerfulness", "joyful", "joy", "merry", "merriment"],
    "Grin": ["grin", "grinned", "smile", "smiled", "smiling", "happy", "happiness", "joy", "joyful", "cheerful", "cheer", "delight", "delighted", "pleasure", "pleased"],
    "Blush": ["blush", "blushed", "embarrassed", "embarrassment", "shy", "shyness", "bashful", "bashfulness", "modest", "modesty", "flustered", "fluster", "self-conscious", "self-consciousness"],
    "Mean": ["mean", "meanness", "cruel", "cruelty", "harsh", "harshness", "unkind", "unkindness", "nasty", "nastiness", "spiteful", "spite", "malicious", "malice"],
    "Taunt": ["taunt", "taunted", "mock", "mocked", "ridicule", "ridiculed", "tease", "teased", "teasing", "sarcasm", "sarcastic", "sardonic", "deride", "derided", "derision"],
    "Smug": ["smug", "smugness", "arrogant", "arrogance", "conceited", "conceit", "self-satisfied", "self-satisfaction", "complacent", "complacency", "superior", "superiority"],
    "Irony": ["irony", "ironic", "sarcasm", "sarcastic", "satirical", "satire", "wry", "wryly", "cynical", "cynicism"],
    "Begging": ["beg", "begged", "begging", "plead", "pleaded", "pleading", "implore", "implored", "beseech", "beseeched", "supplicate", "supplicated", "entreat", "entreated"],
    "Sweat": ["sweat", "sweating", "sweated", "perspire", "perspired", "perspiration", "anxious", "anxiety", "nervous", "nervousness", "worried", "worry", "stressed", "stress"],
    "Dizzy": ["dizzy", "dizziness", "dazed", "daze", "confused", "confusion", "disoriented", "disorientation", "bewildered", "bewilderment", "lightheaded", "lightheadedness"],
    "Ackward": ["awkward", "awkwardness", "uncomfortable", "discomfort", "uneasy", "uneasiness", "embarrassed", "embarrassment", "self-conscious", "self-consciousness", "clumsy", "clumsiness"],
    "Agree": ["agree", "agreed", "agreement", "consent", "consented", "approve", "approved", "approval", "accept", "accepted", "acceptance", "concur", "concurred", "assent", "assented"],
    "Starstruck": ["starstruck", "awe", "awed", "wonder", "wondered", "amazement", "amazed", "admiration", "admire", "admired", "reverence", "reverent", "fascination", "fascinated"],
    "Poison": ["poison", "poisoned", "poisonous", "toxic", "toxicity", "venom", "venomous", "harmful", "harm", "harmed", "noxious", "deadly", "lethal", "fatal"],
    "Cold": ["cold", "coldness", "distant", "distance", "aloof", "aloofness", "unfeeling", "unfeelingness", "frigid", "frigidity", "frosty", "chilly", "indifferent", "indifference"]
}

def get_book_for_word(word: str, available_books: list) -> str:
    """Assign a book deterministically using hash."""
    if not available_books:
        return None
    book_index = hash(word.lower()) % len(available_books)
    return available_books[book_index].name

def get_emoji_for_explanation(explanation: str, word: str = None) -> str:
    """Match emoji based on emotion keywords in explanation."""
    explanation_lower = explanation.lower()
    word_lower = word.lower() if word else ""
    scores = {}
    
    # First, check if the word itself matches an emoji name exactly
    if word:
        for emoji_name in EMOJI_RULES.keys():
            if word_lower == emoji_name.lower():
                return f"{emoji_name}.png"
    
    # Then check keywords in explanation
    for emoji_name, keywords in EMOJI_RULES.items():
        score = 0
        for keyword in keywords:
            # Count occurrences of keyword in explanation
            score += len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', explanation_lower))
        if score > 0:
            scores[emoji_name] = score
    
    if scores:
        # Return emoji with highest score
        best_emoji = max(scores.items(), key=lambda x: x[1])[0]
        return f"{best_emoji}.png"
    
    return "Cool.png"  # Default neutral

def create_new_entries():
    """Create new dream database entries for missing categories."""
    
    # A. Emotional-state dreams
    emotional_entries = [
        {
            "word": "Anxiety",
            "explanations": [
                "To dream of anxiety reflects unresolved feelings that are active in waking life and seeking expression. It suggests inner tension or worry about future events or decisions."
            ]
        },
        {
            "word": "Fear",
            "explanations": [
                "To dream of fear suggests that you are avoiding something in waking life that demands attention. It reflects deep concerns or threats that feel overwhelming."
            ]
        },
        {
            "word": "Helplessness",
            "explanations": [
                "To dream of feeling helpless suggests a loss of control or power in waking life. It reflects situations where you feel unable to influence outcomes or protect yourself."
            ]
        },
        {
            "word": "Pressure",
            "explanations": [
                "To dream of pressure suggests you are feeling overwhelmed by responsibilities or expectations. It reflects stress from demands that feel too heavy to bear."
            ]
        },
        {
            "word": "Shame",
            "explanations": [
                "To dream of shame suggests feelings of unworthiness or exposure of something you wish to hide. It reflects inner judgment or fear of being seen as flawed."
            ]
        },
        {
            "word": "Desire",
            "explanations": [
                "To dream of desire suggests unmet longings or wants that are active in your unconscious. It reflects what you yearn for but may not yet have or acknowledge."
            ]
        },
        {
            "word": "Temptation",
            "explanations": [
                "To dream of temptation suggests inner conflict between what you want and what you believe is right. It reflects choices that challenge your values or self-control."
            ]
        },
        {
            "word": "Guilt",
            "explanations": [
                "To dream of guilt suggests unresolved feelings about past actions or choices. It reflects self-judgment or the need to make amends for something you have done."
            ]
        },
        {
            "word": "Liberation",
            "explanations": [
                "To dream of liberation suggests freedom from constraints or limitations. It reflects breaking free from situations, beliefs, or patterns that have held you back."
            ]
        },
        {
            "word": "Control",
            "explanations": [
                "To dream of control suggests a need for power or influence over your circumstances. It reflects either having control or feeling its absence in waking life."
            ]
        },
        {
            "word": "Loss of Control",
            "explanations": [
                "To dream of losing control suggests fear of chaos or inability to manage your life. It reflects situations where you feel powerless or overwhelmed by events."
            ]
        },
        {
            "word": "Confidence",
            "explanations": [
                "To dream of confidence suggests self-assurance and belief in your abilities. It reflects inner strength and readiness to face challenges or pursue goals."
            ]
        },
        {
            "word": "Confusion",
            "explanations": [
                "To dream of confusion suggests uncertainty or lack of clarity about direction or decisions. It reflects inner disorientation or conflicting information."
            ]
        },
        {
            "word": "Anticipation",
            "explanations": [
                "To dream of anticipation suggests waiting for something significant to happen. It reflects expectation, hope, or anxiety about future events or outcomes."
            ]
        },
        {
            "word": "Vulnerability",
            "explanations": [
                "To dream of vulnerability suggests feeling exposed or unprotected. It reflects situations where you feel open to harm, judgment, or emotional risk."
            ]
        },
        {
            "word": "Urgency",
            "explanations": [
                "To dream of urgency suggests pressure to act quickly or meet deadlines. It reflects time-sensitive concerns or the feeling that something must be done immediately."
            ]
        }
    ]
    
    # B. Situational / stress-pattern dreams
    situational_entries = [
        {
            "word": "Being Chased",
            "explanations": [
                "To dream of being chased suggests avoidance of a fear, responsibility, or truth that demands attention. It reflects running from something you need to confront."
            ]
        },
        {
            "word": "Being Tested",
            "explanations": [
                "To dream of taking a test reflects feelings of scrutiny, self-doubt, or fear of failure in waking life. It suggests you are being evaluated or judging your own performance."
            ]
        },
        {
            "word": "Being Late",
            "explanations": [
                "To dream of being late suggests anxiety about missing opportunities or failing to meet expectations. It reflects fear of not being prepared or falling behind."
            ]
        },
        {
            "word": "Falling",
            "explanations": [
                "To dream of falling signifies loss of stability, fear of exposure, or surrender to an impulse. It reflects the feeling of losing control or descending into uncertainty."
            ]
        },
        {
            "word": "Flying",
            "explanations": [
                "To dream of flying indicates liberation, confidence, or awareness of your own mental freedom. It suggests rising above limitations or gaining a new perspective."
            ]
        },
        {
            "word": "Losing Teeth",
            "explanations": [
                "To dream of teeth breaking or falling suggests anxiety about appearance, power, or personal security. It reflects fear of losing attractiveness, communication ability, or control."
            ]
        },
        {
            "word": "Being Attacked",
            "explanations": [
                "To dream of being attacked suggests feeling threatened or vulnerable in waking life. It reflects fears of harm, criticism, or violation of your boundaries or safety."
            ]
        },
        {
            "word": "Being Unable to Move",
            "explanations": [
                "To dream of being unable to move suggests feeling paralyzed by fear, stress, or circumstances. It reflects situations where you feel stuck or powerless to act."
            ]
        },
        {
            "word": "Being Watched",
            "explanations": [
                "To dream of being watched suggests feeling observed or judged by others. It reflects self-consciousness, fear of exposure, or awareness of scrutiny in waking life."
            ]
        },
        {
            "word": "Being Trapped",
            "explanations": [
                "To dream of being trapped suggests feeling confined or unable to escape a situation. It reflects circumstances where you feel limited, restricted, or without options."
            ]
        }
    ]
    
    # C. Dream-state experiences
    dream_state_entries = [
        {
            "word": "Lucid Dreaming",
            "explanations": [
                "To dream with awareness suggests a growing sense of control or insight into your inner life. It reflects the ability to observe and influence your own mental processes."
            ]
        },
        {
            "word": "Nightmares",
            "explanations": [
                "To experience a nightmare reflects unresolved fears or emotions demanding conscious attention. It suggests powerful anxieties or traumas that need to be addressed."
            ]
        },
        {
            "word": "Recurring Dreams",
            "explanations": [
                "To dream the same dream repeatedly suggests an unresolved issue or pattern that persists in your unconscious. It reflects something that needs attention or integration."
            ]
        },
        {
            "word": "Sleep Paralysis",
            "explanations": [
                "To dream of being awake but unable to move signifies fear, stress, or conflict between mind and body. It reflects the feeling of being conscious but powerless to act."
            ]
        },
        {
            "word": "Out-of-Body Experience",
            "explanations": [
                "To dream of leaving your body suggests detachment from identity, transformation, or altered self-perception. It reflects viewing yourself or your life from a different perspective."
            ]
        },
        {
            "word": "Astral Projection",
            "explanations": [
                "To dream of astral projection suggests separation of consciousness from the physical form. It reflects exploration beyond normal boundaries or seeking freedom from limitations."
            ]
        }
    ]
    
    # D. Spiritual / archetypal symbols (cleaned up)
    spiritual_entries = [
        {
            "word": "Snake",
            "explanations": [
                "To dream of a snake represents transformation, hidden power, temptation, or awakening awareness. It suggests deep change, healing, or the presence of something that requires attention."
            ]
        },
        {
            "word": "Circle",
            "explanations": [
                "To dream of circular forms suggests wholeness, cycles, and movement toward completion. It reflects unity, continuity, or the completion of a cycle in your life."
            ]
        },
        {
            "word": "Wheel",
            "explanations": [
                "To dream of a wheel suggests cycles, change, and the turning of fate. It reflects movement, progress, or the inevitability of change and transformation."
            ]
        },
        {
            "word": "Phoenix",
            "explanations": [
                "To dream of a phoenix signifies rebirth following loss or inner transformation. It suggests rising from difficult circumstances with renewed strength or purpose."
            ]
        },
        {
            "word": "Tree",
            "explanations": [
                "To dream of a tree reflects growth, grounding, and the connection between inner and outer life. It suggests stability, life force, or your relationship to nature and self."
            ]
        },
        {
            "word": "Yin and Yang",
            "explanations": [
                "To dream of dual symbols represents balance, integration, and opposing forces seeking harmony. It reflects the need to reconcile contradictions or find unity in opposites."
            ]
        }
    ]
    
    all_new_entries = emotional_entries + situational_entries + dream_state_entries + spiritual_entries
    
    return all_new_entries

def enrich_database():
    """Add new entries to the dream database."""
    print("Loading dream database...")
    with open(DREAM_DB_FILE, "r", encoding="utf-8") as f:
        dream_db = json.load(f)
    
    # Get existing words to avoid duplicates
    existing_words = {entry["word"].lower() for entry in dream_db}
    
    # Get available books
    books_dir = BOOKS_DIR
    available_books = sorted(books_dir.glob("*.png")) if books_dir.exists() else []
    
    if not available_books:
        print(f"Warning: No books found in {books_dir}")
        return
    
    print(f"Found {len(available_books)} book images")
    
    # Get available emojis
    emojis_dir = EMOJIS_DIR
    available_emojis = {f.name.lower(): f.name for f in emojis_dir.glob("*.png")} if emojis_dir.exists() else {}
    
    print(f"Found {len(available_emojis)} emoji images")
    
    # Create new entries
    new_entries_data = create_new_entries()
    
    print(f"\nProcessing {len(new_entries_data)} new entries...")
    
    # Unlock file for writing
    os.chmod(DREAM_DB_FILE, 0o644)
    
    try:
        added_count = 0
        skipped_count = 0
        
        for entry_data in new_entries_data:
            word = entry_data["word"]
            
            # Skip if already exists
            if word.lower() in existing_words:
                print(f"  Skipping '{word}' - already exists")
                skipped_count += 1
                continue
            
            # Create entry in correct format
            explanations = entry_data["explanations"]
            
            # Normalize explanations
            normalized = []
            for exp in explanations:
                normalized_exp = normalize_explanation(exp, word)
                if normalized_exp:
                    normalized.append(normalized_exp)
            
            # Create normalized_short
            normalized_short = create_normalized_short(normalized, max_sentences=2) if normalized else ""
            
            # Assign book
            book_filename = get_book_for_word(word, available_books)
            
            # Assign emoji based on explanation and word
            combined_explanation = " ".join(explanations)
            emoji_filename = get_emoji_for_explanation(combined_explanation, word)
            
            # Verify emoji exists
            if emoji_filename.lower() not in available_emojis:
                emoji_filename = "Cool.png"  # Fallback
            
            # Create final entry
            new_entry = {
                "word": word,
                "explanations": explanations,
                "book": book_filename,
                "emoji": emoji_filename,
                "normalized": normalized,
                "normalized_short": normalized_short if normalized_short else None
            }
            
            # Remove normalized_short if empty
            if not normalized_short:
                del new_entry["normalized_short"]
            
            dream_db.append(new_entry)
            existing_words.add(word.lower())
            added_count += 1
            
            if added_count % 10 == 0:
                print(f"  Added {added_count} entries...")
        
        # Sort by word (alphabetically)
        dream_db.sort(key=lambda x: x["word"].lower())
        
        # Write back to file
        print(f"\nWriting enriched database...")
        with open(DREAM_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(dream_db, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully added {added_count} new entries!")
        print(f"Skipped {skipped_count} entries (already exist)")
        print(f"Total entries in database: {len(dream_db)}")
        
    finally:
        # Lock file back to read-only
        os.chmod(DREAM_DB_FILE, 0o444)
        print("Database locked (read-only).")

if __name__ == "__main__":
    enrich_database()
