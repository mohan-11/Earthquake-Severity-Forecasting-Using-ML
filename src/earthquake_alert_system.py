import random
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText


class EarthquakeAlertSystem:
    MIN_MAGNITUDE = 1.0
    MAX_MAGNITUDE = 9.5
    SIMULATION_INTERVAL_MS = 3000

    DANGER_THRESHOLD = 6.0
    WARNING_THRESHOLD = 4.0

    COLOR_SAFE = "#009688"
    COLOR_WARNING = "#FF9800"
    COLOR_DANGER = "#D32F2F"
    COLOR_INIT = "#455A64"
    COLOR_PAUSED = "#757575"
    COLOR_LOG_BACKGROUND = "#F5F5F5"
    COLOR_PANEL_BACKGROUND = "#FFFFFF"
    COLOR_TEXT_DARK = "#323232"

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Real-Time Earthquake Alert System")
        self.root.geometry("650x450")
        self.root.minsize(650, 450)

        self.simulation_running = True
        self.locations = [
            "Tokyo, Japan",
            "San Francisco, USA",
            "Jakarta, Indonesia",
            "Mexico City, Mexico",
            "Istanbul, Turkey",
        ]

        self.status_panel: tk.Frame
        self.status_label: tk.Label
        self.log_area: ScrolledText
        self.toggle_button: tk.Button
        self.test_event_box: ttk.Combobox

        self._build_gui()
        self.log("GUI initialized. Starting sensor simulation loop...")
        self.process_earthquake_data(1.5, "System Boot")
        self._schedule_sensor_simulation()

    def _build_gui(self) -> None:
        self.status_panel = tk.Frame(self.root, padx=10, pady=10, bg=self.COLOR_INIT)
        self.status_panel.pack(fill="x")

        self.status_label = tk.Label(
            self.status_panel,
            text="STATUS: INITIALIZING...",
            font=("Segoe UI", 24, "bold"),
            fg="#FFFFFF",
            bg=self.COLOR_INIT,
        )
        self.status_label.pack(pady=10)

        self.log_area = ScrolledText(
            self.root,
            state="normal",
            wrap="word",
            font=("Consolas", 11),
            padx=10,
            pady=10,
            bg=self.COLOR_LOG_BACKGROUND,
            fg=self.COLOR_TEXT_DARK,
            borderwidth=1,
            relief="solid",
        )
        self.log_area.pack(fill="both", expand=True, padx=0, pady=0)
        self.log_area.configure(state="disabled")

        control_panel = tk.Frame(self.root, bg=self.COLOR_PANEL_BACKGROUND, padx=10, pady=10)
        control_panel.pack(fill="x")

        self.toggle_button = tk.Button(
            control_panel,
            text="Pause Simulation",
            command=self.toggle_simulation,
            font=("Segoe UI", 11, "bold"),
            padx=15,
            pady=8,
            fg="#FFFFFF",
            bd=0,
            activeforeground="#FFFFFF",
            cursor="hand2",
        )
        self._style_button(self.toggle_button, "#1976D2")
        self.toggle_button.pack(side="left", padx=(0, 10))

        self.test_event_box = ttk.Combobox(
            control_panel,
            state="readonly",
            values=[
                "Trigger Test Event...",
                "Test Danger (7.2)",
                "Test Warning (4.5)",
                "Test Safe (1.5)",
            ],
            width=24,
            font=("Segoe UI", 11),
        )
        self.test_event_box.current(0)
        self.test_event_box.bind("<<ComboboxSelected>>", self.trigger_test_event)
        self.test_event_box.pack(side="left", padx=(0, 10))

        clear_log_button = tk.Button(
            control_panel,
            text="Clear Log",
            command=self.clear_log,
            font=("Segoe UI", 11, "bold"),
            padx=15,
            pady=8,
            fg="#FFFFFF",
            bd=0,
            activeforeground="#FFFFFF",
            cursor="hand2",
        )
        self._style_button(clear_log_button, "#757575")
        clear_log_button.pack(side="left")

        self.set_alert_status("INITIALIZING", self.COLOR_INIT, "#FFFFFF")

    def _style_button(self, button: tk.Button, background_color: str) -> None:
        button.configure(
            bg=background_color,
            activebackground=background_color,
            highlightthickness=0,
            relief="flat",
        )

    def _schedule_sensor_simulation(self) -> None:
        if self.simulation_running:
            magnitude = self.MIN_MAGNITUDE + (
                self.MAX_MAGNITUDE - self.MIN_MAGNITUDE
            ) * random.random()
            magnitude = round(magnitude, 1)
            location = random.choice(self.locations)
            self.process_earthquake_data(magnitude, location)

        self.root.after(self.SIMULATION_INTERVAL_MS, self._schedule_sensor_simulation)

    def toggle_simulation(self) -> None:
        self.simulation_running = not self.simulation_running

        if self.simulation_running:
            self.toggle_button.configure(text="Pause Simulation")
            self._style_button(self.toggle_button, "#1976D2")
            self.log("Simulation RESUMED.")
        else:
            self.toggle_button.configure(text="Resume Simulation")
            self._style_button(self.toggle_button, "#FF9800")
            self.log("Simulation PAUSED.")
            self.set_alert_status("PAUSED", self.COLOR_PAUSED, "#FFFFFF")

    def trigger_test_event(self, _event: object) -> None:
        selected_index = self.test_event_box.current()
        if selected_index == 0:
            return

        if self.simulation_running:
            self.toggle_simulation()
            self.log("--- Manual Test Event Triggered ---")

        if selected_index == 1:
            self.process_earthquake_data(7.2, "Manual Test Location")
        elif selected_index == 2:
            self.process_earthquake_data(4.5, "Manual Test Location")
        elif selected_index == 3:
            self.process_earthquake_data(1.5, "Manual Test Location")

        self.test_event_box.current(0)

    def process_earthquake_data(self, magnitude: float, location: str) -> None:
        base_message = f"[Sensor Reading] Magnitude {magnitude:.1f} at {location}"

        if magnitude >= self.DANGER_THRESHOLD:
            final_message = f"{base_message} -> DANGER! Major Earthquake Detected!"
            self.set_alert_status("DANGER", self.COLOR_DANGER, "#FFFFFF")
            self.log(final_message)
        elif magnitude >= self.WARNING_THRESHOLD:
            final_message = f"{base_message} -> WARNING! Moderate Earthquake Detected."
            self.set_alert_status("WARNING", self.COLOR_WARNING, "#FFFFFF")
            self.log(final_message)
        else:
            final_message = f"{base_message} -> SAFE. Minor tremor or normal activity."
            self.set_alert_status("SAFE", self.COLOR_SAFE, "#FFFFFF")
            self.log(final_message)

    def set_alert_status(self, status: str, background_color: str, foreground_color: str) -> None:
        self.status_label.configure(text=f"STATUS: {status}", fg=foreground_color, bg=background_color)
        self.status_panel.configure(bg=background_color)

    def log(self, message: str) -> None:
        self.log_area.configure(state="normal")
        self.log_area.insert("end", message + "\n")
        self.log_area.see("end")
        self.log_area.configure(state="disabled")

    def clear_log(self) -> None:
        self.log_area.configure(state="normal")
        self.log_area.delete("1.0", "end")
        self.log_area.configure(state="disabled")

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    app = EarthquakeAlertSystem()
    app.run()


if __name__ == "__main__":
    main()
