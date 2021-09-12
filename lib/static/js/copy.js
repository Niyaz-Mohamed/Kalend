$(".share-button").click(function (event) {
  copyText = $("#share-link").text()
  navigator.clipboard.writeText(copyText);
  alert("Copied the text:\n" + copyText);
});