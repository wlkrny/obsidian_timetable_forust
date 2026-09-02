---
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

const timetableEvents = [
  {
    "day": 0,
    "start": "11:30",
    "end": "13:30",
    "code": "ISDN 1001",
    "section": "L1",
    "room": "Multi-function Room, LG4, LIB",
    "color": "#059669"
  },
  {
    "day": 0,
    "start": "13:30",
    "end": "15:00",
    "code": "ACCT 3010",
    "section": "L1",
    "room": "G012, LSK Bldg (199)",
    "color": "#7c3aed"
  },
  {
    "day": 1,
    "start": "10:30",
    "end": "12:30",
    "code": "ISDN 1001",
    "section": "T2",
    "room": "Rm 6580, Lift 27-28 (48)",
    "color": "#059669"
  },
  {
    "day": 2,
    "start": "15:00",
    "end": "18:00",
    "code": "MGMT 1110",
    "section": "L2",
    "room": "Rm 1009, LSK Bldg (80)",
    "color": "#dc2626"
  },
  {
    "day": 2,
    "start": "19:00",
    "end": "22:00",
    "code": "AESF 5210",
    "section": "L1",
    "room": "G002, CYT Bldg (126)",
    "color": "#0891b2"
  },
  {
    "day": 4,
    "start": "09:00",
    "end": "10:30",
    "code": "ACCT 3010",
    "section": "L1",
    "room": "G012, LSK Bldg (199)",
    "color": "#7c3aed"
  },
  {
    "day": 4,
    "start": "19:00",
    "end": "22:00",
    "code": "IBTM 5050",
    "section": "L1",
    "room": "Rm 3, 30/F, Tower 1,Millennity",
    "color": "#d97706"
  }
];
const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const TIME_ZONE = "Asia/Hong_Kong";
const START_HOUR = 8;
const END_HOUR = 23;
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
    height: 1320px;
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
      transparent 43px,
      var(--grid-line) 43px,
      var(--grid-line) 44px
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
