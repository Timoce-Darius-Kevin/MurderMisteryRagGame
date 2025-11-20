import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from managers.GameManager import GameManager
from Services.ErrorHandler import ErrorHandler
from game_logic import generate_location, register_user_player
from ui.GameUIController import GameUIController


class LoadingIndicator:
    """A Tkinter loading indicator"""
    
    def __init__(self, parent, text="Thinking..."):
        self.parent = parent
        self.text = text
        self.is_running = False
        self.dots_count = 0
        
        # Create loading window
        self.loading_window = tk.Toplevel(parent)
        self.loading_window.title("Processing")
        self.loading_window.geometry("300x120")
        self.loading_window.transient(parent)
        self.loading_window.grab_set()
        
        # Center the loading window
        self.loading_window.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 300) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 120) // 2
        self.loading_window.geometry(f"+{x}+{y}")
        
        # Make it non-resizable
        self.loading_window.resizable(False, False)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the loading indicator UI"""
        # Main frame
        main_frame = tk.Frame(self.loading_window, padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        # Loading text
        self.text_label = tk.Label(
            main_frame,
            text=self.text,
            font=('Arial', 11),
            fg='#2c3e50'
        )
        self.text_label.pack(pady=(0, 15))
        
        # Progress bar
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=250,
        )
        self.progress.pack(pady=5)
        
        # Dots animation
        self.dots_label = tk.Label(
            main_frame,
            text="",
            font=('Arial', 10),
            fg='#7f8c8d'
        )
        self.dots_label.pack(pady=5)
        
    def start(self):
        """Start the loading indicator"""
        self.is_running = True
        self.dots_count = 0
        self.loading_window.deiconify()
        self.progress.start(10)
        self.animate_dots()
        
    def animate_dots(self):
        """Animate the dots for loading effect"""
        if self.is_running:
            self.dots_count = (self.dots_count + 1) % 4
            dots = "." * self.dots_count
            self.dots_label.config(text=dots)
            self.loading_window.after(500, self.animate_dots)
        
    def stop(self):
        """Stop and close the loading indicator"""
        self.is_running = False
        try:
            self.progress.stop()
        except tk.TclError:
            # Progress bar already destroyed, ignore error
            pass
        try:
            if self.loading_window.winfo_exists():
                self.loading_window.destroy()
        except tk.TclError:
            # Window already destroyed, ignore error
            pass


class WelcomeScreen:
    """Welcome screen for player registration"""
    
    def __init__(self, root, on_game_start):
        self.root = root
        self.on_game_start = on_game_start
        self.setup_ui()
    
    def setup_ui(self):
        """Create the welcome screen UI"""
        welcome_frame = tk.Frame(self.root, bg="#191f72", padx=20, pady=20)
        welcome_frame.pack(expand=True, fill='both')
        
        # Title
        title_label = tk.Label(
            welcome_frame, 
            text="MURDER MYSTERY GAME", 
            font=('Arial', 24, 'bold'),
            fg='#e74c3c',
            bg='#2c3e50'
        )
        title_label.pack(pady=20)
        
        # Introduction text
        intro_text = tk.Label(
            welcome_frame,
            text="Welcome to the Murder Mystery Game!\n\nA crime has been committed and you must uncover the truth.\nInterview suspects, gather clues, and solve the mystery before it's too late!",
            font=('Arial', 12),
            fg="#000000",
            bg="#7c0d86",
            justify='center'
        )
        intro_text.pack(pady=20)
        
        # Name entry
        name_frame = tk.Frame(welcome_frame, bg='#2c3e50')
        name_frame.pack(pady=20)
        
        tk.Label(
            name_frame,
            text="Enter your name:",
            font=('Arial', 12, 'bold'),
            fg='#ecf0f1',
            bg='#2c3e50'
        ).pack()
        
        self.name_entry = tk.Entry(
            name_frame,
            font=('Arial', 12),
            width=30
        )
        self.name_entry.pack(pady=10)
        self.name_entry.focus()
        self.name_entry.bind('<Return>', lambda e: self.start_game())
        
        # Start button
        start_btn = tk.Button(
            welcome_frame,
            text="BEGIN INVESTIGATION",
            font=('Arial', 14, 'bold'),
            bg='#27ae60',
            fg='white',
            command=self.start_game,
            padx=20,
            pady=10
        )
        start_btn.pack(pady=20)
    
    def start_game(self):
        """Start the game with the provided player name"""
        player_name = self.name_entry.get().strip()
        if not player_name:
            messagebox.showwarning("Input Required", "Please enter your name to begin.")
            return
        
        # Destroy welcome screen and call the game start callback
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.on_game_start(player_name)


class GameScreen:
    """Main game screen with all game functionality."""

    def __init__(self, root: tk.Tk, player_name: str, error_handler: ErrorHandler | None = None) -> None:
        """Create the main game screen.

        Args:
            root: The Tk root window.
            player_name: Name entered by the player.
            error_handler: Optional shared error handler instance.
        """
        self.root = root
        self.player_name = player_name
        self.error_handler = error_handler or ErrorHandler()

        # Initialize game state in constructor
        self.location = generate_location()
        self.user_player = register_user_player(player_name)
        self.game_manager = GameManager(
            self.location,
            self.user_player,
            error_handler=self.error_handler,
        )
        self.controller = GameUIController(
            self.game_manager,
            self.user_player,
            error_handler=self.error_handler,
        )

        # UI state - initialize with empty/default values
        self.current_action: str = ""
        self.loading_indicator: LoadingIndicator | None = None
        self.current_result_queue = None

        self.setup_ui()
        self.update_display()
        
        # Welcome message
        self.log_message(f"🕵️ Welcome, {player_name}!", '#3498db')
        self.log_message(f"📍 You are at {self.location.name}", '#f39c12')
        self.log_message(f"📖 {self.location.event_description}", '#ecf0f1')
        self.log_message("🔍 Investigate the murder by questioning suspects and gathering clues!", '#27ae60')
    
    def setup_ui(self):
        """Create the main game interface"""
        # Main container
        main_container = tk.Frame(self.root, bg='#34495e')
        main_container.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Top section - Location and suspicion
        top_frame = tk.Frame(main_container, bg='#34495e', relief='raised', bd=2)
        top_frame.pack(fill='x', pady=(0, 10))
        
        self.location_label = tk.Label(
            top_frame,
            font=('Arial', 14, 'bold'),
            fg='#f39c12',
            bg="#34495e",
            justify='left'
        )
        self.location_label.pack(anchor='w', padx=10, pady=5)
        
        self.suspicion_label = tk.Label(
            top_frame,
            font=('Arial', 12, 'bold'),
            fg='#e74c3c',
            bg='#34495e'
        )
        self.suspicion_label.pack(anchor='w', padx=10, pady=(0, 5))
        
        # Middle section - Action buttons and output
        middle_frame = tk.Frame(main_container, bg='#34495e')
        middle_frame.pack(fill='both', expand=True)
        
        # Left panel - Actions
        action_frame = tk.LabelFrame(
            middle_frame, 
            text="Investigation Actions", 
            font=('Arial', 12, 'bold'),
            fg='#ecf0f1',
            bg='#2c3e50',
            bd=2
        )
        action_frame.pack(side='left', fill='y', padx=(0, 10))
        
        # Action buttons
        actions = [
            ("🔍 Ask Question", self.ask_question),
            ("⚖️ Accuse Player", self.accuse_player),
            ("👥 See Players in Room", self.see_players),
            ("🚪 Move to Another Room", self.move_room),
            ("💼 Ask About Inventory", self.ask_inventory),
            ("👤 View Player Details", self.view_player_details),  # NEW
            ("🎒 View My Inventory", self.view_my_inventory),      # NEW
            ("❌ Quit Game", self.quit_game)
        ]
        for text, command in actions:
            btn = tk.Button(
                action_frame,
                text=text,
                font=('Arial', 11),
                bg='#3498db',
                fg='white',
                command=command,
                width=20,
                anchor='w',
                padx=10
            )
            btn.pack(fill='x', pady=5, padx=5)
        
        # Right panel - Game output
        output_frame = tk.LabelFrame(
            middle_frame,
            text="Game Log",
            font=('Arial', 12, 'bold'),
            fg='#ecf0f1',
            bg='#2c3e50',
            bd=2
        )
        output_frame.pack(side='right', fill='both', expand=True)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            font=('Arial', 10),
            bg='#1a1a1a',
            fg='#00ff00',
            width=60,
            height=20
        )
        self.output_text.pack(fill='both', expand=True, padx=5, pady=5)
        self.output_text.config(state=tk.DISABLED)
        
        # Bottom section - Current action
        self.action_frame = tk.Frame(main_container, bg='#34495e', relief='sunken', bd=1)
        self.action_frame.pack(fill='x', pady=(10, 0))
        
        self.action_label = tk.Label(
            self.action_frame,
            text="Select an action to begin...",
            font=('Arial', 11),
            fg='#bdc3c7',
            bg='#34495e'
        )
        self.action_label.pack(pady=5)
    
    def update_display(self):
        """Update the game display with current state."""
        current_room = self.controller.get_current_room()
        
        # Update location info
        location_text = f"📍 {current_room.name}\n{current_room.description}"
        self.location_label.config(text=location_text)
        
        # Update suspicion
        suspicion_text = f"🕵️ Your Suspicion Level: {self.user_player.suspicion}/100"
        self.suspicion_label.config(text=suspicion_text)
        
        # Clear action frame
        for widget in self.action_frame.winfo_children():
            if widget != self.action_label:
                widget.destroy()
    
    def log_message(self, message: str, color: str = '#00ff00') -> None:
        """Add a message to the game log."""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"{message}\n")
        self.output_text.config(state=tk.DISABLED)
        self.output_text.see(tk.END)
    
    def show_loading(self, text: str = "Thinking...") -> None:
        """Show loading indicator."""
        if self.loading_indicator is None:
            self.loading_indicator = LoadingIndicator(self.root, text)
        self.loading_indicator.start()
    
    def hide_loading(self) -> None:
        """Hide loading indicator."""
        if self.loading_indicator:
            self.loading_indicator.stop()
            self.loading_indicator = None
    
    def ask_question(self) -> None:
        """Handle asking questions to players."""
        players = self.controller.get_players_in_current_room()
        
        if not players:
            self.log_message("❌ No one is near you. Move to another room to find suspects.", '#e74c3c')
            return
            
        self.current_action = "ask_question"
        self.show_player_selection(players, "Ask a question to:")
    
    def accuse_player(self) -> None:
        """Handle accusing players."""
        players = self.controller.get_players_in_current_room()
        
        if not players:
            self.log_message("❌ No one is near you. Move to another room to find suspects.", '#e74c3c')
            return
            
        self.current_action = "accuse"
        self.show_player_selection(players, "Accuse someone of murder:")
    
    def ask_inventory(self) -> None:
        """Handle asking about inventory."""
        players = self.controller.get_players_in_current_room()
        
        if not players:
            self.log_message("❌ No one is near you. Move to another room to find suspects.", '#e74c3c')
            return
            
        self.current_action = "inventory"
        self.show_player_selection(players, "Ask about inventory:")
    
    def show_player_selection(self, players, title: str) -> None:
        """Show player selection interface."""
        self.action_label.config(text=title)
        
        for idx, player in enumerate(players):
            btn = tk.Button(
                self.action_frame,
                text=f"👤 {player.name} (Suspicion: {player.suspicion})",
                font=('Arial', 10),
                bg='#8e44ad',
                fg='white',
                command=lambda p=player: self.handle_player_selection(p),
                padx=10
            )
            btn.pack(side='left', padx=5, pady=5)
    
    def ask_question_to_player(self, player) -> None:
        """Show interface for asking a specific question."""
        self.action_label.config(text=f"Ask {player.name} a question:")
        
        # Question entry
        question_frame = tk.Frame(self.action_frame, bg='#34495e')
        question_frame.pack(fill='x', padx=10, pady=5)
        
        question_entry = tk.Entry(question_frame, font=('Arial', 11), width=50)
        question_entry.pack(side='left', padx=(0, 10))
        question_entry.focus()
        
        def submit_question() -> None:
            question_text = question_entry.get().strip()
            if question_text:
                # Show loading indicator
                self.show_loading(f"{player.name} is thinking...")

                # Start conversation asynchronously via controller
                self.current_result_queue = self.controller.start_conversation_async(
                    player, question_text
                )

                # Check for result periodically
                self.check_conversation_result()
        
        submit_btn = tk.Button(
            question_frame,
            text="Ask",
            bg='#27ae60',
            fg='white',
            command=submit_question
        )
        submit_btn.pack(side='left')
        
        question_entry.bind('<Return>', lambda e: submit_question())
    
    def check_conversation_result(self) -> None:
        """Check for conversation result from background thread."""
        if self.current_result_queue is None:
            return

        if not self.current_result_queue.empty():
            status, payload = self.current_result_queue.get()
            self.current_result_queue = None
            self.hide_loading()

            if status == "success":
                result_data = payload
                player = result_data["player"]
                question_text = result_data["question_text"]
                response = result_data["response"]
                sus_speaker = result_data["suspicion_change_speaker"]
                sus_listener = result_data["suspicion_change_listener"]

                self.log_message(
                    f"🗣️ You ask {player.name}: \"{question_text}\"", "#3498db"
                )
                self.log_message(f"💬 {player.name} says: {response}", "#f39c12")

                if sus_speaker != 0 or sus_listener != 0:
                    self.log_suspicion_changes(sus_speaker, sus_listener, player.name)

                self.update_display()
            else:
                error_message = str(payload)
                self.log_message(f"❌ Error: {error_message}", "#e74c3c")
        else:
            # Check again after 100ms
            self.root.after(100, self.check_conversation_result)
    
    def make_accusation(self, player) -> None:
        """Handle player accusation with confirmation."""
        result = messagebox.askyesno(
            "Confirm Accusation",
            f"Are you sure you want to accuse {player.name} of murder?\n\nThis is a serious accusation!"
        )
        
        if result:
            if self.controller.accuse_player(player):
                self.log_message(f"✅ CORRECT! {player.name} was the murderer!", '#27ae60')
                self.log_message("🎉 You solved the mystery! Congratulations!", '#f39c12')
                self.disable_actions()
            else:
                self.log_message(f"❌ WRONG! {player.name} is not the murderer!", '#e74c3c')
                self.log_message("📈 Your suspicion has increased massively!", '#e74c3c')
                self.update_display()
    
    def handle_inventory_question(self, player) -> None:
        """Handle asking about inventory with loading indicator."""
        # Show loading indicator
        self.show_loading(f"Checking {player.name}'s inventory...")

        # Start inventory query asynchronously via controller
        self.current_result_queue = self.controller.start_inventory_query_async(player)
        self.check_inventory_result()
    
    def check_inventory_result(self) -> None:
        """Check for inventory result from background thread."""
        if self.current_result_queue is None:
            return

        if not self.current_result_queue.empty():
            status, payload = self.current_result_queue.get()
            self.current_result_queue = None
            self.hide_loading()

            if status == "success":
                result_data = payload
                player = result_data.get("player")

                self.log_message(
                    f"💼 You ask {player.name} about their inventory", "#3498db"
                )
                self.log_message(
                    f"💬 {player.name} says: {result_data['response']}", "#f39c12"
                )

                if (
                    result_data["suspicion_change_speaker"] != 0
                    or result_data["suspicion_change_listener"] != 0
                ):
                    self.log_suspicion_changes(
                        result_data["suspicion_change_speaker"],
                        result_data["suspicion_change_listener"],
                        player.name,
                    )

                self.update_display()
            else:
                error_message = str(payload)
                self.log_message(f"❌ Error: {error_message}", "#e74c3c")
        else:
            # Check again after 100ms
            self.root.after(100, self.check_inventory_result)
    
    def log_suspicion_changes(self, sus_speaker: int, sus_listener: int, player_name: str) -> None:
        """Log suspicion changes in a formatted way."""
        if sus_speaker != 0:
            change_type = "increased" if sus_speaker > 0 else "decreased"
            self.log_message(f"📊 Your suspicion {change_type} by {abs(sus_speaker)}", '#e67e22')
        if sus_listener != 0:
            change_type = "increased" if sus_listener > 0 else "decreased"
            self.log_message(f"📊 {player_name}'s suspicion {change_type} by {abs(sus_listener)}", '#e67e22')
    
    def see_players(self) -> None:
        """Show players in current room."""
        players = self.controller.get_players_in_current_room()
        
        if not players:
            self.log_message("👥 No other players in this room.", '#bdc3c7')
        else:
            self.log_message("👥 Players in this room:", '#3498db')
            for player in players:
                self.log_message(f"   • {player.name} (Suspicion: {player.suspicion})", '#ecf0f1')
    
    def move_room(self) -> None:
        """Handle moving to another room."""
        rooms = self.controller.get_all_rooms()
        
        self.current_action = "move"
        self.action_label.config(text="Select a room to move to:")
        
        # Create a frame for room buttons with scrollbar if needed
        room_frame = tk.Frame(self.action_frame, bg='#34495e')
        room_frame.pack(fill='x', padx=10, pady=5)
        
        for room in rooms:
            btn = tk.Button(
                room_frame,
                text=f"🚪 {room.name}",
                font=('Arial', 10),
                bg='#16a085',
                fg='white',
                command=lambda r=room: self.handle_room_move(r),
                padx=10,
                anchor='w'
            )
            btn.pack(fill='x', pady=2)
    
    def handle_room_move(self, room) -> None:
        """Handle moving to selected room."""
        self.controller.move_to_room(room)
        self.log_message(f"🚶 You move to the {room.name}", '#3498db')
        self.update_display()
    
    def disable_actions(self) -> None:
        """Disable actions when game is over."""
        self.action_label.config(text="Game Over - Mystery Solved!")
        for widget in self.action_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(state=tk.DISABLED)
    
    def quit_game(self) -> None:
        """Handle game quit with confirmation."""
        if messagebox.askyesno("Quit Game", "Are you sure you want to quit the game?"):
            # Stop any loading indicators
            self.hide_loading()
            self.cleanup_database()
            self.root.destroy()
    
    def cleanup_database(self) -> None:
        """Clean up the vector database on application exit."""
        try:
            self.controller.cleanup()
        except Exception as error:
            # Fallback to simple stdout logging if controller cleanup fails.
            print(f"Error during cleanup: {error}")

    def view_player_details(self) -> None:
        """Handle viewing player details (job and known items)."""
        players = self.controller.get_players_in_current_room()
        
        if not players:
            self.log_message("❌ No other players in this room to view details.", '#e74c3c')
            return
            
        self.current_action = "view_details"
        self.show_player_selection(players, "View details for:")

    def view_my_inventory(self) -> None:
        """Handle viewing the user's own inventory."""
        result = self.controller.get_user_inventory()
        self.log_message("🎒 Your Inventory:", '#3498db')
        self.log_message(result['response'], '#ecf0f1')
        
        # Log item details if any
        if self.user_player.inventory:
            for item in self.user_player.inventory:
                weapon_indicator = " 🔪" if item.murder_weapon else ""
                self.log_message(f"   • {item.name}{weapon_indicator} - {item.description} (Value: {item.value})", '#bdc3c7')

    def handle_player_selection(self, player) -> None:
        """Handle when a player is selected for an action."""
        if self.current_action == "ask_question":
            self.ask_question_to_player(player)
        elif self.current_action == "accuse":
            self.make_accusation(player)
        elif self.current_action == "inventory":
            self.handle_inventory_question(player)
        elif self.current_action == "view_details":
            self.show_player_details(player)

    def show_player_details(self, player) -> None:
        """Show detailed information about a player."""
        self.log_message(f"👤 Player Details: {player.name}", '#3498db')
        self.log_message(f"   Profession: {player.job}", '#ecf0f1')
        self.log_message(f"   Suspicion Level: {player.suspicion}", '#e67e22')
        self.log_message(f"   Current Mood: {player.mood}", '#9b59b6')
        
        known_items = player.get_known_items()
        if known_items:
            self.log_message("   Known Items:", '#27ae60')
            for item in known_items:
                weapon_indicator = " 🔪" if item.murder_weapon else ""
                self.log_message(f"     • {item.name}{weapon_indicator} - {item.description}", '#bdc3c7')
        else:
            self.log_message("   No known items yet.", '#95a5a6')


