document.addEventListener("DOMContentLoaded", (event) => {
  const form = document.querySelector("form");
  form.addEventListener("keypress", (event) => {
    if (event.key === "Enter") {
      form.submit();
    }
  });
  // Select all delete buttons in the list
  const deleteButtons = document.querySelectorAll(".inline");

  // Loop through each element using forEach and add event listener
  deleteButtons.forEach((item) => {
    item.addEventListener("click", function () {
      // Get the URL from the data attribute
      const url = this.getAttribute("data-url");
      // Redirect to the URL
      window.location.href = url;
    });
  });

  // Get all set date buttons in the list
  const setDateButtons = document.querySelectorAll(
    "#task-list li .setDateButton"
  );

  // Loop through each element using forEach and add event listener
  setDateButtons.forEach((item, index) => {
    item.addEventListener("click", function () {
      const datePicker = document.getElementById("date" + item.id);
      const dateValue = datePicker.value;
      if (dateValue) {
        // Get the URL from the data attribute
        const url = this.getAttribute("data-url") + "?date=" + dateValue;
        // Redirect to the URL
        window.location.href = url;
      }
    });
  });

  // Get all mark complete buttons in the list
  const markCompleteButtons = document.querySelectorAll(
    "#task-list li .markCompleteButton"
  );

  // Loop through each element using forEach and add event listener
  markCompleteButtons.forEach((item, index) => {
    item.addEventListener("click", function () {
      const url = this.getAttribute("data-url");
      // Redirect to the URL
      window.location.href = url;
    });
  });
});
