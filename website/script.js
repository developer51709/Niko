const LANG = {
  en: {
    hero_title: "your cozy café‑vibe discord companion",
    hero_sub: "warm, friendly, bilingual — niko brings soft vibes to your server.",
    invite: "invite niko",
    commands: "view commands",
    features_title: "what niko can do",
    feat_personality_title: "café personality system",
    feat_personality_text: "bilingual, cozy responses with personality modes like normal and café — future‑ready for more.",
    feat_music_title: "music system",
    feat_music_text: "lavalink‑powered music with café‑style messages in english and german.",
    feat_level_title: "leveling & stats",
    feat_level_text: "cozy café‑themed leveling embeds with bilingual support.",
    feat_fun_title: "fun & vibes",
    feat_fun_text: "cute animals, memes, tic‑tac‑toe, uwu‑lock and more — all personality‑aware.",
    personality_title: "personality modes",
    personality_text: "niko can speak plainly or like a soft café barista — and is ready for future moods.",
    bilingual_title: "bilingual by design",
    footer_text: "made with love by nyxen ☕"
  },
  de: {
    hero_title: "dein gemütlicher café‑discord‑begleiter",
    hero_sub: "warm, freundlich, zweisprachig — niko bringt cozy vibes auf deinen server.",
    invite: "niko einladen",
    commands: "befehle ansehen",
    features_title: "was niko kann",
    feat_personality_title: "café‑persönlichkeitssystem",
    feat_personality_text: "zweisprachige, gemütliche antworten mit modi wie normal und café — bereit für mehr.",
    feat_music_title: "musiksystem",
    feat_music_text: "lavalink‑musik mit café‑stil nachrichten auf deutsch und englisch.",
    feat_level_title: "level & statistiken",
    feat_level_text: "gemütliche café‑level‑embeds mit zweisprachiger unterstützung.",
    feat_fun_title: "spaß & vibes",
    feat_fun_text: "süße tiere, memes, tic‑tac‑toe, uwu‑lock und mehr — alles persönlichkeitsbewusst.",
    personality_title: "persönlichkeitsmodi",
    personality_text: "niko kann neutral sprechen oder wie ein sanfter barista — und ist bereit für weitere moods.",
    bilingual_title: "von grund auf zweisprachig",
    footer_text: "mit liebe gemacht von nyxen ☕"
  }
};

let currentLang = "en";

function safeSet(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function applyLang(lang) {
  currentLang = lang;
  const t = LANG[lang];

  const fadeEls = document.querySelectorAll(".lang-fade");
  fadeEls.forEach(el => el.classList.add("hidden"));

  setTimeout(() => {
    safeSet("hero-title", t.hero_title);
    safeSet("hero-sub", t.hero_sub);
    safeSet("btn-invite", t.invite);
    safeSet("btn-commands", t.commands);

    safeSet("features-title", t.features_title);
    safeSet("feat-personality-title", t.feat_personality_title);
    safeSet("feat-personality-text", t.feat_personality_text);
    safeSet("feat-music-title", t.feat_music_title);
    safeSet("feat-music-text", t.feat_music_text);
    safeSet("feat-level-title", t.feat_level_title);
    safeSet("feat-level-text", t.feat_level_text);
    safeSet("feat-fun-title", t.feat_fun_title);
    safeSet("feat-fun-text", t.feat_fun_text);

    safeSet("personality-title", t.personality_title);
    safeSet("personality-text", t.personality_text);
    safeSet("bilingual-title", t.bilingual_title);

    safeSet("footer-text", t.footer_text);

    fadeEls.forEach(el => el.classList.remove("hidden"));
  }, 350);

  document.querySelectorAll(".lang-toggle").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.lang === lang);
  });

  localStorage.setItem("niko_lang", lang);
}

function detectLang() {
  const stored = localStorage.getItem("niko_lang");
  if (stored && LANG[stored]) return stored;
  const browser = navigator.language || navigator.userLanguage || "en";
  return browser.toLowerCase().startsWith("de") ? "de" : "en";
}

function setupLangToggle() {
  document.querySelectorAll(".lang-toggle").forEach(btn => {
    btn.addEventListener("click", () => {
      applyLang(btn.dataset.lang);
    });
  });
}

/* smooth page transitions for internal links */

function setupPageTransitions() {
  const links = document.querySelectorAll("a.link--transition");
  links.forEach(link => {
    link.addEventListener("click", e => {
      const href = link.getAttribute("href");
      if (!href || href.startsWith("http")) return;
      e.preventDefault();
      const page = document.querySelector(".page");
      page.classList.add("page--fade-out");
      setTimeout(() => {
        window.location.href = href;
      }, 450);
    });
  });
}

// Smooth scrolling
function smoothScrollTo(targetY, duration = 600) {
  const startY = window.scrollY;
  const diff = targetY - startY;
  let start;

  function step(timestamp) {
    if (!start) start = timestamp;
    const time = timestamp - start;
    const percent = Math.min(time / duration, 1);

    // soft cubic easing
    const eased = percent < 0.5
      ? 4 * percent * percent * percent
      : 1 - Math.pow(-2 * percent + 2, 3) / 2;

    window.scrollTo(0, startY + diff * eased);

    if (time < duration) requestAnimationFrame(step);
  }

  requestAnimationFrame(step);
}


document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener("click", e => {
    const target = document.querySelector(link.getAttribute("href"));
    if (!target) return;

    e.preventDefault();
    const y = target.getBoundingClientRect().top + window.scrollY - 20;
    smoothScrollTo(y, 700);
  });
});

document.addEventListener("DOMContentLoaded", () => {
  setupLangToggle();
  setupPageTransitions();
  applyLang(detectLang());
});