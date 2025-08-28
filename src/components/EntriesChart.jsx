import React, { useEffect, useRef } from "react";
import Chart from "chart.js/auto";

function EntriesChart({ data, onBarClick }) {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    if (chartRef.current) {
      chartRef.current.destroy();
    }

    const ctx = canvasRef.current.getContext("2d");
    chartRef.current = new Chart(ctx, {
      type: "bar",
      data: {
        labels: data.map((d) => d.label),
        datasets: [
          {
            label: "Entries",
            data: data.map((d) => d.value),
            backgroundColor: "#0f62fe",
          },
        ],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        onClick: (_, elements) => {
          if (elements.length > 0) {
            const index = elements[0].index;
            const clickedLabel = data[index].label;
            const clickedKey = data[index].key;
            onBarClick(clickedKey);
          }
        },
      },
    });

    return () => {
      if (chartRef.current) chartRef.current.destroy();
    };
  }, [data, onBarClick]);

  const chartHeight = data.length * 25;

  return (
    <div style={{ maxHeight: "600px", overflowY: "auto", border: "1px solid #393939", padding: "0.5rem" }}>
      <div style={{ position: "relative", height: `${chartHeight}px`, minWidth: "600px" }}>
        <canvas ref={canvasRef}></canvas>
      </div>
    </div>
  );
}

export default EntriesChart;