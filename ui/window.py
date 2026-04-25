import tkinter as tk
import math
import random
from pathlib import Path
from typing import Callable, Optional

# Decorações


class Decoration:
    def __init__(self, canvas, x, y, kind="star", size=8, color="#FFB7D5"):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.base_y = y
        self.kind = kind
        self.size = size
        self.color = color
        self.id = None
        self.offset = random.uniform(0, math.pi * 2)
        self._draw()

    def _draw(self):
        s = self.size
        if self.kind == "star":
            pts = self._star_points(self.x, self.y, s, s // 2, 5)
            self.id = self.canvas.create_polygon(pts, fill=self.color, outline="")
        else:
            self.id = self.canvas.create_text(
                self.x, self.y, text="♥", fill=self.color,
                font=("Lato", s))

    def tick(self, t):
        new_y = self.base_y + math.sin(t * 1.2 + self.offset) * 3
        self.canvas.move(self.id, 0, new_y - self.y)
        self.y = new_y

    @staticmethod
    def _star_points(cx, cy, r_out, r_in, n):
        pts = []
        for i in range(n * 2):
            r = r_out if i % 2 == 0 else r_in
            a = math.pi / n * i - math.pi / 2
            pts.extend([cx + r * math.cos(a), cy + r * math.sin(a)])
        return pts

# Raindrop

class Raindrop:
    def __init__(self, canvas, width, height, color):
        self.canvas = canvas
        self.w = width
        self.h = height
        self.color = color
        self._spawn()

    def _spawn(self):
        self.x = random.randint(0, self.w)
        self.y = random.randint(-self.h, 0)
        self.sp = random.randint(4, 9)
        length = random.randint(8, 16)
        self.id = self.canvas.create_line(
            self.x, self.y, self.x - 2, self.y + length,
            fill=self.color, width=1)

    def tick(self):
        self.canvas.move(self.id, 0, self.sp)
        self.y += self.sp
        if self.y > self.h + 20:
            self.canvas.delete(self.id)
            self._spawn()

# Janela Principal

class FloatingWindow(tk.Tk):

    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self._cb: Optional[Callable] = None
        self._current_state = "default"
        self._decorations = []
        self._raindrops = []
        self._anim_t = 0.0

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.97)
        self.resizable(False, False)
        self.configure(bg=cfg.PALETTE["default_bg"])

        W, H = cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT
        self.W, self.H = W, H

        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{W}x{H}+{sw - W - cfg.MARGIN}+{sh - H - cfg.MARGIN - 48}")

        self.canvas = tk.Canvas(self, width=W, height=H,
                                highlightthickness=0, bd=0,
                                bg=cfg.PALETTE["default_bg"])
        self.canvas.pack(fill="both", expand=True, padx=0, pady=0)
        self.update_idletasks()

        self._build_widgets()
        self._build_decorations()
        self._apply_state("default")

        self.canvas.bind("<ButtonPress-1>", self._drag_start)
        self.canvas.bind("<B1-Motion>", self._drag_motion)

        self._animate()
        self.after(cfg.UPDATE_INTERVAL_MS, self._schedule_update)


    def _build_widgets(self):
        C = self.canvas
        pal = self.cfg.PALETTE
        W, H = self.W, self.H

        self._bg_rect = C.create_rectangle(
            2, 2, W - 2, H - 2,
            fill=pal["default_bg"], outline=pal["default_accent"], width=2)

        # Botão ×
        self._close_btn = C.create_text(
            W - 12, 12, text="×", fill=pal["close_btn"],
            font=("Lato", 14, "bold"), tags="close")
        C.tag_bind("close", "<Button-1>", lambda e: self.destroy())
        C.tag_bind("close", "<Enter>", lambda e: C.itemconfig("close", fill=pal["close_hover"]))
        C.tag_bind("close", "<Leave>", lambda e: C.itemconfig("close", fill=pal["close_btn"]))

        # Botão ⚙
        self._gear_btn = C.create_text(
            W - 28, 12, text="⚙", fill=pal["close_btn"],
            font=("Lato", 10), tags="gear")
        C.tag_bind("gear", "<Button-1>", lambda e: self._open_settings())
        C.tag_bind("gear", "<Enter>", lambda e: C.itemconfig("gear", fill=pal["close_hover"]))
        C.tag_bind("gear", "<Leave>", lambda e: C.itemconfig("gear", fill=pal["close_btn"]))

        self._icon_id = C.create_text(34, H // 2 - 4, text="🌤️",
                                       font=("Noto Color Emoji", 24))

        self._temp_id = C.create_text(
            80, H // 2 - 18, text="--°C",
            font=("Lato", 20, "bold"), fill=pal["default_fg"], anchor="w")

        self._desc_id = C.create_text(
            80, H // 2 + 6, text="aguardando...",
            font=("Lato", 9), fill=pal["default_fg"], anchor="w")

        self._detail_id = C.create_text(
            80, H // 2 + 22, text="💧--% 💨-- km/h",
            font=("Lato", 8), fill=pal["default_fg"], anchor="w")

        self._city_id = C.create_text(
            W // 2, H - 14, text=self.cfg.CITY,
            font=("Lato", 8), fill=pal["default_fg"])

        self._err_id = C.create_text(
            W // 2, H // 2, text="",
            font=("Lato", 8), fill="#C2607A")

    def _build_decorations(self):
        pal = self.cfg.PALETTE
        W, H = self.W, self.H
        for x, y, kind, sz in [
            (18, 20, "star", 7), (W - 30, 28, "star", 5),
            (W - 18, H - 28, "heart", 9), (22, H - 22, "heart", 7),
            (W // 2, 12, "star", 6),
        ]:
            self._decorations.append(
                Decoration(self.canvas, x, y, kind=kind, size=sz, color=pal["default_accent"]))


    def _apply_state(self, state):
        self._current_state = state
        pal = self.cfg.PALETTE
        C = self.canvas
        W, H = self.W, self.H

        key = state if f"{state}_bg" in pal else "default"
        bg  = pal[f"{key}_bg"]
        fg  = pal[f"{key}_fg"]
        acc = pal[f"{key}_accent"]

        icons = {"sunny": "☀️", "rain": "🌧️", "storm": "⛈️",
                 "snow": "❄️", "cloudy": "☁️", "uv": "🌞", "default": "🌤️"}

        self.configure(bg=bg)
        C.configure(bg=bg)
        C.itemconfig(self._bg_rect, fill=bg, outline=acc)

        for item in [self._temp_id, self._desc_id, self._detail_id,
                     self._city_id, self._close_btn, self._gear_btn]:
            C.itemconfig(item, fill=fg)

        C.itemconfig(self._icon_id, text=icons.get(state, "🌤"))

        for rd in self._raindrops:
            C.delete(rd.id)
        self._raindrops.clear()

        for d in self._decorations:
            C.itemconfig(d.id, fill=acc)
            d.color = acc

        if state in ("rain", "storm"):
            for _ in range(18):
                self._raindrops.append(Raindrop(C, W, H, pal["rain_accent"]))


    def _animate(self):
        self._anim_t += 0.04
        t = self._anim_t
        for d in self._decorations:
            d.tick(t)
        for rd in self._raindrops:
            rd.tick()
        if self._current_state == "storm":
            self.canvas.itemconfig(
                self._icon_id, text="⛈️" if int(t * 2) % 2 == 0 else "⚡")
        self.after(40, self._animate)


    def update_weather(self, wd):
        self.after(0, lambda: self._apply_weather(wd))

    def _apply_weather(self, wd):
        unit_sym = "°C" if self.cfg.UNITS == "metric" else "°F"
        self.canvas.itemconfig(self._temp_id,   text=f"{wd.temp:.0f}{unit_sym}")
        self.canvas.itemconfig(self._desc_id,   text=wd.description)
        self.canvas.itemconfig(self._detail_id, text=f"💧{wd.humidity}% 💨{wd.wind_speed_kmh} km/h")
        self.canvas.itemconfig(self._city_id,   text=wd.city)
        self.canvas.itemconfig(self._err_id,    text="")
        if wd.state != self._current_state:
            self._apply_state(wd.state)

    def show_error(self):
        self.after(0, self._show_error_main)

    def _show_error_main(self):
        self.canvas.itemconfig(self._err_id,  text="Sem dados")
        self.canvas.itemconfig(self._temp_id, text="--")

    # Configurações

    def _open_settings(self):
        pal = self.cfg.PALETTE
        bg  = pal["default_bg"]
        fg  = pal["default_fg"]
        acc = pal["default_accent"]
        pnk = pal["close_hover"]

        W, H = 300, 520
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x  = sw - W - self.cfg.MARGIN
        y  = sh - H - self.cfg.WINDOW_HEIGHT - self.cfg.MARGIN - 20

        win = tk.Toplevel(self)
        win.attributes("-topmost", True)
        win.attributes("-alpha", 0.98)
        win.geometry(f"{W}x{H}+{x}+{y}")
        win.configure(bg=bg)
        win.resizable(False, False)
        win.title("")
        win.lift()
        win.focus_force()
        win.grab_set()

        outer = tk.Frame(win, bg=bg, highlightbackground=acc, highlightthickness=2)
        outer.pack(fill="both", expand=True)

        # Barra de título
        title_bar = tk.Frame(outer, bg=acc, height=30)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        title_lbl = tk.Label(title_bar, text="⚙️  configurações  ✦",
                             bg=acc, fg=fg, font=("Lato", 10, "bold"), cursor="fleur")
        title_lbl.pack(side="left", padx=10, pady=5)
        tk.Button(title_bar, text="×", command=win.destroy,
                  bg=acc, fg=fg, relief="flat", font=("Lato", 13, "bold"),
                  activebackground=pnk, bd=0, cursor="hand2", padx=6).pack(side="right")

        def ds(e): win._dx = e.x_root - win.winfo_x(); win._dy = e.y_root - win.winfo_y()
        def dm(e): win.geometry(f"+{e.x_root - win._dx}+{e.y_root - win._dy}")
        title_lbl.bind("<ButtonPress-1>", ds); title_lbl.bind("<B1-Motion>", dm)
        title_bar.bind("<ButtonPress-1>", ds); title_bar.bind("<B1-Motion>", dm)

        body = tk.Frame(outer, bg=bg)
        body.pack(fill="both", expand=True, padx=16, pady=10)

        # Cidade 
        tk.Label(body, text="cidade:", bg=bg, fg=fg,
                 font=("Lato", 9), anchor="w").pack(fill="x")
        city_var = tk.StringVar(value=self.cfg.CITY)
        city_entry = tk.Entry(body, textvariable=city_var, bg=acc, fg=fg,
                              relief="flat", font=("Lato", 11),
                              insertbackground=fg, bd=4)
        city_entry.pack(fill="x", ipady=5)
        city_entry.icursor("end")

        # Unidade 
        tk.Label(body, text="unidade:", bg=bg, fg=fg,
                 font=("Lato", 9), anchor="w").pack(fill="x", pady=(10, 0))
        unit_var = tk.StringVar(value=self.cfg.UNITS)
        rb_frame = tk.Frame(body, bg=bg)
        rb_frame.pack(fill="x")
        for label, val in [("°C  (metric)", "metric"), ("°F  (imperial)", "imperial")]:
            tk.Radiobutton(rb_frame, text=label, variable=unit_var, value=val,
                           bg=bg, fg=fg, selectcolor=acc, activebackground=bg,
                           font=("Lato", 9), bd=0).pack(side="left", padx=(0, 14))

        # Escolha de cor
        tk.Label(body, text="cor de fundo:", bg=bg, fg=fg,
                 font=("Lato", 9), anchor="w").pack(fill="x", pady=(10, 0))

        import math, colorsys
        CW = 200   
        wheel_frame = tk.Frame(body, bg=bg)
        wheel_frame.pack()

        wheel = tk.Canvas(wheel_frame, width=CW, height=CW,
                          bg=bg, highlightthickness=0, bd=0)
        wheel.pack()

        # Círculo cromático
        cx, cy, r = CW // 2, CW // 2, CW // 2 - 4
        for angle in range(0, 360, 2):
            for radius_frac in [i / 50 for i in range(1, 51)]:
                rad   = math.radians(angle)
                h     = angle / 360
                s     = radius_frac
                v     = 1.0
                rgb   = colorsys.hsv_to_rgb(h, s, v)
                color = "#{:02x}{:02x}{:02x}".format(
                    int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
                x1 = cx + (radius_frac * r) * math.cos(rad)
                y1 = cy + (radius_frac * r) * math.sin(rad)
                x2 = cx + ((radius_frac + 0.03) * r) * math.cos(math.radians(angle + 3))
                y2 = cy + ((radius_frac + 0.03) * r) * math.sin(math.radians(angle + 3))
                wheel.create_oval(x1-2, y1-2, x1+2, y1+2, fill=color, outline="")

        # Centro branco 
        for i in range(20, 0, -1):
            frac  = i / 20
            gray  = int(frac * 255)
            color = "#{:02x}{:02x}{:02x}".format(gray, gray, gray)
            wheel.create_oval(cx - i, cy - i, cx + i, cy + i,
                              fill=color, outline="")

        # Cor selecionada
        selected_color = [self.cfg.PALETTE["default_bg"]]
        cursor_id = [None]

        preview_row = tk.Frame(body, bg=bg)
        preview_row.pack(fill="x", pady=(6, 0))
        preview_box = tk.Frame(preview_row, bg=selected_color[0],
                               width=32, height=32,
                               highlightbackground=fg, highlightthickness=1)
        preview_box.pack(side="left", padx=(0, 8))
        preview_lbl = tk.Label(preview_row, text=selected_color[0],
                               bg=bg, fg=fg, font=("Lato", 9))
        preview_lbl.pack(side="left")

        def on_wheel_click(e):
            dx = e.x - cx
            dy = e.y - cy
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > r or dist < 4:
                return
            angle     = math.degrees(math.atan2(dy, dx)) % 360
            sat       = min(dist / r, 1.0)
            rgb       = colorsys.hsv_to_rgb(angle / 360, sat, 1.0)
            hex_color = "#{:02x}{:02x}{:02x}".format(
                int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
            selected_color[0] = hex_color
            preview_box.configure(bg=hex_color)
            preview_lbl.configure(text=hex_color)
            # Move cursor
            if cursor_id[0]:
                wheel.delete(cursor_id[0])
            cursor_id[0] = wheel.create_oval(
                e.x - 6, e.y - 6, e.x + 6, e.y + 6,
                outline="white", width=2)

        wheel.bind("<Button-1>",        on_wheel_click)
        wheel.bind("<B1-Motion>",       on_wheel_click)

        # Cores rápidas
        pastel_row = tk.Frame(body, bg=bg)
        pastel_row.pack(fill="x", pady=(4, 0))
        pastels = ["#FFE4F0","#B8E8FF","#DDE8F5","#FFF3B0","#E8D0F5","#EEF4FF","#FFE8D0","#D0F5E8"]
        for p in pastels:
            def make_pick(c):
                def _pick():
                    selected_color[0] = c
                    preview_box.configure(bg=c)
                    preview_lbl.configure(text=c)
                return _pick
            tk.Button(pastel_row, bg=p, width=2, height=1, relief="flat",
                      cursor="hand2", command=make_pick(p),
                      highlightbackground=fg, highlightthickness=1
                      ).pack(side="left", padx=1)

        # Feedback 
        msg_var = tk.StringVar(value="")
        tk.Label(body, textvariable=msg_var, bg=bg, fg=fg,
                 font=("Lato", 8)).pack(pady=(6, 0))

        # Botões 
        def save():
            new_city  = city_var.get().strip()
            new_units = unit_var.get()
            new_color = selected_color[0]
            if not new_city:
                msg_var.set("Digite uma cidade!")
                return
            base = Path(__file__).parent.parent
            (base / ".env").write_text(
                f"CITY={new_city}\nUNITS={new_units}\nDEFAULT_BG={new_color}\n",
                encoding="utf-8")
            self.cfg.CITY  = new_city
            self.cfg.UNITS = new_units
            # Aplica cor imediatamente em todos os estados
            self.cfg.PALETTE["default_bg"]      = new_color
            self.cfg.PALETTE["default_accent"]  = new_color
            self.canvas.configure(bg=new_color)
            self.configure(bg=new_color)
            self.canvas.itemconfig(self._bg_rect, fill=new_color)
            msg_var.set("Salvo!")
            win.after(900, win.destroy)
            if self._cb:
                import threading
                threading.Thread(target=self._cb, daemon=True).start()

        btn_row = tk.Frame(body, bg=bg)
        btn_row.pack(fill="x", pady=(4, 0))
        tk.Button(btn_row, text="cancelar", command=win.destroy,
                  bg=acc, fg=fg, relief="flat", font=("Lato", 9),
                  activebackground=acc, bd=0, cursor="hand2", height=2
                  ).pack(side="left", expand=True, fill="x", padx=(0, 6))
        tk.Button(btn_row, text="salvar ♥", command=save,
                  bg=pnk, fg=fg, relief="flat", font=("Lato", 9, "bold"),
                  activebackground=pnk, bd=0, cursor="hand2", height=2
                  ).pack(side="left", expand=True, fill="x")

        win.after(100, city_entry.focus_set)


    # PopUp de alerta

    def show_alert_popup(self, alert):
        self.after(0, lambda: self._popup(alert))

    def _popup(self, alert):
        pal = self.cfg.PALETTE
        level_colors = {
            "info":    (pal["default_bg"], pal["default_fg"]),
            "warning": (pal["uv_bg"],      pal["uv_fg"]),
            "danger":  (pal["storm_bg"],   pal["storm_fg"]),
        }
        bg, fg = level_colors.get(alert.level, level_colors["info"])
        accent = (pal["storm_accent"]   if alert.level == "danger"
                  else pal["uv_accent"] if alert.level == "warning"
                  else pal["default_accent"])

        pop = tk.Toplevel(self)
        pop.overrideredirect(True)
        pop.attributes("-topmost", True)
        pop.attributes("-alpha", 0.97)

        W, H = 280, 120
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        pop.geometry(f"{W}x{H}+{sw - W - self.cfg.MARGIN}+{sh - H - self.cfg.WINDOW_HEIGHT - self.cfg.MARGIN - 60}")
        pop.configure(bg=bg)

        c = tk.Canvas(pop, width=W, height=H, bg=bg, highlightthickness=0, bd=0)
        c.pack(fill="both", expand=True)
        c.create_rectangle(3, 3, W - 3, H - 3, fill=bg, outline=accent, width=2)
        c.create_text(W // 2, 28, text=alert.title,
                      font=("Lato", 10, "bold"), fill=fg, width=W - 20)
        c.create_text(W // 2, 65, text=alert.message,
                      font=("Lato", 9), fill=fg, width=W - 24, justify="center")

        btn   = c.create_rectangle(W // 2 - 30, H - 26, W // 2 + 30, H - 8,
                                   fill=accent, outline="")
        btn_t = c.create_text(W // 2, H - 17, text="ok! ♥",
                              font=("Lato", 8, "bold"), fill=fg)

        def close_pop(_=None): pop.destroy()
        c.tag_bind(btn,   "<Button-1>", close_pop)
        c.tag_bind(btn_t, "<Button-1>", close_pop)
        pop.after(12_000, close_pop)


    def _drag_start(self, event):
        self._drag_x = event.x_root - self.winfo_x()
        self._drag_y = event.y_root - self.winfo_y()

    def _drag_motion(self, event):
        self.geometry(f"+{event.x_root - self._drag_x}+{event.y_root - self._drag_y}")

    def set_update_callback(self, cb: Callable):
        self._cb = cb

    def _schedule_update(self):
        import threading
        if self._cb:
            threading.Thread(target=self._cb, daemon=True).start()
        self.after(self.cfg.UPDATE_INTERVAL_MS, self._schedule_update)