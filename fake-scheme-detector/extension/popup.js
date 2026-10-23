document.getElementById('scanBtn').addEventListener('click', async () => {
  const statusBox = document.getElementById('statusBox');
  const scoreBox = document.getElementById('scoreBox');

  statusBox.innerText = "ANALYZING...";
  statusBox.style.backgroundColor = "#6c757d";
  statusBox.style.color = "#ffffff";

  let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab || !tab.id) {
    statusBox.innerText = "TAB CORRUPT";
    return;
  }

  // Scrape page DOM text layer cleanly
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => document.body.innerText
  }, async (results) => {
    if (!results || !results[0]) {
      statusBox.innerText = "DOM SCRAPE FAILED";
      return;
    }

    const scrapedText = results[0].result;

    try {
      const response = await fetch('http://127.0.0', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: tab.url,
          text: scrapedText.substring(0, 1500)
        })
      });

      const payload = await response.json();
      statusBox.innerText = payload.status;
      scoreBox.innerText = `Scam Risk Level: ${payload.scam_probability}`;

      // Dynamically alter dashboard layout based on response parameters
      if (payload.status.includes("SAFE")) {
        statusBox.style.backgroundColor = "#28a745"; // Green
        statusBox.style.color = "#ffffff";
      } else if (payload.status.includes("SUSPICIOUS")) {
        statusBox.style.backgroundColor = "#ffc107"; // Yellow
        statusBox.style.color = "#000000";
      } else {
        statusBox.style.backgroundColor = "#dc3545"; // Red
        statusBox.style.color = "#ffffff";
      }
    } catch (err) {
      statusBox.innerText = "SERVER OFFLINE";
      scoreBox.innerText = "Run api/main.py in PyCharm";
      statusBox.style.backgroundColor = "#343a40";
    }
  });
});