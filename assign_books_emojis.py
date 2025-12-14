#!/usr/bin/env python3
"""
Assign books and emojis to dream database words.
- Books: Deterministic hash-based assignment (1 of 50)
- Emojis: Emotion-based matching from explanation text
"""

import json
import re
from pathlib import Path
from collections import Counter

DREAM_DB_FILE = Path("data/dream_database.json")
BOOKS_DIR = Path("without background BOOK")
EMOJIS_DIR = Path("without background")

# Emotion keyword mapping to emoji files - enriched with synonyms and logical connections
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
    "Tired": ["tired", "tire", "tiredness", "exhausted", "exhaustion", "weary", "weariness", "fatigued", "fatigue", "drained", "drain", "drained", "spent", "worn", "worn out", "depleted"],
    "Bored": ["bored", "boredom", "tedious", "tedium", "monotonous", "monotony", "dull", "dullness", "uninteresting", "tiresome", "wearisome"],
    "Cool": ["calm", "calmly", "cool", "composed", "collected", "serene", "serenity", "peaceful", "peace", "tranquil", "tranquility", "placid", "steady", "steadily", "unruffled", "unperturbed"],
    "Unbothered": ["unbothered", "indifferent", "indifference", "unconcerned", "unconcern", "detached", "detachment", "aloof", "nonchalant", "nonchalance", "apathetic", "apathy"],
    "Playful": ["playful", "play", "played", "fun", "funny", "joy", "joyful", "merry", "merriment", "cheerful", "cheer", "cheered", "jovial", "jolly", "lighthearted", "frolicsome"],
    "Grin": ["grin", "grinned", "smile", "smiled", "smiling", "happy", "happiness", "joy", "joyful", "pleasure", "pleased", "pleasing", "delight", "delighted", "delightful", "glad", "gladness", "cheerful", "cheer"],
    "Blush": ["blush", "blushed", "blushing", "embarrass", "embarrassed", "embarrassment", "shy", "shyness", "modest", "modesty", "bashful", "bashfulness", "self-conscious", "flushed"],
    "Mean": ["mean", "meanness", "cruel", "cruelty", "harsh", "harshness", "unkind", "unkindness", "malicious", "malice", "nasty", "nastiness", "spiteful", "spite", "vicious", "viciousness"],
    "Taunt": ["taunt", "taunted", "mock", "mocked", "mocking", "ridicule", "ridiculed", "ridiculous", "tease", "teased", "teasing", "insult", "insulted", "insulting", "deride", "derided", "derision", "scoff", "scoffed"],
    "Smug": ["smug", "smugness", "arrogant", "arrogance", "conceited", "conceit", "self-satisfied", "self-satisfaction", "complacent", "complacency", "pompous", "pomposity", "haughty", "haughtiness"],
    "Irony": ["irony", "ironic", "sarcasm", "sarcastic", "mockery", "mocking", "satire", "satirical", "satirize", "satirized", "sardonic", "sardonically"],
    "Begging": ["beg", "begged", "begging", "plead", "pleaded", "pleading", "supplicate", "supplication", "entreat", "entreated", "entreaty", "beseech", "beseeched", "implore", "implored"],
    "Sweat": ["sweat", "sweating", "sweated", "anxious", "anxiety", "nervous", "nervousness", "worried", "worry", "worries", "perspire", "perspiring", "perspired"],
    "Dizzy": ["dizzy", "dizziness", "confused", "confusion", "disoriented", "disorientation", "bewildered", "bewilderment", "perplexed", "perplexity", "puzzled", "puzzle", "baffled", "bafflement"],
    "Ackward": ["awkward", "awkwardness", "uncomfortable", "uncomfortableness", "embarrassing", "embarrassment", "clumsy", "clumsiness", "inept", "ineptitude", "ungainly", "gauche"],
    "Agree": ["agree", "agreed", "agreement", "accept", "accepted", "acceptance", "consent", "consented", "approve", "approved", "approval", "assent", "assented", "concur", "concurred", "accord", "accorded"],
    "Starstruck": ["starstruck", "admire", "admired", "admiration", "idolize", "idolized", "worship", "worshiped", "revere", "revered", "reverence", "venerate", "venerated", "adore", "adored"],
    "Poison": ["poison", "poisoned", "poisonous", "toxic", "toxicity", "venom", "venomous", "harmful", "harm", "harmed", "noxious", "deadly", "lethal", "fatal"],
    "Cold": ["cold", "coldness", "distant", "distance", "aloof", "aloofness", "unfeeling", "unfeelingness", "frigid", "frigidity", "frosty", "chilly", "indifferent", "indifference"]
}

