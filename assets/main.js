/*
  TalkToWalk project page: mobile menu, route animation, BibTeX copy.
  The page is complete without this file; the script only adds behaviour.
  Language-specific labels live in data-* attributes in each HTML file.
  Each feature runs in isolation: if one fails, it falls back to the
  no-JavaScript version of itself and the others keep working.
*/
(() => {
  "use strict";

  const root = document.documentElement;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  // MediaQueryList.addEventListener is missing in Safari before 14.
  const onMediaChange = (query, handler) => {
    if (typeof query.addEventListener === "function") query.addEventListener("change", handler);
    else if (typeof query.addListener === "function") query.addListener(handler);
  };

  const run = (name, init, fallback) => {
    try {
      init();
    } catch (error) {
      try {
        fallback();
      } catch (ignored) {
        /* nothing more to undo */
      }
      if (window.console) window.console.error(`TalkToWalk: ${name} disabled`, error);
    }
  };

  /* Mobile menu: a disclosure button that shows or hides the section links. */
  function initNav() {
    const nav = document.querySelector(".site-nav");
    const toggle = document.querySelector(".nav-toggle");
    const list = document.getElementById("nav-list");
    if (!nav || !toggle || !list) return;

    const isOpen = () => toggle.getAttribute("aria-expanded") === "true";
    const setOpen = (open) => toggle.setAttribute("aria-expanded", String(open));

    toggle.addEventListener("click", () => setOpen(!isOpen()));
    list.addEventListener("click", (event) => {
      if (event.target.closest("a")) setOpen(false);
    });
    // Close the menu when keyboard focus moves to an element outside it, so it never covers
    // the focused element. (relatedTarget is null for clicks on the menu's own padding;
    // clicks outside are handled by the document listener below.)
    nav.addEventListener("focusout", (event) => {
      if (isOpen() && event.relatedTarget && !nav.contains(event.relatedTarget)) setOpen(false);
    });
    document.addEventListener("click", (event) => {
      if (isOpen() && !nav.contains(event.target)) setOpen(false);
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && isOpen()) {
        setOpen(false);
        toggle.focus();
      }
    });
    onMediaChange(window.matchMedia("(min-width: 900px)"), () => setOpen(false));
    toggle.hidden = false;
  }

  function navFallback() {
    root.classList.add("nav-static");
    const toggle = document.querySelector(".nav-toggle");
    if (toggle) toggle.hidden = true;
  }

  /* Hero illustration: the robot walks the route and the command it is following is highlighted. */
  const routeCard = document.querySelector("[data-route]");

  function revealTrail() {
    const trail = routeCard && routeCard.querySelector(".map-trail");
    if (trail) trail.style.strokeDashoffset = "0";
  }

  function initRoute() {
    if (!routeCard) return;

    const trail = routeCard.querySelector(".map-trail");
    const robot = routeCard.querySelector(".map-robot");
    const button = routeCard.querySelector(".route-toggle");
    const label = routeCard.querySelector(".route-toggle-label");
    const steps = Array.from(routeCard.querySelectorAll(".route-step"));
    const junctions = Array.from(routeCard.querySelectorAll(".junction"));
    if (!trail || !robot || !button || !label || steps.length !== junctions.length + 1) {
      throw new Error("route markup is incomplete");
    }
    if (typeof trail.getTotalLength !== "function") throw new Error("SVG geometry API unavailable");

    const total = trail.getTotalLength();
    if (!total) throw new Error("route has no length");
    // Dash values use the path's pathLength attribute (1000), positions use real lengths.
    const dashLength = Number(trail.getAttribute("pathLength")) || total;

    const WALK_MS = 13000; // one lap
    const HOLD_MS = 2200; // pause on "stop" before the next lap
    const CYCLE_MS = WALK_MS + HOLD_MS;

    // Distance along the route at which the robot is closest to each junction.
    const samples = [];
    for (let s = 0; s <= total; s += 1.5) {
      const p = trail.getPointAtLength(s);
      samples.push([s, p.x, p.y]);
    }
    const junctionAt = junctions.map((node) => {
      const cx = Number(node.getAttribute("cx"));
      const cy = Number(node.getAttribute("cy"));
      let best = 0;
      let bestDist = Infinity;
      for (const [s, x, y] of samples) {
        const d = (x - cx) ** 2 + (y - cy) ** 2;
        if (d < bestDist) {
          bestDist = d;
          best = s;
        }
      }
      return best;
    });

    const headingAt = (s) => {
      const a = trail.getPointAtLength(Math.max(0, s - 1));
      const b = trail.getPointAtLength(Math.min(total, s + 1));
      return (Math.atan2(b.y - a.y, b.x - a.x) * 180) / Math.PI;
    };

    const placeRobot = (s) => {
      const p = trail.getPointAtLength(s);
      robot.setAttribute(
        "transform",
        `translate(${p.x.toFixed(2)} ${p.y.toFixed(2)}) rotate(${headingAt(s).toFixed(1)})`
      );
    };

    const pulse = (node) => {
      node.classList.remove("is-hit");
      void node.getBoundingClientRect(); // restart the CSS animation
      node.classList.add("is-hit");
    };
    junctions.forEach((node) => node.addEventListener("animationend", () => node.classList.remove("is-hit")));

    let passedBefore = 0;

    // Command k is the model's input on the way to junction k; the last one ("stop") ends the lap.
    function draw(distance) {
      const s = Math.min(Math.max(distance, 0), total);
      trail.style.strokeDashoffset = String(dashLength * (1 - s / total));
      placeRobot(s);

      let passed = 0;
      junctions.forEach((node, i) => {
        const isPassed = s >= junctionAt[i];
        node.classList.toggle("is-passed", isPassed);
        if (isPassed) passed += 1;
      });
      if (passed > passedBefore) pulse(junctions[passed - 1]);
      passedBefore = passed;

      steps.forEach((step, i) => {
        step.classList.toggle("is-active", i === passed);
        step.classList.toggle("is-done", i < passed);
      });
    }

    // Static overview: the whole route drawn, robot at the start, no highlighted command.
    function showOverview() {
      routeCard.classList.remove("is-animating");
      revealTrail();
      junctions.forEach((node) => node.classList.add("is-passed"));
      steps.forEach((step) => step.classList.remove("is-active", "is-done"));
      placeRobot(0);
    }

    let playing = !reducedMotion.matches;
    let visible = true;
    let elapsed = 0;
    let startTime = null;
    let frame = 0;
    let lap = -1;

    function tick(now) {
      if (startTime === null) startTime = now - elapsed;
      elapsed = now - startTime;

      const currentLap = Math.floor(elapsed / CYCLE_MS);
      if (currentLap !== lap) {
        lap = currentLap;
        passedBefore = 0;
      }
      const t = elapsed % CYCLE_MS;
      draw(t < WALK_MS ? (t / WALK_MS) * total : total);

      frame = window.requestAnimationFrame(tick);
    }

    function update() {
      const shouldRun = playing && visible && !document.hidden;
      if (shouldRun && !frame) {
        startTime = null;
        routeCard.classList.add("is-animating");
        frame = window.requestAnimationFrame(tick);
      } else if (!shouldRun && frame) {
        window.cancelAnimationFrame(frame);
        frame = 0;
      }
      button.dataset.state = playing ? "playing" : "paused";
      label.textContent = playing ? button.dataset.labelPause : button.dataset.labelPlay;
    }

    if (playing) draw(0);
    else showOverview();

    button.addEventListener("click", () => {
      playing = !playing;
      update();
    });

    if ("IntersectionObserver" in window) {
      new IntersectionObserver(
        (entries) => {
          visible = entries[entries.length - 1].isIntersecting;
          update();
        },
        { threshold: 0.1 }
      ).observe(routeCard);
    }
    document.addEventListener("visibilitychange", update);
    onMediaChange(reducedMotion, (event) => {
      if (event.matches && playing) {
        playing = false;
        update();
      }
    });

    button.hidden = false;
    update();
  }

  function routeFallback() {
    if (!routeCard) return;
    routeCard.classList.remove("is-animating");
    revealTrail();
    const button = routeCard.querySelector(".route-toggle");
    if (button) button.hidden = true;
  }

  /* Copy the BibTeX entry; if the clipboard is unavailable, select the text instead. */
  function initCopy() {
    document.querySelectorAll("[data-copy-target]").forEach((button) => {
      const source = document.getElementById(button.dataset.copyTarget);
      const status = document.getElementById(button.dataset.copyStatus);
      if (!source || !status) return;

      let clearTimer = 0;
      const announce = (message) => {
        status.textContent = "";
        window.clearTimeout(clearTimer);
        // A short delay makes screen readers announce the same message again.
        window.setTimeout(() => {
          status.textContent = message;
        }, 60);
        clearTimer = window.setTimeout(() => {
          status.textContent = "";
        }, 6000);
      };

      const selectSource = () => {
        const range = document.createRange();
        range.selectNodeContents(source);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
      };

      button.addEventListener("click", async () => {
        try {
          if (!navigator.clipboard || !window.isSecureContext) throw new Error("Clipboard API unavailable");
          await navigator.clipboard.writeText(`${source.textContent.trim()}\n`);
          announce(button.dataset.labelCopied);
        } catch (error) {
          selectSource();
          announce(button.dataset.labelFailed);
        }
      });
      button.hidden = false;
    });
  }

  function copyFallback() {
    document.querySelectorAll("[data-copy-target]").forEach((button) => {
      button.hidden = true;
    });
  }

  run("menu", initNav, navFallback);
  run("route animation", initRoute, routeFallback);
  run("copy button", initCopy, copyFallback);
})();
