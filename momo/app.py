import traceback
import uuid

from flask import Flask, jsonify, render_template, request

import chat_service
import config
import db
import llm
import vector_memory

db.init_db()

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    session_id = None
    try:
        data = request.get_json() or {}
        user_message = (data.get("message") or "").strip()
        session_id = data.get("session_id") or str(uuid.uuid4())

        if not user_message:
            return jsonify({
                "reply": "你说啥？我没听见🥲",
                "session_id": session_id,
            })

        user_id = config.DEFAULT_USER_ID

        messages = chat_service.build_chat_messages(user_id, session_id, user_message)
        db.save_message(user_id, session_id, "user", user_message)

        ai_reply = llm.chat_completion(messages)
        db.save_message(user_id, session_id, "assistant", ai_reply)

        try:
            chat_service.maybe_store_vector_memory(user_message)
        except Exception as exc:
            print("MEMORY SAVE ERROR:", exc)

        try:
            chat_service.maybe_update_summary(user_id, session_id)
        except Exception as exc:
            print("SUMMARY UPDATE ERROR:", exc)

        return jsonify({"reply": ai_reply, "session_id": session_id})

    except Exception as exc:
        print("ERROR:", exc)
        traceback.print_exc()
        return jsonify({
            "reply": f"系统错误：{exc}",
            "session_id": session_id,
        }), 500


@app.route("/history")
def history():
    session_id = request.args.get("session_id")
    return jsonify(db.get_recent_history(session_id=session_id))


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, port=5003)
