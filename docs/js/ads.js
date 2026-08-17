(function setupAds() {
  const config = window.PB_ADS || { enabled: false, provider: "placeholder", slots: {} };
  const nodes = document.querySelectorAll("[data-ad]");
  if (!config.enabled) {
    nodes.forEach((node) => {
      node.hidden = true;
    });
    return;
  }

  const useAdsense = config.provider === "adsense" && config.adsenseClient;
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
    if (!slot) {
      node.hidden = true;
      return;
    }
    node.setAttribute("aria-label", "Advertisement");
    if (useAdsense && slot.adsenseSlot) {
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
    const size = node.classList.contains("ad-mobile") ? slot.mobileSize || slot.size : slot.size;
    const placeholder = node.querySelector(".ad-placeholder");
    if (placeholder) placeholder.textContent = size.replace("x", " × ");
  });
})();
