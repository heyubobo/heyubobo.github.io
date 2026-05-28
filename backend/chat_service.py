import config
import db
import llm
import prompts
import vector_memory


def build_chat_messages(user_id: str, session_id: str, user_message: str) -> list[dict]:
    related_memories = vector_memory.search_memory(user_message)
    messages: list[dict] = [
        {"role": "system", "content": prompts.build_system_prompt(related_memories)},
    ]

    summary = db.get_summary(user_id)
    if summary:
        messages.append(
            {
                "role": "system",
                "content": (
                    f"这是你对用户的长期记忆：\n{summary[:1000]}\n"
                    "请自然参考这些记忆。"
                ),
            }
        )

    for row in db.get_recent_messages(session_id):
        messages.append({"role": row["role"], "content": row["content"]})

    messages.append({"role": "user", "content": user_message})
    return messages


def maybe_update_summary(user_id: str, session_id: str) -> None:
    count = db.get_message_count(session_id)
    if count == 0 or count % config.SUMMARY_EVERY_N_MESSAGES != 0:
        return

    history_text = db.get_session_history_for_summary(session_id)
    if not history_text.strip():
        return

    summary = llm.generate_summary(history_text)
    if summary:
        db.update_summary(user_id, summary)


def maybe_store_vector_memory(user_message: str) -> None:
    if prompts.should_remember_message(user_message):
        vector_memory.add_memory(user_message)
