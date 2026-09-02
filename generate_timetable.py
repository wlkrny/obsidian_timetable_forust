#!/usr/bin/env python3
"""Generate an Obsidian weekly timetable from an iCalendar (.ics) file.

Usage:
    python3 generate_timetable.py timetable.ics
    python3 generate_timetable.py timetable.ics -o My Timetable.md

The generated Markdown file only requires the Dataview plugin in Obsidian.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


PALETTE = [
    "#7c3aed",
    "#0891b2",
    "#d97706",
    "#059669",
    "#dc2626",
    "#2563eb",
    "#be185d",
    "#65a30d",
]


DATAVIEW_TEMPLATE = r'''---
tags:
  - timetable
  - dataviewjs
---

# Weekly Timetable

```dataviewjs
/*
 * This block was generated from an iCalendar file.
 * Day: 0 = Monday ... 6 = Sunday
 * Click a class block to create or open its class note.
 */

const timetableEvents = __EVENTS__;
const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const TIME_ZONE = "__TIME_ZONE__";
const START_HOUR = __START_HOUR__;
const END_HOUR = __END_HOUR__;
const ROW_HEIGHT = 44;
const MINUTES_PER_ROW = 30;
const PX_PER_MINUTE = ROW_HEIGHT / MINUTES_PER_ROW;
const totalHeight = (END_HOUR - START_HOUR) * 60 * PX_PER_MINUTE;
const root = dv.container;

if (window.__weeklyTimetableTimer) clearInterval(window.__weeklyTimetableTimer);
root.innerHTML = "";

const style = document.createElement("style");
style.textContent = `
  .weekly-timetable {
    --time-width: 58px;
    --day-width: minmax(110px, 1fr);
    --line: color-mix(in srgb, var(--text-muted) 22%, transparent);
    --grid-line: color-mix(in srgb, var(--text-muted) 13%, transparent);
    margin: 0.75rem 0 1rem;
    font-family: var(--font-interface);
  }
  .weekly-timetable-scroll {
    overflow-x: auto;
    padding-bottom: 4px;
  }
  .weekly-timetable-inner {
    width: 100%;
    min-width: 900px;
  }
  .weekly-timetable-header,
  .weekly-timetable-body {
    display: grid;
    grid-template-columns: var(--time-width) repeat(7, var(--day-width));
  }
  .weekly-timetable-header {
    position: sticky;
    top: 0;
    z-index: 5;
    background: var(--background-primary);
    border-bottom: 1px solid var(--line);
  }
  .weekly-timetable-header > div {
    min-height: 47px;
    padding: 7px 5px 6px;
    text-align: center;
    font-size: 0.78rem;
    color: var(--text-muted);
    border-left: 1px solid var(--grid-line);
  }
  .weekly-timetable-header > div:first-child { border-left: 0; }
  .weekly-timetable-header .is-today {
    color: var(--text-normal);
    font-weight: 700;
    background: color-mix(in srgb, var(--interactive-accent) 9%, transparent);
  }
  .weekly-timetable-header small {
    display: block;
    margin-top: 2px;
    font-size: 0.68rem;
    font-weight: 400;
  }
  .weekly-timetable-body {
    position: relative;
    height: __TOTAL_HEIGHT__px;
    border-bottom: 1px solid var(--line);
  }
  .weekly-timetable-time {
    position: relative;
    color: var(--text-muted);
    font-size: 0.67rem;
    text-align: right;
  }
  .weekly-timetable-time-label {
    position: absolute;
    right: 7px;
    transform: translateY(-50%);
    white-space: nowrap;
  }
  .weekly-timetable-day {
    position: relative;
    border-left: 1px solid var(--grid-line);
    background-image: repeating-linear-gradient(
      to bottom,
      transparent 0,
      transparent __GRID_LINE_OFFSET__px,
      var(--grid-line) __GRID_LINE_OFFSET__px,
      var(--grid-line) __ROW_HEIGHT__px
    );
  }
  .weekly-timetable-day:nth-child(7),
  .weekly-timetable-day:nth-child(8) {
    background-color: color-mix(in srgb, var(--background-secondary) 34%, transparent);
  }
  .weekly-timetable-event {
    position: absolute;
    cursor: pointer;
    user-select: none;
    left: 4px;
    right: 4px;
    overflow: hidden;
    padding: 5px 6px;
    border-left: 4px solid var(--event-color);
    border-radius: 5px;
    background: color-mix(in srgb, var(--event-color) 16%, var(--background-primary));
    box-shadow: 0 1px 2px color-mix(in srgb, var(--text-normal) 12%, transparent);
    color: var(--text-normal);
    line-height: 1.18;
    font-size: 0.72rem;
  }
  .weekly-timetable-event:hover {
    filter: brightness(0.97);
  }
  .weekly-timetable-event strong {
    display: block;
    font-size: 0.77rem;
  }
  .weekly-timetable-event span {
    display: block;
    margin-top: 2px;
    color: var(--text-muted);
    font-size: 0.66rem;
  }
  .weekly-timetable-now-line {
    position: absolute;
    left: var(--time-width);
    right: 0;
    z-index: 4;
    height: 2px;
    background: #e06c75;
    box-shadow: 0 0 0 1px color-mix(in srgb, #e06c75 18%, transparent);
    pointer-events: none;
  }
  .weekly-timetable-now-dot {
    position: absolute;
    left: -4px;
    top: -3px;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #e06c75;
  }
  .weekly-timetable-now-label {
    position: absolute;
    left: 4px;
    top: -10px;
    padding: 1px 3px;
    border-radius: 3px;
    background: #e06c75;
    color: white;
    font-size: 0.61rem;
    line-height: 1.2;
    white-space: nowrap;
  }
`;
root.appendChild(style);

function getCurrentTime() {
  const parts = Object.fromEntries(
    new Intl.DateTimeFormat("en-CA", {
      timeZone: TIME_ZONE,
      year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", hour12: false,
    }).formatToParts(new Date()).map(({ type, value }) => [type, value])
  );
  const hour = Number(parts.hour) % 24;
  const date = new Date(Date.UTC(Number(parts.year), Number(parts.month) - 1, Number(parts.day)));
  const day = (date.getUTCDay() + 6) % 7;
  return {
    date,
    day,
    minutes: hour * 60 + Number(parts.minute),
    time: `${String(hour).padStart(2, "0")}:${parts.minute}`,
  };
}

function formatTime(time) {
  const [hour, minute] = time.split(":").map(Number);
  return `${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`;
}

function minutes(time) {
  const [hour, minute] = time.split(":").map(Number);
  return hour * 60 + minute;
}

function weekDate(baseDate, offset) {
  const date = new Date(baseDate);
  date.setUTCDate(date.getUTCDate() - ((date.getUTCDay() + 6) % 7) + offset);
  return `${String(date.getUTCMonth() + 1).padStart(2, "0")}/${String(date.getUTCDate()).padStart(2, "0")}`;
}

function isoDate(baseDate, offset) {
  const date = new Date(baseDate);
  date.setUTCDate(date.getUTCDate() - ((date.getUTCDay() + 6) % 7) + offset);
  return date.toISOString().slice(0, 10);
}

const pendingNotePaths = new Set();

async function openClassNote(event) {
  const current = getCurrentTime();
  const date = isoDate(current.date, event.day);
  const title = `${event.code} - ${date}`;
  const courseFolder = event.code.replace(/[^A-Za-z0-9]+/g, "_").replace(/^_|_$/g, "");
  const path = `${courseFolder}/${title}.md`;

  if (pendingNotePaths.has(path)) return;
  pendingNotePaths.add(path);

  try {
    let file = app.vault.getAbstractFileByPath(path);
    if (!file) {
      if (!app.vault.getAbstractFileByPath(courseFolder)) {
        try {
          await app.vault.createFolder(courseFolder);
        } catch (error) {
          if (!app.vault.getAbstractFileByPath(courseFolder)) throw error;
        }
      }

      const content = `---
course: "${event.code}"
date: ${date}
---

# ${title}

`;
      file = await app.vault.create(path, content);
      new Notice(`Created note: ${title}`);
    } else {
      new Notice(`Opened existing note: ${title}`);
    }

    await app.workspace.getLeaf(true).openFile(file);
  } catch (error) {
    console.error("Unable to create class note", error);
    new Notice(`Failed to create note: ${error.message}`);
  } finally {
    pendingNotePaths.delete(path);
  }
}

function render() {
  const now = getCurrentTime();
  const dateLabels = days.map((_, index) => weekDate(now.date, index));

  const timetable = root.createDiv({ cls: "weekly-timetable" });
  const scroll = timetable.createDiv({ cls: "weekly-timetable-scroll" });
  const inner = scroll.createDiv({ cls: "weekly-timetable-inner" });
  const header = inner.createDiv({ cls: "weekly-timetable-header" });
  const headerCells = [];
  header.createDiv();
  days.forEach((day, index) => {
    const cell = header.createDiv({ text: day });
    if (index === now.day) cell.addClass("is-today");
    cell.createEl("small", { text: dateLabels[index] });
    headerCells.push(cell);
  });

  const body = inner.createDiv({ cls: "weekly-timetable-body" });
  const timeColumn = body.createDiv({ cls: "weekly-timetable-time" });
  for (let hour = START_HOUR; hour <= END_HOUR; hour++) {
    const label = timeColumn.createDiv({ cls: "weekly-timetable-time-label", text: `${String(hour).padStart(2, "0")}:00` });
    label.style.top = `${(hour - START_HOUR) * 60 * PX_PER_MINUTE}px`;
    if (hour === START_HOUR) label.style.transform = "translateY(0)";
    if (hour === END_HOUR) label.style.transform = "translateY(-100%)";
  }

  const dayColumns = days.map(() => body.createDiv({ cls: "weekly-timetable-day" }));
  timetableEvents.forEach((event) => {
    const block = dayColumns[event.day].createDiv({ cls: "weekly-timetable-event" });
    const start = minutes(event.start);
    const end = minutes(event.end);
    block.style.setProperty("--event-color", event.color);
    block.style.top = `${(start - START_HOUR * 60) * PX_PER_MINUTE + 2}px`;
    block.style.height = `${(end - start) * PX_PER_MINUTE - 4}px`;
    block.setAttribute("aria-label", `${event.code} ${event.section}, ${event.start}–${event.end}, ${event.room}`);
    block.setAttribute("title", "Click to create or open the class note");
    block.addEventListener("click", () => void openClassNote(event));
    block.createEl("strong", { text: `${event.code}${event.section ? ` · ${event.section}` : ""}` });
    block.createEl("span", { text: `${formatTime(event.start)}–${formatTime(event.end)}` });
    if (event.room) block.createEl("span", { text: event.room });
  });

  const nowLine = body.createDiv({ cls: "weekly-timetable-now-line" });
  nowLine.createDiv({ cls: "weekly-timetable-now-dot" });
  const nowLabel = nowLine.createDiv({ cls: "weekly-timetable-now-label" });

  function updateNowLine() {
    const current = getCurrentTime();
    const visible = current.minutes >= START_HOUR * 60 && current.minutes <= END_HOUR * 60;
    nowLine.style.display = visible ? "block" : "none";
    nowLine.style.top = `${(current.minutes - START_HOUR * 60) * PX_PER_MINUTE}px`;
    nowLabel.setText(current.time);

    days.forEach((_, index) => {
      const cell = headerCells[index];
      const dateLabel = cell.querySelector("small");
      if (dateLabel) dateLabel.textContent = weekDate(current.date, index);
      cell.classList.toggle("is-today", index === current.day);
    });
  }

  updateNowLine();
  window.__weeklyTimetableTimer = setInterval(updateNowLine, 30_000);
}

render();
```
'''


def unfold_ics(text: str) -> list[str]:
    """Unfold RFC 5545 continuation lines."""
    lines: list[str] = []
    for raw_line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if raw_line.startswith((" ", "\t")) and lines:
            lines[-1] += raw_line[1:]
        else:
            lines.append(raw_line)
    return lines


def parse_property(line: str) -> tuple[str, dict[str, str], str] | None:
    if ":" not in line:
        return None
    left, value = line.split(":", 1)
    parts = left.split(";")
    name = parts[0].upper()
    params: dict[str, str] = {}
    for item in parts[1:]:
        if "=" in item:
            key, parameter_value = item.split("=", 1)
            params[key.upper()] = parameter_value
    return name, params, value


def unescape_ics(value: str) -> str:
    return (
        value.replace("\\n", "\n")
        .replace("\\N", "\n")
        .replace("\\,", ",")
        .replace("\\;", ";")
        .replace("\\\\", "\\")
    ).strip()


def parse_datetime(value: str, params: dict[str, str], time_zone: str) -> datetime | None:
    value = value.strip()
    if params.get("VALUE", "").upper() == "DATE" or len(value) == 8:
        return None

    formats = ["%Y%m%dT%H%M%S", "%Y%m%dT%H%M"]
    is_utc = value.endswith("Z")
    if is_utc:
        value = value[:-1]

    parsed = None
    for fmt in formats:
        try:
            parsed = datetime.strptime(value, fmt)
            break
        except ValueError:
            continue
    if parsed is None:
        return None

    if is_utc:
        try:
            return parsed.replace(tzinfo=timezone.utc).astimezone(ZoneInfo(time_zone)).replace(tzinfo=None)
        except Exception:
            return parsed
    return parsed


def get_first(properties: dict[str, list[tuple[dict[str, str], str]]], name: str) -> tuple[dict[str, str], str] | None:
    values = properties.get(name, [])
    return values[0] if values else None


def read_events(path: Path, time_zone: str) -> tuple[list[dict[str, object]], str]:
    lines = unfold_ics(path.read_text(encoding="utf-8-sig"))
    calendar_properties: dict[str, list[tuple[dict[str, str], str]]] = {}
    raw_events: list[dict[str, list[tuple[dict[str, str], str]]]] = []
    current: dict[str, list[tuple[dict[str, str], str]]] | None = None

    for line in lines:
        parsed = parse_property(line)
        if not parsed:
            continue
        name, params, value = parsed
        if name == "BEGIN" and value.upper() == "VEVENT":
            current = {}
        elif name == "END" and value.upper() == "VEVENT":
            if current is not None:
                raw_events.append(current)
            current = None
        elif current is not None:
            current.setdefault(name, []).append((params, value))
        elif name == "X-WR-TIMEZONE":
            calendar_properties.setdefault(name, []).append((params, value))

    if not raw_events:
        raise ValueError(f"No VEVENT entries found in {path}")

    calendar_time_zone = get_first(calendar_properties, "X-WR-TIMEZONE")
    if calendar_time_zone and time_zone == "Asia/Hong_Kong":
        time_zone = unescape_ics(calendar_time_zone[1]) or time_zone

    events: list[dict[str, object]] = []
    seen: set[tuple[object, ...]] = set()
    course_order: list[str] = []

    for properties in raw_events:
        start_property = get_first(properties, "DTSTART")
        end_property = get_first(properties, "DTEND")
        summary_property = get_first(properties, "SUMMARY")
        if not start_property or not end_property or not summary_property:
            continue

        start = parse_datetime(start_property[1], start_property[0], time_zone)
        end = parse_datetime(end_property[1], end_property[0], time_zone)
        if not start or not end or end <= start:
            continue

        summary = unescape_ics(summary_property[1])
        location_property = get_first(properties, "LOCATION")
        room = unescape_ics(location_property[1]) if location_property else ""
        match = re.match(r"^(.*?)\s*\(([^()]*)\)\s*$", summary)
        if match:
            code = match.group(1).strip()
            section = match.group(2).strip()
        else:
            code = summary.strip()
            section = ""

        key = (start.weekday(), start.strftime("%H:%M"), end.strftime("%H:%M"), code, section, room)
        if key in seen:
            continue
        seen.add(key)
        if code not in course_order:
            course_order.append(code)
        events.append(
            {
                "day": start.weekday(),
                "start": start.strftime("%H:%M"),
                "end": end.strftime("%H:%M"),
                "code": code,
                "section": section,
                "room": room,
            }
        )

    if not events:
        raise ValueError("No timed events could be parsed from the calendar")

    colors = {course: PALETTE[index % len(PALETTE)] for index, course in enumerate(course_order)}
    for event in events:
        event["color"] = colors[event["code"]]
    events.sort(key=lambda event: (event["day"], event["start"], event["end"], event["code"]))
    return events, time_zone


def generate_markdown(events: list[dict[str, object]], time_zone: str) -> str:
    earliest = min(int(str(event["start"]).split(":")[0]) for event in events)
    latest_end = max(
        int(str(event["end"]).split(":")[0]) + (1 if str(event["end"]).split(":")[1] != "00" else 0)
        for event in events
    )
    start_hour = max(0, earliest - 1)
    end_hour = min(24, latest_end + 1)
    if end_hour <= start_hour:
        end_hour = min(24, start_hour + 1)

    row_height = 44
    total_height = (end_hour - start_hour) * 2 * row_height
    grid_line_offset = row_height - 1
    replacements = {
        "__EVENTS__": json.dumps(events, ensure_ascii=False, indent=2),
        "__TIME_ZONE__": time_zone.replace('\\', '\\\\').replace('"', '\\"'),
        "__START_HOUR__": str(start_hour),
        "__END_HOUR__": str(end_hour),
        "__TOTAL_HEIGHT__": str(total_height),
        "__GRID_LINE_OFFSET__": str(grid_line_offset),
        "__ROW_HEIGHT__": str(row_height),
    }
    output = DATAVIEW_TEMPLATE
    for placeholder, value in replacements.items():
        output = output.replace(placeholder, value)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an Obsidian DataviewJS timetable from an .ics file.")
    parser.add_argument("ics_file", type=Path, help="Input iCalendar file")
    parser.add_argument("-o", "--output", type=Path, default=Path("Weekly Timetable.md"), help="Output Markdown file")
    parser.add_argument("--timezone", default="Asia/Hong_Kong", help="Timezone used for UTC calendar values")
    args = parser.parse_args()

    if not args.ics_file.is_file():
        parser.error(f"Input file does not exist: {args.ics_file}")

    events, time_zone = read_events(args.ics_file, args.timezone)
    markdown = generate_markdown(events, time_zone)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    print(f"Generated {args.output} from {args.ics_file} ({len(events)} class blocks)")


if __name__ == "__main__":
    main()
