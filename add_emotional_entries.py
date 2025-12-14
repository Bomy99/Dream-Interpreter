#!/usr/bin/env python3
"""
Add emotional-state dream entries with unique explanations.
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

def create_emotional_entries():
    """Create new emotional dream entries with unique explanations."""
    
    entries = []
    
    # Loneliness & Isolation
    entries.extend([
        {
            "word": "Loneliness",
            "explanations": [
                "To dream of loneliness reflects emotional distance from others or a sense of disconnection. It suggests unmet needs for companionship or understanding that are present in waking life."
            ]
        },
        {
            "word": "Isolation",
            "explanations": [
                "To dream of isolation suggests separation from connection or support. It reflects feelings of being cut off from others or choosing solitude over engagement."
            ]
        },
        {
            "word": "Abandonment",
            "explanations": [
                "To dream of abandonment points to fears of being left behind or rejected. It reflects vulnerability around attachment and the anxiety of losing important connections."
            ]
        },
        {
            "word": "Rejection",
            "explanations": [
                "To dream of rejection suggests fear of not being accepted or valued. It reflects concerns about belonging and the pain of feeling excluded or dismissed."
            ]
        },
        {
            "word": "Being Ignored",
            "explanations": [
                "To dream of being ignored indicates feelings of invisibility or insignificance. It reflects the need to be seen, heard, or acknowledged in your relationships or environment."
            ]
        },
        {
            "word": "Disconnection",
            "explanations": [
                "To dream of disconnection suggests a break in communication or emotional bonds. It reflects distance from others or from parts of yourself that feel out of reach."
            ]
        },
        {
            "word": "Emptiness",
            "explanations": [
                "To dream of emptiness points to a sense of void or lack of meaning. It reflects feelings of hollowness or the absence of something important that once filled your life."
            ]
        },
        {
            "word": "Being Alone",
            "explanations": [
                "To dream of being alone reflects emotional distance, unmet connection, or self-reliance. It suggests either a need for solitude or a fear of isolation depending on the dream's context."
            ]
        },
        {
            "word": "Sex",
            "explanations": [
                "To dream of sex reflects intimacy, connection, or the merging of different aspects of yourself. It suggests desire for closeness, creative union, or the integration of opposing forces within your psyche."
            ]
        }
    ])
    
    # Stress, Pressure & Overload
    entries.extend([
        {
            "word": "Stress",
            "explanations": [
                "To dream of stress indicates mental or emotional overload that exceeds your capacity to cope. It reflects accumulated tension seeking release or acknowledgment in your waking life."
            ]
        },
        {
            "word": "Overwhelm",
            "explanations": [
                "To dream of overwhelm suggests being flooded by demands, emotions, or responsibilities. It reflects a sense of being unable to process or manage everything that requires your attention."
            ]
        },
        {
            "word": "Exhaustion",
            "explanations": [
                "To dream of exhaustion points to depletion of energy, resources, or emotional reserves. It reflects the need for rest, recovery, or the recognition that you have given too much of yourself."
            ]
        },
        {
            "word": "Burnout",
            "explanations": [
                "To dream of burnout suggests complete depletion from prolonged stress or effort. It reflects the need to step back, recharge, or reassess what is truly sustainable in your life."
            ]
        },
        {
            "word": "Tension",
            "explanations": [
                "To dream of tension indicates unresolved conflict or opposing forces pulling in different directions. It reflects the strain between what you want and what you must do, or between different parts of yourself."
            ]
        },
        {
            "word": "Being Rushed",
            "explanations": [
                "To dream of being rushed suggests time pressure or the feeling that you cannot keep up with demands. It reflects anxiety about deadlines, expectations, or the pace of your life."
            ]
        }
    ])
    
    # Sadness & Loss
    entries.extend([
        {
            "word": "Sadness",
            "explanations": [
                "To dream of sadness points to emotional processing or unresolved loss. It reflects the need to acknowledge and work through feelings of grief, disappointment, or melancholy that may be suppressed in waking life."
            ]
        },
        {
            "word": "Grief",
            "explanations": [
                "To dream of grief suggests deep loss or the process of mourning something or someone important. It reflects the need to honor what has been lost and allow yourself to feel the full weight of that absence."
            ]
        },
        {
            "word": "Mourning",
            "explanations": [
                "To dream of mourning indicates active processing of loss or change. It reflects the natural need to grieve and integrate the reality of what can no longer be."
            ]
        },
        {
            "word": "Melancholy",
            "explanations": [
                "To dream of melancholy suggests a reflective sadness or wistful longing. It reflects contemplation of what has passed or what might have been, often with a sense of beauty in the sadness itself."
            ]
        },
        {
            "word": "Regret",
            "explanations": [
                "To dream of regret points to feelings about past choices or missed opportunities. It reflects the wish to change what cannot be changed and the need to make peace with your history."
            ]
        },
        {
            "word": "Hopelessness",
            "explanations": [
                "To dream of hopelessness suggests a loss of faith in positive outcomes or the future. It reflects despair or the feeling that efforts are futile, often signaling the need for support or perspective."
            ]
        },
        {
            "word": "Disappointment",
            "explanations": [
                "To dream of disappointment indicates unmet expectations or the gap between what you hoped for and what actually occurred. It reflects the need to adjust expectations or process the reality of limitations."
            ]
        },
        {
            "word": "Longing",
            "explanations": [
                "To dream of longing suggests deep yearning for something absent or unattainable. It reflects desire for connection, fulfillment, or a return to a state that feels out of reach."
            ]
        }
    ])
    
    # Anger & Conflict
    entries.extend([
        {
            "word": "Anger",
            "explanations": [
                "To dream of anger reflects suppressed conflict or unmet boundaries. It suggests feelings of injustice, frustration, or violation that need expression or resolution in your waking life."
            ]
        },
        {
            "word": "Rage",
            "explanations": [
                "To dream of rage indicates intense, overwhelming anger that has been contained or denied. It reflects explosive emotions seeking release or acknowledgment of deep grievances."
            ]
        },
        {
            "word": "Frustration",
            "explanations": [
                "To dream of frustration suggests obstacles preventing you from achieving goals or expressing yourself. It reflects the feeling of being blocked or unable to move forward as desired."
            ]
        },
        {
            "word": "Resentment",
            "explanations": [
                "To dream of resentment points to lingering anger or bitterness about past wrongs. It reflects unresolved grievances that continue to influence your emotional state and relationships."
            ]
        },
        {
            "word": "Irritation",
            "explanations": [
                "To dream of irritation suggests minor annoyances or sensitivities that are accumulating. It reflects small frustrations that, when combined, create significant discomfort or tension."
            ]
        },
        {
            "word": "Bitterness",
            "explanations": [
                "To dream of bitterness indicates deep resentment or cynicism about past experiences. It reflects the hardening of emotions and the need to release old wounds to move forward."
            ]
        },
        {
            "word": "Hostility",
            "explanations": [
                "To dream of hostility suggests antagonism or opposition, either from others or within yourself. It reflects conflict that needs to be addressed rather than avoided or suppressed."
            ]
        },
        {
            "word": "Aggression",
            "explanations": [
                "To dream of aggression indicates forceful energy or the need to assert yourself. It reflects either the expression of pent-up anger or the drive to overcome obstacles through direct action."
            ]
        }
    ])
    
    # Shame, Guilt & Exposure
    entries.extend([
        {
            "word": "Shame",
            "explanations": [
                "To dream of shame suggests fear of judgment or self-criticism. It reflects feelings of unworthiness or exposure of something you believe makes you fundamentally flawed or unacceptable."
            ]
        },
        {
            "word": "Guilt",
            "explanations": [
                "To dream of guilt points to self-blame or responsibility for harm done. It reflects the need to make amends, forgive yourself, or acknowledge mistakes without being consumed by them."
            ]
        },
        {
            "word": "Embarrassment",
            "explanations": [
                "To dream of embarrassment suggests self-consciousness or fear of social judgment. It reflects concern about how others perceive you or anxiety about being exposed in a vulnerable way."
            ]
        },
        {
            "word": "Humiliation",
            "explanations": [
                "To dream of humiliation indicates deep shame or degradation, often in a public context. It reflects feelings of being diminished, exposed, or stripped of dignity in a way that feels unbearable."
            ]
        },
        {
            "word": "Self-blame",
            "explanations": [
                "To dream of self-blame suggests taking responsibility for outcomes beyond your control. It reflects the tendency to internalize fault and the need to distinguish between accountability and unnecessary self-punishment."
            ]
        },
        {
            "word": "Exposure",
            "explanations": [
                "To dream of exposure suggests being revealed or seen in a way that feels vulnerable. It reflects fears of having hidden aspects of yourself discovered or judged by others."
            ]
        },
        {
            "word": "Being Judged",
            "explanations": [
                "To dream of being judged indicates fear of evaluation or criticism from others. It reflects anxiety about not measuring up or being found lacking in some important way."
            ]
        }
    ])
    
    # Desire, Love & Attachment
    entries.extend([
        {
            "word": "Lust",
            "explanations": [
                "To dream of lust suggests intense physical or emotional desire seeking expression. It reflects powerful attraction or the need to connect with your own sensuality and passion."
            ]
        },
        {
            "word": "Attraction",
            "explanations": [
                "To dream of attraction indicates magnetic pull toward someone or something. It reflects desire, interest, or the recognition of qualities that draw you closer to what you want."
            ]
        },
        {
            "word": "Affection",
            "explanations": [
                "To dream of affection suggests warmth, tenderness, or care in relationships. It reflects the need to give or receive love, or the recognition of emotional bonds that provide comfort and connection."
            ]
        },
        {
            "word": "Passion",
            "explanations": [
                "To dream of passion indicates intense enthusiasm, desire, or commitment. It reflects powerful energy directed toward something that deeply matters to you or ignites your spirit."
            ]
        },
        {
            "word": "Attachment",
            "explanations": [
                "To dream of attachment suggests emotional bonds or dependency on others. It reflects the need for connection, security, or the fear of losing what you hold dear."
            ]
        },
        {
            "word": "Yearning",
            "explanations": [
                "To dream of yearning indicates deep longing for something absent or unattainable. It reflects desire that goes beyond simple want, touching on fundamental needs for fulfillment or completion."
            ]
        }
    ])
    
    # Control & Power Dynamics
    entries.extend([
        {
            "word": "Dominance",
            "explanations": [
                "To dream of dominance suggests power, control, or the assertion of authority. It reflects either the need to lead, the fear of being controlled, or the recognition of power dynamics in your relationships."
            ]
        },
        {
            "word": "Submission",
            "explanations": [
                "To dream of submission indicates yielding to others or accepting a subordinate role. It reflects either healthy surrender, the fear of asserting yourself, or the need to find balance between control and letting go."
            ]
        },
        {
            "word": "Empowerment",
            "explanations": [
                "To dream of empowerment suggests gaining strength, confidence, or agency in your life. It reflects the recognition of your own power and the ability to influence your circumstances."
            ]
        },
        {
            "word": "Authority",
            "explanations": [
                "To dream of authority indicates power, leadership, or the right to make decisions. It reflects either your own sense of command, respect for those in power, or conflicts around who has the right to control situations."
            ]
        }
    ])
    
    # Confusion & Uncertainty
    entries.extend([
        {
            "word": "Doubt",
            "explanations": [
                "To dream of doubt suggests uncertainty about decisions, beliefs, or your own judgment. It reflects the questioning of what you thought you knew and the need to find clarity or trust your instincts."
            ]
        },
        {
            "word": "Disorientation",
            "explanations": [
                "To dream of disorientation indicates loss of direction or confusion about where you are. It reflects feeling lost, uncertain of your path, or disconnected from familiar reference points in your life."
            ]
        },
        {
            "word": "Forgetfulness",
            "explanations": [
                "To dream of forgetfulness suggests losing track of important information or memories. It reflects the fear of losing what matters, or the need to let go of what no longer serves you."
            ]
        },
        {
            "word": "Indecision",
            "explanations": [
                "To dream of indecision indicates difficulty choosing between options or paths. It reflects the paralysis that comes from too many choices, fear of making the wrong decision, or conflicting desires."
            ]
        }
    ])
    
    # Relief, Safety & Calm
    entries.extend([
        {
            "word": "Relief",
            "explanations": [
                "To dream of relief suggests release from pressure, worry, or pain. It reflects the experience of tension dissolving and the recognition that something difficult has passed or been resolved."
            ]
        },
        {
            "word": "Safety",
            "explanations": [
                "To dream of safety indicates protection, security, or freedom from harm. It reflects the need for a safe space, the recognition of being cared for, or the creation of boundaries that allow you to feel secure."
            ]
        },
        {
            "word": "Comfort",
            "explanations": [
                "To dream of comfort suggests ease, support, or the alleviation of distress. It reflects the need for nurturing, the presence of what soothes you, or the ability to provide comfort to yourself or others."
            ]
        },
        {
            "word": "Peace",
            "explanations": [
                "To dream of peace indicates calm, resolution, or the absence of conflict. It reflects inner tranquility, the resolution of tensions, or the recognition that all is well in this moment."
            ]
        },
        {
            "word": "Acceptance",
            "explanations": [
                "To dream of acceptance suggests embracing what is, without resistance or judgment. It reflects the ability to make peace with reality, yourself, or circumstances that cannot be changed."
            ]
        },
        {
            "word": "Reassurance",
            "explanations": [
                "To dream of reassurance indicates comfort, validation, or the confirmation that things will be okay. It reflects the need for support, the presence of those who care, or the ability to soothe your own anxieties."
            ]
        }
    ])
    
    # Joy & Positive Activation
    entries.extend([
        {
            "word": "Joy",
            "explanations": [
                "To dream of joy signals emotional release or alignment. It reflects happiness, fulfillment, or the recognition that something in your life is bringing you genuine pleasure and satisfaction."
            ]
        },
        {
            "word": "Happiness",
            "explanations": [
                "To dream of happiness suggests contentment, well-being, or positive emotional states. It reflects the experience of pleasure, satisfaction, or the recognition of what brings you genuine fulfillment."
            ]
        },
        {
            "word": "Excitement",
            "explanations": [
                "To dream of excitement indicates anticipation, enthusiasm, or energized interest. It reflects the thrill of possibility, new experiences, or the recognition that something meaningful is about to happen."
            ]
        },
        {
            "word": "Freedom",
            "explanations": [
                "To dream of freedom suggests liberation from constraints, limitations, or obligations. It reflects the ability to move, choose, or express yourself without restriction or the need to break free from what holds you back."
            ]
        },
        {
            "word": "Playfulness",
            "explanations": [
                "To dream of playfulness indicates lightheartedness, spontaneity, or the ability to engage without seriousness. It reflects the need for fun, creativity, or the recognition that not everything needs to be heavy or important."
            ]
        },
        {
            "word": "Curiosity",
            "explanations": [
                "To dream of curiosity suggests interest, exploration, or the desire to understand. It reflects openness to new experiences, questions about the unknown, or the drive to discover what lies beyond familiar territory."
            ]
        },
        {
            "word": "Wonder",
            "explanations": [
                "To dream of wonder indicates awe, amazement, or the recognition of something extraordinary. It reflects the ability to see beauty, mystery, or magic in the world around you or within yourself."
            ]
        }
    ])
    
    # Special Dream-Specific Feelings (emotion + state hybrids)
    entries.extend([
        {
            "word": "Floating",
            "explanations": [
                "To dream of floating suggests detachment, weightlessness, or freedom from gravity. It reflects either liberation from constraints, a sense of being untethered, or the need to rise above difficult circumstances."
            ]
        }
    ])
    
    return entries

def add_emotional_entries():
    """Add new emotional entries to the dream database."""
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
    new_entries_data = create_emotional_entries()
    
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
    add_emotional_entries()
