document.addEventListener('DOMContentLoaded', () => {
  // New Package
  document.getElementById("newPackageButton").onclick = () => {
    clearForm();
    document.getElementById("newPackageModal").style.display = "block";
  };

  // Edit Package: redirect to GET /update/<id>
  document.querySelectorAll(".updateButton").forEach(btn => {
    btn.onclick = () => {
      const id = btn.getAttribute("data-id");
      window.location.href = `/packages/update/${id}`;
    };
  });

  // Modal close
  document.getElementById("closeModal").onclick = hideModal;
  document.getElementById("cancelModal").onclick = hideModal;
  window.onclick = e => {
    if (e.target === document.getElementById("newPackageModal")) {
      hideModal();
    }
  };

  // Alert close
  document.querySelector('.close-alert').onclick = () => {
    document.getElementById('alertMessage').classList.add('hidden');
  };
});

function hideModal() {
  document.getElementById("newPackageModal").style.display = "none";
}

function clearForm() {
  document.getElementById("package_name").value = '';
  document.getElementById("price").value        = '0.00';
  document.getElementById("active").selectedIndex = 0;
  const sel = document.getElementById("contents");
  [...sel.options].forEach(opt => opt.selected = false);
}

function showAlert(message, type) {
  const box  = document.getElementById('alertMessage');
  const text = document.getElementById('alertText');
  text.textContent = message;
  box.className = `fixed top-4 right-4 px-4 py-2 rounded shadow ${
    type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
  }`;
  box.classList.remove('hidden');
  setTimeout(() => box.classList.add('hidden'), 3000);
}
