(function() {
  const pageData = {
    url: window.location.href,
    bodyText: document.body.innerText ? document.body.innerText.substring(0, 3000) : "",
    formsCount: document.querySelectorAll('form').length,
    hasPasswordOrOtpField: !!document.querySelector('input[type="password"]') || document.body.innerText.includes("OTP")
  };

  chrome.runtime.sendMessage({ action: "analyzeSite", data: pageData }, (response) => {
    if (response && response.isFake) {
      injectWarningBanner(response.reasons, response.confidence);
    }
  });
})();

function injectWarningBanner(reasons, confidence) {
  if (document.getElementById('govshield-alert-banner')) return;

  const banner = document.createElement('div');
  banner.id = 'govshield-alert-banner';
  banner.style = "position:fixed; top:0; left:0; width:100%; background-color:#d32f2f; color:#fff; text-align:center; padding:15px; z-index:999999; font-family:sans-serif; font-size:16px; box-shadow:0 4px 10px rgba(0,0,0,0.3);";

  banner.innerHTML = `
    <strong>⚠️ WARNING: SUSPECTED FRAUDULENT SITE DETECTED (${(confidence * 100).toFixed(0)}% Match)</strong><br>
    This portal matches patterns of a fake government scheme scam targeting rural citizens.<br>
    <small>Reason: ${reasons.join(' ')}</small>
    <button id="govshield-close" style="margin-left:20px; background:#fff; color:#d32f2f; border:none; padding:5px 10px; cursor:pointer; font-weight:bold;">Ignore</button>
  `;

  document.body.appendChild(banner);
  document.getElementById('govshield-close').addEventListener('click', () => banner.remove());
}
