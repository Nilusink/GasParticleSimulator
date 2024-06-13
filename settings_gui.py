"""
settings_gui.py
24. May 2024

A simple settings panel

Author:
Nilusink
"""
from threading import Thread
import customtkinter as ctk
import socket
import json


class Window(ctk.CTk):
    running = True

    def __init__(self):
        self._box_length = ...

        super().__init__()

        # connection to pygame
        self._pg_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._pg_socket.connect(("127.0.0.1", 24323))
        self._pg_socket.settimeout(1)

        # setup GUI
        self._init_gui()

        self.protocol("WM_DELETE_WINDOW", self.close)

        # start receive thread
        Thread(target=self.receive).start()

    def _init_gui(self) -> None:
        """
        repetitive tkinter stuff
        """
        # gui settings
        self.title("Gas Particle Simulation Settings")

        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure((0, 2), weight=1)

        # heat
        ctk.CTkButton(
            self,
            text="-",
            command=lambda: self.change_speed(.95)
        ).grid(
            row=0,
            rowspan=2,
            column=0,
            sticky="nsew",
            padx=20,
            pady=10
        )
        ctk.CTkLabel(
            self,
            text="Temperature"
        ).grid(row=0, column=1, sticky="nsew")
        self._temperature_label = ctk.CTkLabel(
            self,
            text="0"
        )
        self._temperature_label.grid(row=1, column=1, sticky="nsew")

        ctk.CTkButton(
            self,
            text="+",
            command=lambda: self.change_speed(1.05)
        ).grid(
            row=0,
            rowspan=2,
            column=2,
            sticky="nsew",
            padx=20,
            pady=10
        )

        # number of particles
        ctk.CTkButton(
            self,
            text="-",
            command=lambda: self.change_n_particles(-1)
        ).grid(
            row=2,
            rowspan=2,
            column=0,
            sticky="nsew",
            padx=20,
            pady=10
        )
        ctk.CTkLabel(
            self,
            text="N molecules"
        ).grid(row=2, column=1, sticky="nsew")
        self._n_particles_label = ctk.CTkLabel(
            self,
            text="0"
        )
        self._n_particles_label.grid(row=3, column=1, sticky="nsew")

        ctk.CTkButton(
            self,
            text="+",
            command=lambda: self.change_n_particles(1)
        ).grid(
            row=2,
            rowspan=2,
            column=2,
            sticky="nsew",
            padx=20,
            pady=10
        )

        # length
        ctk.CTkButton(
            self,
            text="-",
            command=lambda: self.change_length(-50)
        ).grid(
            row=4,
            rowspan=2,
            column=0,
            sticky="nsew",
            padx=20,
            pady=10
        )
        ctk.CTkLabel(
            self,
            text="Length"
        ).grid(row=4, column=1, sticky="nsew")
        self._length_label = ctk.CTkLabel(
            self,
            text="0"
        )
        self._length_label.grid(row=5, column=1, sticky="nsew")
        ctk.CTkButton(
            self,
            text="+",
            command=lambda: self.change_length(50)
        ).grid(
            row=4,
            rowspan=2,
            column=2,
            sticky="nsew",
            padx=20,
            pady=10
        )

        # spacer
        self.grid_rowconfigure(6, minsize=50)

        # stats
        ctk.CTkLabel(self, text="Pressure").grid(row=7, column=0)
        self._pressure_label = ctk.CTkLabel(
            self,
            text="0"
        )

        self._pressure_label.grid(row=7, column=1)

    def change_speed(self, factor: float) -> None:
        self._pg_socket.send(json.dumps({"vel": factor}).encode("utf-8"))

    def change_n_particles(self, number: int) -> None:
        self._pg_socket.send(json.dumps({"num": number}).encode("utf-8"))

    def change_length(self, number: int) -> None:
        if self._box_length is ...:
            return

        self._pg_socket.send(
            json.dumps({"len": self._box_length + number}).encode("utf-8")
        )

    def _update_values(self, interval: int) -> None:
        """
        update velocity and number of particles (recursive)
        """
        # only execute if running
        if not self.running:
            return

        # send update request
        self._pg_socket.send(json.dumps(
            {"rstats": 1, "rnum": 1}
        ).encode("utf-8"))
        self.after(interval, lambda: self._update_values(interval))

    def receive(self) -> None:
        """
        receive answers from the server
        """
        # start updating
        self.after(500, lambda: self._update_values(500))

        while self.running:
            try:
                msg = self._pg_socket.recv(1024)
                data = json.loads(msg.decode('utf-8'))

            except (TimeoutError, json.JSONDecodeError):
                continue

            except (ConnectionError, ConnectionResetError):
                self.close()
                return

            # parse request
            for key in data:
                match key:
                    case "num":
                        self._n_particles_label.configure(
                            text=str(data[key])
                        )

                    case "stats":
                        values = data[key]

                        self._pressure_label.configure(
                            text=str(round(values["p"], 2)) + " P"
                        )
                        self._temperature_label.configure(
                            text=str(round(values["t"], 2)) + " °K"
                        )
                        self._length_label.configure(
                            text=str(round(values["l"], 2))
                        )

                        self._box_length = values["l"]

                    case "close":
                        self.close()
                        return

                    case _:
                        print(f"INVALID KEY: \"{key}\"")

    def close(self) -> None:
        """
        close the window
        """
        self.running = False
        self.destroy()
        exit(0)


def main() -> None:
    w = Window()
    w.mainloop()


if __name__ == "__main__":
    main()
