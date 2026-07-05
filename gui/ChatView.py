import customtkinter as ctk
import ollama
from datetime import datetime


class ChatView(ctk.CTkFrame):
    def __init__(self, parent, db, on_navigate, theme):
        super().__init__(parent, fg_color=theme["bg_main"])
        self.db = db
        self.on_navigate = on_navigate
        self.theme = theme

        # local history
        self.chat_history = []

        # context based on today's mood
        self.prepare_context()
        self.build_ui()

    def prepare_context(self):
        # 1. AI personality
        self.chat_history.append({
            "role": "system",
            "content": (
                "You are an emphatic and warm companion in an emotion journal app."
                
                "Your role is to listen to the user, to validate what they are feeling."
                
                "Keep the conversation short and professional, do not validate clinical/medical tips."
                
                "Always remember to the user that you are only a chatbot."
                
                "Ensure the user about the confidential data and that the chat is 100% private and the app "
                "is not using their data."
            )
        })

        # 2. take today's feeling and the note(optionally)
        today_str = datetime.today().strftime("%Y-%m-%d")
        dominant_emotion = self.db.get_dominant_emotion_for_today()
        note = self.db.get_note_for_date(today_str)

        context_prompt = "Hello, I've opened the chat!"
        if dominant_emotion:
            context_prompt = f"Hello! Today, during the face scan the app detected that i am [{dominant_emotion}]."
            if note:
                context_prompt += f" In the notes I left this: '{note}'."
            context_prompt += " Begin the conversation with a short reply adequate to my feelings."

        self.chat_history.append({"role": "user", "content": context_prompt})

        def_response = self.get_ollama_response()
        self.chat_history.append({"role": "assistant", "content": def_response})

    def build_ui(self):
        ctk.CTkLabel(self, text="💬  Empathetic AI Companion", font=("Arial", 26, "bold")).pack(pady=(25, 10))
        ctk.CTkLabel(self, text="100% Offline & Private Conversation", font=("Arial", 12),
                     text_color=self.theme["text_dim"]).pack(pady=(0, 15))

        self.messages_area = ctk.CTkScrollableFrame(self, fg_color=self.theme["bg_card"], corner_radius=12)
        self.messages_area.pack(expand=True, fill="both", padx=30, pady=(0, 15))

        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=30, pady=(0, 25))

        self.message_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="How was your day? Type here...",
            fg_color=self.theme["bg_card"],
            height=45,
            font=("Arial", 14)
        )
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.message_entry.bind("<Return>", lambda e: self.send_message())

        send_btn = ctk.CTkButton(
            input_frame,
            text="Send",
            command=self.send_message,
            fg_color=self.theme["accent"],
            hover_color="#5a6ed0",
            width=120,
            height=45,
            font=("Arial", 14, "bold")
        )
        send_btn.pack(side="right")

        self.render_chat_from_history()

    def send_message(self):
        user_text = self.message_entry.get().strip()
        if not user_text:
            return

        #clear the message input
        self.message_entry.delete(0, "end")

        # 1. add message on the screen and in the chat history
        self.chat_history.append({"role": "user", "content": user_text})
        self.append_message_to_ui("Tu", user_text, "#6c82f0")

        # AI thniking
        self.append_message_to_ui("AI Companion", "Thinking...", self.theme["text_dim"], is_temporary=True)

        # call AI
        self.after(10, self.process_ai_response)

    def process_ai_response(self):
        ai_response = self.get_ollama_response()

        # delete thinking message
        children = self.messages_area.winfo_children()
        if children:
            children[-1].destroy()

        # 3. add final answer on the screen and in history
        self.chat_history.append({"role": "assistant", "content": ai_response})
        self.append_message_to_ui("AI Companion", ai_response, "#4CAF50")

    def get_ollama_response(self):
        try:
            response = ollama.chat(
                model='llama3',
                messages=self.chat_history
            )
            return response['message']['content']
        except Exception as e:
            print(f"Error - Ollama: {e}")
            return "Sorry i have a technical problem, make sure that ollama is running."
    def append_message_to_ui(self, sender, text, color, is_temporary=False):
        msg_card = ctk.CTkFrame(self.messages_area, fg_color="transparent")
        msg_card.pack(fill="x", pady=6, padx=5)

        ctk.CTkLabel(
            msg_card,
            text=f"{sender}:",
            font=("Arial", 13, "bold"),
            text_color=color
        ).pack(anchor="w")

        ctk.CTkLabel(
            msg_card,
            text=text,
            font=("Arial", 14),
            text_color=self.theme["text_main"],
            wraplength=900,
            justify="left"
        ).pack(anchor="w", pady=(2, 0))
        self.messages_area._parent_canvas.yview_moveto(1.0)

    def render_chat_from_history(self):
        for msg in self.chat_history:
            if msg["role"] == "system":
                continue
            if msg["role"] == "user" and "Today, during the face scan" in msg["content"]:
                continue

            sender = "You" if msg["role"] == "user" else "AI Companion"
            color = "#6c82f0" if msg["role"] == "user" else "#4CAF50"
            self.append_message_to_ui(sender, msg["content"], color)