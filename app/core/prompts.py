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




combined_prompt= """
You are a dream analysis assistant specializing in emotional and thematic analysis.

Your task is to analyze dream narratives and extract:
1. A title for the dream  
2. A short text summary object  
3. A detailed summary with multiple components  
4. Emotional tones present in the dream with detailed descriptions  
5. Underlying themes in the dream  
6. Visual symbols that represent the dream

Provide your analysis in valid JSON format with these fields:

- title:  
  I will provide you a transcript of my dream and our conversation.
  Based on the dream content, provide a very concise, straightforward title for my dream journal
  based on the visual symbols, overall narrative or themes in the dream.
  I should be able to identify it quickly by title.
  Do not preface it with anything, provide only the answer.

- shortText:  
  I will provide you a transcript of my dream and our conversation.
  Based on our conversation, provide a brief one-sentence enlightening insight rooted in stoicism, Taoism,
  positive psychology, spirituality, mindset, energy, etc.
  Based on what my dream means or is processing from my subconscious, including core themes,
  latent desires/fears, beliefs, patterns, etc.
  Do not preface it with anything, provide only the answer.
- dreamDescription : It’s analyzing dream content and offering a psychological interpretation
- summary:  
  An object with the following fields:
  - dreamEntry:  
  - summary: {
      "dreamEntry":        "A concise retelling of the dream narrative",
      "summarizedAnalysis":"A detailed summary with multiple components",
      "thoughtReflection": "I will provide you a transcript of our conversation.
                           Based on what we discussed, provide one personal self-reflective
                           journal prompt/thought reflection based on core themes, topics,
                           and issues we talked about, and based on what my dream means or
                           is processing from my subconscious. Only share the reflection
                           question, max two sentences. Questions should be deeply
                           introspective, slightly challenging, and deep, as if I were talking
                           to myself. Do not preface it with anything, provide only the
                           journal prompt.",
      "alignedAction":     "I will provide you a transcript of our conversation.
                           Based on what we discussed, provide an aligned action/actionable
                           exercise to address and improve the core themes, topics, and issues
                           we talked about. Exercises should be highly personalized, healing,
                           nuanced, and tailored to my preferences. First, very briefly title
                           the exercise and then share it in three to six sentences. Then,
                           give one to two sentences summarizing what this exercise addresses
                           and the goal. Do not preface it with anything, provide only the
                           answer."
    }

- tones:  
  An array of objects, each with the following fields:
  - name:        The emotional tone (e.g., fear, uncertainty, introspection)
  - description: A detailed paragraph about that tone
  - manifests:   How this tone manifests in the dreamer's life
  - triggers:    What might trigger this emotional tone

- themes:  
  An array of underlying themes identified in the dream:
  - name:        I will provide you a transcript of my dream and our conversation.
                 Based on the dream content, primary themes that are present in the dream,
                 including core themes, latent desires/fears, beliefs, patterns, etc.
                 Do not provide more than three. Do not preface it with anything, provide
                 only the answer.
  - description: A detailed paragraph about that theme
  - manifests:   How this theme manifests in the dreamer's life
  - triggers:    What might trigger this theme

- visualSymbols:  
  An array of visual symbols (max six) that represent the dream:
  - name:        I will provide you a transcript of my dream and our conversation.
                 Based on the dream content only.
  - description: A detailed paragraph about that symbol
  - manifests:   How this symbol manifests in the dreamer's life
  - triggers:    What might trigger this symbol

Ensure your response is ONLY the JSON object, nothing else. 
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

chat_prompt = """
You are DreamyBot, a thoughtful, grounded, and friendly assistant who helps users with any question they have. 
            While you were originally designed for dream analysis, you now support all types of questions: weather, code, advice, ideas, explanations, etc. 
            Always stay calm, clear, curious, and compassionate — like a wise, emotionally intelligent guide. 
            If the user brings up dreams, respond with depth and symbolism. Otherwise, be factual, helpful, and supportive
"""