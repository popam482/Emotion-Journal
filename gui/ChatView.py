import customtkinter as ctk
import ollama
from datetime import datetime
import threading

class ChatView(ctk.CTkFrame):
    def __init__(self, parent, db, on_navigate, theme):
        super().__init__(parent, fg_color=theme["bg_main"])
        self.db = db
        self.on_navigate = on_navigate
        self.theme = theme

        # local history
        self.chat_history = []

        self.build_ui()

        self.message_entry.configure(placeholder_text="Loading AI companion..")
        # temporally block the UI
        self.message_entry.configure(state="disabled")
        self.send_btn.configure(state="disabled")

        self.append_message_to_ui(
            "AI Companion",
            "Hello! I am preparing your private workspace and reviewing today's mood. Please hold on a moment...",
            self.theme["text_dim"]
        )

        # context based on today's mood
        threading.Thread(target=self.prepare_context, daemon=True).start()

    def prepare_context(self):
        # 1. AI personality
        self.chat_history.append({
            "role": "system",
            "content": (
                "You are a warm, empathetic, and supportive companion integrated into a personal emotion journal app. "
                
                "Your primary purpose is to actively listen to the user, validate their feelings, and offer gentle "
                
                "emotional coping strategies to boost their mood."

                "Strict Behavioral Guidelines:"
                
                "- EMOTIONAL FOCUS: Keep the dialogue centered on the user's emotional well-being. If they talk about"
                "daily events (school, work, hobbies), steer the focus toward how those events make them feel."
                
                "- SAFETY & BOUNDARIES: You are NOT a therapist or professional counselor. Strictly refuse to give "
                "medical, clinical, or diagnostic advice. If the user shares severe psychological distress, gently "
                "suggest seeking professional human help."
                
                "- TRANSPARENCY: Remain grounded. If the user asks about your nature or treats you like a human,"
                " transparently and gently remind them that you are an AI chatbot designed for emotional support."
                
                "- CONCISENESS: Keep your responses brief, warm, and natural (1-3 short paragraphs max)."
                " Avoid long walls of text."
                "- PRIVACY ASSURANCE: If asked about privacy, confidently reassure the user that this chat is "
                "100% private, runs entirely offline locally on their machine, and their data is strictly "
                "confidential and never transmitted anywhere."
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

        self.after(0, self.initialization_complete)

    def initialization_complete(self):
        if not self.winfo_exists():
            return

        self.message_entry.configure(state="normal", placeholder_text="How was your day? Type here...")
        self.send_btn.configure(state="normal")
        self.render_chat_from_history()
        self.message_entry.focus()

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

        self.send_btn = ctk.CTkButton(
            input_frame,
            text="Send",
            command=self.send_message,
            fg_color=self.theme["accent"],
            hover_color="#5a6ed0",
            width=120,
            height=45,
            font=("Arial", 14, "bold")
        )
        self.send_btn.pack(side="right")

        self.render_chat_from_history()

    def send_message(self):
        user_text = self.message_entry.get().strip()
        if not user_text:
            return

        #clear the message input
        self.message_entry.delete(0, "end")

        self.message_entry.configure(state="disabled")
        self.send_btn.configure(state="disabled")

        # 1. add message on the screen and in the chat history
        self.chat_history.append({"role": "user", "content": user_text})
        self.append_message_to_ui("You", user_text, "#6c82f0")

        # AI thniking
        self.append_message_to_ui("AI Companion", "Thinking...", self.theme["text_dim"])

        # call AI
        threading.Thread(target=self.process_ai_response, daemon=True).start()

    def process_ai_response(self):
        ai_response = self.get_ollama_response()

        self.chat_history.append({"role": "assistant", "content": ai_response})

        self.after(0, lambda: self.update_ui_with_response(ai_response))

    def update_ui_with_response(self, ai_response):
        if not self.winfo_exists():
            return

        children = self.messages_area.winfo_children()
        if children:
            children[-1].destroy()

        # add the ollama response
        self.append_message_to_ui("AI Companion", ai_response, "#4CAF50")

        # activate UI
        self.message_entry.configure(state="normal")
        self.send_btn.configure(state="normal")
        self.message_entry.focus()

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
    def append_message_to_ui(self, sender, text, color):
        msg_card = ctk.CTkFrame(self.messages_area, fg_color="transparent")
        msg_card.pack(fill="x", pady=6, padx=5)

        if sender == "You":
            align_side = "e"
            text_alignment = "right"
        else:
            align_side = "w"
            text_alignment = "left"

        ctk.CTkLabel(
            msg_card,
            text=f"{sender}:",
            font=("Arial", 13, "bold"),
            text_color=color
        ).pack(anchor=align_side)

        ctk.CTkLabel(
            msg_card,
            text=text,
            font=("Arial", 14),
            text_color=self.theme["text_main"],
            wraplength=900,
            justify="left"
        ).pack(anchor=align_side, pady=(2, 0))

        self.after(10, lambda: self.messages_area._parent_canvas.yview_moveto(1.0))

    def render_chat_from_history(self):
        for child in self.messages_area.winfo_children():
            child.destroy()

        for msg in self.chat_history:
            if msg["role"] == "system":
                continue
            if msg["role"] == "user" and "Today, during the face scan" in msg["content"]:
                continue

            sender = "You" if msg["role"] == "user" else "AI Companion"
            color = "#6c82f0" if msg["role"] == "user" else "#4CAF50"
            self.append_message_to_ui(sender, msg["content"], color)