#!/usr/bin/env python3
"""
Add comprehensive dream entries covering emotions, situations, modern objects, body experiences, archetypes, and dream-state meta symbols.
All entries have unique, non-generic interpretations.
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
    "Sweat": ["sweat", "sweating", "sweated", "perspire", "perspired", "perspiration", "anxious", "anxiety", "nervous", "nervousness", "worried", "worry", "stressed", "stress"]
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

def create_comprehensive_entries():
    """Create comprehensive dream entries with unique explanations."""
    
    entries = []
    
    # 1. Core Dream Feelings - Fear/Anxiety spectrum
    entries.extend([
        {
            "word": "Panic",
            "explanations": [
                "To dream of panic suggests overwhelming fear that has reached a breaking point. It reflects the experience of being completely overwhelmed by anxiety or danger, often signaling the need for immediate support or intervention."
            ]
        },
        {
            "word": "Dread",
            "explanations": [
                "To dream of dread indicates deep, persistent fear about something anticipated. It reflects the heavy weight of foreboding and the sense that something terrible is approaching, even if you cannot name what it is."
            ]
        },
        {
            "word": "Terror",
            "explanations": [
                "To dream of terror suggests extreme fear that paralyzes or overwhelms. It reflects the experience of being completely consumed by horror, often pointing to trauma or deeply buried fears that need attention."
            ]
        },
        {
            "word": "Paranoia",
            "explanations": [
                "To dream of paranoia indicates mistrust, suspicion, or the feeling that others are against you. It reflects fear of being watched, judged, or harmed, often stemming from past betrayals or current insecurities."
            ]
        },
        {
            "word": "Being Hunted",
            "explanations": [
                "To dream of being hunted suggests feeling pursued by something that wants to harm or consume you. It reflects the fear of being caught, exposed, or destroyed by forces beyond your control."
            ]
        }
    ])
    
    # Sadness/Loss additions
    entries.extend([
        {
            "word": "Missing Someone",
            "explanations": [
                "To dream of missing someone suggests the absence of an important connection or relationship. It reflects longing for closeness, the pain of separation, or the recognition of what you have lost or never had."
            ]
        },
        {
            "word": "Nostalgia",
            "explanations": [
                "To dream of nostalgia indicates wistful longing for the past or a time that felt better. It reflects the bittersweet recognition of what has changed and the desire to return to moments of comfort or happiness."
            ]
        }
    ])
    
    # Anger/Conflict additions
    entries.extend([
        {
            "word": "Powerlessness",
            "explanations": [
                "To dream of powerlessness suggests feeling unable to influence outcomes or protect yourself. It reflects the frustration of being at the mercy of others or circumstances, often triggering anger or despair."
            ]
        },
        {
            "word": "Injustice",
            "explanations": [
                "To dream of injustice indicates the experience of being wronged or treated unfairly. It reflects anger at unfairness, the violation of your rights, or the recognition that the world does not operate as it should."
            ]
        },
        {
            "word": "Revenge",
            "explanations": [
                "To dream of revenge suggests the desire to retaliate against those who have harmed you. It reflects unresolved anger, the wish to restore balance, or the recognition that you have been wronged and want justice."
            ]
        },
        {
            "word": "Betrayal",
            "explanations": [
                "To dream of betrayal indicates the experience of being deceived or abandoned by someone you trusted. It reflects the deep hurt of broken trust and the fear that those closest to you cannot be relied upon."
            ]
        }
    ])
    
    # Love/Attachment additions
    entries.extend([
        {
            "word": "Intimacy",
            "explanations": [
                "To dream of intimacy suggests deep closeness, vulnerability, or the merging of boundaries with another. It reflects the desire for authentic connection, the fear of being truly seen, or the experience of profound emotional union."
            ]
        },
        {
            "word": "Connection",
            "explanations": [
                "To dream of connection indicates the experience of being linked, understood, or in harmony with others. It reflects the need for belonging, the recognition of shared experience, or the feeling of being part of something larger."
            ]
        },
        {
            "word": "Obsession",
            "explanations": [
                "To dream of obsession suggests fixated attention on someone or something that consumes your thoughts. It reflects the loss of balance, the intensity of desire, or the fear that you cannot control your own impulses."
            ]
        },
        {
            "word": "Craving",
            "explanations": [
                "To dream of craving indicates intense, persistent desire for something you cannot have. It reflects unmet needs, addiction, or the recognition that you are driven by wants that may not serve your highest good."
            ]
        }
    ])
    
    # Self-related emotions
    entries.extend([
        {
            "word": "Pride",
            "explanations": [
                "To dream of pride suggests satisfaction in your achievements or identity. It reflects healthy self-worth, the recognition of your value, or the need to acknowledge what you have accomplished."
            ]
        },
        {
            "word": "Inadequacy",
            "explanations": [
                "To dream of inadequacy indicates feeling insufficient, unworthy, or not good enough. It reflects self-doubt, the fear of being exposed as a fraud, or the belief that you lack what is needed to succeed or be loved."
            ]
        },
        {
            "word": "Self-worth",
            "explanations": [
                "To dream of self-worth suggests the recognition of your own value and dignity. It reflects the need to honor yourself, the struggle to believe in your worth, or the experience of finally seeing yourself as deserving of good things."
            ]
        }
    ])
    
    # 2. Common Dream Situations - Loss of control
    entries.extend([
        {
            "word": "Can't Move",
            "explanations": [
                "To dream of being unable to move suggests paralysis, fear, or the feeling of being trapped. It reflects situations where you feel powerless to act, frozen by anxiety, or unable to escape what threatens you."
            ]
        },
        {
            "word": "Can't Speak",
            "explanations": [
                "To dream of being unable to speak suggests voicelessness, suppression, or the inability to express yourself. It reflects the fear of not being heard, the weight of unspoken words, or the experience of being silenced."
            ]
        },
        {
            "word": "Can't Scream",
            "explanations": [
                "To dream of being unable to scream suggests the inability to call for help or express terror. It reflects feeling trapped in silence, the fear that no one will hear you, or the suppression of urgent emotions that need release."
            ]
        },
        {
            "word": "Frozen",
            "explanations": [
                "To dream of being frozen suggests complete immobility, shock, or emotional paralysis. It reflects the experience of being so overwhelmed that you cannot respond, move, or think clearly about what to do next."
            ]
        },
        {
            "word": "Stuck",
            "explanations": [
                "To dream of being stuck indicates inability to progress, move forward, or escape a situation. It reflects feeling trapped in circumstances, relationships, or patterns that prevent you from advancing or changing."
            ]
        },
        {
            "word": "Lost",
            "explanations": [
                "To dream of being lost suggests disorientation, lack of direction, or uncertainty about your path. It reflects feeling without a clear sense of where you are going, what you want, or how to find your way back to safety."
            ]
        },
        {
            "word": "Missed Train",
            "explanations": [
                "To dream of missing a train suggests the fear of missing opportunities or being left behind. It reflects anxiety about timing, the sense that life is moving without you, or the regret of not acting when you had the chance."
            ]
        },
        {
            "word": "Missed Exam",
            "explanations": [
                "To dream of missing an exam indicates fear of being unprepared or failing to meet expectations. It reflects anxiety about being tested, judged, or found lacking in knowledge or ability when it matters most."
            ]
        },
        {
            "word": "Missed Flight",
            "explanations": [
                "To dream of missing a flight suggests the fear of missing important opportunities or transitions. It reflects anxiety about timing, the sense that you are not where you should be, or the fear of being left behind by life's changes."
            ]
        }
    ])
    
    # Social stress
    entries.extend([
        {
            "word": "Being Laughed At",
            "explanations": [
                "To dream of being laughed at suggests fear of ridicule, humiliation, or social rejection. It reflects the vulnerability of being exposed, the fear of being seen as foolish, or the pain of not being taken seriously."
            ]
        },
        {
            "word": "Public Failure",
            "explanations": [
                "To dream of public failure indicates the fear of being exposed as inadequate or incompetent in front of others. It reflects anxiety about judgment, the shame of not meeting expectations, or the terror of being seen at your worst."
            ]
        },
        {
            "word": "Naked in Public",
            "explanations": [
                "To dream of being naked in public suggests vulnerability, exposure, or the fear of being seen without protection. It reflects the anxiety of being truly known, the shame of being exposed, or the feeling that you have nothing to hide behind."
            ]
        },
        {
            "word": "Being Excluded",
            "explanations": [
                "To dream of being excluded suggests the pain of not belonging or being left out. It reflects the fear of rejection, the longing to be part of a group, or the recognition that you are on the outside looking in."
            ]
        },
        {
            "word": "Rejected by Group",
            "explanations": [
                "To dream of being rejected by a group indicates the fear of not fitting in or being cast out. It reflects the deep need for belonging, the pain of exclusion, or the fear that you are fundamentally unacceptable to others."
            ]
        }
    ])
    
    # Threat & survival
    entries.extend([
        {
            "word": "Hiding",
            "explanations": [
                "To dream of hiding suggests the need to protect yourself, avoid danger, or conceal something important. It reflects fear of being found, the desire to remain unseen, or the recognition that you are not safe in the open."
            ]
        },
        {
            "word": "Running Away",
            "explanations": [
                "To dream of running away suggests the need to escape danger, responsibility, or difficult situations. It reflects the urge to flee rather than face what threatens you, or the recognition that you cannot stay where you are."
            ]
        },
        {
            "word": "Drowning",
            "explanations": [
                "To dream of drowning suggests being overwhelmed by emotions, circumstances, or responsibilities. It reflects the feeling of being pulled under, unable to breathe, or consumed by something that threatens to destroy you."
            ]
        },
        {
            "word": "Suffocating",
            "explanations": [
                "To dream of suffocating indicates the feeling of being unable to breathe or get enough air. It reflects being smothered by circumstances, relationships, or emotions that leave you without space or freedom."
            ]
        },
        {
            "word": "Trapped in a Room",
            "explanations": [
                "To dream of being trapped in a room suggests confinement, limitation, or the inability to escape a situation. It reflects feeling stuck in circumstances, relationships, or patterns that prevent you from moving forward or finding freedom."
            ]
        }
    ])
    
    # 3. Modern Objects & Places
    entries.extend([
        {
            "word": "Phone",
            "explanations": [
                "To dream of a phone suggests communication, connection, or the need to reach out or be reached. It reflects the desire for contact, the fear of missing important messages, or the anxiety of being disconnected from others."
            ]
        },
        {
            "word": "Message",
            "explanations": [
                "To dream of a message suggests communication, information, or something that needs to be conveyed. It reflects the need to express yourself, receive important news, or the anxiety about what has been left unsaid."
            ]
        },
        {
            "word": "Text",
            "explanations": [
                "To dream of a text suggests digital communication, urgency, or the need for immediate response. It reflects the pressure of constant connection, the fear of missing out, or the anxiety of being always available."
            ]
        },
        {
            "word": "Email",
            "explanations": [
                "To dream of email suggests communication, information overload, or the need to respond to demands. It reflects the weight of expectations, the fear of missing important messages, or the anxiety of being overwhelmed by responsibilities."
            ]
        },
        {
            "word": "Internet",
            "explanations": [
                "To dream of the internet suggests connection, information, or the vast network of possibilities. It reflects the desire for knowledge, the fear of being disconnected, or the overwhelming sense of infinite options and information."
            ]
        },
        {
            "word": "Screen",
            "explanations": [
                "To dream of a screen suggests the interface between you and the world, or the barrier that separates you from direct experience. It reflects the mediated nature of modern life, the fear of missing reality, or the need to look beyond surfaces."
            ]
        },
        {
            "word": "Camera",
            "explanations": [
                "To dream of a camera suggests being watched, recorded, or the need to capture moments. It reflects the fear of being observed, the desire to preserve memories, or the anxiety of being exposed and documented."
            ]
        },
        {
            "word": "Social Media",
            "explanations": [
                "To dream of social media suggests the performance of identity, the fear of judgment, or the need for validation. It reflects the anxiety of being seen, the pressure to present yourself perfectly, or the fear of being excluded from connection."
            ]
        },
        {
            "word": "Video Call",
            "explanations": [
                "To dream of a video call suggests mediated connection, the pressure of being seen, or the anxiety of virtual presence. It reflects the need for connection despite distance, the fear of being exposed on camera, or the recognition that technology cannot fully replace real presence."
            ]
        },
        {
            "word": "Elevator",
            "explanations": [
                "To dream of an elevator suggests transitions, movement between levels, or the fear of being trapped. It reflects the anxiety of change, the fear of mechanical failure, or the sense of moving up or down in life without control."
            ]
        },
        {
            "word": "Escalator",
            "explanations": [
                "To dream of an escalator suggests automatic movement, progress without effort, or the fear of being carried along. It reflects the sense that life is moving you forward or backward without your active participation, or the anxiety of being unable to stop."
            ]
        },
        {
            "word": "Subway",
            "explanations": [
                "To dream of a subway suggests underground movement, collective journey, or the fear of being lost in transit. It reflects the anxiety of navigating complex systems, the sense of being one among many, or the fear of missing your stop."
            ]
        },
        {
            "word": "Airport",
            "explanations": [
                "To dream of an airport suggests transitions, departures, or the anxiety of travel and change. It reflects the fear of missing connections, the excitement of new beginnings, or the sense of being in limbo between destinations."
            ]
        },
        {
            "word": "Car Crash",
            "explanations": [
                "To dream of a car crash suggests sudden disruption, loss of control, or the fear of catastrophic change. It reflects the anxiety of things going wrong suddenly, the fear of being powerless in the face of disaster, or the recognition that life can change in an instant."
            ]
        },
        {
            "word": "School",
            "explanations": [
                "To dream of school suggests learning, evaluation, or the anxiety of being tested. It reflects the fear of judgment, the pressure to perform, or the sense of being in a place where you are constantly evaluated and compared to others."
            ]
        },
        {
            "word": "Classroom",
            "explanations": [
                "To dream of a classroom suggests being in a learning environment, the fear of being called on, or the anxiety of not knowing the answer. It reflects the pressure to perform, the fear of exposure, or the sense of being judged by authority figures."
            ]
        },
        {
            "word": "Office",
            "explanations": [
                "To dream of an office suggests work, productivity, or the pressure of professional expectations. It reflects the anxiety of performance, the fear of not measuring up, or the sense of being trapped in routines and responsibilities."
            ]
        },
        {
            "word": "Workplace",
            "explanations": [
                "To dream of a workplace suggests the environment where you are evaluated and must perform. It reflects the anxiety of professional judgment, the pressure to succeed, or the fear of being exposed as inadequate in your career."
            ]
        },
        {
            "word": "Hospital Room",
            "explanations": [
                "To dream of a hospital room suggests vulnerability, healing, or the fear of illness and death. It reflects the anxiety of being dependent on others, the fear of losing control over your body, or the recognition of your own mortality."
            ]
        },
        {
            "word": "Bathroom",
            "explanations": [
                "To dream of a bathroom suggests privacy, vulnerability, or the need for basic functions. It reflects the fear of exposure, the anxiety of not finding privacy when needed, or the recognition of your most basic and vulnerable needs."
            ]
        },
        {
            "word": "Bedroom",
            "explanations": [
                "To dream of a bedroom suggests intimacy, rest, or the private space where you are most yourself. It reflects the need for safety and privacy, the fear of intrusion, or the recognition of your most personal and vulnerable space."
            ]
        },
        {
            "word": "Childhood Home",
            "explanations": [
                "To dream of your childhood home suggests nostalgia, the past, or the foundation of who you are. It reflects the longing to return to safety, the recognition of what shaped you, or the need to reconnect with your origins and early experiences."
            ]
        }
    ])
    
    # 4. Body & Identity
    entries.extend([
        {
            "word": "Pain",
            "explanations": [
                "To dream of pain suggests emotional or physical suffering that needs attention. It reflects the need to acknowledge hurt, the fear of being damaged, or the recognition that something in your life is causing you distress."
            ]
        },
        {
            "word": "Bleeding",
            "explanations": [
                "To dream of bleeding suggests loss, vulnerability, or the fear of being wounded. It reflects the anxiety of being hurt, the recognition that you are losing something vital, or the fear that you cannot stop what is draining you."
            ]
        },
        {
            "word": "Wound",
            "explanations": [
                "To dream of a wound suggests injury, trauma, or damage that has not healed. It reflects the recognition of being hurt, the fear of being vulnerable, or the need to tend to emotional or physical injuries that require attention."
            ]
        },
        {
            "word": "Illness",
            "explanations": [
                "To dream of illness suggests vulnerability, weakness, or the fear of losing control over your body. It reflects the anxiety of being dependent, the recognition of your mortality, or the fear that something is wrong that you cannot fix."
            ]
        },
        {
            "word": "Vomiting",
            "explanations": [
                "To dream of vomiting suggests the need to expel something toxic, harmful, or unwanted. It reflects the recognition that you have taken in something that is poisoning you, or the need to release what cannot be digested."
            ]
        },
        {
            "word": "Choking",
            "explanations": [
                "To dream of choking suggests the inability to breathe, speak, or swallow. It reflects the fear of being silenced, the anxiety of being unable to express yourself, or the recognition that something is blocking your ability to function."
            ]
        },
        {
            "word": "Pregnancy",
            "explanations": [
                "To dream of pregnancy suggests creation, potential, or the development of something new within you. It reflects the anxiety of responsibility, the fear of change, or the recognition that you are nurturing something that will transform your life."
            ]
        },
        {
            "word": "Birth",
            "explanations": [
                "To dream of birth suggests new beginnings, creation, or the emergence of something important. It reflects the anxiety of bringing something into the world, the fear of the unknown, or the recognition that you are giving life to something that will change everything."
            ]
        },
        {
            "word": "Own Death",
            "explanations": [
                "To dream of your own death suggests transformation, endings, or the fear of ceasing to exist. It reflects the anxiety of mortality, the recognition that something in your life must end, or the fear of being forgotten or erased."
            ]
        },
        {
            "word": "Aging Suddenly",
            "explanations": [
                "To dream of aging suddenly suggests the fear of time passing, losing youth, or the recognition of mortality. It reflects the anxiety of change, the fear of becoming irrelevant, or the recognition that you cannot stop the passage of time."
            ]
        },
        {
            "word": "Losing Hair",
            "explanations": [
                "To dream of losing hair suggests the fear of losing power, attractiveness, or identity. It reflects the anxiety of aging, the fear of being seen as less valuable, or the recognition that something you associate with your identity is slipping away."
            ]
        },
        {
            "word": "Being Someone Else",
            "explanations": [
                "To dream of being someone else suggests identity confusion, the desire to escape yourself, or the exploration of different aspects of who you could be. It reflects the fear of not knowing who you are, the wish to be different, or the recognition of parts of yourself you have not yet integrated."
            ]
        },
        {
            "word": "Watching Yourself",
            "explanations": [
                "To dream of watching yourself suggests self-observation, dissociation, or the ability to see yourself from outside. It reflects the need for perspective, the fear of being disconnected from yourself, or the recognition that you are both observer and observed."
            ]
        },
        {
            "word": "Doppelgänger",
            "explanations": [
                "To dream of a doppelgänger suggests the shadow self, the parts of you that are hidden, or the fear of encountering your double. It reflects the recognition of aspects of yourself you have not acknowledged, or the fear that there is another version of you that is dangerous or unknown."
            ]
        },
        {
            "word": "Shadow Self",
            "explanations": [
                "To dream of your shadow self suggests the parts of you that are repressed, denied, or hidden. It reflects the recognition of aspects of yourself you have not integrated, or the fear of confronting what you have tried to keep in darkness."
            ]
        },
        {
            "word": "Mask",
            "explanations": [
                "To dream of a mask suggests concealment, performance, or the fear of being seen as you truly are. It reflects the need to hide your true self, the fear of exposure, or the recognition that you are presenting a false face to the world."
            ]
        },
        {
            "word": "Disguise",
            "explanations": [
                "To dream of a disguise suggests the need to hide your identity or true nature. It reflects the fear of being recognized, the desire to escape who you are, or the recognition that you are not showing your authentic self to others."
            ]
        }
    ])
    
    # 5. Archetypal / Symbolic
    entries.extend([
        {
            "word": "Shadow",
            "explanations": [
                "To dream of a shadow suggests the unconscious, the repressed, or the parts of yourself you have not acknowledged. It reflects the recognition of what you have kept in darkness, or the fear of confronting aspects of yourself that feel dangerous or unacceptable."
            ]
        },
        {
            "word": "Guide",
            "explanations": [
                "To dream of a guide suggests wisdom, direction, or the need for someone to show you the way. It reflects the recognition that you need help navigating your path, or the presence of inner wisdom that is trying to lead you forward."
            ]
        },
        {
            "word": "Teacher",
            "explanations": [
                "To dream of a teacher suggests learning, authority, or the need for knowledge and guidance. It reflects the recognition that you have something to learn, the fear of being judged, or the presence of wisdom that can help you grow."
            ]
        },
        {
            "word": "Inner Child",
            "explanations": [
                "To dream of your inner child suggests the vulnerable, innocent, or wounded parts of yourself from childhood. It reflects the need to nurture yourself, the recognition of early wounds that need healing, or the fear of being stuck in childlike patterns."
            ]
        },
        {
            "word": "Psychological Mother",
            "explanations": [
                "To dream of the psychological mother suggests nurturing, protection, or the archetypal feminine principle. It reflects the need for care, the recognition of what nurtures you, or the fear of being abandoned by what should protect and support you."
            ]
        },
        {
            "word": "Psychological Father",
            "explanations": [
                "To dream of the psychological father suggests authority, structure, or the archetypal masculine principle. It reflects the need for guidance, the recognition of what provides order, or the fear of being without protection or direction."
            ]
        },
        {
            "word": "Stranger",
            "explanations": [
                "To dream of a stranger suggests the unknown, the unfamiliar, or parts of yourself you have not yet met. It reflects the fear of the other, the recognition of what is foreign, or the presence of something new that is trying to enter your awareness."
            ]
        },
        {
            "word": "Enemy",
            "explanations": [
                "To dream of an enemy suggests opposition, conflict, or the parts of yourself or others that threaten you. It reflects the fear of being attacked, the recognition of what opposes you, or the need to confront what stands in your way."
            ]
        },
        {
            "word": "Monster",
            "explanations": [
                "To dream of a monster suggests fear, the unknown, or the parts of yourself or the world that feel dangerous. It reflects the recognition of what terrifies you, the fear of being consumed, or the need to confront what you have kept at a distance."
            ]
        },
        {
            "word": "Giant",
            "explanations": [
                "To dream of a giant suggests overwhelming power, intimidation, or the feeling of being small and insignificant. It reflects the fear of being crushed, the recognition of forces larger than yourself, or the need to find your own power in the face of what seems insurmountable."
            ]
        },
        {
            "word": "Void",
            "explanations": [
                "To dream of a void suggests emptiness, nothingness, or the absence of meaning or structure. It reflects the fear of being lost in nothingness, the recognition of emptiness, or the need to find something to fill the space where meaning should be."
            ]
        },
        {
            "word": "Door",
            "explanations": [
                "To dream of a door suggests opportunity, transition, or the boundary between different spaces or states. It reflects the fear of what lies beyond, the recognition of new possibilities, or the need to decide whether to open or close what separates you from change."
            ]
        },
        {
            "word": "Key",
            "explanations": [
                "To dream of a key suggests access, solution, or the means to unlock something important. It reflects the recognition that you have what you need to open doors, the fear of losing access, or the need to find the right tool to solve a problem."
            ]
        },
        {
            "word": "Mirror",
            "explanations": [
                "To dream of a mirror suggests self-reflection, truth, or the need to see yourself clearly. It reflects the fear of what you might see, the recognition of your true self, or the need to confront the image you present to the world versus who you really are."
            ]
        },
        {
            "word": "Labyrinth",
            "explanations": [
                "To dream of a labyrinth suggests confusion, the search for meaning, or the complex path you must navigate. It reflects the fear of being lost, the recognition that the way forward is not straightforward, or the need to find your way through complexity."
            ]
        },
        {
            "word": "Threshold",
            "explanations": [
                "To dream of a threshold suggests transition, the boundary between states, or the moment of crossing from one phase to another. It reflects the anxiety of change, the recognition that you are at a turning point, or the need to step across into something new."
            ]
        }
    ])
    
    # 6. Dream-State Meta Symbols
    entries.extend([
        {
            "word": "Awareness",
            "explanations": [
                "To dream with awareness suggests consciousness within the dream, the ability to observe and influence. It reflects the recognition that you are dreaming, the growing sense of control, or the ability to see your own mental processes from a new perspective."
            ]
        },
        {
            "word": "Repetition",
            "explanations": [
                "To dream of repetition suggests patterns, cycles, or the need to work through something that keeps returning. It reflects the recognition that you are stuck in a loop, the need to break free from recurring patterns, or the importance of what keeps appearing."
            ]
        },
        {
            "word": "Déjà Vu",
            "explanations": [
                "To dream of déjà vu suggests the sense that you have experienced this before, the recognition of patterns, or the feeling that time is looping. It reflects the anxiety of being unable to escape repetition, or the recognition that history is repeating itself."
            ]
        },
        {
            "word": "Time Distortion",
            "explanations": [
                "To dream of time distortion suggests the fluidity of time, the sense that it moves too fast or too slow, or the recognition that time does not operate as expected. It reflects the anxiety of time passing, the fear of running out of time, or the sense that time is not linear."
            ]
        },
        {
            "word": "Slow Motion",
            "explanations": [
                "To dream in slow motion suggests the need to observe carefully, the fear of what is happening, or the sense that time has stretched. It reflects the anxiety of being unable to act quickly enough, or the recognition that you need to pay closer attention to what is unfolding."
            ]
        },
        {
            "word": "Infinite Space",
            "explanations": [
                "To dream of infinite space suggests boundlessness, the absence of limits, or the overwhelming sense of vastness. It reflects the fear of being lost in endlessness, the recognition of infinite possibilities, or the anxiety of having no boundaries or structure."
            ]
        },
        {
            "word": "Weightlessness",
            "explanations": [
                "To dream of weightlessness suggests freedom from gravity, liberation, or the sense of being untethered. It reflects the desire to escape constraints, the fear of floating away, or the recognition that you are free from what normally holds you down."
            ]
        }
    ])
    
    return entries

def add_comprehensive_entries():
    """Add comprehensive entries to the dream database."""
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
    new_entries_data = create_comprehensive_entries()
    
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
            
            # Assign emoji based on explanation
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
            
            if added_count % 20 == 0:
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
    add_comprehensive_entries()
