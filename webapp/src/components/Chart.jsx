import React from "react";
import { Line } from "react-chartjs-2";
import "chartjs-plugin-annotation";

const Chart = () => {
  const data = {
    labels: ["January", "February", "March", "April", "May", "June", "July"],
    datasets: [
      {
        label: "",
        fill: false,
        lineTension: 0,
        backgroundColor: "rgba(75,192,192,0.4)",
        borderColor: "rgba(75,192,192,1)",
        borderCapStyle: "butt",
        borderDash: [],
        borderDashOffset: 0.0,
        borderJoinStyle: "miter",
        pointBorderColor: "rgba(75,192,192,1)",
        pointBackgroundColor: "#fff",
        pointBorderWidth: 1,
        pointHoverRadius: 5,
        pointHoverBackgroundColor: "rgba(75,192,192,1)",
        pointHoverBorderColor: "rgba(220,220,220,1)",
        pointHoverBorderWidth: 2,
        pointRadius: 1,
        pointHitRadius: 10,
        data: [10, 20, 30, 100]
      },
      {
        label: "",
        fill: false,
        lineTension: 0,
        backgroundColor: "rgba(75,192,192,0.4)",
        borderColor: "red",
        borderCapStyle: "butt",
        borderDash: [],
        borderDashOffset: 0.0,
        borderJoinStyle: "miter",
        pointBorderColor: "rgba(75,192,192,1)",
        pointBackgroundColor: "#fff",
        pointBorderWidth: 1,
        pointHoverRadius: 5,
        pointHoverBackgroundColor: "rgba(75,192,192,1)",
        pointHoverBorderColor: "rgba(220,220,220,1)",
        pointHoverBorderWidth: 2,
        pointRadius: 1,
        pointHitRadius: 10,
        data: [20, 40, 10, 100, 56, 55, 40]
      }
    ]
  };

  const options = {
    legend: {
      display: false
    },
    annotation: {
      annotations: [
        {
          drawTime: "afterDraw",
          borderColor: "black",
          borderWidth: 2,
          mode: "horizontal",
          type: "line",
          value: 60,
          scaleID: "y-axis-0",
        },
        {
          drawTime: "afterDraw",
          borderColor: "green",
          borderWidth: 2,
          mode: "horizontal",
          type: "line",
          value: 20,
          scaleID: "y-axis-0",
        }
      ]
    }
  };

  return <Line data={data} options={options} />;
};

export default Chart;
