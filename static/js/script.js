var spendChart = document.getElementById("spendChart").getContext("2d");

new Chart(spendChart, {
  type: 'line',
  data: {
    labels: spendLabels,
    datasets: [{
      label: "Spending",
      fill: true,
      data: dataSpends,
      backgroundColor: 'rgba(255, 0, 0, 0.75)',
      borderColor: 'rgba(255, 0, 0, 0.75)',
      borderWidth: 1,
      pointHoverRadius: 6,
      tension: 0.4
    }]
  },
  options: {
    responsive: true,
    scales: {
      x: {
        ticks: {
          display: false
        },
        grid: {
          display: false
        }
      },
      y: {
        beginAtZero: true
      }
    },
    plugins: {
      tooltip: {
        callbacks: {
          title: function(tooltipItems) {
            return tooltipItems[0].label;
          }
        }
      },
      legend: {
        display: false
      }
    }
  }
});

var earnChart = document.getElementById("earnChart").getContext("2d");

new Chart(earnChart, {
  type: 'line',
  data: {
    labels: earnLabels,
    datasets: [{
      label: "Incomes",
      fill: true,
      data: dataEarns,
      backgroundColor: 'rgba(0, 0, 255, 0.67)',
      borderColor: 'rgba(0, 0, 255, 0.67)',
      borderWidth: 1,
      pointHoverRadius: 6,
      tension: 0.4
    }]
  },
  options: {
    responsive: true,
    scales: {
      x: {
        ticks: {
          display: false
        },
        grid: {
          display: false
        }
      },
      y: {
        beginAtZero: true
      }
    },
    plugins: {
      tooltip: {
        callbacks: {
          title: function(tooltipItems) {
            return tooltipItems[0].label;
          }
        }
      },
      legend: {
        display: false
      }
    }
  }
});


document.querySelector(".modal .close").addEventListener("click", () => {
  document.getElementById("transaction-modal").style.display = "none";
});

window.addEventListener("click", (e) => {
  if (e.target.id === "transaction-modal") {
    document.getElementById("transaction-modal").style.display = "none";
  }
});

let currentTxnId = null;

document.querySelectorAll(".transactionRow").forEach(row => {
  row.addEventListener("click", () => {
    currentTxnId = row.dataset.id;
    document.getElementById("transactionId").value = row.dataset.id;

    
    // Fill and show values
    document.getElementById("modal-id").innerText = row.dataset.id;
    document.getElementById("modal-amount").innerText = row.dataset.amount;
    document.getElementById("modal-type").innerText = row.dataset.type === 'i' ? 'Income' : 'Expenditure';
    document.getElementById("modal-category").innerText = row.dataset.category;
    document.getElementById("modal-date").innerText = row.dataset.date;
    document.getElementById("modal-time").innerText = row.dataset.time;

    // Fill edit inputs
    document.getElementById("edit-amount").value = row.dataset.amount;
    document.getElementById("edit-type").value = row.dataset.type;
    document.getElementById("edit-category").value = row.dataset.category;
    document.getElementById("edit-date").value = row.dataset.date;

    // QR fetch
    fetch(`/qr/${currentTxnId}`)
      .then(res => res.text())
      .then(qrDataUri => {
        document.getElementById("modal-qr").src = qrDataUri;
      });

    document.getElementById("transaction-modal").style.display = "flex";
  });
});

const editSaveBtn = document.getElementById("edit-save-btn");
let isEditMode = false;

editSaveBtn.addEventListener("click", function () {
  if (!isEditMode) {
    // Switch to edit mode
    isEditMode = true;
    editSaveBtn.textContent = "Save";

    // Show inputs, hide static text
    toggleEditFields(true);
  } else {
    // Save updated data
    const txnId = document.getElementById("transactionId").value;
    const updatedData = {
      amount: document.getElementById("edit-amount").value,
      transaction_type: document.getElementById("edit-type").value,
      category: document.getElementById("edit-category").value,
      date_created: document.getElementById("edit-date").value
    };

    fetch(`/edit/${txnId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updatedData)
    })
      .then((res) => {
        if (res.ok) {
          alert("Transaction updated!");
          location.reload();
        } else {
          alert("Failed to update.");
        }
      });

    isEditMode = false;
    editSaveBtn.textContent = "Edit";
    toggleEditFields(false);
  }
});

function toggleEditFields(enable) {
  // Toggle amount
  document.getElementById("modal-amount").style.display = enable ? "none" : "inline";
  document.getElementById("edit-amount").style.display = enable ? "inline" : "none";

  // Toggle type
  document.getElementById("modal-type").style.display = enable ? "none" : "inline";
  document.getElementById("edit-type").style.display = enable ? "inline" : "none";

  // Toggle category
  document.getElementById("modal-category").style.display = enable ? "none" : "inline";
  document.getElementById("edit-category").style.display = enable ? "inline" : "none";

  // Toggle date
  document.getElementById("modal-date").style.display = enable ? "none" : "inline";
  document.getElementById("edit-date").style.display = enable ? "inline" : "none";
}

document.getElementById("delete-btn").addEventListener("click", function () {
  const txnId = document.getElementById("transactionId").value;

  if (!txnId) {
    alert("No transaction selected to delete.");
    return;
  }

  const confirmDelete = confirm("Are you sure you want to delete this transaction?");
  if (!confirmDelete) return;

  fetch(`/delete/${txnId}`, {
    method: "DELETE"
  })
  .then((response) => {
    if (response.ok) {
      alert("Transaction deleted successfully.");
      location.reload();
    } else {
      alert("Failed to delete transaction.");
    }
  });
});
