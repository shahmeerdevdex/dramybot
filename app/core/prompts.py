"""Dream interpretation prompts and configurations."""

DREAM_DICTIONARY_PROMPT = """I want you to act as a dream interpreter, writer, and analyst. I will give you a dream
symbol, theme or situation, and you will have a thorough, in-depth interpretation
about what this symbol represents for me personally when in my dreams for my
own highly tailored and personalized dream dictionary/encyclopedia, based on my
dream logs and conversations and your deep knowledge of dreaming and sleep
science, dream symbolism, psychology, faith and spirituality, society and culture,
intuition, relationships, remote associations, subconscious processing, limiting
and expansive beliefs, nervous system, neuroscience, active listening, cognitive
and unconscious bias, and mental health. Your goal is to help me identify the
thoughts, fears, desires, insecurities, stressors, and anxieties that are manifesting
my dreams/subconscious and how this symbol does that when it appears by
collectively analyzing my dreams featuring this symbol. I will provide you
transcript logs of my dreams and conversations with you that have the assigned
symbol. Based on all of my collective dream content with this symbol and the
following conversations/interpretations, provide a write a 3-4 sentence
interpreting this symbol and what it means personally for me in my dreams. Focus
on just the significance of this symbol only and what it means in my dreams. Be
straightforward and limit hyperbole. Do not offer advice or
direction/reminders/suggestions, focus solely on what it means. Do not preface it
with anything, provide only the answer."""

DREAM_MANIFESTATION_PROMPT = """I will provide you transcript logs of my dreams and conversations that contain a
specific visual symbol. Based on all of my collective dream content with this
symbol, provide 4-5 sentences describing how this symbol tends to visually
manifest in my dreams. Focus on just the chosen symbol and how it shows up in
my dreams and reference/cite my dreams for proof to show your reasoning. Be
concise, straightforward and limit hyperbole. Do not offer advice or
direction/reminders/suggestions, focus solely on what it means. Do not preface it
with anything, provide only the answer."""

DREAM_TRIGGERS_PROMPT = """I will provide you transcript logs of my dreams and conversations that contain a
specific visual symbol. Based on all of my collective dream content with this
symbol, provide 4-5 sentences describing when this symbol tends to occur in my
life and what waking life triggers or patterns seem to be causing it. Focus on just
the chosen symbol and the waking life triggers that are happening when this
specific symbol shows up in my dreams and when it's likely to occur.
Reference/cite my dreams for proof to show your reasoning. Be concise,
straightforward and limit hyperbole. Do not offer advice or
direction/reminders/suggestions, focus solely on what it means. Do not preface it
with anything, provide only the answer."""

DREAM_TITLE_PROMPT = """I will provide you a transcript of my dream and our conversation. Based on the
dream content, provide a very concise, straightforward title for my dream journal
based on the visual symbols, overall narrative or themes in the dream. I should be
able to identify it quickly by title. Do not preface it with anything, provide only the
answer."""

DREAM_INSIGHT_PROMPT = """I will provide you a transcript of my dream and our conversation. Based on our
conversation, provide a brief 1 sentence enlightening insight rooted in stoicism,
taoism, positive psychology, spirituality, mindset, energy, etc. based on what my
dream means or is processing from my subconscious, including the core themes,
latent desires and fears, beliefs, patterns etc. that are coming up based on the
visual symbols, emotions, overarching themes, intentions, etc. in the dream. Do
not preface it with anything, provide only the answer."""

DREAM_SYMBOLS_PROMPT = """I will provide you a transcript of my dream and our conversation. Based on the
dream content only, provide a comma separated list of the primary visual symbols.
Do not list more than 6. Do not preface it with anything, provide only the answer."""

DREAM_EMOTIONS_PROMPT = """I will provide you a transcript of my dream and our conversation. Based on the
dream content, provide a comma separated list of the primary emotional tones
that are present in the dream based on the feelings wheel. Do not provide more
than 4. Do not preface it with anything, provide only the answer."""

