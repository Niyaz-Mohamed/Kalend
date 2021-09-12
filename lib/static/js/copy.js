$(".share-button").click(function (event) {
  copyText = $("#share-link").value
  navigator.clipboard.writeText(copyText.value);
  alert("Copied the text:\n" + copyText.value);
});