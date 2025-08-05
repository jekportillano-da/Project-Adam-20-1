document.getElementById("budget-form").addEventListener("submit", async function(event) {
  event.preventDefault();

  const budget = document.getElementById("budget").value;
  const duration = document.getElementById("duration").value;
  const suggestionBox = document.getElementById("suggestion");

  suggestionBox.textContent = "Thinking...";

  try {
    const res = await fetch("/api/tip", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        budget: budget,
        duration: duration
      })
    });

    const data = await res.json();
    const lines = data.tip.trim().split("\n").filter(line => line.trim() !== "");
    let html = "";
    let hasAdvice = false;

    lines.forEach(line => {
      if (line.startsWith("Title:")) {
        html += `<strong>${line.replace("Title:", "").trim()}</strong><br>`;
      } else if (line.startsWith("Breakdown:")) {
        html += `<u>Breakdown:</u><br>`;
      } else if (line.startsWith("- ")) {
        html += `${line}<br>`;
      } else if (line.startsWith("Advice:")) {
        html += `<i>${line.replace("Advice:", "").trim()}</i>`;
        hasAdvice = true;
      }
    });

    // Fallback advice
    if (!hasAdvice) {
      html += `<br><i>Tip: Be mindful of needs vs. wants. Every peso counts!</i>`;
    }

    suggestionBox.innerHTML = html;
  } catch (err) {
    console.error("Error fetching tip:", err);
    suggestionBox.textContent = "Something went wrong. Please try again.";
  }
});
