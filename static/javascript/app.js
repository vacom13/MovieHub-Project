var swiper = new Swiper(".mySwiper", {
        slidesPerView: "auto",
        spaceBetween: 30,
        freeMode: true,
      });

var element = document.querySelector("#search-input");
var button = document.querySelector("#btn");
var sb = document.getElementById("box");
function myScript(){
    txt = element.value;
    if (txt==""){
        button.disabled = true;
        sb.classList.remove('search-box-active');
    }
    else{
        button.disabled = false;
        sb.classList.add('search-box-active');
    }
}
element.addEventListener("input", myScript);