DREAM_THEMES_PROMPT = """I will provide you a transcript of my dream and our conversation. Based on the
dream content, provide a comma separated list of the primary themes that are
present in the dream based on what my dream means or is processing from my
subconscious, including the core themes, latent desires and fears, beliefs,
patterns etc. that are coming up based on the visual symbols, emotions,
overarching themes, intentions, etc. in the dream. Do not provide more than 3. Do
not preface it with anything, provide only the answer."""

DREAM_ANALYSIS_PROMPT = """I will provide you a transcript of our conversation. Based on what we discussed,
provide a 3-4 sentence summary about what my dream means or is processing
from my subconscious, including the core themes, latent desires and fears,
beliefs, patterns etc. that are coming up based on the visual symbols, emotions,
overarching themes, intentions, etc. in the dream and what we discussed."""

DREAM_REFLECTION_PROMPT = """I will provide you a transcript of our conversation. Based on what we discussed,
provide 1 personal self-reflective journal prompt/thought reflection based on the
core themes, topics, and issues that we talked about and based on what my
dream means or is processing from my subconscious, including the core themes,
latent desires and fears, beliefs, patterns etc. that are coming up based on the
visual symbols, emotions, overarching themes, intentions, etc. in the dream. Only
share the reflection question, max 2 sentences. Questions should be deeply
introspective, slightly challenging and deep, as if I was talking to myself. Do not
preface it with anything, provide only the journal prompt."""

DREAM_ACTION_PROMPT = """I will provide you a transcript of our conversation. Based on what we discussed,
provide an aligned action/actionable exercise to address and improve the core
themes, topics, and issues that we talked about based on what my dream means
or is processing from my subconscious, including the core themes, latent desires
and fears, beliefs, patterns etc. that are coming up based on the visual symbols,
emotions, overarching themes, intentions, etc. in the dream. Exercises should be
highly personalized, healing, nuanced, and tailored to my preferences and what
would be the most impactful for me. First, very briefly title the exercise and then
share the exercise in 3-6 sentences. Then, give me 1-2 sentences summarizing
what this exercise addresses and the goal. Do not preface it with anything,
provide only the answer."""

# Sampling parameters for different models
SAMPLING_PARAMS = {
    "gemma": {
        "temperature": 0.48,
        "top_p": 1.0,
        "top_k": 0,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "repetition_penalty": 0,
        "min_p": 0,
        "top_a": 0
    },
    "gpt4_mini": {
        "temperature": 0.43,
        "top_p": 1.0,
        "top_k": 0,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "repetition_penalty": 0,
        "min_p": 0,
        "top_a": 0
    }
}


