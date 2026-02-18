import customtkinter as ctk


class HomeView(ctk.CTkFrame):
    def __init__(self, parent, db, on_navigate):
        super().__init__(parent, fg_color="#242424")
        self.db = db
        self.on_navigate = on_navigate
        self.build_ui()

    def build_ui(self):

        header = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=15)
        header.pack(fill="x", padx=30, pady=(30, 10))

        ctk.CTkLabel(header, text="Emotion Dashboard",
                     font=("Arial", 28, "bold")).pack(side="left", padx=30, pady=40)


        stats = self.db.get_stats()
        stats_frame = ctk.CTkFrame(header, fg_color="#333333", corner_radius=10)
        stats_frame.pack(side="right", padx=30, pady=20)

        total = stats["total"]
        last = stats["last_emotion"].capitalize()
        ctk.CTkLabel(stats_frame,
                     text=f"Total Checks: {total}  |  Last: {last}",
                     font=("Arial", 14), text_color="#aaaaaa").pack(padx=20, pady=10)


        ctk.CTkLabel(self,
                     text="Monitor your emotional well-being using AI facial recognition.",
                     font=("Arial", 16), text_color="gray").pack(pady=(20, 40))


        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(expand=True, fill="x", padx=30)
        for i in range(4):
            cards.grid_columnconfigure(i, weight=1)

        self._create_card(cards, "Check-in", "🔍",
                          lambda: self.on_navigate("scan"), 0)
        self._create_card(cards, "History", "📅",
                          lambda: self.on_navigate("calendar"), 1)
        self._create_card(cards, "Alerts", "🔔",
                          lambda: self.on_navigate("alerts"), 2)
        self._create_card(cards, "Settings", "⚙️",
                          lambda: self.on_navigate("settings"), 3)

    def _create_card(self, parent, title, icon, command, col):
        card = ctk.CTkFrame(parent, corner_radius=15, fg_color="#2b2b2b",
                            border_width=1, border_color="#3d3d3d")
        card.grid(row=0, column=col, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(card, text=icon, font=("Arial", 32)).pack(pady=(20, 5))
        ctk.CTkLabel(card, text=title, font=("Arial", 18, "bold")).pack(pady=5)
        ctk.CTkButton(card, text="Select", command=command,
                      fg_color="#6c82f0", hover_color="#5a6ed0",
                      width=140, height=32).pack(side="bottom", pady=20)