(function setupAds() {
  const config = window.PB_ADS || { enabled: false, provider: "placeholder", slots: {} };
  const nodes = document.querySelectorAll("[data-ad]");
  const useAdsense = Boolean(config.enabled && config.provider === "adsense" && config.adsenseClient);
  const showPlaceholders = Boolean(config.showPlaceholders);

  if (useAdsense && !document.querySelector("script[data-pb-adsense]")) {
    const script = document.createElement("script");
    script.async = true;
    script.dataset.pbAdsense = "true";
    script.crossOrigin = "anonymous";
    script.src = `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${encodeURIComponent(config.adsenseClient)}`;
    document.head.appendChild(script);
  }

  nodes.forEach((node) => {
    const key = node.getAttribute("data-ad");
    const slot = config.slots[key];
    const live = Boolean(useAdsense && slot && slot.adsenseSlot);
    if (!config.enabled || !slot || (!live && !showPlaceholders)) {
      node.hidden = true;
      return;
    }
    node.hidden = false;
    node.setAttribute("aria-label", "Advertisement");
    if (live) {
      node.innerHTML = "";
      const ins = document.createElement("ins");
      ins.className = "adsbygoogle";
      ins.style.display = "block";
      ins.setAttribute("data-ad-client", config.adsenseClient);
      ins.setAttribute("data-ad-slot", slot.adsenseSlot);
      ins.setAttribute("data-ad-format", "auto");
      ins.setAttribute("data-full-width-responsive", "true");
      node.appendChild(ins);
      const push = () => {
        try {
          (window.adsbygoogle = window.adsbygoogle || []).push({});
        } catch (_error) {
          /* AdSense script may still be loading */
        }
      };
      if (window.adsbygoogle) push();
      else window.addEventListener("load", push, { once: true });
      return;
    }
    const placeholder = node.querySelector(".ad-placeholder");
    if (placeholder) placeholder.textContent = slot.size.replace("x", " × ");
  });

  document.querySelectorAll(".ad-rail, .ad-band").forEach((group) => {
    const visible = [...group.querySelectorAll("[data-ad]")].some((node) => !node.hidden);
    group.hidden = !visible;
  });
  const rail = document.querySelector(".ad-rail");
  if (!rail || rail.hidden) {
    document.querySelector(".page-shell")?.classList.add("no-rail");
  }
})();