class MysteryGameUI:
    """Main application controller for the Murder Mystery game UI."""

    def __init__(self) -> None:
        """Initialize the Tkinter root window and welcome screen."""
        self.root = tk.Tk()
        self.error_handler = ErrorHandler()
        self.root.title("Murder Mystery Game")
        self.root.geometry("900x700")
        self.root.configure(bg="#c6c2c9")
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
        self.welcome_screen = WelcomeScreen(self.root, self.start_game)
        self.game_screen: GameScreen | None = None

    def on_window_close(self) -> None:
        """Handle window close event."""
        if self.game_screen:
            self.game_screen.hide_loading()
            self.game_screen.cleanup_database()
            self.root.destroy()
        else:
            self.root.destroy()

    def start_game(self, player_name: str) -> None:
        """Start the main game with the provided player name."""
        try:
            self.game_screen = GameScreen(self.root, player_name, self.error_handler)
        except Exception as error:
            self.error_handler.log_error(error, context="MysteryGameUI.start_game")
            messagebox.showerror(
                "Error",
                "An unexpected error occurred while starting the game."
            )

    def run(self) -> None:
        """Start the application event loop."""
        self.root.mainloop()


def start_ui() -> None:
    """Entry point for starting the UI."""
    app = MysteryGameUI()
    app.run()


if __name__ == "__main__":
    start_ui()