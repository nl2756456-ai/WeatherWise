"""
charts.py

Builds matplotlib Figures for temperature, wind, humidity, and pressure
trends. Returned figures are embedded into the Tkinter UI with
FigureCanvasTkAgg inside ui.py.
"""

import matplotlib
matplotlib.use("Agg")  # renders off-screen; ui.py embeds the canvas itself
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def _style_axes(ax, fg: str, bg: str) -> None:
    ax.set_facecolor(bg)
    ax.tick_params(colors=fg, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(fg)
        spine.set_alpha(0.2)
    ax.grid(color=fg, alpha=0.1)


def temperature_chart(hourly: list[dict], fg: str = "#F5F7FA", bg: str = "#141C2F", accent: str = "#4F8EF7") -> Figure:
    fig = Figure(figsize=(5, 2.2), dpi=100)
    fig.patch.set_facecolor(bg)
    ax = fig.add_subplot(111)
    _style_axes(ax, fg, bg)

    labels = [h["time"].strftime("%H:%M") for h in hourly]
    temps = [h["temp"] for h in hourly]

    ax.plot(labels, temps, color=accent, linewidth=2, marker="o", markersize=3)
    ax.fill_between(range(len(temps)), temps, min(temps) - 1, color=accent, alpha=0.15)
    fig.tight_layout()
    return fig


def rain_chance_chart(hourly: list[dict], fg: str = "#F5F7FA", bg: str = "#141C2F", accent: str = "#00C2FF") -> Figure:
    fig = Figure(figsize=(5, 2.2), dpi=100)
    fig.patch.set_facecolor(bg)
    ax = fig.add_subplot(111)
    _style_axes(ax, fg, bg)

    labels = [h["time"].strftime("%H:%M") for h in hourly]
    pops = [h["pop"] for h in hourly]

    ax.bar(labels, pops, color=accent, alpha=0.7, width=0.5)
    ax.set_ylim(0, 100)
    fig.tight_layout()
    return fig


def wind_chart(hourly: list[dict], fg: str = "#F5F7FA", bg: str = "#141C2F", accent: str = "#4F8EF7") -> Figure:
    fig = Figure(figsize=(5, 2.2), dpi=100)
    fig.patch.set_facecolor(bg)
    ax = fig.add_subplot(111)
    _style_axes(ax, fg, bg)

    labels = [h["time"].strftime("%H:%M") for h in hourly]
    winds = [h["wind_speed"] * 3.6 for h in hourly]  # m/s -> km/h

    ax.plot(labels, winds, color=accent, linewidth=2, marker="o", markersize=3)
    fig.tight_layout()
    return fig
