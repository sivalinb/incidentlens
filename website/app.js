const scenarios = {
  payment: {
    metricTitle: "Checkout error rate", unit: "%", values: [.6, .7, 12.4, 28.2, 27.8],
    metric: "28.2%", metricSummary: "Baseline 0.6%; incident peak 28.2%",
    logs: ["ERROR checkout - connection refused", "WARN checkout - order not committed", "INFO payment - health check OK"],
    spans: ["frontend - POST /checkout - ERROR", "checkout - Checkout - ERROR", "payment - Charge - UNAVAILABLE"],
    traceSummary: "Failure occurs before payment request handling.",
    cause: "Invalid payment-service address", confidence: "92% confidence",
    rationale: "All three signals agree; the successful payment health check weakens a crashed-process theory.",
    counter: "Payment is healthy at its configured endpoint, so the critic favors a caller-address mismatch.",
    recommendation: "Restore the approved payment-service endpoint.",
    verification: "Re-run checkout traffic and confirm errors, logs, and traces return to baseline."
  },
  email: {
    metricTitle: "Email resident memory", unit: " MiB", values: [118, 206, 322, 441, 536],
    metric: "536 MiB", metricSummary: "Baseline 118 MiB; monotonic growth to 536 MiB",
    logs: ["WARN email - GC reclaimed only 2%", "WARN email - retained allocation set increasing", "INFO email - requests remain successful"],
    spans: ["checkout - PlaceOrder - OK", "email - SendEmail - OK"],
    traceSummary: "Business requests succeed while memory grows.",
    cause: "Email process retains allocations", confidence: "91% confidence",
    rationale: "Monotonic growth and weak reclamation coexist with healthy request traces.",
    counter: "Successful requests weaken dependency-outage explanations.",
    recommendation: "Disable the leak fault and recycle the email instance after approval.",
    verification: "Confirm memory stabilizes while email traces remain successful."
  },
  kafka: {
    metricTitle: "Accounting consumer lag", unit: " messages", values: [104, 890, 4200, 9100, 12480],
    metric: "12,480 messages", metricSummary: "Baseline 104; incident peak 12,480",
    logs: ["WARN accounting - poll interval exceeded", "INFO kafka - producer throughput 3.4x baseline"],
    spans: ["checkout - PublishOrder - OK", "accounting - Consume - 8.2 s"],
    traceSummary: "Consumption is slow while publishing remains healthy.",
    cause: "Consumer delay plus producer pressure", confidence: "90% confidence",
    rationale: "Lag, slow consumer spans, and increased producer throughput point to the same bottleneck.",
    counter: "Healthy publishing weakens a checkout regression or complete broker outage.",
    recommendation: "Reduce consumer delay or scale accounting consumption after approval.",
    verification: "Confirm lag drains and producer/consumer rates converge."
  }
};

const byId = id => document.getElementById(id);

function render() {
  const scenario = scenarios[byId("scenario").value];
  byId("metric-title").textContent = scenario.metricTitle;
  byId("metric-value").textContent = scenario.metric;
  byId("metric-summary").textContent = scenario.metricSummary;
  const max = Math.max(...scenario.values);
  byId("chart").innerHTML = scenario.values.map(value =>
    `<span class="bar" style="height:${Math.max(5, value / max * 100)}%" title="${value}${scenario.unit}"></span>`
  ).join("");
  byId("log-lines").textContent = scenario.logs.join("\n\n");
  byId("trace-path").innerHTML = scenario.spans.map(item => `<div class="span"><span>${item}</span></div>`).join("");
  byId("trace-summary").textContent = scenario.traceSummary;
  byId("cause").textContent = scenario.cause;
  byId("confidence").textContent = scenario.confidence;
  byId("rationale").textContent = scenario.rationale;
  byId("counter").textContent = scenario.counter;
  byId("recommendation").textContent = scenario.recommendation;
  byId("verification").textContent = scenario.verification;
  byId("decision-status").textContent = "State: awaiting_approval";
}

document.querySelectorAll(".tab").forEach(tab => tab.addEventListener("click", () => {
  document.querySelectorAll(".tab,.panel").forEach(item => item.classList.remove("active"));
  tab.classList.add("active");
  byId(tab.dataset.tab).classList.add("active");
}));
byId("scenario").addEventListener("change", render);
byId("approve").addEventListener("click", () => {
  byId("decision-status").textContent = "State: approved_pending_verification - no production write";
});
render();

