/* NextGen Coders Lab — password gate
   How it works:
     1. Student types a password on unlock.html
     2. We SHA-256 it and compare against PASSWORD_HASH below
     3. On match, we save a token to localStorage and let them through
     4. Every lesson page calls requireUnlock() on load; if no token, redirect to unlock.html

   To change the password:
     • In bash:  echo -n "NEW_PASSWORD" | sha256sum
     • Paste the hex value into PASSWORD_HASH below
*/

const PASSWORD_HASH = "a3b35602cb9c68237f6f5401de2cc6bade3f44adb3e6df3fac69681ab24ce522";
const STORAGE_KEY   = "ngc_galaxy_unlock_v1";
const TOKEN_VALUE   = "unlocked";

async function sha256(text) {
  const buf = new TextEncoder().encode(text);
  const hash = await crypto.subtle.digest("SHA-256", buf);
  return Array.from(new Uint8Array(hash))
    .map(b => b.toString(16).padStart(2, "0"))
    .join("");
}

/* Called from unlock.html on form submit */
async function tryUnlock(event) {
  event.preventDefault();
  const input = document.getElementById("pw");
  const errEl = document.getElementById("err");
  errEl.textContent = "";
  const guess = (input.value || "").trim();
  if (!guess) { errEl.textContent = "Type your access password."; return; }

  const hashed = await sha256(guess);
  if (hashed === PASSWORD_HASH) {
    localStorage.setItem(STORAGE_KEY, TOKEN_VALUE);
    // Land them on Lesson 0
    window.location.href = "lessons/00-big-picture.html";
  } else {
    errEl.textContent = "Hmm — that password doesn't match. Try again.";
    input.value = "";
    input.focus();
  }
}

/* Called from every lesson page on load. If not unlocked, send to unlock.html */
function requireUnlock(pathToUnlock) {
  const ok = localStorage.getItem(STORAGE_KEY) === TOKEN_VALUE;
  if (!ok) {
    window.location.replace(pathToUnlock || "../unlock.html");
  }
}

/* Optional: a "Sign out" link can call this */
function clearUnlock() {
  localStorage.removeItem(STORAGE_KEY);
  window.location.href = "index.html";
}

/* ── Progress tracking ────────────────────────────────────────
   We remember which lessons the student has visited so the
   roadmap on Lesson 0 (and the dropdown nav) can show ✓ ticks. */

const PROGRESS_KEY = "ngc_galaxy_progress_v1";

function getCompletedLessons() {
  try {
    return new Set(JSON.parse(localStorage.getItem(PROGRESS_KEY) || "[]"));
  } catch (e) {
    return new Set();
  }
}

function markLessonComplete(num) {
  const done = getCompletedLessons();
  if (!done.has(num)) {
    done.add(num);
    localStorage.setItem(PROGRESS_KEY, JSON.stringify([...done]));
  }
}

function resetProgress() {
  localStorage.removeItem(PROGRESS_KEY);
}

/* ── Lesson dropdown menu helper ──────────────────────────────
   Call once on page load with the current lesson number.
   - Highlights the current entry
   - Adds ✓ next to every visited lesson
   - Adds 🔒 next to paid lessons if the visitor isn't unlocked  */

function initLessonMenu(currentLesson) {
  const items = document.querySelectorAll(".lesson-menu li a");
  if (!items.length) return;

  const done = getCompletedLessons();
  const unlocked = localStorage.getItem(STORAGE_KEY) === TOKEN_VALUE;

  items.forEach(a => {
    const num = parseInt(a.dataset.lesson, 10);
    if (Number.isNaN(num)) return;

    if (num === currentLesson) a.classList.add("current");

    // Tick if visited
    if (done.has(num)) {
      const tick = document.createElement("span");
      tick.className = "tick";
      tick.textContent = "✓";
      a.appendChild(tick);
    }

    // Free? show FREE; locked + not unlocked? show 🔒
    const isFree = (num === 0 || num === 1);
    if (isFree) {
      const tag = document.createElement("span");
      tag.className = "free-tag";
      tag.textContent = "FREE";
      a.appendChild(tag);
    } else if (!unlocked) {
      const lock = document.createElement("span");
      lock.className = "lock";
      lock.textContent = "🔒";
      a.appendChild(lock);
    }
  });
}

/* Used by Lesson 0 to put ✓ ticks on the roadmap tiles. */
function initRoadmapTicks() {
  const done = getCompletedLessons();
  document.querySelectorAll(".roadmap a").forEach(a => {
    const numEl = a.querySelector(".num");
    if (!numEl) return;
    const num = parseInt(numEl.textContent, 10);
    if (done.has(num)) {
      a.classList.add("done");
      const tick = document.createElement("span");
      tick.className = "tick";
      tick.textContent = "✓";
      a.appendChild(tick);
    }
  });
}
