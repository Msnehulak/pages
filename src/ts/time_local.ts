// Najde všechna <time datetime="..."> a převede jejich text do časové zóny uživatele.

type TimeFormat = "datetime" | "date" | "time";

const FORMATS: Record<TimeFormat, Intl.DateTimeFormatOptions> = {
  datetime: {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    timeZoneName: "short",
  },
  date: {
    year: "numeric",
    month: "short",
    day: "numeric",
  },
  time: {
    hour: "2-digit",
    minute: "2-digit",
    timeZoneName: "short",
  },
};

function parseFormat(value: string | null): TimeFormat {
  return value === "date" || value === "time" ? value : "datetime";
}

function convert(el: HTMLTimeElement, formatter: Intl.DateTimeFormat): void {
  const raw = el.getAttribute("datetime");
  if (!raw) return;

  const date = new Date(raw);
  if (Number.isNaN(date.getTime())) {
    console.warn(`[time_local] Neplatné datum: "${raw}"`, el);
    return;
  }

  // Původní UTC hodnotu si schováme do tooltipu (a do data atributu pro debugging)
  el.title = raw;
  el.dataset.utc = raw;

  el.textContent = formatter.format(date);
  el.dataset.localized = "true";
}

document.addEventListener("DOMContentLoaded", () => {
  const nodes = document.querySelectorAll<HTMLTimeElement>("time[datetime]");
  if (nodes.length === 0) return;

  const lang = document.documentElement.lang || "en";
  const formatters = new Map<TimeFormat, Intl.DateTimeFormat>();

  const getFormatter = (fmt: TimeFormat): Intl.DateTimeFormat => {
    let f = formatters.get(fmt);
    if (!f) {
      f = new Intl.DateTimeFormat(lang, FORMATS[fmt]);
      formatters.set(fmt, f);
    }
    return f;
  };

  nodes.forEach((el) => {
    // Přeskočit už převedené (např. pokud skript běží víckrát)
    if (el.dataset.localized === "true") return;

    const fmt = parseFormat(el.dataset.format ?? null);
    convert(el, getFormatter(fmt));
  });
});