combined_prompt = f"""
I will provide you a transcript of my dream and our conversation. Based on the content, return a valid JSON object with these exact fields (no extra keys, and nothing else in your response):

1. title:
   I will provide you a transcript of my dream and our conversation.  
   Based on the dream content, provide a very concise, straightforward title for my dream journal  
   based on the visual symbols, overall narrative or themes in the dream.  
   I should be able to identify it quickly by title. Do not preface it with anything, provide only the answer.

2. shortText (Insight Block):
   Detailed Insights - Dream Page 1  
   I will provide you a transcript of my dream and our conversation.  
   Based on our conversation, provide a brief 1 sentence enlightening insight rooted in stoicism, taoism, positive psychology, spirituality, mindset, energy, etc.  
   Based on what my dream means or is processing from my subconscious, including core themes, latent desires/fears, beliefs, patterns, etc.  
   Do not preface it with anything, provide only the answer.

3. visualSymbols (Key Visual Symbols):
   Detailed Insights - Dream Page 2  
   I will provide you a transcript of my dream and our conversation.  
   Based on the dream content only, provide a comma separated list of the primary visual symbols.  
   Do not list more than 6. Do not preface it with anything, provide only the answer.

4. tones (Emotional Tones):
   Detailed Insights - Dream Page 3  
   I will provide you a transcript of my dream and our conversation.  
   Based on the dream content, provide a comma separated list of the primary emotional tones that are present in the dream based on the feelings wheel.  
   Do not provide more than 4. Do not preface it with anything, provide only the answer.

5. themes:
   Detailed Insights - Dream Page 4  
   I will provide you a transcript of my dream and our conversation.  
   Based on the dream content, provide a comma separated list of the primary themes that are present in the dream  
   based on what my dream means or is processing from my subconscious, including core themes, latent desires/fears, beliefs, patterns, etc.  
   Do not provide more than 3. Do not preface it with anything, provide only the answer.

6. summary (Summarized Analysis):
   Detailed Insights - Dream Page 5  
   I will provide you a transcript of our last 3 conversations. Based on what we
   discussed, provide a brief 1 sentence summary about what my subconscious
   seems to be currently processing, including the core themes, latent desires and
   fears, beliefs, patterns etc. that revealed themselves based on the dream and our
   following conversation. "Based on your most recent dreams, it sounds like ..." Do
   not preface it with anything, provide only the answer. Your tone should be warm,
   curious, supportive, gentle, nonjudgmental, non-confrontational. Second person.

7. thoughtReflection (Thought Reflection/Journal):
   Detailed Insights - Dream Page 6  
   I will provide you a transcript of our conversation.  
   Based on what we discussed, provide 1 personal self-reflective journal prompt/thought reflection based on core themes, topics, and issues we talked about,  
   and based on what my dream means or is processing from my subconscious (core themes, latent desires/fears, beliefs, patterns, etc.).  
   Only share the reflection question, max 2 sentences. Questions should be deeply introspective, slightly challenging, and deep, as if I were talking to myself.  
   Do not preface it with anything, provide only the journal prompt.

8. alignedAction (Aligned Action):
   Detailed Insights - Dream Page 7  
   I will provide you a transcript of our conversation.  
   Based on what we discussed, provide an aligned action/actionable exercise to address and improve the core themes, topics, and issues we talked about  
   based on what my dream means or is processing from my subconscious (core themes, latent desires/fears, beliefs, patterns, etc.).  
   Exercises should be highly personalized, healing, nuanced, and tailored to my preferences and what would be the most impactful for me.  
   First, very briefly title the exercise and then share the exercise in 3–6 sentences. Then, give me 1–2 sentences summarizing what this exercise addresses and the goal.  
   Do not preface it with anything, provide only the answer.

Conversation:
"""

summary_prompt = """
I will give you a dream symbol, theme or situation, and you will provide 4-6
sentences about what this symbol represents for me personally when it appears in
my dreams for my own highly tailored and personalized dream dictionary, based
on the commonality of how this symbol manifests in my collective dream logs and
discussions that feature this symbol. Use your deep knowledge of dreaming and
sleep science, dream symbolism, psychology, faith and spirituality, society and
culture, intuition, relationships, remote associations, subconscious processing,
limiting and expansive beliefs, nervous system, neuroscience, active listening,
cognitive and unconscious bias, and mental health to determine what this symbol
Dream Dictionary 1
means for me and what it represents in my subconscious mind and how it
connects to any repressed behavior, latent fears, self-image and inner beliefs,
desires, values, anxieties, boundaries, self-sabotage, self-perception and
personality, insecurities, environment, mental blocks, internal conflicts, coping
mechanisms, projections, inner child, emotional processing etc.
Focus on just the significance of this symbol only. Be straightforward, and limit
hyperbole. Show your reasoning or references. Do not offer advice or
direction/reminders/suggestions. Do not preface it with anything, provide only the
answer.
 Do not include phrases like 'Here is a summary' or 'Here is a concise 2-line summary'. Just provide the summary directly.
"""


dream_summary_prompt = """
I will provide you a transcript of our last 3 conversations. Based on what we
discussed, provide a brief 1 sentence summary about what my subconscious
seems to be currently processing, including the core themes, latent desires and
fears, beliefs, patterns etc. that revealed themselves based on the dream and our
following conversation. "Based on your most recent dreams, it sounds like ..." Do
not preface it with anything, provide only the answer. Your tone should be warm,
curious, supportive, gentle, nonjudgmental, non-confrontational. Second person.Do not preface it with anything, provide only the
answer.
 Do not include phrases like 'Here is a summary' or 'Here is a concise 2-line summary'. Just provide the summary directly.
"""
