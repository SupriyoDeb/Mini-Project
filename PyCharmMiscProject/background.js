chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "analyzeSite") {
    const url = request.data.url;
    const bodyText = request.data.bodyText;

    let isFake = false;
    let reasons = [];
    let confidence = 0.0;

    const targetKeywords = ["pmkisan", "mnrega", "ayushman", "sukanya", "awas-yojana"];
    const containsKeyword = targetKeywords.some(kw => url.toLowerCase().includes(kw));
    const isOfficialGov = url.endsWith(".gov.in") || url.endsWith(".nic.in");

    if (containsKeyword && !isOfficialGov) {
      isFake = true;
      reasons.push("Uses government scheme keywords but is not hosted on a .gov.in or .nic.in domain.");
      confidence = 0.94;
    } else if (!isOfficialGov && (bodyText.includes("PM-KISAN") || bodyText.includes("MNREGA"))) {
      if (bodyText.includes("बैंक खाता") || bodyText.includes("आधार नंबर") || bodyText.includes("OTP")) {
        isFake = true;
        reasons.push("Unofficial site scraping sensitive text fields and banking terms.");
        confidence = 0.88;
      }
    }
    sendResponse({ isFake: isFake, confidence: confidence, reasons: reasons });
  }
  return true;
});
