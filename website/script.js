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

function applyLang(lang) {
  currentLang = lang;
  const t = LANG[lang];

  // All elements that should fade
  const fadeEls = document.querySelectorAll(".lang-fade");

  // Fade out
  fadeEls.forEach(el => el.classList.add("hidden"));

  // After fade-out, swap text, then fade back in
  setTimeout(() => {
    document.getElementById("hero-title").textContent = t.hero_title;
    document.getElementById("hero-sub").textContent = t.hero_sub;
    document.getElementById("btn-invite").textContent = t.invite;
    document.getElementById("btn-commands").textContent = t.commands;

    document.getElementById("features-title").textContent = t.features_title;
    document.getElementById("feat-personality-title").textContent = t.feat_personality_title;
    document.getElementById("feat-personality-text").textContent = t.feat_personality_text;
    document.getElementById("feat-music-title").textContent = t.feat_music_title;
    document.getElementById("feat-music-text").textContent = t.feat_music_text;
    document.getElementById("feat-level-title").textContent = t.feat_level_title;
    document.getElementById("feat-level-text").textContent = t.feat_level_text;
    document.getElementById("feat-fun-title").textContent = t.feat_fun_title;
    document.getElementById("feat-fun-text").textContent = t.feat_fun_text;

    document.getElementById("personality-title").textContent = t.personality_title;
    document.getElementById("personality-text").textContent = t.personality_text;
    document.getElementById("bilingual-title").textContent = t.bilingual_title;

    document.getElementById("footer-text").textContent = t.footer_text;

    // Fade back in
    fadeEls.forEach(el => el.classList.remove("hidden"));
  }, 350); // matches CSS transition

  // Update toggle buttons
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

document.addEventListener("DOMContentLoaded", () => {
  setupLangToggle();
  setupPageTransitions();
  applyLang(detectLang());
});