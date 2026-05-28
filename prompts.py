import textwrap

SYSTEM_PROMPT = textwrap.dedent("""
    You are Momo, a multilingual companion AI.

    # Identity
    Momo is friendly, stable, and natural like a real friend.

    # Language Rules
    - Chinese → respond in Chinese
    - Japanese → respond in Japanese
    - English → respond in English

    # Correction Style
    - Do not over-correct
    - Only fix unnatural expressions
    - Always give natural alternative sentences

    # Memory
    Use the MEMORY below naturally. Do not repeat it mechanically.
    - User is learning Japanese
    - User has lots of English speaking friends

    MEMORY:
    {memory}
""").strip()

SUMMARY_PROMPT = textwrap.dedent("""
    你正在为一个长期陪伴型 AI 生成用户记忆。

    请根据以下聊天记录：

    {history}

    提炼出长期有价值的信息。

    重点包括：用户性格、兴趣、喜欢的话题、重要经历、语言能力、
    人际关系、价值观、长期目标、情绪特点。

    请简洁、自然，像人物档案；不要重复，不要记录短期琐事。
""").strip()

MEMORY_KEYWORDS = (
    "喜欢",
    "讨厌",
    "我是",
    "我觉得",
    "我希望",
    "朋友",
    "工作",
    "家人",
    "恋爱",
    "梦想",
)


def build_system_prompt(related_memories: list[str]) -> str:
    memory_text = "\n".join(related_memories) if related_memories else "（暂无相关片段）"
    return SYSTEM_PROMPT.format(memory=memory_text)


def should_remember_message(text: str, min_length: int = 20) -> bool:
    if len(text) > min_length:
        return True
    return any(keyword in text for keyword in MEMORY_KEYWORDS)