def get_book_for_word(word: str, available_books: list) -> str:
    """Assign a book deterministically using hash."""
    # Use hash for deterministic assignment
    if not available_books:
        return None
    book_index = hash(word.lower()) % len(available_books)
    return available_books[book_index].name

def get_emoji_for_explanation(explanation: str) -> str:
    """Match emoji based on emotion keywords in explanation."""
    explanation_lower = explanation.lower()
    
    # Score each emoji based on keyword matches
    scores = {}
    for emoji_name, keywords in EMOJI_RULES.items():
        score = 0
        for keyword in keywords:
            # Count occurrences of keyword in explanation
            score += len(re.findall(r'\b' + re.escape(keyword) + r'\b', explanation_lower))
        if score > 0:
            scores[emoji_name] = score
    
    if scores:
        # Get emoji with highest score
        best_emoji = max(scores.items(), key=lambda x: x[1])[0]
        return f"{best_emoji}.png"
    else:
        # Default to neutral emoji
        return "Cool.png"

def assign_books_and_emojis():
    """Assign books and emojis to all words in dream database."""
    print("Loading dream database...")
    with open(DREAM_DB_FILE, "r", encoding="utf-8") as f:
        dream_db = json.load(f)
    
    print(f"Processing {len(dream_db)} words...")
    
    # Get available books
    books_dir = BOOKS_DIR
    available_books = sorted(books_dir.glob("*.png")) if books_dir.exists() else []
    num_books = len(available_books)
    
    if num_books == 0:
        print(f"Warning: No books found in {books_dir}")
        return
    
    print(f"Found {num_books} book images")
    
    # Get available emojis
    emojis_dir = EMOJIS_DIR
    available_emojis = {f.name.lower(): f.name for f in emojis_dir.glob("*.png")} if emojis_dir.exists() else {}
    
    print(f"Found {len(available_emojis)} emoji images")
    
    # Process each word
    updated_count = 0
    for entry in dream_db:
        word = entry["word"]
        explanations = entry.get("explanations", [])
        
        # Assign book deterministically
        book_filename = get_book_for_word(word, available_books)
        entry["book"] = book_filename
        
        # Assign emoji based on explanation
        if explanations:
            # Use the first explanation (or combine all for better emotion detection)
            combined_explanation = " ".join(explanations)
            emoji_filename = get_emoji_for_explanation(combined_explanation)
            
            # Verify emoji exists
            if emoji_filename.lower() not in available_emojis:
                emoji_filename = "Cool.png"  # Fallback to neutral
            
            entry["emoji"] = emoji_filename
        else:
            entry["emoji"] = "Cool.png"  # Default neutral
        
        updated_count += 1
    
    # Save updated database
    print(f"\nUpdating database with books and emojis...")
    with open(DREAM_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dream_db, f, indent=2, ensure_ascii=False)
    
    print(f"Updated {updated_count} words with book and emoji assignments")
    
    # Show some examples
    print("\nExamples:")
    for entry in dream_db[:5]:
        print(f"  {entry['word']}: book={entry.get('book')}, emoji={entry.get('emoji')}")

if __name__ == "__main__":
    assign_books_and_emojis()
