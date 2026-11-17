"""Gym & Fitness Management System - Production Desktop Application.

Modern Tkinter GUI frontend connected to MySQL database with complete CRUD,
search filtering, input validation, and real-time database sync.
"""

from datetime import date
import re
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Dict, List, Optional
from db_helper import Database


class ModernTheme:
    """Design tokens and color palette (Catppuccin Mocha inspired)."""

    BG_DARK = "#181825"         # Sidebar & Header base
    BG_CONTENT = "#1e1e2e"      # Content workspace base
    BG_CARD = "#313244"         # Input cards & frames
    BG_INPUT = "#45475a"        # Entry field background
    TEXT_PRIMARY = "#cdd6f4"    # Main high-contrast text
    TEXT_MUTED = "#a6adc8"      # Subheadings & hints
    ACCENT_PRIMARY = "#89b4fa"  # Calm Blue button/accent
    ACCENT_SUCCESS = "#a6e3a1"  # Mint Green for success/add
    ACCENT_WARNING = "#f9e2af"  # Warm Yellow for updates
    ACCENT_DANGER = "#f38ba8"   # Coral Red for delete/danger
    BORDER_COLOR = "#585b70"    # Subtle borders
    SELECTED_ROW = "#45475a"    # Treeview selection color


class GymApp(tk.Tk):
    """Main application window for the Gym & Fitness Management System."""

    def __init__(self) -> None:
        super().__init__()

        self.title("Gym & Fitness Management System")
        self.geometry("1180x720")
        self.minsize(980, 620)
        self.configure(bg=ModernTheme.BG_CONTENT)

        # Initialize Database connection helper
        self.db = Database()

        # State Variables
        self.active_member_id: Optional[int] = None
        self.status_var = tk.StringVar(value="Initializing application...")
        self.count_var = tk.StringVar(value="Members: 0")

        # Configure custom TTK styling
        self._configure_styles()

        # Build Main UI Layout
        self._build_layout()

        # Initial Database Connection Check & Data Load
        self.after(200, self._initial_connection_check)

    # ------------------------------------------------------------------
    # Styles Configuration
    # ------------------------------------------------------------------
    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        # Global Treeview Styling
        style.configure(
            "Treeview",
            background=ModernTheme.BG_CONTENT,
            foreground=ModernTheme.TEXT_PRIMARY,
            fieldbackground=ModernTheme.BG_CONTENT,
            rowheight=32,
            font=("Segoe UI", 10),
            borderwidth=0,
        )
        style.map(
            "Treeview",
            background=[("selected", ModernTheme.ACCENT_PRIMARY)],
            foreground=[("selected", "#11111b")],
        )

        style.configure(
            "Treeview.Heading",
            background=ModernTheme.BG_CARD,
            foreground=ModernTheme.TEXT_PRIMARY,
            font=("Segoe UI", 10, "bold"),
            padding=(8, 6),
            borderwidth=1,
            relief="flat",
        )
        style.map(
            "Treeview.Heading",
            background=[("active", ModernTheme.BG_INPUT)],
            foreground=[("active", "#ffffff")],
        )

        # Scrollbar styling
        style.configure(
            "Vertical.TScrollbar",
            background=ModernTheme.BG_CARD,
            troughcolor=ModernTheme.BG_CONTENT,
            bordercolor=ModernTheme.BORDER_COLOR,
            arrowcolor=ModernTheme.TEXT_PRIMARY,
        )

        # Combobox styling
        style.configure(
            "TCombobox",
            fieldbackground=ModernTheme.BG_INPUT,
            background=ModernTheme.BG_CARD,
            foreground=ModernTheme.TEXT_PRIMARY,
            arrowcolor=ModernTheme.TEXT_PRIMARY,
            padding=5,
        )

    # ------------------------------------------------------------------
    # Layout Builder
    # ------------------------------------------------------------------
    def _build_layout(self) -> None:
        # Top Global Header
        self.header_frame = tk.Frame(self, bg=ModernTheme.BG_DARK, height=64)
        self.header_frame.pack(side=tk.TOP, fill=tk.X)
        self.header_frame.pack_propagate(False)

        header_title = tk.Label(
            self.header_frame,
            text="⚡ TITAN GYM & FITNESS MANAGEMENT",
            font=("Segoe UI", 14, "bold"),
            bg=ModernTheme.BG_DARK,
            fg=ModernTheme.TEXT_PRIMARY,
            padx=20,
        )
        header_title.pack(side=tk.LEFT, fill=tk.Y)

        self.db_status_badge = tk.Label(
            self.header_frame,
            text="● MySQL: Connecting...",
            font=("Segoe UI", 9, "bold"),
            bg="#313244",
            fg=ModernTheme.TEXT_MUTED,
            padx=12,
            pady=4,
        )
        self.db_status_badge.pack(side=tk.RIGHT, padx=20, pady=16)

        # Body Frame (Sidebar + Workspace)
        self.body_frame = tk.Frame(self, bg=ModernTheme.BG_CONTENT)
        self.body_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Left Navigation Sidebar
        self._build_sidebar(self.body_frame)

        # Right Dynamic Workspace
        self.workspace_frame = tk.Frame(self.body_frame, bg=ModernTheme.BG_CONTENT)
        self.workspace_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # View Containers
        self.views: Dict[str, tk.Frame] = {}
        self.views["directory"] = self._build_directory_view(self.workspace_frame)
        self.views["form"] = self._build_form_view(self.workspace_frame)
        self.views["settings"] = self._build_settings_view(self.workspace_frame)

        # Bottom Global Status Bar
        self.status_bar = tk.Frame(self, bg=ModernTheme.BG_DARK, height=28)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar.pack_propagate(False)

        status_lbl = tk.Label(
            self.status_bar,
            textvariable=self.status_var,
            font=("Segoe UI", 9),
            bg=ModernTheme.BG_DARK,
            fg=ModernTheme.TEXT_MUTED,
            padx=15,
        )
        status_lbl.pack(side=tk.LEFT)

        count_lbl = tk.Label(
            self.status_bar,
            textvariable=self.count_var,
            font=("Segoe UI", 9, "bold"),
            bg=ModernTheme.BG_DARK,
            fg=ModernTheme.ACCENT_PRIMARY,
            padx=15,
        )
        count_lbl.pack(side=tk.RIGHT)

        # Show Directory View by default
        self.show_view("directory")

    # ------------------------------------------------------------------
    # Sidebar Construction
    # ------------------------------------------------------------------
    def _build_sidebar(self, parent: tk.Frame) -> None:
        self.sidebar_frame = tk.Frame(parent, bg=ModernTheme.BG_DARK, width=220)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)

        nav_label = tk.Label(
            self.sidebar_frame,
            text="NAVIGATION",
            font=("Segoe UI", 8, "bold"),
            bg=ModernTheme.BG_DARK,
            fg=ModernTheme.TEXT_MUTED,
            padx=20,
            pady=16,
            anchor="w",
        )
        nav_label.pack(fill=tk.X)

        self.btn_nav_dir = self._create_sidebar_btn(
            "📋 Member Directory", lambda: self.show_view("directory")
        )
        self.btn_nav_form = self._create_sidebar_btn(
            "➕ Register Member", self._prepare_new_registration
        )
        self.btn_nav_settings = self._create_sidebar_btn(
            "⚙️ Database Settings", lambda: self.show_view("settings")
        )

        # Separator spacer
        spacer = tk.Frame(self.sidebar_frame, bg=ModernTheme.BG_DARK)
        spacer.pack(fill=tk.BOTH, expand=True)

        # Quick Actions Section
        action_label = tk.Label(
            self.sidebar_frame,
            text="QUICK SYNC",
            font=("Segoe UI", 8, "bold"),
            bg=ModernTheme.BG_DARK,
            fg=ModernTheme.TEXT_MUTED,
            padx=20,
            pady=10,
            anchor="w",
        )
        action_label.pack(fill=tk.X)

        self._create_sidebar_btn("🔄 Refresh Data", self.refresh_records)
        self._create_sidebar_btn("🚪 Exit App", self.destroy, is_danger=True)

    def _create_sidebar_btn(
        self, text: str, command: Any, is_danger: bool = False
    ) -> tk.Button:
        hover_bg = "#45475a" if not is_danger else "#58202b"
        btn = tk.Button(
            self.sidebar_frame,
            text=text,
            command=command,
            font=("Segoe UI", 10),
            bg=ModernTheme.BG_DARK,
            fg=ModernTheme.TEXT_PRIMARY if not is_danger else ModernTheme.ACCENT_DANGER,
            activebackground=hover_bg,
            activeforeground="#ffffff",
            bd=0,
            padx=20,
            pady=12,
            anchor="w",
            cursor="hand2",
            relief="flat",
        )
        btn.pack(fill=tk.X)

        def on_enter(e):
            btn.configure(bg=hover_bg)

        def on_leave(e):
            btn.configure(bg=ModernTheme.BG_DARK)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    # ------------------------------------------------------------------
    # View 1: Member Directory (Interactive Table + Search)
    # ------------------------------------------------------------------
    def _build_directory_view(self, parent: tk.Frame) -> tk.Frame:
        view = tk.Frame(parent, bg=ModernTheme.BG_CONTENT)

        # Top Action & Search Bar Panel
        search_card = tk.Frame(view, bg=ModernTheme.BG_CARD, padx=16, pady=14)
        search_card.pack(side=tk.TOP, fill=tk.X, padx=20, pady=(20, 10))

        lbl_filter = tk.Label(
            search_card,
            text="Filter By:",
            font=("Segoe UI", 10, "bold"),
            bg=ModernTheme.BG_CARD,
            fg=ModernTheme.TEXT_PRIMARY,
        )
        lbl_filter.pack(side=tk.LEFT, padx=(0, 8))

        self.search_field_var = tk.StringVar(value="All")
        field_dropdown = ttk.Combobox(
            search_card,
            textvariable=self.search_field_var,
            values=["All", "Name", "Phone", "Email", "Plan", "Status"],
            state="readonly",
            width=10,
        )
        field_dropdown.pack(side=tk.LEFT, padx=(0, 10))

        lbl_search = tk.Label(
            search_card,
            text="Query:",
            font=("Segoe UI", 10, "bold"),
            bg=ModernTheme.BG_CARD,
            fg=ModernTheme.TEXT_PRIMARY,
        )
        lbl_search.pack(side=tk.LEFT, padx=(0, 8))

        self.search_entry_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_card,
            textvariable=self.search_entry_var,
            font=("Segoe UI", 10),
            bg=ModernTheme.BG_INPUT,
            fg=ModernTheme.TEXT_PRIMARY,
            insertbackground=ModernTheme.TEXT_PRIMARY,
            bd=0,
            relief="flat",
            width=26,
        )
        self.search_entry.pack(side=tk.LEFT, ipady=4, padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.perform_search())

        btn_search = tk.Button(
            search_card,
            text="🔍 Search",
            command=self.perform_search,
            font=("Segoe UI", 9, "bold"),
            bg=ModernTheme.ACCENT_PRIMARY,
            fg="#11111b",
            activebackground="#b4befe",
            bd=0,
            padx=14,
            pady=5,
            cursor="hand2",
        )
        btn_search.pack(side=tk.LEFT, padx=(0, 6))

        btn_reset = tk.Button(
            search_card,
            text="✕ Reset",
            command=self.reset_search,
            font=("Segoe UI", 9),
            bg=ModernTheme.BG_INPUT,
            fg=ModernTheme.TEXT_PRIMARY,
            activebackground=ModernTheme.BORDER_COLOR,
            bd=0,
            padx=12,
            pady=5,
            cursor="hand2",
        )
        btn_reset.pack(side=tk.LEFT)

        btn_edit_selected = tk.Button(
            search_card,
            text="✏️ Edit Selected",
            command=self.open_selected_for_edit,
            font=("Segoe UI", 9, "bold"),
            bg=ModernTheme.ACCENT_WARNING,
            fg="#11111b",
            activebackground="#f9e2af",
            bd=0,
            padx=14,
            pady=5,
            cursor="hand2",
        )
        btn_edit_selected.pack(side=tk.RIGHT)

        # Treeview Table Container Frame
        table_container = tk.Frame(view, bg=ModernTheme.BG_CONTENT)
        table_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))

        columns = ("member_id", "name", "phone", "email", "join_date", "plan_type", "status")
        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        col_configs = [
            ("member_id", "ID", 60, "center"),
            ("name", "Full Name", 180, "w"),
            ("phone", "Phone", 130, "center"),
            ("email", "Email Address", 210, "w"),
            ("join_date", "Join Date", 110, "center"),
            ("plan_type", "Membership Plan", 130, "center"),
            ("status", "Status", 100, "center"),
        ]

        for col_id, heading_text, width, anchor_align in col_configs:
            self.tree.heading(col_id, text=heading_text, anchor=anchor_align)
            self.tree.column(col_id, width=width, minwidth=60, anchor=anchor_align)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Event Binding: Double Click and Selection
        self.tree.bind("<Double-1>", lambda event: self.open_selected_for_edit())

        return view

    # ------------------------------------------------------------------
    # View 2: Member Form View (Register / Edit Member)
    # ------------------------------------------------------------------
    def _build_form_view(self, parent: tk.Frame) -> tk.Frame:
        view = tk.Frame(parent, bg=ModernTheme.BG_CONTENT)

        # Header Title Card
        title_card = tk.Frame(view, bg=ModernTheme.BG_CARD, padx=20, pady=16)
        title_card.pack(fill=tk.X, padx=24, pady=(20, 12))

        self.form_mode_title = tk.Label(
            title_card,
            text="Register New Gym Member",
            font=("Segoe UI", 13, "bold"),
            bg=ModernTheme.BG_CARD,
            fg=ModernTheme.TEXT_PRIMARY,
        )
        self.form_mode_title.pack(side=tk.LEFT)

        btn_back_to_dir = tk.Button(
            title_card,
            text="← Back to Directory",
            command=lambda: self.show_view("directory"),
            font=("Segoe UI", 9),
            bg=ModernTheme.BG_INPUT,
            fg=ModernTheme.TEXT_PRIMARY,
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2",
        )
        btn_back_to_dir.pack(side=tk.RIGHT)

        # Main Form Container (Card)
        form_card = tk.Frame(view, bg=ModernTheme.BG_CARD, padx=30, pady=24)
        form_card.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 20))

        # Form Variables
        self.form_id_var = tk.StringVar(value="(Auto-Generated)")
        self.form_name_var = tk.StringVar()
        self.form_phone_var = tk.StringVar()
        self.form_email_var = tk.StringVar()
        self.form_date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        self.form_plan_var = tk.StringVar(value="Monthly")
        self.form_status_var = tk.StringVar(value="Active")

        # Form Grid Layout Configuration
        form_card.columnconfigure(0, weight=0, minsize=140)
        form_card.columnconfigure(1, weight=1)
        form_card.columnconfigure(2, weight=0, minsize=140)
        form_card.columnconfigure(3, weight=1)

        fields = [
            (
                "Member ID:",
                tk.Label(
                    form_card,
                    textvariable=self.form_id_var,
                    font=("Segoe UI", 10, "bold"),
                    bg=ModernTheme.BG_CARD,
                    fg=ModernTheme.ACCENT_PRIMARY,
                    anchor="w",
                ),
                0, 0,
            ),
            (
                "Full Name *:",
                tk.Entry(
                    form_card,
                    textvariable=self.form_name_var,
                    font=("Segoe UI", 10),
                    bg=ModernTheme.BG_INPUT,
                    fg=ModernTheme.TEXT_PRIMARY,
                    insertbackground=ModernTheme.TEXT_PRIMARY,
                    bd=0,
                    relief="flat",
                ),
                1, 0,
            ),
            (
                "Phone Number *:",
                tk.Entry(
                    form_card,
                    textvariable=self.form_phone_var,
                    font=("Segoe UI", 10),
                    bg=ModernTheme.BG_INPUT,
                    fg=ModernTheme.TEXT_PRIMARY,
                    insertbackground=ModernTheme.TEXT_PRIMARY,
                    bd=0,
                    relief="flat",
                ),
                2, 0,
            ),
            (
                "Email Address *:",
                tk.Entry(
                    form_card,
                    textvariable=self.form_email_var,
                    font=("Segoe UI", 10),
                    bg=ModernTheme.BG_INPUT,
                    fg=ModernTheme.TEXT_PRIMARY,
                    insertbackground=ModernTheme.TEXT_PRIMARY,
                    bd=0,
                    relief="flat",
                ),
                3, 0,
            ),
            (
                "Join Date (YYYY-MM-DD):",
                tk.Entry(
                    form_card,
                    textvariable=self.form_date_var,
                    font=("Segoe UI", 10),
                    bg=ModernTheme.BG_INPUT,
                    fg=ModernTheme.TEXT_PRIMARY,
                    insertbackground=ModernTheme.TEXT_PRIMARY,
                    bd=0,
                    relief="flat",
                ),
                4, 0,
            ),
            (
                "Membership Plan:",
                ttk.Combobox(
                    form_card,
                    textvariable=self.form_plan_var,
                    values=["Monthly", "Quarterly", "Semi-Annual", "Annual"],
                    state="readonly",
                ),
                5, 0,
            ),
            (
                "Account Status:",
                ttk.Combobox(
                    form_card,
                    textvariable=self.form_status_var,
                    values=["Active", "Inactive", "Suspended", "Expired"],
                    state="readonly",
                ),
                6, 0,
            ),
        ]

        for label_text, widget, row_idx, col_offset in fields:
            lbl = tk.Label(
                form_card,
                text=label_text,
                font=("Segoe UI", 10),
                bg=ModernTheme.BG_CARD,
                fg=ModernTheme.TEXT_PRIMARY,
                anchor="w",
            )
            lbl.grid(row=row_idx, column=col_offset, sticky="w", pady=10, padx=(0, 10))

            if isinstance(widget, tk.Entry):
                widget.grid(row=row_idx, column=col_offset + 1, sticky="ew", pady=10, ipady=6)
            elif isinstance(widget, ttk.Combobox):
                widget.grid(row=row_idx, column=col_offset + 1, sticky="ew", pady=10)
            else:
                widget.grid(row=row_idx, column=col_offset + 1, sticky="w", pady=10)

        # Action Buttons Row
        btn_frame = tk.Frame(form_card, bg=ModernTheme.BG_CARD)
        btn_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(24, 0))

        self.btn_save = tk.Button(
            btn_frame,
            text="💾 Save Member",
            command=self.save_member,
            font=("Segoe UI", 10, "bold"),
            bg=ModernTheme.ACCENT_SUCCESS,
            fg="#11111b",
            activebackground="#a6e3a1",
            bd=0,
            padx=18,
            pady=8,
            cursor="hand2",
        )
        self.btn_save.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_update = tk.Button(
            btn_frame,
            text="🔄 Update Record",
            command=self.update_member_record,
            font=("Segoe UI", 10, "bold"),
            bg=ModernTheme.ACCENT_WARNING,
            fg="#11111b",
            activebackground="#f9e2af",
            bd=0,
            padx=18,
            pady=8,
            cursor="hand2",
        )
        self.btn_update.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_delete = tk.Button(
            btn_frame,
            text="🗑️ Delete Record",
            command=self.delete_member_record,
            font=("Segoe UI", 10, "bold"),
            bg=ModernTheme.ACCENT_DANGER,
            fg="#11111b",
            activebackground="#f38ba8",
            bd=0,
            padx=18,
            pady=8,
            cursor="hand2",
        )
        self.btn_delete.pack(side=tk.LEFT, padx=(0, 10))

        btn_clear = tk.Button(
            btn_frame,
            text="🧹 Clear Form",
            command=self.clear_form,
            font=("Segoe UI", 10),
            bg=ModernTheme.BG_INPUT,
            fg=ModernTheme.TEXT_PRIMARY,
            activebackground=ModernTheme.BORDER_COLOR,
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
        )
        btn_clear.pack(side=tk.LEFT)

        return view

    # ------------------------------------------------------------------
    # View 3: Database Settings & Live Connection Test
    # ------------------------------------------------------------------
    def _build_settings_view(self, parent: tk.Frame) -> tk.Frame:
        view = tk.Frame(parent, bg=ModernTheme.BG_CONTENT)

        card = tk.Frame(view, bg=ModernTheme.BG_CARD, padx=30, pady=25)
        card.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

        title = tk.Label(
            card,
            text="MySQL Workbench Connection Settings",
            font=("Segoe UI", 14, "bold"),
            bg=ModernTheme.BG_CARD,
            fg=ModernTheme.TEXT_PRIMARY,
        )
        title.pack(anchor="w", pady=(0, 10))

        desc = tk.Label(
            card,
            text="Configure parameters matching your MySQL Server / Workbench instance.",
            font=("Segoe UI", 10),
            bg=ModernTheme.BG_CARD,
            fg=ModernTheme.TEXT_MUTED,
        )
        desc.pack(anchor="w", pady=(0, 20))

        form_grid = tk.Frame(card, bg=ModernTheme.BG_CARD)
        form_grid.pack(anchor="w", fill=tk.X)
        form_grid.columnconfigure(0, weight=0, minsize=140)
        form_grid.columnconfigure(1, weight=1)

        self.cfg_host_var = tk.StringVar(value=self.db.config["host"])
        self.cfg_port_var = tk.StringVar(value=str(self.db.config["port"]))
        self.cfg_user_var = tk.StringVar(value=self.db.config["user"])
        self.cfg_pass_var = tk.StringVar(value=self.db.config["password"])
        self.cfg_db_var = tk.StringVar(value=self.db.config["database"])

        configs = [
            ("Server Host:", self.cfg_host_var, False),
            ("Server Port:", self.cfg_port_var, False),
            ("Username:", self.cfg_user_var, False),
            ("Password:", self.cfg_pass_var, True),
            ("Database Name:", self.cfg_db_var, False),
        ]

        for idx, (label_text, str_var, is_secret) in enumerate(configs):
            lbl = tk.Label(
                form_grid,
                text=label_text,
                font=("Segoe UI", 10),
                bg=ModernTheme.BG_CARD,
                fg=ModernTheme.TEXT_PRIMARY,
            )
            lbl.grid(row=idx, column=0, sticky="w", pady=8)

            entry = tk.Entry(
                form_grid,
                textvariable=str_var,
                font=("Segoe UI", 10),
                bg=ModernTheme.BG_INPUT,
                fg=ModernTheme.TEXT_PRIMARY,
                insertbackground=ModernTheme.TEXT_PRIMARY,
                show="*" if is_secret else "",
                bd=0,
                width=30,
            )
            entry.grid(row=idx, column=1, sticky="w", pady=8, ipady=5)

        btn_test = tk.Button(
            card,
            text="⚡ Test & Connect to MySQL",
            command=self.apply_db_settings,
            font=("Segoe UI", 10, "bold"),
            bg=ModernTheme.ACCENT_PRIMARY,
            fg="#11111b",
            activebackground="#b4befe",
            bd=0,
            padx=18,
            pady=8,
            cursor="hand2",
        )
        btn_test.pack(side=tk.LEFT, pady=(24, 0), padx=(0, 10))

        btn_demo = tk.Button(
            card,
            text="🧪 Switch to Local Demo Mode",
            command=self.activate_demo_mode,
            font=("Segoe UI", 10),
            bg=ModernTheme.BG_INPUT,
            fg=ModernTheme.TEXT_PRIMARY,
            activebackground=ModernTheme.BORDER_COLOR,
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
        )
        btn_demo.pack(side=tk.LEFT, pady=(24, 0))

        return view

    # ------------------------------------------------------------------
    # View Switching Controller
    # ------------------------------------------------------------------
    def show_view(self, view_name: str) -> None:
        """Switch current visible view container in the workspace."""
        for name, frame in self.views.items():
            if name == view_name:
                frame.pack(fill=tk.BOTH, expand=True)
            else:
                frame.pack_forget()

        self.status_var.set(f"Viewing: {view_name.capitalize()}")

    # ------------------------------------------------------------------
    # Data & Database Sync Handlers
    # ------------------------------------------------------------------
    def activate_demo_mode(self) -> None:
        """Activate offline local SQLite demo mode."""
        msg = self.db.enable_demo_mode()
        self.db_status_badge.configure(
            text="● Demo Mode: Local DB",
            bg="#3a301e",
            fg=ModernTheme.ACCENT_WARNING,
        )
        self.status_var.set(msg)
        self.refresh_records()
        self.show_view("directory")
        messagebox.showinfo("Demo Mode Active", "Local storage active with 5 preloaded members.\nYou can test full CRUD operations right away!")

    def _initial_connection_check(self) -> None:
        """Perform initial connection test and populate table."""
        success, msg = self.db.test_connection()
        if success:
            self.db_status_badge.configure(
                text="● MySQL: Connected (127.0.0.1)",
                bg="#1e3a2f",
                fg=ModernTheme.ACCENT_SUCCESS,
            )
            self.status_var.set(msg)
            self.refresh_records()
        else:
            self.db_status_badge.configure(
                text="● MySQL: Offline",
                bg="#451e24",
                fg=ModernTheme.ACCENT_DANGER,
            )
            self.status_var.set(f"Offline: {msg}")
            use_demo = messagebox.askyesno(
                "MySQL Server Offline",
                f"Could not connect to MySQL Server at 127.0.0.1:3306.\n\n"
                f"Details: {msg}\n\n"
                "Would you like to launch in Local Demo Mode (with 5 sample records preloaded) so you can test the application right away?",
            )
            if use_demo:
                self.activate_demo_mode()
            else:
                self.show_view("settings")

    def apply_db_settings(self) -> None:
        """Update active DB connection parameters from the settings view."""
        try:
            port = int(self.cfg_port_var.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Input", "Port must be a valid integer (e.g. 3306).")
            return

        self.db.config["host"] = self.cfg_host_var.get().strip()
        self.db.config["port"] = port
        self.db.config["user"] = self.cfg_user_var.get().strip()
        self.db.config["password"] = self.cfg_pass_var.get()
        self.db.config["database"] = self.cfg_db_var.get().strip()

        success, msg = self.db.test_connection()
        if success:
            self.db_status_badge.configure(
                text=f"● MySQL: Connected ({self.db.config['host']})",
                bg="#1e3a2f",
                fg=ModernTheme.ACCENT_SUCCESS,
            )
            self.status_var.set(msg)
            messagebox.showinfo("Connection Verified", msg)
            self.refresh_records()
            self.show_view("directory")
        else:
            self.db_status_badge.configure(
                text="● MySQL: Disconnected",
                bg="#451e24",
                fg=ModernTheme.ACCENT_DANGER,
            )
            self.status_var.set(f"Error: {msg}")
            messagebox.showerror("Connection Failed", msg)

    def refresh_records(self) -> None:
        """Reload all member records from MySQL into Treeview."""
        success, records, msg = self.db.fetch_all_members()
        if not success:
            self.status_var.set(msg)
            return

        self._populate_treeview(records)
        self.status_var.set(f"Successfully loaded {len(records)} members.")

    def _populate_treeview(self, records: List[Dict[str, Any]]) -> None:
        """Helper to clear and refill Treeview with records."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in records:
            # Format date display cleanly
            join_date_val = str(row.get("join_date", ""))
            self.tree.insert(
                "",
                tk.END,
                values=(
                    row["member_id"],
                    row["name"],
                    row["phone"],
                    row["email"],
                    join_date_val,
                    row["plan_type"],
                    row["status"],
                ),
            )

        self.count_var.set(f"Members: {len(records)}")

    def perform_search(self) -> None:
        """Execute parameterized query based on search query and field dropdown."""
        query = self.search_entry_var.get().strip()
        if not query:
            self.refresh_records()
            return

        field = self.search_field_var.get()
        success, results, msg = self.db.search_members(query, field)
        if success:
            self._populate_treeview(results)
            self.status_var.set(msg)
        else:
            messagebox.showerror("Search Error", msg)

    def reset_search(self) -> None:
        """Clear search input and reload full table."""
        self.search_entry_var.set("")
        self.search_field_var.set("All")
        self.refresh_records()

    # ------------------------------------------------------------------
    # Form Operations & Validation
    # ------------------------------------------------------------------
    def _validate_inputs(self) -> Tuple[bool, str]:
        """Validate all required fields prior to save or update."""
        name = self.form_name_var.get().strip()
        phone = self.form_phone_var.get().strip()
        email = self.form_email_var.get().strip()
        join_date_str = self.form_date_var.get().strip()

        if not name:
            return False, "Full Name is required."

        if not phone or len(phone) < 7:
            return False, "Please enter a valid phone number (at least 7 digits)."

        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_pattern, email):
            return False, "Please enter a valid email address (e.g. user@example.com)."

        # Validate Date format YYYY-MM-DD
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(date_pattern, join_date_str):
            return False, "Join Date must be in YYYY-MM-DD format."

        try:
            parts = [int(p) for p in join_date_str.split("-")]
            date(parts[0], parts[1], parts[2])
        except ValueError:
            return False, "Join Date is not a valid calendar date."

        return True, ""

    def _prepare_new_registration(self) -> None:
        """Set up form in 'Create New Member' mode and switch view."""
        self.clear_form()
        self.show_view("form")

    def open_selected_for_edit(self) -> None:
        """Populate form with selected Treeview row data and switch to form view."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Selection Required", "Please select a member row from the directory.")
            return

        item = selected_items[0]
        values = self.tree.item(item, "values")

        # Map values to form entries
        self.active_member_id = int(values[0])
        self.form_id_var.set(str(self.active_member_id))
        self.form_name_var.set(values[1])
        self.form_phone_var.set(values[2])
        self.form_email_var.set(values[3])
        self.form_date_var.set(values[4])
        self.form_plan_var.set(values[5])
        self.form_status_var.set(values[6])

        # Update Form View title & buttons
        self.form_mode_title.configure(text=f"Editing Member Record: ID #{self.active_member_id}")
        self.btn_save.configure(state=tk.DISABLED)
        self.btn_update.configure(state=tk.NORMAL)
        self.btn_delete.configure(state=tk.NORMAL)

        self.show_view("form")

    def save_member(self) -> None:
        """Add a new member to the database."""
        is_valid, err_msg = self._validate_inputs()
        if not is_valid:
            messagebox.showerror("Validation Error", err_msg)
            return

        success, msg, new_id = self.db.add_member(
            name=self.form_name_var.get(),
            phone=self.form_phone_var.get(),
            email=self.form_email_var.get(),
            join_date=self.form_date_var.get(),
            plan_type=self.form_plan_var.get(),
            status=self.form_status_var.get(),
        )

        if success:
            messagebox.showinfo("Success", msg)
            self.refresh_records()
            self.clear_form()
            self.show_view("directory")
        else:
            messagebox.showerror("Database Error", msg)

    def update_member_record(self) -> None:
        """Persist changes to an existing member record."""
        if not self.active_member_id:
            messagebox.showwarning("Notice", "No existing member is currently selected for update.")
            return

        is_valid, err_msg = self._validate_inputs()
        if not is_valid:
            messagebox.showerror("Validation Error", err_msg)
            return

        success, msg = self.db.update_member(
            member_id=self.active_member_id,
            name=self.form_name_var.get(),
            phone=self.form_phone_var.get(),
            email=self.form_email_var.get(),
            join_date=self.form_date_var.get(),
            plan_type=self.form_plan_var.get(),
            status=self.form_status_var.get(),
        )

        if success:
            messagebox.showinfo("Success", msg)
            self.refresh_records()
            self.show_view("directory")
        else:
            messagebox.showerror("Database Error", msg)

    def delete_member_record(self) -> None:
        """Prompt confirmation and delete active member record."""
        if not self.active_member_id:
            messagebox.showwarning("Notice", "No member selected for deletion.")
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to permanently delete Member ID #{self.active_member_id}?\n\n"
            "All associated payment history will also be removed.",
            icon="warning",
        )
        if not confirm:
            return

        success, msg = self.db.delete_member(self.active_member_id)
        if success:
            messagebox.showinfo("Deleted", msg)
            self.refresh_records()
            self.clear_form()
            self.show_view("directory")
        else:
            messagebox.showerror("Database Error", msg)

    def clear_form(self) -> None:
        """Reset all input fields and return form to Add/Register mode."""
        self.active_member_id = None
        self.form_id_var.set("(Auto-Generated)")
        self.form_name_var.set("")
        self.form_phone_var.set("")
        self.form_email_var.set("")
        self.form_date_var.set(date.today().strftime("%Y-%m-%d"))
        self.form_plan_var.set("Monthly")
        self.form_status_var.set("Active")

        self.form_mode_title.configure(text="Register New Gym Member")
        self.btn_save.configure(state=tk.NORMAL)
        self.btn_update.configure(state=tk.DISABLED)
        self.btn_delete.configure(state=tk.DISABLED)


# ----------------------------------------------------------------------
# Application Entry Point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = GymApp()
    app.mainloop()
